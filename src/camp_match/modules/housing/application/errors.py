"""Module Housing: errors.py"""
"""Housing application errors."""

from camp_match.shared_kernel.application.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


class PropertyNotFound(NotFoundError):
    code = "property_not_found"


class UnitNotFound(NotFoundError):
    code = "unit_not_found"


class ListingNotFound(NotFoundError):
    code = "listing_not_found"


class InventoryUnavailable(ConflictError):
    code = "inventory_unavailable"


class InvalidListingStateTransition(ConflictError):
    code = "invalid_listing_state_transition"


class InvalidLocation(ValidationError):
    code = "invalid_location"
