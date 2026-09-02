import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from camp_match.config.settings import get_settings

# Force test database URL for all tests
settings = get_settings()
test_db_url = settings.database_url.replace("_dev", "_test")
os.environ["DATABASE_URL"] = test_db_url
get_settings.cache_clear()

from camp_match.app import create_app, lifespan
from camp_match.platform.db.base import Base


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    settings = get_settings()
    # Connect to default database to create test DB
    base_url = settings.database_url.rsplit("/", 1)[0]
    engine = create_async_engine(f"{base_url}/postgres", isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        await conn.execute(text("DROP DATABASE IF EXISTS camp_match_test"))
        await conn.execute(text("CREATE DATABASE camp_match_test"))

    await engine.dispose()

    # Run migrations/create tables on test DB
    test_engine = create_async_engine(settings.database_url)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


@pytest.fixture
async def db_session(setup_test_db):
    settings = get_settings()
    test_engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    await test_engine.dispose()


@pytest.fixture
async def client():
    app = create_app()
    # Manually trigger the lifespan of the application to setup db engine/session factory
    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
