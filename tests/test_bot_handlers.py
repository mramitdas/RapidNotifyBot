"""Tests for Telegram bot handler logic (no Telegram network calls)."""

import re

import anyio
from sqlalchemy import select

from app.bot.handlers import HELP, WELCOME, subscribe
from app.core.config import Settings
from app.core.security import hash_key
from app.db import models as m


def _settings() -> Settings:
    return Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite://",
        bot_token="TESTTOKEN",
        key_pepper="test-pepper",
        public_base_url="https://rapid.example",
    )


def _make_db(tmp_path):
    from sqlalchemy import pool
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.db.engine import Base

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path}/bot.db", poolclass=pool.NullPool
    )

    async def _create() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    anyio.run(_create)
    return async_sessionmaker(engine, expire_on_commit=False)


def test_subscribe_creates_user_and_returns_key_once(tmp_path) -> None:
    sm = _make_db(tmp_path)

    async def _run() -> str:
        async with sm() as session:
            text = await subscribe(session, _settings(), 777)
            await session.commit()
        return text

    text = anyio.run(_run)
    assert "Your new API key" in text
    assert "`rn_" in text
    assert "rapid.example/api/channels/entry/" in text

    async def _check() -> m.User | None:
        async with sm() as session:
            return await session.scalar(
                select(m.User).where(m.User.telegram_user_id == 777)
            )

    user = anyio.run(_check)
    assert isinstance(user, m.User)
    assert len(user.api_key_hash) == 64
    # exactly one key occurrence (shown once)
    assert len(re.findall(r"`rn_[^`]+`", text)) == 1


def test_subscribe_again_rotates_key(tmp_path) -> None:
    sm = _make_db(tmp_path)

    async def _run(subscribe_id: int) -> str:
        async with sm() as session:
            text = await subscribe(session, _settings(), subscribe_id)
            await session.commit()
        return text

    first = anyio.run(_run, 888)
    second = anyio.run(_run, 888)
    assert "rotated" in second
    raw_first = re.search(r"`(rn_[^`]+)`", first).group(1)
    raw_second = re.search(r"`(rn_[^`]+)`", second).group(1)
    assert raw_first != raw_second

    async def _count() -> int:
        async with sm() as session:
            users = await session.scalars(
                select(m.User).where(m.User.telegram_user_id == 888)
            )
            keys = [u.api_key_hash for u in users.unique().all()]
        assert len(keys) == 1
        return len(keys)

    count = anyio.run(_count)
    assert count == 1

    # Stored hash corresponds to the second key, never the first.
    async def _hash_matches() -> bool:
        async with sm() as session:
            stored = await session.scalar(
                select(m.User.api_key_hash).where(m.User.telegram_user_id == 888)
            )
        return stored in (hash_key(raw_second, "test-pepper"),)

    assert anyio.run(_hash_matches)


def test_registration_tokens_accumulate(tmp_path) -> None:
    sm = _make_db(tmp_path)

    async def _run() -> int:
        async with sm() as session:
            await subscribe(session, _settings(), 999)
            await session.commit()
            tokens = await session.scalars(select(m.RegistrationToken))
            return len(tokens.all())

    assert anyio.run(_run) == 1


def test_welcome_and_help_content() -> None:
    assert "/subscribe" in WELCOME
    assert "/help" in HELP


def test_subscribe_creates_implicit_telegram_channel(tmp_path) -> None:
    sm = _make_db(tmp_path)

    async def _run(subscribe_id: int) -> None:
        async with sm() as session:
            await subscribe(session, _settings(), subscribe_id)
            await session.commit()

    anyio.run(_run, 555)

    async def _check() -> m.Channel | None:
        async with sm() as session:
            user = await session.scalar(
                select(m.User).where(m.User.telegram_user_id == 555)
            )
            return await session.scalar(
                select(m.Channel).where(
                    m.Channel.user_id == user.id, m.Channel.type == "telegram"
                )
            )

    channel = anyio.run(_check)
    assert isinstance(channel, m.Channel)
    assert channel.enabled is True
    assert channel.config == {"chat_id": 555}


def test_rotate_also_backfills_missing_telegram_channel(tmp_path) -> None:
    sm = _make_db(tmp_path)

    async def _run(subscribe_id: int) -> None:
        async with sm() as session:
            await subscribe(session, _settings(), subscribe_id)
            await session.commit()

    async def _telegram_channel_exists(subscribe_id: int) -> bool:
        async with sm() as session:
            user = await session.scalar(
                select(m.User).where(m.User.telegram_user_id == subscribe_id)
            )
            ch = await session.scalar(
                select(m.Channel).where(
                    m.Channel.user_id == user.id, m.Channel.type == "telegram"
                )
            )
            return ch is not None

    async def _drop_channel(subscribe_id: int) -> None:
        async with sm() as session:
            user = await session.scalar(
                select(m.User).where(m.User.telegram_user_id == subscribe_id)
            )
            ch = await session.scalar(
                select(m.Channel).where(
                    m.Channel.user_id == user.id, m.Channel.type == "telegram"
                )
            )
            await session.delete(ch)
            await session.commit()

    # First subscribe creates it; second (rotate) keeps it.
    anyio.run(_run, 666)
    assert anyio.run(_telegram_channel_exists, 666)

    # Simulate a legacy user whose telegram row is missing: rotate must backfill.
    anyio.run(_drop_channel, 666)
    assert not anyio.run(_telegram_channel_exists, 666)
    anyio.run(_run, 666)
    assert anyio.run(_telegram_channel_exists, 666)
