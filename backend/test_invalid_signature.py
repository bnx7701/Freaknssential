
import uuid
import requests

from backend.core.signatures import generate_key_pair, sign_action

BASE_URL = "http://127.0.0.1:8000"


def main():
    print("\n=== INVALID SIGNATURE SECURITY TEST ===")

    agent_id = f"agent-{uuid.uuid4().hex[:8]}"
    keys = generate_key_pair()

    registration = requests.post(
        f"{BASE_URL}/agents/register",
        json={
            "agent_id": agent_id,
            "public_key": keys["public_key"],
            "allowed_actions": ["read_file", "write_file"],
        },
    )

    print("[1] Registration:", registration.status_code)
    registration.raise_for_status()

    action = {
        "agent_id": agent_id,
        "action": "write_file",
        "resource": "safe-test.txt",
    }

    # Sign different data, creating a signature
    # that does not match the submitted action.
    forged_signature = sign_action(
        {
            **action,
            "resource": "different-file.txt",
        },
        keys["private_key"],
    )

    response = requests.post(
        f"{BASE_URL}/actions/submit",
        json={
            **action,
            "signature": forged_signature,
        },
    )

    print("[2] Response:", response.status_code)
    print("[3] Result:", response.json())

    data = response.json()

    if (
        response.status_code == 200
        and data.get("status") == "blocked"
        and data.get("reason") == "Invalid digital signature"
    ):
        print("\nPASS: Forged signature was blocked!")
    else:
        print("\nFAIL: Unexpected security response!")


if __name__ == "__main__":
    main()
