import asyncio
from camp_match.app import create_app
from camp_match.modules.university_location.adapters.persistence.repository import SqlAlchemyUniversityRepository
from camp_match.modules.university_location.application.use_cases.list_universities import ListUniversitiesUseCase
from camp_match.modules.university_location.application.ports.inbound import ListUniversitiesRequest
from camp_match.shared_kernel.application.pagination import PageRequest

async def main():
    app = create_app()
    async with app.router.lifespan_context(app):
        session_factory = app.state.db_session_factory
        async with session_factory() as session:
            repo = SqlAlchemyUniversityRepository(session)
            use_case = ListUniversitiesUseCase(repo)
            
            print("--- Repository Direct Call ---")
            page = await repo.list_universities(PageRequest(1, 20))
            print(f"Repo items count: {len(page.items)}")
            for u in page.items:
                 print(f"  - {u.official_name} (status: {u.status})")
            
            print("\n--- Use Case Call ---")
            req = ListUniversitiesRequest(page_request=PageRequest(1, 20))
            resp_page = await use_case.execute(req)
            print(f"Use Case items count: {len(resp_page.items)}")
            for item in resp_page.items:
                 print(f"  - {item.official_name} (status: {item.status})")

if __name__ == "__main__":
    asyncio.run(main())
