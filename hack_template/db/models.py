from collections.abc import Mapping
from typing import Any

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hack_template.common.users.base import UserType
from hack_template.db.base import Base, TimestampMixin
from hack_template.db.utils import make_pg_enum


class User(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[UserType] = mapped_column(
        make_pg_enum(UserType, name="user_type"),
        nullable=False,
        index=True,
        default=UserType.REGULAR.value,
    )
    username: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    properties: Mapped[Mapping[str, Any]] = mapped_column(
        JSONB(),
        server_default="{}",
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Telegram(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, index=True, unique=True
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    is_banned: Mapped[bool] = mapped_column(nullable=False, default=False)

    user: Mapped[User] = relationship("User", backref="telegram", uselist=False)

    def __repr__(self) -> str:
        return (
            f"Telegram(id={self.id!r}, user_id={self.user_id!r}, "
            f"chat_id={self.chat_id!r}, is_banned={self.is_banned!r})"
        )
