from camp_match.modules.profile.application.errors import (
    InvalidProfileData,
    InvalidProfileState,
    ProfileAlreadyExists,
    ProfileNotFound,
    UnauthorizedProfileAccess,
    UnsupportedProfileType,
)
from camp_match.shared_kernel.application.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


def test_profile_errors_hierarchy_and_codes():
    errors = [
        (ProfileNotFound, NotFoundError, "profile_not_found"),
        (ProfileAlreadyExists, ConflictError, "profile_already_exists"),
        (InvalidProfileData, ValidationError, "invalid_profile_data"),
        (UnsupportedProfileType, ValidationError, "unsupported_profile_type"),
        (UnauthorizedProfileAccess, ForbiddenError, "unauthorized_profile_access"),
        (InvalidProfileState, ValidationError, "invalid_profile_state"),
    ]

    for error_class, parent_class, expected_code in errors:
        error = error_class("Some message")
        assert isinstance(error, parent_class)
        assert error.code == expected_code
