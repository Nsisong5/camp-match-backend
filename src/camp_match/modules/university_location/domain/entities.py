from __future__ import annotations

from datetime import UTC, datetime

from camp_match.modules.university_location.domain.value_objects import (
    Coordinates,
    InstitutionStatus,
    InstitutionType,
    clean_name,
    normalize_name,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


class University:
    def __init__(
        self,
        id: EntityId,
        official_name: str,
        institution_type: InstitutionType,
        short_name: str | None = None,
        status: InstitutionStatus = InstitutionStatus.ACTIVE,
        country: str = "Nigeria",
        state_region: str | None = None,
        source: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if not (1 <= len(official_name.strip()) <= 200):
            raise ValueError("official_name must be 1-200 characters")

        self._id = id
        self._official_name = clean_name(official_name)
        self._normalized_name = normalize_name(self._official_name)
        self._short_name = short_name.strip() if short_name else None
        self._institution_type = institution_type
        self._status = status
        self._country = country
        self._state_region = state_region.strip() if state_region else None
        self._source = source
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def official_name(self) -> str:
        return self._official_name

    @property
    def normalized_name(self) -> str:
        return self._normalized_name

    @property
    def short_name(self) -> str | None:
        return self._short_name

    @property
    def institution_type(self) -> InstitutionType:
        return self._institution_type

    @property
    def status(self) -> InstitutionStatus:
        return self._status

    @property
    def country(self) -> str:
        return self._country

    @property
    def state_region(self) -> str | None:
        return self._state_region

    @property
    def source(self) -> str | None:
        return self._source

    @property
    def external_reference(self) -> str | None:
        return self._source

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update(
        self,
        official_name: str | None = None,
        short_name: str | None = None,
        institution_type: InstitutionType | None = None,
        status: InstitutionStatus | None = None,
        country: str | None = None,
        state_region: str | None = None,
        source: str | None = None,
    ) -> None:
        if official_name is not None:
            if not (1 <= len(official_name.strip()) <= 200):
                raise ValueError("official_name must be 1-200 characters")
            self._official_name = clean_name(official_name)
            self._normalized_name = normalize_name(self._official_name)
        if short_name is not None:
            self._short_name = short_name.strip() if short_name else None
        if institution_type is not None:
            self._institution_type = institution_type
        if status is not None:
            self._status = status
        if country is not None:
            self._country = country
        if state_region is not None:
            self._state_region = state_region.strip() if state_region else None
        if source is not None:
            self._source = source
        self._updated_at = datetime.now(UTC)


class Campus:
    def __init__(
        self,
        id: EntityId,
        university_id: EntityId,
        name: str,
        coordinates: Coordinates,
        city: str | None = None,
        state_region: str | None = None,
        is_main_campus: bool = False,
        status: InstitutionStatus = InstitutionStatus.ACTIVE,
        source: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if not (1 <= len(name.strip()) <= 200):
            raise ValueError("name must be 1-200 characters")

        self._id = id
        self._university_id = university_id
        self._name = clean_name(name)
        self._normalized_name = normalize_name(self._name)
        self._coordinates = coordinates
        self._city = city.strip() if city else None
        self._state_region = state_region.strip() if state_region else None
        self._is_main_campus = is_main_campus
        self._status = status
        self._source = source
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def university_id(self) -> EntityId:
        return self._university_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def normalized_name(self) -> str:
        return self._normalized_name

    @property
    def coordinates(self) -> Coordinates:
        return self._coordinates

    @property
    def city(self) -> str | None:
        return self._city

    @property
    def state_region(self) -> str | None:
        return self._state_region

    @property
    def is_main_campus(self) -> bool:
        return self._is_main_campus

    @property
    def status(self) -> InstitutionStatus:
        return self._status

    @property
    def source(self) -> str | None:
        return self._source

    @property
    def external_reference(self) -> str | None:
        return self._source

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update(
        self,
        name: str | None = None,
        coordinates: Coordinates | None = None,
        city: str | None = None,
        state_region: str | None = None,
        is_main_campus: bool | None = None,
        status: InstitutionStatus | None = None,
        source: str | None = None,
    ) -> None:
        if name is not None:
            if not (1 <= len(name.strip()) <= 200):
                raise ValueError("name must be 1-200 characters")
            self._name = clean_name(name)
            self._normalized_name = normalize_name(self._name)
        if coordinates is not None:
            self._coordinates = coordinates
        if city is not None:
            self._city = city.strip() if city else None
        if state_region is not None:
            self._state_region = state_region.strip() if state_region else None
        if is_main_campus is not None:
            self._is_main_campus = is_main_campus
        if status is not None:
            self._status = status
        if source is not None:
            self._source = source
        self._updated_at = datetime.now(UTC)
