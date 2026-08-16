class ApplicationError(Exception):
    """Base class for use-case-level failures."""

    code: str | None = None


class NotFoundError(ApplicationError):
    """The requested resource does not exist."""


class ValidationError(ApplicationError):
    """Input failed validation beyond what the DTO layer already checked."""


class ConflictError(ApplicationError):
    """The requested operation conflicts with current state (e.g. duplicate, already booked)."""


class UnauthorizedError(ApplicationError):
    """The caller is not authenticated."""


class ForbiddenError(ApplicationError):
    """The caller is authenticated but not permitted to perform this action."""
