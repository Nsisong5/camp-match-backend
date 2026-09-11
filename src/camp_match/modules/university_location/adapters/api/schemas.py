from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from camp_match.modules.university_location.domain.value_objects import (
    InstitutionStatus,
    InstitutionType,
)


class CreateUniversitySchema(BaseModel):
    official_name: str = Field(..., min_length=1, max_length=200)
    institution_type: InstitutionType
    short_name: str | None = None
    status: InstitutionStatus = InstitutionStatus.ACTIVE
    country: str = "Nigeria"
    state_region: str | None = None
    source: str | None = None

class UniversityResponseSchema(BaseModel):
    id: UUID
    official_name: str
    normalized_name: str
    short_name: str | None
    institution_type: str
    status: str
    country: str
    state_region: str | None
    source: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateUniversitySchema(BaseModel):
    official_name: str | None = Field(None, min_length=1, max_length=200)
    short_name: str | None = None
    institution_type: InstitutionType | None = None
    status: InstitutionStatus | None = None
    country: str | None = None
    state_region: str | None = None
    source: str | None = None

class CreateCampusSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    city: str | None = None
    state_region: str | None = None
    is_main_campus: bool = False
    status: InstitutionStatus = InstitutionStatus.ACTIVE
    source: str | None = None

class CampusResponseSchema(BaseModel):
    id: UUID
    university_id: UUID
    name: str
    normalized_name: str
    latitude: float
    longitude: float
    city: str | None
    state_region: str | None
    is_main_campus: bool
    status: str
    source: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateCampusSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    city: str | None = None
    state_region: str | None = None
    is_main_campus: bool | None = None
    status: InstitutionStatus | None = None
    source: str | None = None

class UniversityListResponseSchema(BaseModel):
    items: list[UniversityResponseSchema]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)

class CampusListResponseSchema(BaseModel):
    items: list[CampusResponseSchema]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)
