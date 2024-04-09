from collections.abc import Mapping
from typing import Any

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from hack_template.db.base import Base, TimestampMixin
from hack_template.utils.db import make_pg_enum
from hack_template.utils.users.base import UserType


class User(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[UserType] = mapped_column(
        make_pg_enum(UserType),
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
