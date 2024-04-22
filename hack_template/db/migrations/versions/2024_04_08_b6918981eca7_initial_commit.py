"""Initial commit

Revision ID: b6918981eca7
Revises:
Create Date: 2024-04-08 22:41:29.201312

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b6918981eca7"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_type = postgresql.ENUM("ADMIN", "REGULAR", name="user_type")


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", user_type, nullable=False),
        sa.Column("username", sa.String(length=256), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column(
            "properties",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__user")),
    )
    op.create_index(op.f("ix__user__type"), "user", ["type"], unique=False)
    op.create_index(op.f("ix__user__username"), "user", ["username"], unique=True)
    op.create_table(
        "telegram",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("is_banned", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk__telegram__user_id__user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__telegram")),
    )
    op.create_index(
        op.f("ix__telegram__chat_id"), "telegram", ["chat_id"], unique=False
    )
    op.create_index(op.f("ix__telegram__user_id"), "telegram", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix__telegram__user_id"), table_name="telegram")
    op.drop_index(op.f("ix__telegram__chat_id"), table_name="telegram")
    op.drop_table("telegram")
    op.drop_index(op.f("ix__user__username"), table_name="user")
    op.drop_index(op.f("ix__user__type"), table_name="user")
    op.drop_table("user")
    user_type.drop(op.get_bind())
