
import base64
import binascii
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_key_pair():
    private_key = Ed25519PrivateKey.generate()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return {
        "private_key": base64.b64encode(private_bytes).decode("utf-8"),
        "public_key": base64.b64encode(public_bytes).decode("utf-8"),
    }


def canonicalize_action(action: dict) -> bytes:
    return json.dumps(
        action,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sign_action(action: dict, private_key_b64: str) -> str:
    private_bytes = base64.b64decode(private_key_b64, validate=True)
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)

    signature = private_key.sign(canonicalize_action(action))

    return base64.b64encode(signature).decode("utf-8")


def verify_action_signature(
    action: dict,
    signature_b64: str,
    public_key_b64: str,
) -> bool:
    try:
        public_bytes = base64.b64decode(public_key_b64, validate=True)
        signature = base64.b64decode(signature_b64, validate=True)

        public_key = Ed25519PublicKey.from_public_bytes(public_bytes)
        public_key.verify(signature, canonicalize_action(action))

        return True

    except (InvalidSignature, ValueError, TypeError, binascii.Error):
        return False
