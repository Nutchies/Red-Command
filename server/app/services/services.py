from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Client, Action, AIExtracted
from app.services.ai_analyzer import AIAnalyzer
import time


class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_client(self, client_id: str, hostname: str, ip: str, version: str) -> Client:
        client = self.db.query(Client).filter(Client.client_id == client_id).first()
        if client:
            client.hostname = hostname
            client.ip_address = ip
            client.last_heartbeat = time.time()
            client.status = "online"
            client.version = version
        else:
            client = Client(
                client_id=client_id,
                hostname=hostname,
                ip_address=ip,
                status="online",
                last_heartbeat=time.time(),
                version=version
            )
            self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update_heartbeat(self, client_id: str, hostname: str, ip: str, version: str) -> Client:
        return self.get_or_create_client(client_id, hostname, ip, version)

    def get_all_clients(self) -> List[Client]:
        return self.db.query(Client).order_by(desc(Client.last_heartbeat)).all()

    def get_online_clients(self) -> List[Client]:
        return self.db.query(Client).filter(Client.status == "online").all()

    def check_offline_clients(self, timeout: int = 90) -> int:
        current_time = time.time()
        offline_count = 0

        clients = self.db.query(Client).filter(Client.status == "online").all()
        for client in clients:
            if client.last_heartbeat and (current_time - client.last_heartbeat) > timeout:
                client.status = "offline"
                offline_count += 1

        self.db.commit()
        return offline_count

    def delete_client(self, client_id: int) -> bool:
        from sqlalchemy import text
        result = self.db.execute(text('SELECT id FROM clients WHERE id = :client_id'), {'client_id': client_id})
        row = result.fetchone()
        if not row:
            return False
        self.db.execute(text('DELETE FROM actions WHERE client_id = :client_id'), {'client_id': client_id})
        self.db.execute(text('DELETE FROM clients WHERE id = :client_id'), {'client_id': client_id})
        self.db.commit()
        return True


class ActionService:
    def __init__(self, db: Session):
        self.db = db

    def create_action(self, client_id: int, action_type: str, content: str,
                     result: str, exit_code: int, timestamp: float) -> Action:
        action = Action(
            client_id=client_id,
            action_type=action_type,
            content=content,
            result=result,
            exit_code=exit_code,
            timestamp=timestamp
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def create_actions_batch(self, client_id: int, actions_data: List[dict]) -> List[Action]:
        actions = []
        analyzer = AIAnalyzer(self.db)

        for action_data in actions_data:
            action = self.create_action(
                client_id=client_id,
                action_type=action_data.get("action_type", "unknown"),
                content=action_data.get("content", ""),
                result=action_data.get("result", ""),
                exit_code=action_data.get("exit_code", 0),
                timestamp=action_data.get("timestamp", time.time())
            )
            actions.append(action)

            try:
                analyzer.analyze_and_save(action)
            except Exception:
                pass

        return actions

    def get_actions(self, limit: int = 100, offset: int = 0,
                   client_id: Optional[int] = None,
                   action_type: Optional[str] = None) -> List[Action]:
        query = self.db.query(Action)

        if client_id:
            query = query.filter(Action.client_id == client_id)
        if action_type:
            query = query.filter(Action.action_type == action_type)

        return query.order_by(desc(Action.timestamp)).offset(offset).limit(limit).all()

    def get_actions_today_count(self) -> int:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from sqlalchemy import func
        return self.db.query(func.count(Action.id)).filter(
            Action.created_at >= today_start
        ).scalar()
