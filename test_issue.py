import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from unittest.mock import AsyncMock

async def test():
    # Try using the real session to see if scalars().all() works
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        result = await conn.execute(select(1))
        # If this is the real result, it should have a non-coroutine scalars() method
        scalars = result.scalars()
        print(f"Type of scalars result: {type(scalars)}")
        print(f"Value: {scalars.all()}")

asyncio.run(test())
