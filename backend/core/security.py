
from uuid import uuid4

from backend.core.permissions import check_permission
from backend.core.signatures import verify_action_signature
from backend.core.approvals import request_approval


SENSITIVE_ACTIONS = {
    "delete_file",
    "send_email",
    "write_file",
}


def evaluate_action(
    action: dict,
    signature: str,
    public_key: str,
    allowed_actions: list[str],
) -> dict:
    """
    Validate an agent action before allowing it to proceed.
    This function does not execute the action.
    """

    # 1. Verify digital signature
    if not verify_action_signature(action, signature, public_key):
        return {
            "status": "blocked",
            "reason": "Invalid digital signature",
        }

    # 2. Check agent permissions
    action_name = action.get("action")

    if not check_permission(action_name, allowed_actions):
        return {
            "status": "blocked",
            "reason": "Permission denied",
        }

    # 3. Require human approval for sensitive actions
    if action_name in SENSITIVE_ACTIONS:
        action_id = str(uuid4())

        approval = request_approval(action_id, action)

        return {
            "status": "pending_approval",
            "reason": "Human approval required",
            "action_id": approval["action_id"],
        }

    # 4. Action passed all security checks
    return {
        "status": "authorized",
        "reason": "All security checks passed",
    }

