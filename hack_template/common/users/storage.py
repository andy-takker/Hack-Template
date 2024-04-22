import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, NamedTuple

from pydantic import TypeAdapter
from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hack_template.common.models.pagination import MetaPaginationModel
from hack_template.common.users.base import UserType
from hack_template.common.users.models import (
    ShortUserModel,
    UserModel,
    UserPaginationModel,
)
from hack_template.db.models import User
from hack_template.db.utils import IStorage, inject_session


class UsersStats(NamedTuple):
    admins_count: int
    regulars_count: int


@dataclass(frozen=True)
class UserStorage(IStorage):
    session_factory: async_sessionmaker[AsyncSession]

    @inject_session
    async def create(
        self,
        session: AsyncSession,
        *,
        username: str,
        password_hash: str,
        properties: Mapping[str, Any],
        commit: bool = True,
    ) -> UserModel:
        stmt = (
            insert(User)
            .values(
                username=username,
                password_hash=password_hash,
                properties=properties,
            )
            .returning(User)
        )
        obj = (await session.scalars(stmt)).one()
        if commit:
            await session.commit()
        return UserModel.model_validate(obj)

    @inject_session
    async def get_by_id(
        self,
        /,
        session: AsyncSession,
        user_id: int,
        user_type: UserType = UserType.REGULAR,
    ) -> UserModel | None:
        stmt = select(User).where(
            User.type == user_type,
            User.id == user_id,
        )
        obj = (await session.scalars(stmt)).first()
        return UserModel.model_validate(obj) if obj else None

    @inject_session
    async def get_by_username(
        self,
        *,
        session: AsyncSession,
        username: str,
    ) -> UserModel | None:
        stmt = select(User).where(User.username == username)
        obj = (await session.scalars(stmt)).first()
        return UserModel.model_validate(obj) if obj else None

    @inject_session
    async def get_by_username_and_password_hash(
        self,
        session: AsyncSession,
        username: str,
        password_hash: str,
    ) -> UserModel | None:
        stmt = select(User).where(
            User.username == username,
            User.password_hash == password_hash,
        )
        obj = (await session.scalars(stmt)).first()
        return UserModel.model_validate(obj) if obj else None

    async def pagination(
        self,
        limit: int,
        offset: int,
        user_type: UserType | None,
    ) -> UserPaginationModel:
        total, items = await asyncio.gather(
            self._get_count(user_type=user_type),
            self._get_items(
                user_type=user_type,
                limit=limit,
                offset=offset,
            ),
        )
        return UserPaginationModel(
            meta=MetaPaginationModel(
                total=total,
                limit=limit,
                offset=offset,
            ),
            items=items,
        )

    @inject_session
    async def _get_count(
        self,
        session: AsyncSession,
        user_type: UserType | None,
    ) -> int:
        query = select(func.count(User.id))
        if user_type is not None:
            query = query.where(User.type == user_type)
        return (await session.execute(query)).scalar_one()

    @inject_session
    async def _get_items(
        self,
        session: AsyncSession,
        user_type: UserType | None,
        limit: int,
        offset: int,
    ) -> Sequence[ShortUserModel]:
        query = select(User).limit(limit).offset(offset).order_by(User.id)
        if user_type is not None:
            query = query.where(User.type == user_type)
        users = await session.scalars(query)
        return TypeAdapter(Sequence[ShortUserModel]).validate_python(users.all())  # type:ignore[return-value]

    @inject_session
    async def update_by_id(
        self,
        session: AsyncSession,
        user_id: int,
        new_data: Mapping[str, Any],
        commit: bool = True,
    ) -> UserModel | None:
        user = await self.get_by_id(session=session, user_id=user_id)
        if user is None:
            return None
        if not new_data:
            return user
        properties = {
            **new_data,
        }
        query = (
            update(User)
            .where(User.id == user_id)
            .values(properties=properties)
            .returning(User)
        )
        updated_user = (await session.scalars(query)).one()
        if commit:
            await session.commit()
        return UserModel.model_validate(updated_user)

    @inject_session
    async def get_users_stats(self, session: AsyncSession) -> UsersStats:
        query = select(
            func.coalesce(
                select(func.count())
                .select_from(User)
                .where(User.type == UserType.ADMIN)
                .scalar_subquery(),
                0,
            ).label("admins_count"),
            func.coalesce(
                select(func.count())
                .select_from(User)
                .where(User.type == UserType.REGULAR)
                .scalar_subquery(),
                0,
            ).label("regulars_count"),
        )
        result = (await session.execute(query)).one()._asdict()
        return UsersStats(**result)
