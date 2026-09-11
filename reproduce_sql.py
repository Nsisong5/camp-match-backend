import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class T(Base):
    __tablename__ = 't'
    id = Column(Integer, primary_key=True)
    val = Column(String)

async def main():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(select(T).insert_values([{'val': 'a'}]))
        result = await conn.execute(select(T.val))
        print(f"Result type: {type(result)}")
        try:
            roles = result.scalars().all()
            print(f"Success: {roles}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

asyncio.run(main())
