
import uuid
import requests

from backend.core.signatures import (
    generate_key_pair,
    sign_action,
    verify_action_signature,
)

BASE_URL = "http://127.0.0.1:8000"
AGENT_ID = f"agent-{uuid.uuid4().hex[:8]}"


def main():
    print("\n=== FREAKNSSENTIAL SECURITY TEST ===")
    print(f"Test Agent: {AGENT_ID}")

    # 1. Generate a matching key pair
    keys = generate_key_pair()

    private_key = keys["private_key"]
    public_key = keys["public_key"]

    print("\n[1] Key pair generated successfully")

    # 2. Register a fresh test agent
    registration = requests.post(
        f"{BASE_URL}/agents/register",
        json={
            "agent_id": AGENT_ID,
            "public_key": public_key,
            "allowed_actions": [
                "read_file",
                "write_file",
                "send_email",
            ],
        },
    )

    if registration.status_code != 201:
        print("Registration failed:", registration.text)
        return

    print("[2] Agent registered successfully")

    # 3. Prepare sensitive action
    action = {
        "agent_id": AGENT_ID,
        "action": "delete_file",
        "resource": "safe-test.txt",
         "nonce": uuid.uuid4().hex,
    }

    # 4. Generate digital signature
    signature = sign_action(action, private_key)

    # 5. Verify signature using registered public key
    registered = requests.get(
        f"{BASE_URL}/agents/{AGENT_ID}"
    )
    registered.raise_for_status()

    registered_public_key = registered.json()["public_key"]

    valid = verify_action_signature(
        action,
        signature,
        registered_public_key,
    )

    print("[3] Signature generated:", bool(signature))
    print("[4] Registered key matches:", valid)

    if not valid:
        print("Signature verification failed!")
        return

    # 6. Submit sensitive action
    result = requests.post(
        f"{BASE_URL}/actions/submit",
        json={
            **action,
            "signature": signature,
        },
    )

    print("\n[5] Action submission response:")
    print(result.status_code)
    print(result.json())


if __name__ == "__main__":
    main()
