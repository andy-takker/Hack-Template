from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser

from hack_template.common.telegram.models import ANONYMOUS_TELEGRAM_USER
from hack_template.common.telegram.storage import TelegramStorage


class UserMiddleware(BaseMiddleware):
    _telegram_storage: TelegramStorage

    def __init__(self, telegram_storage: TelegramStorage) -> None:
        self._telegram_storage = telegram_storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        telegram_user: TelegramUser = data["event_from_user"]
        user = await self._telegram_storage.get_by_chat_id(chat_id=telegram_user.id)
        data["user"] = user or ANONYMOUS_TELEGRAM_USER
        return await handler(event, data)
