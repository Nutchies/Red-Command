from app.db.database import SessionLocal
from app.models.models import Action, Client

db = SessionLocal()

action_types = db.query(Action.action_type).distinct().all()
print(f'Action types: {[t[0] for t in action_types]}')

non_collect_actions = db.query(Action).filter(Action.action_type != 'collect').all()
print(f'\nNon-collect actions: {len(non_collect_actions)}')
for a in non_collect_actions[:20]:
    print(f'  ID: {a.id}, Client ID: {a.client_id}, Type: {a.action_type}, Content: {a.content[:50]}')

clients = db.query(Client).all()
print(f'\nTotal clients: {len(clients)}')
for c in clients:
    print(f'  ID: {c.id}, Client ID: {c.client_id}, Hostname: {c.hostname}')
    client_non_collect_actions = db.query(Action).filter(Action.client_id == c.id, Action.action_type != 'collect').all()
    print(f'    Non-collect actions: {len(client_non_collect_actions)}')
