"""Safe local Cyber Range manager.

This module only manages directories and metadata for isolated training labs.
It does not execute commands against external or real-world targets.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import uuid
from datetime import datetime, timezone

BASE = Path("labs")

@dataclass
class Lab:
    lab_id: str
    owner_id: int
    name: str
    status: str = "created"
    created_at: str = ""

class LabManager:
    def __init__(self, base: Path = BASE):
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)

    def create(self, owner_id: int, name: str = "Cyber Range") -> Lab:
        lab = Lab(str(uuid.uuid4()), owner_id, name, "created", datetime.now(timezone.utc).isoformat())
        folder = self.base / lab.lab_id
        folder.mkdir()
        (folder / "metadata.json").write_text(json.dumps(asdict(lab), ensure_ascii=False, indent=2), encoding="utf-8")
        return lab

    def set_status(self, lab_id: str, status: str) -> Lab:
        folder = self.base / lab_id
        meta = folder / "metadata.json"
        if not meta.exists():
            raise FileNotFoundError("Lab not found")
        data = json.loads(meta.read_text(encoding="utf-8"))
        if status not in {"created", "running", "stopped", "reset"}:
            raise ValueError("Invalid lab status")
        data["status"] = status
        meta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return Lab(**data)

    def reset(self, lab_id: str) -> Lab:
        return self.set_status(lab_id, "reset")

    def list(self):
        result = []
        for meta in self.base.glob("*/metadata.json"):
            result.append(Lab(**json.loads(meta.read_text(encoding="utf-8"))))
        return result
