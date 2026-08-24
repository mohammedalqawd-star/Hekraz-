"""Safe lifecycle manager for isolated Cyber Range labs."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class LabState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    RESET = "reset"

@dataclass
class Lab:
    lab_id: str
    owner_id: int
    state: LabState = LabState.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class LabManager:
    def __init__(self):
        self.labs: dict[str, Lab] = {}

    def create(self, lab_id: str, owner_id: int) -> Lab:
        if lab_id in self.labs:
            raise ValueError("Lab already exists")
        lab = Lab(lab_id=lab_id, owner_id=owner_id)
        self.labs[lab_id] = lab
        return lab

    def start(self, lab_id: str, owner_id: int) -> Lab:
        lab = self._owned(lab_id, owner_id)
        lab.state = LabState.RUNNING
        return lab

    def stop(self, lab_id: str, owner_id: int) -> Lab:
        lab = self._owned(lab_id, owner_id)
        lab.state = LabState.STOPPED
        return lab

    def reset(self, lab_id: str, owner_id: int) -> Lab:
        lab = self._owned(lab_id, owner_id)
        lab.state = LabState.RESET
        return lab

    def _owned(self, lab_id: str, owner_id: int) -> Lab:
        lab = self.labs.get(lab_id)
        if lab is None:
            raise KeyError("Lab not found")
        if lab.owner_id != owner_id:
            raise PermissionError("You do not own this lab")
        return lab
