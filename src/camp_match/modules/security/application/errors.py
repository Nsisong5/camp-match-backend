from __future__ import annotations

from camp_match.shared_kernel.application.errors import (
    ApplicationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


class UnauthorizedError(ApplicationError):
    code = "unauthenticated"


class SecurityForbiddenError(ForbiddenError):
    code = "forbidden"


class UnknownPermissionError(ValidationError):
    code = "unknown_permission"


class InvalidAuthorizationContextError(ValidationError):
    code = "invalid_authorization_context"


class RoleNotFoundError(NotFoundError):
    code = "role_not_found"


class PolicyViolationError(ForbiddenError):
    code = "policy_violation"
