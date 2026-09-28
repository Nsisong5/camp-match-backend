from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final

from camp_match.shared_kernel.domain.identifiers import EntityId


class AccommodationType(Enum):
    SELF_CONTAINED_HOUSE = "SELF_CONTAINED_HOUSE"
    LODGE = "LODGE"
    APARTMENT_BUILDING = "APARTMENT_BUILDING"
    HOSTEL = "HOSTEL"
    OTHER = "OTHER"


class Amenity(Enum):
    WATER = auto()
    ELECTRICITY = auto()
    SECURITY = auto()
    PARKING = auto()
    GENERATOR = auto()
    CCTV = auto()
    WIFI = auto()
    FURNISHED = auto()
    PRIVATE_BATHROOM = auto()
    KITCHEN = auto()


class BillingPeriod(Enum):
    YEAR = "YEAR"
    SEMESTER = "SEMESTER"
    MONTH = "MONTH"


class VerificationState(Enum):
    VERIFIED = auto()
    UNVERIFIED = auto()
    UNKNOWN = auto()


@dataclass(frozen=True, slots=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


class SortOption(Enum):
    RELEVANCE = auto()
    PRICE_ASC = auto()
    PRICE_DESC = auto()
    DISTANCE = auto()
    NEWEST = auto()


@dataclass(frozen=True)
class SearchCriteria:
    campus_id: EntityId | None = None
    min_price_kobo: int | None = None
    max_price_kobo: int | None = None
    billing_period: BillingPeriod | None = None
    accommodation_type: AccommodationType | None = None
    amenities: frozenset[Amenity] = field(default_factory=frozenset)
    max_distance_km: float | None = None
    verified_only: bool = False
    sort_by: SortOption = SortOption.RELEVANCE

    def __post_init__(self) -> None:
        if (self.min_price_kobo is not None or self.max_price_kobo is not None) and self.billing_period is None:
            raise ValueError("billing_period must be set if price bounds are set")
        
        if self.min_price_kobo is not None and self.min_price_kobo < 0:
            raise ValueError("min_price_kobo cannot be negative")
        
        if self.max_price_kobo is not None and self.max_price_kobo < 0:
            raise ValueError("max_price_kobo cannot be negative")
            
        if self.max_distance_km is not None and self.max_distance_km <= 0:
            raise ValueError("max_distance_km must be positive")


@dataclass(frozen=True)
class CandidateListing:
    listing_id: EntityId
    property_id: EntityId
    title: str
    accommodation_type: AccommodationType
    price_amount_kobo: int
    price_currency: str
    price_period: BillingPeriod
    coordinates: Coordinates
    campus_id: EntityId | None
    amenities: frozenset[Amenity]
    available_count: int
    created_at: str # ISO string
    media: list[dict] = field(default_factory=list)
    

@dataclass(frozen=True)
class ScoredCandidate:
    listing: CandidateListing
    score: float
    distance_km: float | None = None
