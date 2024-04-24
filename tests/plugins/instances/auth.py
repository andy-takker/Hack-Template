import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from hack_template.rest.auth.base import IAuthProvider, SecurityManager
from hack_template.rest.auth.jwt import JwtAuthProvider, JwtProcessor
from hack_template.rest.auth.rsa import get_private_key, stringify_private_key


@pytest.fixture(scope="session")
def private_key() -> rsa.RSAPrivateKey:
    return get_private_key()


@pytest.fixture(scope="session")
def private_key_str(private_key: rsa.RSAPrivateKey) -> str:
    return stringify_private_key(private_key)


@pytest.fixture
def jwt_processor(private_key_str) -> JwtProcessor:
    return JwtProcessor(private_key=private_key_str)


@pytest.fixture
def auth_provider(jwt_processor: JwtProcessor) -> IAuthProvider:
    return JwtAuthProvider(
        jwt_processor=jwt_processor,
        auth_header="Authorization",
        auth_cookie="token",
    )


@pytest.fixture
def security_manager(auth_provider: IAuthProvider) -> SecurityManager:
    return SecurityManager(auth_provider=auth_provider)
