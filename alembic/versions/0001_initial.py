"""initial users, channels, rate-limit, registration-tokens

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-23
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("api_key_hash", sa.String(length=64), nullable=False),
        sa.Column("rate_limit_tier", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_users_telegram_user_id", "users", ["telegram_user_id"], unique=True
    )
    op.create_index("ix_users_api_key_hash", "users", ["api_key_hash"], unique=True)

    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("config", JSONB(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_channels_user_type", "channels", ["user_id", "type"], unique=True
    )

    op.create_table(
        "rate_limit_hits",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("api_key_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_rl_key_ts", "rate_limit_hits", ["api_key_hash", "ts"])
    op.create_index(
        "ix_rate_limit_hits_api_key_hash", "rate_limit_hits", ["api_key_hash"]
    )

    op.create_table(
        "registration_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_registration_tokens_token_hash",
        "registration_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_registration_tokens_telegram_user_id",
        "registration_tokens",
        ["telegram_user_id"],
    )


def downgrade() -> None:
    op.drop_table("registration_tokens")
    op.drop_table("rate_limit_hits")
    op.drop_table("channels")
    op.drop_table("users")
