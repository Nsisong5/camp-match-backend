import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def test():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_session.execute.return_value = mock_result
    
    # FIX: Make scalars NOT an AsyncMock, but a MagicMock so it's not a coroutine
    mock_result.scalars = MagicMock()
    mock_scalar_result = MagicMock()
    mock_result.scalars.return_value = mock_scalar_result
    
    stmt = select(1)
    result = await mock_session.execute(stmt)
    scalars = result.scalars()
    print(f'Type of scalars: {type(scalars)}')
    print(f'Result of .all(): {scalars.all()}')

asyncio.run(test())
