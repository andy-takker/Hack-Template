import factory
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hack_template.common.users.base import UserType
from hack_template.common.users.models import UserModel
from hack_template.db.models import User


class UserPropertiesFactory(factory.Factory):
    class Meta:
        model = dict


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    type = UserType.REGULAR
    username = factory.Sequence(lambda n: f"username-{n+1}")
    password_hash = "secret"
    properties = factory.SubFactory(UserPropertiesFactory)


@pytest.fixture
def create_user(session: AsyncSession):
    async def _create(**kwargs):
        user = UserFactory(**kwargs)
        session.add(user)
        await session.commit()
        return user

    return _create


@pytest.fixture
def read_user(session: AsyncSession):
    async def _read_user(user_id: int) -> UserModel | None:
        stmt = select(User).where(User.id == user_id)
        obj = (await session.scalars(stmt)).first()
        if obj is None:
            return None
        await session.refresh(obj)
        return UserModel.model_validate(obj)

    return _read_user
