import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hack_template.common.users.storage import UserStorage
from hack_template.rest.auth.base import IAuthProvider
from hack_template.rest.auth.passgen import Passgen
from hack_template.rest.users.dispatcher import UserDispatcher


@pytest.fixture
def passgen() -> Passgen:
    return Passgen(secret="secret")


@pytest.fixture
def user_storage(
    session_factory: async_sessionmaker[AsyncSession],
) -> UserStorage:
    return UserStorage(session_factory=session_factory)


@pytest.fixture
def user_dispatcher(
    user_storage: UserStorage, auth_provider: IAuthProvider, passgen: Passgen
) -> UserDispatcher:
    return UserDispatcher(
        user_storage=user_storage, auth_provider=auth_provider, passgen=passgen
    )
