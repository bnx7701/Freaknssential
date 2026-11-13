
from typing import List


def check_permission(action: str, allowed_actions: List[str]) -> bool:
    """
    Check whether an agent is authorized to perform an action.
    """
    if not isinstance(allowed_actions, list):
        return False

    return action in allowed_actions

