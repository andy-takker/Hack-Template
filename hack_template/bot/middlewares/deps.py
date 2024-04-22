from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DepsMiddleware(BaseMiddleware):
    _deps: Mapping[str, Any]

    def __init__(self, deps: Mapping[str, Any]) -> None:
        self._deps = deps

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data.update(self._deps)
        return await handler(event, data)
