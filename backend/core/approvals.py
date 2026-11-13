
from typing import Dict

pending_approvals: Dict[str, dict] = {}


def request_approval(action_id: str, action: dict) -> dict:
    """Create an in-memory approval request."""

    approval = {
        "action_id": action_id,
        "action": action,
        "status": "pending",
    }

    pending_approvals[action_id] = approval

    return approval


def approve_action(action_id: str) -> dict:
    """Approve an existing in-memory request."""

    approval = pending_approvals.get(action_id)

    if not approval or approval["status"] != "pending":
        raise ValueError("Approval not found or already processed")

    approval["status"] = "approved"
    return approval


def reject_action(action_id: str) -> dict:
    """Reject an existing in-memory request."""

    approval = pending_approvals.get(action_id)

    if not approval or approval["status"] != "pending":
        raise ValueError("Approval not found or already processed")

    approval["status"] = "rejected"
    return approval
