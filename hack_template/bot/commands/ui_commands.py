from collections.abc import Callable, Sequence
from enum import StrEnum, unique

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from hack_template.bot.commands.help import help_command
from hack_template.bot.commands.start import start_command


@unique
class Commands(StrEnum):
    START = "start"
    HELP = "help"


COMMAND_HANDLERS: Sequence[tuple[str, Callable]] = (
    (Commands.START, start_command),
    (Commands.HELP, help_command),
)


async def set_ui_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command=Commands.START, description="Start work with bot"),
        BotCommand(command=Commands.HELP, description="Get help with bot"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())


def register_commands(root_router: Router) -> None:
    for command, handler in COMMAND_HANDLERS:
        root_router.message(Command(command))(handler)
