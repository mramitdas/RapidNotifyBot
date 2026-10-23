"""Model round-trip test against a disposable SQLite (async) database.

JSONB-specific behavior is covered by the Postgres migration; this test
verifies general ORM behavior with JSONB compiled to JSON on SQLite.
"""

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from app.db import models as m  # noqa: F401
from app.db.engine import Base

# Compile JSONB as JSON when the SQLite dialect renders model DDL.
compiles(PG_JSONB, "sqlite")(lambda type_, compiler, **kw: "JSON")


async def test_channel_user_roundtrip() -> None:
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        user = m.User(telegram_user_id=123, api_key_hash="a" * 64)
        session.add(user)
        await session.commit()

        ch = m.Channel(user_id=user.id, type="telegram", config={"chat_id": 123})
        session.add(ch)
        await session.commit()

        stmt = (
            sqlalchemy.select(m.User)
            .options(sqlalchemy.orm.selectinload(m.User.channels))
            .where(m.User.id == user.id)
        )
        (loaded,) = (await session.execute(stmt)).scalars()
        assert isinstance(loaded, m.User)
        assert loaded.channels and loaded.channels[0].type == "telegram"
        assert loaded.channels[0].config == {"chat_id": 123}
