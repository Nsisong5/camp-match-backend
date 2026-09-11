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
    # Use postgresql+asyncpg
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost/camp_match_test')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(select(T).from_statement(select(T)).insert_values([{'val': 'a'}])) # Simplified insert
        
        # Testing the specific line
        result = await conn.execute(select(T.val))
        print(f"Result type: {type(result)}")
        try:
            # The line causing error: result.scalars().all()
            roles = result.scalars().all()
            print(f"Success: {roles}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

# asyncio.run(main()) # Cannot run because of DB dependency, just checking the syntax
