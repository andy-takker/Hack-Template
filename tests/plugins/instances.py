import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hack_template.common.users.storage import UserStorage


@pytest.fixture
def user_storage(
    session_factory: async_sessionmaker[AsyncSession],
) -> UserStorage:
    return UserStorage(session_factory=session_factory)
