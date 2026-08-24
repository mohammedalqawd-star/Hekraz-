"""Minimal append-only audit logging for CyberGuard operations."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass
class AuditEvent:
    actor_id: int
    action: str
    target: str | None
    status: str
    detail: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

def record(event: AuditEvent, path: str = "data/audit.jsonl") -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
