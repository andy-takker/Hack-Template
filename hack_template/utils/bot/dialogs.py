from aiogram_dialog import DialogManager, ShowMode, StartMode

from hack_template.bot.dialogs.states import MainMenuSG


async def start_new_dialog(dialog_manager: DialogManager) -> None:
    await dialog_manager.start(
        state=MainMenuSG.menu,
        mode=StartMode.RESET_STACK,
        show_mdoe=ShowMode.SEND,
    )
