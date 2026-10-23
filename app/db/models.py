"""ORM models for the v2 schema (see issue #98)."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.engine import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    rate_limit_tier: Mapped[str] = mapped_column(String(32), default="standard")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )

    channels: Mapped[list["Channel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Channel(Base):
    __tablename__ = "channels"
    __table_args__ = (Index("ix_channels_user_type", "user_id", "type", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(32))
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="channels")


class RateLimitHit(Base):
    """One row per accepted request, sliding window via count."""

    __tablename__ = "rate_limit_hits"
    __table_args__ = (Index("ix_rl_key_ts", "api_key_hash", "ts"),)

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    api_key_hash: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )


class RegistrationToken(Base):
    """Short-lived single-use token linking a Telegram user to the web page."""

    __tablename__ = "registration_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
