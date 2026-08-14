class DomainError(Exception):
    """Base class for violations of a business rule. Framework-agnostic."""


class InvariantViolationError(DomainError):
    """Raised when an entity or aggregate would be left in an invalid state."""
