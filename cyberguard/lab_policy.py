"""Safe Cyber Range policy checks."""
from dataclasses import dataclass

@dataclass(frozen=True)
class LabTarget:
    lab_id: str
    target: str
    isolated: bool = True

class LabPolicyError(PermissionError):
    pass

def require_isolated_lab(target: LabTarget) -> None:
    if not target.isolated:
        raise LabPolicyError(
            "Practical offensive exercises are restricted to isolated Cyber Range labs."
        )

def validate_target(target: LabTarget) -> str:
    require_isolated_lab(target)
    if not target.target.strip():
        raise LabPolicyError("Lab target is required.")
    return target.target
