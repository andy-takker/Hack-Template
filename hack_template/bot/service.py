import logging
from collections.abc import Sequence

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from aiomisc import Service

from hack_template.bot.commands.ui_commands import set_ui_commands
from hack_template.bot.dialogs.router import register_dialogs
from hack_template.bot.handlers import on_unknown_intent, on_unknown_state

log = logging.getLogger(__name__)


class TelegramBotService(Service):
    __dependencies__ = (
        "bot",
        "dispatcher",
        "bot_middlewares",
    )

    bot: Bot
    dispatcher: Dispatcher
    bot_middlewares: Sequence[BaseMiddleware]

    async def start(self) -> None:
        log.info("Initialize bot")
        await self._setup_bot()
        await self._setup_dispatcher()
        self.start_event.set()
        log.info("Start polling")
        await self.dispatcher.start_polling(self.bot)

    async def stop(self, exception: Exception | None = None) -> None:
        await self.bot.session.close()

    async def _setup_bot(self) -> None:
        await set_ui_commands(self.bot)
        await self.bot.delete_webhook(drop_pending_updates=True)

    async def _setup_dispatcher(self) -> None:
        await self._setup_middlewares()
        await self._setup_dialogs()
        await self._setup_error_handlers()

    async def _setup_middlewares(self) -> None:
        for middleware in self.bot_middlewares:
            self.dispatcher.update.outer_middleware(middleware)

    async def _setup_dialogs(self) -> None:
        register_dialogs(self.dispatcher)
        setup_dialogs(self.dispatcher)

    async def _setup_error_handlers(self) -> None:
        self.dispatcher.errors.register(
            on_unknown_intent,
            ExceptionTypeFilter(UnknownIntent),
        )
        self.dispatcher.errors.register(
            on_unknown_state,
            ExceptionTypeFilter(UnknownState),
        )
