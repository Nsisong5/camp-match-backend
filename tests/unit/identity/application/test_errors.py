from camp_match.modules.identity.application.errors import (
    AccountDisabled,
    AccountSuspended,
    IdentityAlreadyExists,
    IdentityNotFound,
    InvalidAuthenticationRequest,
    InvalidCredentials,
)
from camp_match.shared_kernel.application.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def test_identity_errors_inheritance_and_codes():
    errors = [
        (IdentityAlreadyExists, ConflictError, "identity_already_exists"),
        (InvalidCredentials, UnauthorizedError, "invalid_credentials"),
        (AccountSuspended, ForbiddenError, "account_suspended"),
        (AccountDisabled, ForbiddenError, "account_disabled"),
        (IdentityNotFound, NotFoundError, "identity_not_found"),
        (InvalidAuthenticationRequest, ValidationError, "invalid_authentication_request"),
    ]

    for error_cls, parent_cls, expected_code in errors:
        instance = error_cls("message")
        assert isinstance(instance, parent_cls)
        assert instance.code == expected_code
