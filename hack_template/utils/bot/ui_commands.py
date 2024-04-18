from enum import StrEnum, unique

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


@unique
class Commands(StrEnum):
    START = "start"
    HELP = "help"


async def set_ui_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command=Commands.START, description="Start work with bot"),
        BotCommand(command=Commands.HELP, description="Get help with bot"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
