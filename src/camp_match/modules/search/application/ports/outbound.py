from camp_match.modules.search.domain.value_objects import AccommodationType, BillingPeriod, Coordinates, EntityId, Amenity
from typing import Protocol

class HousingProvider(Protocol):
    async def list_eligible_candidates(
        self, campus_id: EntityId | None, accommodation_type: AccommodationType | None, max_price_kobo: int | None
    ) -> list:
        ...

class UniversityLocationProvider(Protocol):
    async def get_campus_coordinates(self, campus_id: EntityId) -> Coordinates | None:
        ...

class ProfileProvider(Protocol):
    async def get_student_preferences(self, identity_id: EntityId) -> dict | None:
        ...

class VerificationProvider(Protocol):
    async def get_verification_states(self, listing_ids: list[EntityId]) -> dict[EntityId, str]:
        ...
