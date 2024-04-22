from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict

from hack_template.common.users.base import UserType
from hack_template.common.users.models import UserModel
from hack_template.db.models import Telegram


class TelegramModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    is_banned: bool


class TelegramUserModel(BaseModel):
    telegram: TelegramModel
    user: UserModel

    @property
    def is_admin(self) -> bool:
        return self.user.type == UserType.ADMIN

    @property
    def is_regular(self) -> bool:
        return self.user.type == UserType.REGULAR

    @classmethod
    def build_from_db(cls, telegram: Telegram) -> Self:
        return cls(
            telegram=TelegramModel.model_validate(telegram),
            user=UserModel.model_validate(telegram.user),
        )


ANONYMOUS_TELEGRAM_USER = TelegramUserModel(
    telegram=TelegramModel(id=0, chat_id=0, is_banned=False),
    user=UserModel(
        id=0,
        type=UserType.REGULAR,
        username="anonymous",
        properties={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    ),
)
