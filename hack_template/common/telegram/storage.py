from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from hack_template.common.telegram.models import TelegramUserModel
from hack_template.db.models import Telegram
from hack_template.db.utils import IStorage, inject_session


@dataclass(frozen=True)
class TelegramStorage(IStorage):
    session_factory: async_sessionmaker[AsyncSession]

    @inject_session
    async def get_by_chat_id(
        self, /, session: AsyncSession, chat_id: int
    ) -> TelegramUserModel | None:
        query = (
            select(Telegram)
            .options(joinedload(Telegram.user))
            .where(Telegram.chat_id == chat_id)
        )

        result = (await session.scalars(query)).one_or_none()
        return TelegramUserModel.build_from_db(result) if result else None
