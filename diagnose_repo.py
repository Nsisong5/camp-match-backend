import asyncio
from camp_match.app import create_app
from camp_match.modules.university_location.adapters.persistence.repository import SqlAlchemyUniversityRepository
from camp_match.shared_kernel.application.pagination import PageRequest

async def main():
    app = create_app()
    async with app.router.lifespan_context(app):
        session_factory = app.state.db_session_factory
        async with session_factory() as session:
            repo = SqlAlchemyUniversityRepository(session)
            print("--- Repository Query ---")
            page = await repo.list_universities(PageRequest(1, 20))
            print(f"Items: {len(page.items)}")
            
            # Check what's in the session
            from sqlalchemy import select
            from camp_match.modules.university_location.adapters.persistence.models import UniversityModel
            result = await session.execute(select(UniversityModel))
            raw_items = result.scalars().all()
            print(f"Raw Items in DB: {len(raw_items)}")

if __name__ == "__main__":
    asyncio.run(main())
