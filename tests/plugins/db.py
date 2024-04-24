import os
from types import SimpleNamespace

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from hack_template.db.models import Base
from hack_template.db.utils import (
    create_async_engine,
    create_async_session_factory,
    make_alembic_config,
)


@pytest.fixture(scope="session")
def db_name() -> str:
    default = "test_db"
    return os.getenv("APP_PG_DB_NAME", default)


@pytest.fixture(scope="session")
def stairway_db_name() -> str:
    return "stairway"


@pytest.fixture(scope="session")
def pg_dsn(localhost: str, db_name: str) -> str:
    default = f"postgresql+asyncpg://pguser:pgpass@{localhost}:5432/{db_name}"
    return os.getenv("APP_DB_PG_DSN", default)


@pytest.fixture(scope="session")
def base_pg_dsn(localhost: str) -> str:
    default = f"postgresql+asyncpg://pguser:pgpass@{localhost}:5432/postgres"
    return os.getenv("APP_BASE_PG_DSN", default)


@pytest.fixture(scope="session")
def alembic_config(pg_dsn: str) -> AlembicConfig:
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_dsn=pg_dsn,
        raiseerr=False,
        x=False,
    )
    return make_alembic_config(cmd_options)


@pytest.fixture
async def async_engine(
    pg_dsn: str,
):
    engine = create_async_engine(pg_dsn)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def session_factory(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return create_async_session_factory(engine=async_engine)


@pytest.fixture
async def session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncSession:
    try:
        session = session_factory()
        yield session
    finally:
        await session.close()
