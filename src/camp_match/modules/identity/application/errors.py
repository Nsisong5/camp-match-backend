from camp_match.shared_kernel.application.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class IdentityAlreadyExists(ConflictError):
    """Email is already registered to an account."""

    code = "identity_already_exists"


class InvalidCredentials(UnauthorizedError):
    """Email/password combination didn't check out or token is invalid."""

    code = "invalid_credentials"


class AccountSuspended(ForbiddenError):
    """Credentials were valid; the account's status forbids login right now."""

    code = "account_suspended"


class AccountDisabled(ForbiddenError):
    """Credentials were valid; the account's status forbids login right now."""

    code = "account_disabled"


class IdentityNotFound(NotFoundError):
    """Looked up by ID and nothing's there."""

    code = "identity_not_found"


class InvalidAuthenticationRequest(ValidationError):
    """Reserved for a business-level input problem Pydantic couldn't have caught."""

    code = "invalid_authentication_request"
