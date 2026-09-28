from camp_match.shared_kernel.application.errors import (
    NotFoundError,
    ValidationError,
    ApplicationError,
)


class MediaNotFound(NotFoundError):
    def __init__(self, message: str = "Media file not found.") -> None:
        super().__init__(message=message)
        self.code = "media_not_found"


class UnsupportedMediaType(ValidationError):
    def __init__(self, message: str = "Unsupported media type.") -> None:
        super().__init__(message=message)
        self.code = "unsupported_media_type"


class MediaTooLarge(ValidationError):
    def __init__(self, message: str = "Media file is too large.") -> None:
        super().__init__(message=message)
        self.code = "media_too_large"


class MediaUploadFailed(ApplicationError):
    def __init__(self, message: str = "Media upload failed.") -> None:
        super().__init__(message=message)
        self.code = "media_upload_failed"


class MediaNotAvailable(ValidationError):
    def __init__(self, message: str = "Media file is not available.") -> None:
        super().__init__(message=message)
        self.code = "media_not_available"
