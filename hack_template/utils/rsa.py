from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key


def parse_private_key(private_key: str) -> rsa.RSAPrivateKey:
    return load_pem_private_key(  # type: ignore[return-value]
        private_key.encode(),
        password=None,
    )


def get_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65_537,
        key_size=2048,
    )


def stringify_private_key(private_key: rsa.RSAPrivateKey) -> str:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def stringify_public_key(public_key: rsa.RSAPublicKey) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
