from aiogram.types import Message
from aiogram_dialog import DialogManager

from hack_template.bot.utils.dialogs import start_new_dialog


async def start_command(message: Message, dialog_manager: DialogManager) -> None:
    await start_new_dialog(dialog_manager=dialog_manager)
