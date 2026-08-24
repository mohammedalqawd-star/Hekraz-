"""Small role-based access control layer for Telegram users."""
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ANALYST = "analyst"
    ADMIN = "admin"

def can_manage_users(role: Role) -> bool:
    return role == Role.ADMIN

def can_manage_labs(role: Role) -> bool:
    return role in {Role.ANALYST, Role.ADMIN}

def can_view_audit(role: Role) -> bool:
    return role == Role.ADMIN

def can_run_lab(role: Role) -> bool:
    return role in {Role.ANALYST, Role.ADMIN}

def can_run_real_target(role: Role) -> bool:
    # Real-target operations require a separate authorization check.
    return False
