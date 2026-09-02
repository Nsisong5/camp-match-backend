from dataclasses import dataclass
from typing import Protocol

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

class CreateProfile(Protocol):
    async def execute(self, request: CreateProfileRequest) -> ProfileResponse: ...

class GetCurrentUserProfile(Protocol):
    async def execute(self, request: GetProfileRequest) -> ProfileResponse: ...

class GetPublicProfile(Protocol):
    async def execute(self, request: GetPublicProfileRequest) -> ProfileResponse: ...

class UpdateProfile(Protocol):
    async def execute(self, request: UpdateProfileRequest) -> ProfileResponse: ...

class UpdateStudentProfile(Protocol):
    async def execute(self, request: UpdateStudentProfileRequest) -> ProfileResponse: ...

class UpdateScoutProfile(Protocol):
    async def execute(self, request: UpdateScoutProfileRequest) -> ProfileResponse: ...
