from camp_match.shared_kernel.application.errors import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


class UniversityAlreadyExists(ConflictError):
    """Raised when a university with the same normalized name already exists."""

    pass


class CampusAlreadyExists(ConflictError):
    """Raised when a campus with the same normalized name already exists within the same university."""

    pass


class UniversityNotFound(NotFoundError):
    """Raised when a referenced university does not exist."""

    pass


class CampusNotFound(NotFoundError):
    """Raised when a referenced campus does not exist."""

    pass


class InactiveInstitution(ValidationError):
    """Raised when trying to perform an operation on a deactivated university/institution."""

    pass


class InvalidLocation(ValidationError):
    """Raised when coordinates are out of bounds or invalid."""

    pass
