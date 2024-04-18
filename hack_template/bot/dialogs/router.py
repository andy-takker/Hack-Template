from aiogram import Router
from aiogram.filters import Command

from hack_template.utils.bot.ui_commands import Commands


def register_dialogs(root_router: Router) -> None:
    root_router.include_routers(
        admin_dialog_router,
        user_dialog_router,
    )
    root_router.message(Command(Commands.START))(start__command)
