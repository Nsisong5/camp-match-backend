import pytest
from sqlalchemy import text

from camp_match.config.settings import get_settings
from camp_match.platform.db.session import create_engine, create_session_factory
from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork


@pytest.mark.integration
@pytest.mark.asyncio
async def test_uow_commit_works():
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)
        async with uow:
            await session.execute(text("CREATE TEMP TABLE test_commit (id serial PRIMARY KEY)"))
            await uow.commit()

    # Verify persistence
    async with session_factory() as session:
        query = text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'test_commit')"
        )
        result = await session.execute(query)
        assert result.scalar() is True

    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_uow_rollback_works():
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)
        try:
            async with uow:
                query = text("CREATE TEMP TABLE test_rollback (id serial PRIMARY KEY)")
                await session.execute(query)
                raise Exception("Trigger rollback")
        except Exception:
            pass

    # Verify rollback
    async with session_factory() as session:
        query = text(
            "SELECT EXISTS ("
            "SELECT FROM information_schema.tables WHERE table_name = 'test_rollback'"
            ")"
        )
        result = await session.execute(query)
        assert result.scalar() is False

    await engine.dispose()
