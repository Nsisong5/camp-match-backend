from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


class PropertyType(Enum):
    SELF_CONTAINED_HOUSE = "SELF_CONTAINED_HOUSE"
    LODGE = "LODGE"
    APARTMENT_BUILDING = "APARTMENT_BUILDING"
    HOSTEL = "HOSTEL"
    OTHER = "OTHER"


class PropertyStatus(Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ListingStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    UNAVAILABLE = "UNAVAILABLE"
    ARCHIVED = "ARCHIVED"


class Currency(Enum):
    NGN = "NGN"


class BillingPeriod(Enum):
    YEAR = "YEAR"
    SEMESTER = "SEMESTER"
    MONTH = "MONTH"


@dataclass(slots=True)
class Price:
    amount_kobo: int
    currency: Currency
    period: BillingPeriod

    def __post_init__(self) -> None:
        if self.amount_kobo < 0:
            raise ValueError("Price amount cannot be negative")
