
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open("test_agent_private.pem", "wb") as f:
    f.write(private_pem)

with open("test_agent_public.pem", "wb") as f:
    f.write(public_pem)

print("New Ed25519 key pair generated!")
print("\nPUBLIC KEY:\n")
print(public_pem.decode())
print("Private key saved securely. Never share it.")
