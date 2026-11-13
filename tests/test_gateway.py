
from backend.core.security import evaluate_action
from backend.core.signatures import generate_key_pair, sign_action


def setup_agent():
    keys = generate_key_pair()

    action = {
        "agent_id": "agent_001",
        "action": "read_file",
        "resource": "report.txt",
    }

    signature = sign_action(action, keys["private_key"])

    return keys, action, signature


def test_authorized_action():
    keys, action, signature = setup_agent()

    result = evaluate_action(
        action,
        signature,
        keys["public_key"],
        ["read"],
    )

    assert result["status"] == "authorized"


def test_unauthorized_action():
    keys, action, signature = setup_agent()

    result = evaluate_action(
        action,
        signature,
        keys["public_key"],
        ["write"],
    )

    assert result["status"] == "blocked"


def test_tampered_action():
    keys, action, signature = setup_agent()

    modified_action = {
        **action,
        "action": "delete_file",
    }

    result = evaluate_action(
        modified_action,
        signature,
        keys["public_key"],
        ["read", "delete"],
    )

    assert result["status"] == "blocked"


def test_sensitive_action_requires_approval():
    keys = generate_key_pair()

    action = {
        "agent_id": "agent_001",
        "action": "delete_file",
        "resource": "important.txt",
    }

    signature = sign_action(action, keys["private_key"])

    result = evaluate_action(
        action,
        signature,
        keys["public_key"],
        ["delete"],
    )

    assert result["status"] == "pending_approval"
    assert "action_id" in result
