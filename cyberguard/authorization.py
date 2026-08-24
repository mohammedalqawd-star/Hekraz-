"""Authorization gate for local Cyber Range operations."""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import secrets
from urllib.parse import urlparse

@dataclass
class Authorization:
    authorization_id: str
    user_id: int
    target: str
    scope: str
    starts_at: datetime
    expires_at: datetime
    approved: bool = True

    def active(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.approved and self.starts_at <= now <= self.expires_at

def is_local_target(target: str) -> bool:
    value = target.strip()
    if value in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        host = urlparse(value if "://" in value else f"http://{value}").hostname
        return host in {"localhost", "127.0.0.1", "::1"}
    except ValueError:
        return False

def issue_authorization(user_id: int, target: str, scope: str = "CTF/LAB", ttl_hours: int = 2) -> Authorization:
    if not is_local_target(target):
        raise ValueError("Only local Cyber Range targets are allowed.")
    if not 1 <= ttl_hours <= 24:
        raise ValueError("ttl_hours must be between 1 and 24")
    now = datetime.now(timezone.utc)
    return Authorization(
        authorization_id="AUTH-" + secrets.token_hex(6).upper(),
        user_id=user_id,
        target=target,
        scope=scope,
        starts_at=now,
        expires_at=now + timedelta(hours=ttl_hours),
    )

def is_target_authorized(auth: Authorization, target: str, user_id: int) -> bool:
    return auth.user_id == user_id and auth.target == target and is_local_target(target) and auth.active()
