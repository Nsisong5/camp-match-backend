"""Fakes for housing module testing."""

from camp_match.modules.housing.application.ports.outbound import (
    AuthorizationService,
    ProfileProvider,
    PropertyRepository,
    UniversityLocationProvider,
)
from camp_match.modules.housing.domain.entities import Property
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.modules.security.domain.value_objects import Permission

class FakePropertyRepository:
    def __init__(self):
        self.properties = {}

    async def add(self, property_: Property) -> None:
        self.properties[property_.id] = property_

class FakeProfileProvider:
    def __init__(self, profiles=None):
        self.profiles = profiles or {}

    async def get_profile_type(self, identity_id: EntityId) -> str | None:
        return self.profiles.get(identity_id)

class FakeUniversityLocationProvider:
    def __init__(self, campuses=None):
        self.campuses = campuses or set()

    async def campus_exists(self, campus_id: EntityId) -> bool:
        return campus_id in self.campuses

class FakeAuthorizationService:
    def __init__(self):
        self.authorized = True

    async def authorize(
        self,
        identity_id: EntityId,
        permission: Permission,
        resource_owner_id: EntityId | None = None
    ) -> None:
        if not self.authorized:
            from camp_match.shared_kernel.application.errors import ForbiddenError
            raise ForbiddenError("Not authorized")
