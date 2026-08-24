"""Safe CTF challenge catalog and progress helpers."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Challenge:
    id: str
    title: str
    level: str
    objective: str
    hint: str
    points: int

CHALLENGES = [
    Challenge("web-001", "Security Headers", "Beginner", "Identify missing defensive HTTP headers in the lab.", "Inspect the response headers.", 100),
    Challenge("net-001", "DNS Investigation", "Beginner", "Analyze a supplied DNS dataset and identify suspicious records.", "Compare record types and TTL values.", 100),
    Challenge("ir-001", "Suspicious Login", "Intermediate", "Investigate supplied authentication logs and identify the anomalous session.", "Look for unusual time, location, and user-agent patterns.", 200),
]

def get_challenges(level: str | None = None) -> list[Challenge]:
    if level is None:
        return CHALLENGES.copy()
    return [challenge for challenge in CHALLENGES if challenge.level.lower() == level.lower()]
