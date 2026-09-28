from dataclasses import dataclass
from typing import Protocol

from camp_match.modules.profile.domain.entities import Profile
from camp_match.modules.profile.domain.value_objects import (
    AccommodationTypePreference,
    CleanlinessPreference,
    ProfileType,
    ScoutAvailabilityStatus,
    SleepSchedule,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class CreateProfileRequest:
    identity_id: EntityId
    display_name: str
    profile_type: ProfileType
    student_details: dict[str, str | int] | None = None
    scout_details: dict[str, str | int] | None = None
    bio: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None

@dataclass(frozen=True)
class ProfileResponse:
    id: EntityId
    identity_id: EntityId
    profile_type: ProfileType
    display_name: str
    completeness_percentage: float = 0.0
    bio: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    avatar_media_id: EntityId | None = None
    student_details: dict[str, str | int] | None = None
    scout_details: dict[str, str | int] | None = None

@dataclass(frozen=True)
class GetProfileRequest:
    identity_id: EntityId

@dataclass(frozen=True)
class GetPublicProfileRequest:
    profile_id: EntityId

@dataclass(frozen=True)
class UpdateProfileRequest:
    identity_id: EntityId
    display_name: str | None = None
    bio: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None

@dataclass(frozen=True)
class UpdateStudentProfileRequest:
    identity_id: EntityId
    university_name: str | None = None
    department: str | None = None
    budget_min_naira: int | None = None
    budget_max_naira: int | None = None
    preferred_accommodation_type: AccommodationTypePreference | None = None
    cleanliness_preference: CleanlinessPreference | None = None
    sleep_schedule: SleepSchedule | None = None

@dataclass(frozen=True)
class UpdateScoutProfileRequest:
    identity_id: EntityId
    business_name: str | None = None
    business_description: str | None = None
    years_active: int | None = None
    availability_status: ScoutAvailabilityStatus | None = None

class ProfileRepository(Protocol):
    async def add(self, profile: Profile) -> None: ...
    async def get_by_identity_id(self, identity_id: EntityId) -> Profile | None: ...
    async def get_by_id(self, profile_id: EntityId) -> Profile | None: ...
    async def update_core(self, profile: Profile) -> None: ...
    async def update_student_extension(self, profile: Profile) -> None: ...
    async def update_scout_extension(self, profile: Profile) -> None: ...

class IdentityProvider(Protocol):
    async def get_identity(self, identity_id: EntityId) -> object | None: ...
