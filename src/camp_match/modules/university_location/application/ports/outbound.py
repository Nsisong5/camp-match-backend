from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from camp_match.modules.university_location.domain.entities import Campus, University
    from camp_match.shared_kernel.application.pagination import Page, PageRequest
    from camp_match.shared_kernel.domain.identifiers import EntityId


class UniversityRepository(Protocol):
    async def add(self, university: University) -> None:
        """Persist a new university."""
        ...

    async def get_by_id(self, university_id: EntityId) -> University | None:
        """Retrieve a university by ID."""
        ...

    async def get_by_normalized_name(self, normalized_name: str) -> University | None:
        """Retrieve a university by its normalized name."""
        ...

    async def update(self, university: University) -> None:
        """Update an existing university."""
        ...

    async def list_universities(
        self,
        page_request: PageRequest,
        name_query: str | None = None,
        state_region: str | None = None,
        include_inactive: bool = False,
    ) -> Page[University]:
        """List universities with pagination and filtering."""
        ...


class CampusRepository(Protocol):
    async def add(self, campus: Campus) -> None:
        """Persist a new campus."""
        ...

    async def get_by_id(self, campus_id: EntityId) -> Campus | None:
        """Retrieve a campus by ID."""
        ...

    async def get_by_university_and_normalized_name(
        self, university_id: EntityId, normalized_name: str
    ) -> Campus | None:
        """Retrieve a campus by university ID and normalized campus name."""
        ...

    async def update(self, campus: Campus) -> None:
        """Update an existing campus."""
        ...

    async def list_campuses(
        self,
        page_request: PageRequest,
        name_query: str | None = None,
        state_region: str | None = None,
        include_inactive: bool = False,
    ) -> Page[Campus]:
        """List campuses with pagination and filtering."""
        ...
