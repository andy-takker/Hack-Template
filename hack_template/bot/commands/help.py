from aiogram.types import Message


async def help_command(message: Message) -> None:
    await message.answer(text="Бот для хакатона.")
