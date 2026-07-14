import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Action, AIExtracted


class AIAnalyzer:
    PATTERNS = {
        "port": re.compile(r'(\d+)/(tcp|udp)\s+(open|closed|filtered)', re.IGNORECASE),
        "service": re.compile(r'(\d+)/(tcp|udp)\s+\w+\s*(\w+)', re.IGNORECASE),
        "vulnerability": re.compile(r'(CVE-\d{4}-\d{4,})|(\bvuln\w*\b)|(\bexploit\b)', re.IGNORECASE),
        "credential": re.compile(r'(\w+:|\w+@)([^\s]+)', re.IGNORECASE),
        "ip_address": re.compile(r'\b(\d{1,3}\.){3}\d{1,3}\b'),
        "hostname": re.compile(r'\b([a-zA-Z][a-zA-Z0-9.-]+)\b'),
    }

    def __init__(self, db: Session):
        self.db = db

    def analyze_action(self, action: Action) -> List[Dict[str, Any]]:
        results = []
        content = action.content or ""
        result = action.result or ""

        text = f"{content} {result}"

        ports = self._extract_ports(text)
        for port in ports:
            results.append({
                "type": "port",
                "value": {"port": port["port"], "protocol": port["protocol"], "status": port["status"]},
                "confidence": 0.9
            })

        credentials = self._extract_credentials(text)
        for cred in credentials:
            results.append({
                "type": "credential",
                "value": {"username": cred["username"], "password": cred["password"]},
                "confidence": 0.7
            })

        ips = self._extract_ips(text)
        for ip in ips:
            results.append({
                "type": "ip_address",
                "value": {"ip": ip},
                "confidence": 0.95
            })

        vulns = self._extract_vulnerabilities(text)
        for vuln in vulns:
            results.append({
                "type": "vulnerability",
                "value": {"cve": vuln},
                "confidence": 0.85
            })

        return results

    def _extract_ports(self, text: str) -> List[Dict[str, str]]:
        ports = []
        for match in self.PATTERNS["port"].finditer(text):
            ports.append({
                "port": int(match.group(1)),
                "protocol": match.group(2).lower(),
                "status": match.group(3).lower()
            })
        return ports

    def _extract_credentials(self, text: str) -> List[Dict[str, str]]:
        credentials = []
        for match in self.PATTERNS["credential"].finditer(text):
            full_match = match.group(0)
            if ':' in full_match and '@' not in full_match:
                parts = full_match.split(':', 1)
                if len(parts) == 2:
                    credentials.append({
                        "username": parts[0],
                        "password": parts[1]
                    })
        return credentials

    def _extract_ips(self, text: str) -> List[str]:
        ips = set()
        for match in self.PATTERNS["ip_address"].finditer(text):
            ip = match.group(0)
            if not ip.startswith('0.') and not ip.startswith('255.'):
                ips.add(ip)
        return list(ips)

    def _extract_vulnerabilities(self, text: str) -> List[str]:
        vulns = []
        for match in self.PATTERNS["vulnerability"].finditer(text):
            if match.group(1):
                vulns.append(match.group(1))
        return vulns

    def analyze_and_save(self, action: Action) -> List[AIExtracted]:
        results = self.analyze_action(action)
        extracted_objects = []

        for result in results:
            extracted = AIExtracted(
                client_id=action.client_id,
                source_action_id=action.id,
                type=result["type"],
                value=result["value"],
                confidence=result["confidence"]
            )
            self.db.add(extracted)
            extracted_objects.append(extracted)

        self.db.commit()
        return extracted_objects

    def get_statistics(self) -> Dict[str, int]:
        stats = {}

        stats["ports"] = self.db.query(AIExtracted).filter(
            AIExtracted.type == "port"
        ).count()

        stats["credentials"] = self.db.query(AIExtracted).filter(
            AIExtracted.type == "credential"
        ).count()

        stats["vulnerabilities"] = self.db.query(AIExtracted).filter(
            AIExtracted.type == "vulnerability"
        ).count()

        stats["ip_addresses"] = self.db.query(AIExtracted).filter(
            AIExtracted.type == "ip_address"
        ).count()

        return stats
