from camp_match.shared_kernel.application.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


class ProfileNotFound(NotFoundError):
    def __init__(self, message: str = "Profile not found.") -> None:
        super().__init__(message=message)
        self.code = "profile_not_found"

class UnauthorizedProfileAccess(ForbiddenError):
    def __init__(self, message: str = "Unauthorized profile access.") -> None:
        super().__init__(message=message)
        self.code = "unauthorized_profile_access"

class ProfileAlreadyExists(ConflictError):
    def __init__(self, message: str = "Profile already exists.") -> None:
        super().__init__(message=message)
        self.code = "profile_already_exists"

class InvalidProfileData(ValidationError):
    def __init__(self, message: str = "Invalid profile data.") -> None:
        super().__init__(message=message)
        self.code = "invalid_profile_data"

class UnsupportedProfileType(ValidationError):
    def __init__(self, message: str = "Unsupported profile type.") -> None:
        super().__init__(message=message)
        self.code = "unsupported_profile_type"

class InvalidProfileState(ValidationError):
    def __init__(self, message: str = "Invalid profile state.") -> None:
        super().__init__(message=message)
        self.code = "invalid_profile_state"
