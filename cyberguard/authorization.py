"""Authorization guard for practical security operations."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Authorization:
    authorization_id: str
    target: str
    approved_by: int
    starts_at: datetime
    expires_at: datetime

    def active(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.starts_at <= now <= self.expires_at

def is_target_authorized(auth: Authorization, target: str, user_id: int) -> bool:
    return auth.approved_by == user_id and auth.target == target and auth.active()
