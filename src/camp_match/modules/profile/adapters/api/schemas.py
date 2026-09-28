from uuid import UUID

from pydantic import BaseModel

from camp_match.modules.profile.domain.value_objects import (
    AccommodationTypePreference,
    CleanlinessPreference,
    ProfileType,
    ScoutAvailabilityStatus,
    SleepSchedule,
)


class StudentDetailsSchema(BaseModel):
    university_name: str | None = None
    department: str | None = None
    budget_min_naira: int | None = None
    budget_max_naira: int | None = None
    preferred_accommodation_type: AccommodationTypePreference | None = None
    cleanliness_preference: CleanlinessPreference | None = None
    sleep_schedule: SleepSchedule | None = None

class ScoutDetailsSchema(BaseModel):
    business_name: str | None = None
    business_description: str | None = None
    years_active: int | None = None
    availability_status: ScoutAvailabilityStatus | None = None

class ProfileCreateRequest(BaseModel):
    display_name: str
    profile_type: ProfileType
    bio: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    student_details: dict | None = None
    scout_details: dict | None = None

class ProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None

class StudentProfileUpdateRequest(BaseModel):
    university_name: str | None = None
    department: str | None = None
    budget_min_naira: int | None = None
    budget_max_naira: int | None = None
    preferred_accommodation_type: AccommodationTypePreference | None = None
    cleanliness_preference: CleanlinessPreference | None = None
    sleep_schedule: SleepSchedule | None = None

class ScoutProfileUpdateRequest(BaseModel):
    business_name: str | None = None
    business_description: str | None = None
    years_active: int | None = None
    availability_status: ScoutAvailabilityStatus | None = None

class ProfileResponseSchema(BaseModel):
    id: UUID
    identity_id: UUID
    profile_type: ProfileType
    display_name: str
    completeness_percentage: float
    bio: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    avatar_media_id: UUID | None = None
    avatar: dict | None = None
    student_details: StudentDetailsSchema | None = None
    scout_details: ScoutDetailsSchema | None = None

    class Config:
        from_attributes = True

class PublicProfileResponseSchema(BaseModel):
    id: UUID
    profile_type: ProfileType
    display_name: str
    completeness_percentage: float
    bio: str | None = None
    avatar_url: str | None = None
    avatar_media_id: UUID | None = None
    avatar: dict | None = None
    student_details: dict | None = None
    scout_details: dict | None = None

    class Config:
        from_attributes = True
