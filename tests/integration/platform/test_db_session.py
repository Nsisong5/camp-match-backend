import pytest
from sqlalchemy import text

from camp_match.config.settings import get_settings
from camp_match.platform.db.session import create_engine, create_session_factory


@pytest.mark.integration
@pytest.mark.asyncio
async def test_db_session():
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    await engine.dispose()
