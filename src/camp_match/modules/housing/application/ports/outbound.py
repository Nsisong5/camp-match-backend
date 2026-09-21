"""Module Housing: outbound.py"""
"""Housing outbound ports."""

from typing import Protocol

from camp_match.modules.housing.domain.entities import Property, Unit, Listing
from camp_match.modules.housing.domain.value_objects import PropertyType
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.domain.clock import Clock
from camp_match.shared_kernel.application.pagination import PageRequest, Page
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

class PropertyRepository(Protocol):
    async def add(self, property_: Property) -> None:
        ...

    async def get_by_id(self, property_id: EntityId) -> Property | None:
        ...

    async def update(self, property_: Property) -> None:
        ...
    
    async def list_for_provider(self, provider_id: EntityId, page: PageRequest) -> Page[Property]:
        ...


class UnitRepository(Protocol):
    async def add(self, unit: Unit) -> None:
        ...

    async def get_by_id(self, unit_id: EntityId) -> Unit | None:
        ...

    async def update(self, unit: Unit) -> None:
        ...

    async def try_reserve(self, unit_id: EntityId) -> bool:
        ...

    async def try_release(self, unit_id: EntityId) -> bool:
        ...


class ListingRepository(Protocol):
    async def add(self, listing: Listing) -> None:
        ...

    async def get_by_id(self, listing_id: EntityId) -> Listing | None:
        ...

    async def update(self, listing: Listing) -> None:
        ...

    async def get_by_unit_id(self, unit_id: EntityId) -> Listing | None:
        ...

    async def list_active(
        self, 
        campus_id: EntityId | None, 
        property_type: PropertyType | None, 
        page: PageRequest
    ) -> Page[Listing]:
        ...


class ProfileProvider(Protocol):
    async def get_profile_type(self, identity_id: EntityId) -> str | None:
        ...


class UniversityLocationProvider(Protocol):
    async def campus_exists(self, campus_id: EntityId) -> bool:
        ...


class AuthorizationService(Protocol):
    async def authorize(
        self,
        identity_id: EntityId,
        permission: Permission,
        resource_owner_id: EntityId | None = None
    ) -> None:
        ...
