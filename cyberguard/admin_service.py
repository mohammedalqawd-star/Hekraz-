"""Administrative service layer used by the Telegram admin panel."""
from .storage import Storage

ROLES = {"user", "analyst", "admin"}

class AdminService:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.storage.init()

    def is_admin(self, user_id: int) -> bool:
        return self.storage.role(user_id) == "admin"

    def set_role(self, actor_id: int, target_id: int, role: str):
        if not self.is_admin(actor_id):
            raise PermissionError("Admin role required")
        if role not in ROLES:
            raise ValueError("Invalid role")
        self.storage.ensure_user(target_id)
        self.storage.set_role(target_id, role)
        self.storage.audit(actor_id, "set_role", f"target={target_id}, role={role}")

    def users(self, actor_id: int):
        if not self.is_admin(actor_id):
            raise PermissionError("Admin role required")
        return self.storage.users()

    def audit_logs(self, actor_id: int, limit=50):
        if not self.is_admin(actor_id):
            raise PermissionError("Admin role required")
        return self.storage.audits(limit)
