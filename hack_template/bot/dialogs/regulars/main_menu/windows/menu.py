from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const

from hack_template.bot.dialogs.regulars.states import MainMenuSG

window = Window(
    Const("Основное меню обычного пользователя"),
    state=MainMenuSG.menu,
)
