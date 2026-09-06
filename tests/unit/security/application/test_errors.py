import pytest
from camp_match.modules.security.application.errors import (
    UnauthorizedError,
    SecurityForbiddenError,
    UnknownPermissionError,
    InvalidAuthorizationContextError,
    RoleNotFoundError,
    PolicyViolationError,
)
from camp_match.shared_kernel.application.errors import (
    ApplicationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)

def test_error_codes():
    assert UnauthorizedError("msg").code == "unauthenticated"
    assert SecurityForbiddenError("msg").code == "forbidden"
    assert UnknownPermissionError("msg").code == "unknown_permission"
    assert InvalidAuthorizationContextError("msg").code == "invalid_authorization_context"
    assert RoleNotFoundError("msg").code == "role_not_found"
    assert PolicyViolationError("msg").code == "policy_violation"

def test_error_inheritance():
    assert isinstance(UnauthorizedError("msg"), ApplicationError)
    assert isinstance(SecurityForbiddenError("msg"), ForbiddenError)
    assert isinstance(UnknownPermissionError("msg"), ValidationError)
    assert isinstance(InvalidAuthorizationContextError("msg"), ValidationError)
    assert isinstance(RoleNotFoundError("msg"), NotFoundError)
    assert isinstance(PolicyViolationError("msg"), ForbiddenError)
