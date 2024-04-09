import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import TypeAdapter
from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hack_template.db.models import User
from hack_template.utils.db import IStorage, inject_session
from hack_template.utils.pagination import MetaPaginationModel
from hack_template.utils.users.base import UserType
from hack_template.utils.users.models import (
    ShortUserModel,
    UserModel,
    UserPaginationModel,
)


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
        properties: Mapping[str, str],
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
    async def read_by_id(
        self,
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
    async def read_by_username(
        self,
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
        query = select(User)
        if user_type is not None:
            query = query.where(User.type == user_type)
        stmt = select(func.count()).select_from(query.scalar_subquery())
        return (await session.execute(stmt)).scalar_one()

    @inject_session
    async def _get_items(
        self,
        session: AsyncSession,
        user_type: UserType | None,
        limit: int,
        offset: int,
    ) -> Sequence[ShortUserModel]:
        query = select(User).limit(limit).offset(offset)
        if user_type is not None:
            query = query.where(User.type == user_type)
        users = await session.scalars(query)
        return TypeAdapter(Sequence[ShortUserModel]).validate_python(users)  # type:ignore[return-value]

    @inject_session
    async def update_by_id(
        self,
        session: AsyncSession,
        user_id: int,
        new_data: Mapping[str, Any],
        commit: bool = True,
    ) -> UserModel | None:
        user = await self.read_by_id(session=session, user_id=user_id)
        if user is None:
            return None
        properties = {
            **user.properties,
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
