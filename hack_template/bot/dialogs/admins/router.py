from aiogram import Router

from hack_template.bot.dialogs.admins.main_menu.dialog import dialog as main_menu_dialog

router = Router(name="admin_router")
router.include_routers(
    main_menu_dialog,
)
