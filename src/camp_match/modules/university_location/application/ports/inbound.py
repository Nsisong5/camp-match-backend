from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from camp_match.modules.university_location.domain.value_objects import (
    InstitutionStatus,
    InstitutionType,
)
from camp_match.shared_kernel.application.pagination import Page, PageRequest

# --- Admin Use Case Protocols ---

@dataclass(frozen=True)
class CreateUniversityRequest:
    official_name: str
    institution_type: InstitutionType
    short_name: str | None = None
    status: InstitutionStatus = InstitutionStatus.ACTIVE
    country: str = "Nigeria"
    state_region: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class UniversityResponse:
    id: str
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


@dataclass(frozen=True)
class UpdateUniversityRequest:
    university_id: str
    official_name: str | None = None
    short_name: str | None = None
    institution_type: InstitutionType | None = None
    status: InstitutionStatus | None = None
    country: str | None = None
    state_region: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class CreateCampusRequest:
    university_id: str
    name: str
    latitude: float
    longitude: float
    city: str | None = None
    state_region: str | None = None
    is_main_campus: bool = False
    status: InstitutionStatus = InstitutionStatus.ACTIVE
    source: str | None = None


@dataclass(frozen=True)
class CampusResponse:
    id: str
    university_id: str
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


@dataclass(frozen=True)
class UpdateCampusRequest:
    campus_id: str
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    city: str | None = None
    state_region: str | None = None
    is_main_campus: bool | None = None
    status: InstitutionStatus | None = None
    source: str | None = None


@dataclass(frozen=True)
class ListUniversitiesRequest:
    page_request: PageRequest
    name_query: str | None = None
    state_region: str | None = None
    include_inactive: bool = False


@dataclass(frozen=True)
class ListCampusesRequest:
    page_request: PageRequest
    name_query: str | None = None
    state_region: str | None = None
    include_inactive: bool = False


@dataclass(frozen=True)
class BulkImportRequest:
    file_path: str


@dataclass(frozen=True)
class ImportRowResult:
    row_index: int
    success: bool
    error_reason: str | None = None


@dataclass(frozen=True)
class BulkImportResponse:
    processed_count: int
    created_count: int
    skipped_count: int
    errors: list[ImportRowResult]


class CreateUniversity(Protocol):
    async def execute(self, request: CreateUniversityRequest) -> UniversityResponse:
        ...


class UpdateUniversity(Protocol):
    async def execute(self, request: UpdateUniversityRequest) -> UniversityResponse:
        ...


class GetUniversity(Protocol):
    async def execute(self, university_id: str) -> UniversityResponse:
        ...


class ListUniversities(Protocol):
    async def execute(self, request: ListUniversitiesRequest) -> Page[UniversityResponse]:
        ...


class CreateCampus(Protocol):
    async def execute(self, request: CreateCampusRequest) -> CampusResponse:
        ...


class UpdateCampus(Protocol):
    async def execute(self, request: UpdateCampusRequest) -> CampusResponse:
        ...


class GetCampus(Protocol):
    async def execute(self, campus_id: str) -> CampusResponse:
        ...


class ListCampuses(Protocol):
    async def execute(self, request: ListCampusesRequest) -> Page[CampusResponse]:
        ...


class BulkImport(Protocol):
    async def execute(self, request: BulkImportRequest) -> BulkImportResponse:
        ...


# --- Public Cross-Module Query Port ---

@dataclass(frozen=True)
class UniversitySummary:
    id: str
    official_name: str
    short_name: str | None
    institution_type: str
    status: str
    country: str
    state_region: str | None


@dataclass(frozen=True)
class CampusSummary:
    id: str
    university_id: str
    name: str
    is_main_campus: bool
    status: str
    city: str | None
    state_region: str | None


@dataclass(frozen=True)
class CampusLocation:
    id: str
    name: str
    latitude: float
    longitude: float


class UniversityLocationQueryPort(Protocol):
    async def get_university(self, university_id: str) -> UniversitySummary | None:
        ...

    async def get_campus(self, campus_id: str) -> CampusSummary | None:
        ...

    async def get_campus_location(self, campus_id: str) -> CampusLocation | None:
        ...

    async def list_campuses_for_university(self, university_id: str) -> list[CampusSummary]:
        ...
