from typing import Any

from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format

from hack_template.bot.dialogs.admins.states import MainMenuSG
from hack_template.common.users.storage import UserStorage

MESSAGE_TEMPLATE = """
Всего пользователей: {users_count}

Из них
- адмнистраторов: {admins_count}
- обычных: {regulars_count}
"""


async def get_users_stat(user_storage: UserStorage, **kwargs: Any) -> dict[str, Any]:
    stats = await user_storage.get_users_stats()
    return {
        "users_count": stats.admins_count + stats.regulars_count,
        "regulars_count": stats.regulars_count,
        "admins_count": stats.admins_count,
    }


window = Window(
    Const("Меню администратора"),
    Format(MESSAGE_TEMPLATE),
    state=MainMenuSG.menu,
    getter=get_users_stat,
)
