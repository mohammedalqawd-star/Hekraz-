"""Authorization + audit guard for local Cyber Range lab lifecycle actions."""
from .authorization import Authorization, is_target_authorized
from .audit import record_operation
from .lab_manager import LabManager, Lab

class LabGuard:
    def __init__(self, manager: LabManager | None = None):
        self.manager = manager or LabManager()

    def _check(self, auth: Authorization, user_id: int, target: str, action: str, lab_id: str) -> None:
        if not is_target_authorized(auth, target, user_id):
            record_operation(user_id, action, target, "denied", "invalid or expired authorization", auth.authorization_id)
            raise PermissionError("Valid authorization for this local target is required.")
        record_operation(user_id, action, target, "authorized", lab_id, auth.authorization_id)

    def create(self, lab_id: str, user_id: int, target: str, auth: Authorization) -> Lab:
        self._check(auth, user_id, target, "lab.create", lab_id)
        return self.manager.create(lab_id, user_id)

    def start(self, lab_id: str, user_id: int, target: str, auth: Authorization) -> Lab:
        self._check(auth, user_id, target, "lab.start", lab_id)
        return self.manager.start(lab_id, user_id)

    def stop(self, lab_id: str, user_id: int, target: str, auth: Authorization) -> Lab:
        self._check(auth, user_id, target, "lab.stop", lab_id)
        return self.manager.stop(lab_id, user_id)

    def reset(self, lab_id: str, user_id: int, target: str, auth: Authorization) -> Lab:
        self._check(auth, user_id, target, "lab.reset", lab_id)
        return self.manager.reset(lab_id, user_id)
