"""Safe CTF training engine using local, non-destructive challenges."""
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Challenge:
    id: str
    title: str
    level: str
    objective: str
    hint: str
    points: int
    answer: str

CHALLENGES: List[Challenge] = [
    Challenge("web-001", "Security Headers", "Beginner", "Identify missing defensive HTTP headers in the lab.", "Inspect the supplied response headers.", 100, "content-security-policy"),
    Challenge("net-001", "DNS Investigation", "Beginner", "Analyze a supplied DNS dataset and identify suspicious records.", "Compare record types and TTL values.", 100, "event-17"),
    Challenge("ir-001", "Suspicious Login", "Intermediate", "Investigate supplied authentication logs and identify the anomalous session.", "Look for unusual time, location, and user-agent patterns.", 200, "event-17"),
]

class CTFEngine:
    def __init__(self):
        self.progress: Dict[int, Dict[str, bool]] = {}

    def get_challenges(self, level: str | None = None) -> list[Challenge]:
        if level is None:
            return CHALLENGES.copy()
        return [c for c in CHALLENGES if c.level.lower() == level.lower()]

    def get(self, challenge_id: str):
        return next((c for c in CHALLENGES if c.id == challenge_id), None)

    def submit(self, user_id: int, challenge_id: str, answer: str) -> bool:
        challenge = self.get(challenge_id)
        if not challenge:
            return False
        ok = answer.strip().lower() == challenge.answer.lower()
        if ok:
            self.progress.setdefault(user_id, {})[challenge_id] = True
        return ok

    def score(self, user_id: int) -> int:
        completed = self.progress.get(user_id, {})
        return sum(c.points for c in CHALLENGES if completed.get(c.id))
