from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from camp_match.modules.housing.domain.value_objects import (
    ListingStatus,
    PropertyStatus,
    PropertyType,
)

if TYPE_CHECKING:
    from camp_match.modules.housing.domain.value_objects import Coordinates, Price
    from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass
class Property:
    id: EntityId
    provider_id: EntityId
    property_type: PropertyType
    name: str
    description: str | None
    address: str
    coordinates: Coordinates
    campus_id: EntityId | None
    has_water: bool = False
    has_electricity: bool = False
    has_security: bool = False
    has_parking: bool = False
    has_generator: bool = False
    has_cctv: bool = False
    has_wifi: bool = False
    status: PropertyStatus = PropertyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Unit:
    id: EntityId
    property_id: EntityId
    label: str
    total_capacity: int
    occupied_count: int = 0
    is_furnished: bool = False
    has_private_bathroom: bool = False
    has_kitchen: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.total_capacity <= 0:
            raise ValueError("Total capacity must be positive")
        self._validate_occupancy(self.occupied_count)

    def _validate_occupancy(self, count: int) -> None:
        if count < 0:
            raise ValueError("Occupied count cannot be negative")
        if count > self.total_capacity:
            raise ValueError("Occupied count cannot exceed total capacity")

    def set_occupied_count(self, count: int) -> None:
        self._validate_occupancy(count)
        self.occupied_count = count

    @property
    def available_count(self) -> int:
        return self.total_capacity - self.occupied_count


@dataclass
class Listing:
    id: EntityId
    property_id: EntityId
    unit_id: EntityId
    title: str
    description: str | None
    price: Price
    status: ListingStatus = ListingStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    _TRANSITIONS = {
        ListingStatus.DRAFT: {ListingStatus.PUBLISHED, ListingStatus.ARCHIVED},
        ListingStatus.PUBLISHED: {ListingStatus.UNAVAILABLE, ListingStatus.ARCHIVED},
        ListingStatus.UNAVAILABLE: {ListingStatus.PUBLISHED, ListingStatus.ARCHIVED},
        ListingStatus.ARCHIVED: set(),
    }

    def transition_to(self, new_status: ListingStatus) -> None:
        if new_status == self.status:
            return

        allowed = self._TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(f"Invalid transition from {self.status} to {new_status}")

        self.status = new_status
