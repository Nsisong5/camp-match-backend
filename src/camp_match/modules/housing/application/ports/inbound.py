"""Module Housing: inbound.py"""
"""Housing inbound ports."""

from dataclasses import dataclass
from typing import Protocol

from camp_match.modules.housing.domain.value_objects import PropertyType
from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class CreatePropertyCommand:
    provider_id: EntityId
    property_type: PropertyType
    name: str
    description: str | None
    address: str
    latitude: float
    longitude: float
    campus_id: EntityId | None


@dataclass(frozen=True)
class UpdatePropertyCommand:
    identity_id: EntityId
    property_id: EntityId
    name: str | None = None
    description: str | None = None
    address: str | None = None
    has_water: bool | None = None
    has_electricity: bool | None = None
    has_security: bool | None = None
    has_parking: bool | None = None
    has_generator: bool | None = None
    has_cctv: bool | None = None
    has_wifi: bool | None = None


@dataclass(frozen=True)
class ArchivePropertyCommand:
    identity_id: EntityId
    property_id: EntityId


@dataclass(frozen=True)
class CreateUnitCommand:
    identity_id: EntityId
    property_id: EntityId
    label: str
    total_capacity: int
    is_furnished: bool = False
    has_private_bathroom: bool = False
    has_kitchen: bool = False


@dataclass(frozen=True)
class UpdateUnitCommand:
    identity_id: EntityId
    unit_id: EntityId
    label: str | None = None
    total_capacity: int | None = None
    is_furnished: bool | None = None
    has_private_bathroom: bool | None = None
    has_kitchen: bool | None = None


@dataclass(frozen=True)
class CreateListingCommand:
    identity_id: EntityId
    property_id: EntityId
    unit_id: EntityId
    title: str
    description: str | None
    price_amount_kobo: int
    price_currency: str
    price_period: str


@dataclass(frozen=True)
class UpdateListingCommand:
    identity_id: EntityId
    listing_id: EntityId
    title: str | None = None
    description: str | None = None
    price_amount_kobo: int | None = None


@dataclass(frozen=True)
class PublishListingCommand:
    identity_id: EntityId
    listing_id: EntityId


@dataclass(frozen=True)
class UnpublishListingCommand:
    identity_id: EntityId
    listing_id: EntityId


@dataclass(frozen=True)
class ArchiveListingCommand:
    identity_id: EntityId
    listing_id: EntityId


class CreateUnit(Protocol):
    async def __call__(self, command: CreateUnitCommand) -> EntityId:
        ...


class UpdateUnit(Protocol):
    async def __call__(self, command: UpdateUnitCommand) -> None:
        ...


class CreateListing(Protocol):
    async def __call__(self, command: CreateListingCommand) -> EntityId:
        ...


class UpdateListing(Protocol):
    async def __call__(self, command: UpdateListingCommand) -> None:
        ...


class PublishListing(Protocol):
    async def __call__(self, command: PublishListingCommand) -> None:
        ...


class UnpublishListing(Protocol):
    async def __call__(self, command: UnpublishListingCommand) -> None:
        ...


class AvailabilityPort(Protocol):
    async def check_availability(self, unit_id: EntityId) -> int:
        ...

    async def reserve_slot(self, unit_id: EntityId) -> bool:
        ...

    async def release_slot(self, unit_id: EntityId) -> None:
        ...
