import uuid
import requests

from backend.core.signatures import generate_key_pair, sign_action

BASE_URL = "http://127.0.0.1:8000"


def main():
    agent_id = f"agent-{uuid.uuid4().hex[:8]}"

    keys = generate_key_pair()
    private_key = keys["private_key"]
    public_key = keys["public_key"]

    # Register test agent
    registration = requests.post(
        f"{BASE_URL}/agents/register",
        json={
            "agent_id": agent_id,
            "public_key": public_key,
            "allowed_actions": ["write_file"],
        },
    )

    print("Registration:", registration.status_code)
    if registration.status_code != 201:
        print(registration.text)
        return

    # Prepare sensitive action
    action = {
        "agent_id": agent_id,
        "action": "write_file",
        "resource": "safe-test.txt",
        "nonce": uuid.uuid4().hex,
    }

    signature = sign_action(action, private_key)

    # Submit action
    response = requests.post(
        f"{BASE_URL}/actions/submit",
        json={**action, "signature": signature},
    )

    print("\nAction response:", response.status_code)
    print(response.json())


if __name__ == "__main__":
    main()