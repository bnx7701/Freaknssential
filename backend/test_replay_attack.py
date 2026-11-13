
import uuid
import requests

from backend.core.signatures import generate_key_pair, sign_action

BASE_URL = "http://127.0.0.1:8000"


def main():
    print("\n=== REPLAY ATTACK SECURITY TEST ===")

    agent_id = f"agent-{uuid.uuid4().hex[:8]}"
    keys = generate_key_pair()

    # Register a fresh agent
    registration = requests.post(
        f"{BASE_URL}/agents/register",
        json={
            "agent_id": agent_id,
            "public_key": keys["public_key"],
            "allowed_actions": ["read_file"],
        },
    )
    registration.raise_for_status()
    print("[1] Agent registered successfully")

    # Create one signed action with one nonce
    action = {
        "agent_id": agent_id,
        "action": "read_file",
        "resource": "safe-test.txt",
        "nonce": uuid.uuid4().hex,
    }

    signature = sign_action(action, keys["private_key"])

    request_data = {
        **action,
        "signature": signature,
    }

    # Submit the exact same request twice
    first = requests.post(
        f"{BASE_URL}/actions/submit",
        json=request_data,
    )

    second = requests.post(
        f"{BASE_URL}/actions/submit",
        json=request_data,
    )

    print("\n[2] First submission:")
    print(first.status_code, first.json())

    print("\n[3] Second submission:")
    print(second.status_code, second.json())

    if (
        first.json().get("status") == "authorized"
        and second.json().get("status") == "blocked"
        and second.json().get("reason")
        == "Replay detected: nonce already used"
    ):
        print("\nPASS: Replay attack successfully blocked!")
    else:
        print("\nFAIL: Replay protection did not behave as expected!")


if __name__ == "__main__":
    main()
