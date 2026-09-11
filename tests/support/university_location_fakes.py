from camp_match.modules.university_location.application.ports.outbound import (
    CampusRepository,
    UniversityRepository,
)
from camp_match.modules.university_location.domain.entities import Campus, University
from camp_match.shared_kernel.application.pagination import Page, PageRequest
from camp_match.shared_kernel.domain.identifiers import EntityId


class FakeUniversityRepository(UniversityRepository):
    def __init__(self) -> None:
        self.universities: dict[EntityId, University] = {}

    async def add(self, university: University) -> None:
        self.universities[university.id] = university

    async def get_by_id(self, university_id: EntityId) -> University | None:
        return self.universities.get(university_id)

    async def get_by_normalized_name(self, normalized_name: str) -> University | None:
        for u in self.universities.values():
            if u.normalized_name == normalized_name:
                return u
        return None

    async def update(self, university: University) -> None:
        self.universities[university.id] = university

    async def list_universities(
        self,
        page_request: PageRequest,
        name_query: str | None = None,
        state_region: str | None = None,
        include_inactive: bool = False,
    ) -> Page[University]:
        # Simple implementation for fakes
        items = list(self.universities.values())
        if not include_inactive:
            # Filtering would be added here
            pass
        return Page(items=items, total=len(items), page=page_request.page, page_size=page_request.page_size)


class FakeCampusRepository(CampusRepository):
    def __init__(self) -> None:
        self.campuses: dict[EntityId, Campus] = {}

    async def add(self, campus: Campus) -> None:
        self.campuses[campus.id] = campus

    async def get_by_id(self, campus_id: EntityId) -> Campus | None:
        return self.campuses.get(campus_id)

    async def get_by_university_and_normalized_name(
        self, university_id: EntityId, normalized_name: str
    ) -> Campus | None:
        for c in self.campuses.values():
            if c.university_id == university_id and c.normalized_name == normalized_name:
                return c
        return None

    async def update(self, campus: Campus) -> None:
        self.campuses[campus.id] = campus

    async def list_campuses(
        self,
        page_request: PageRequest,
        name_query: str | None = None,
        state_region: str | None = None,
        include_inactive: bool = False,
    ) -> Page[Campus]:
        # Simple implementation for fakes
        items = list(self.campuses.values())
        return Page(items=items, total=len(items), page=page_request.page, page_size=page_request.page_size)
