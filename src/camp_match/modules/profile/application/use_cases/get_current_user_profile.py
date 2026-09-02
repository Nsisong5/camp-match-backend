import structlog

from camp_match.modules.profile.application.errors import ProfileNotFound
from camp_match.modules.profile.application.ports.inbound import GetProfileRequest, ProfileResponse
from camp_match.modules.profile.application.ports.outbound import ProfileRepository

logger = structlog.get_logger()

class GetCurrentUserProfileUseCase:
    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    async def execute(self, request: GetProfileRequest) -> ProfileResponse:
        profile = await self._repository.get_by_identity_id(request.identity_id)
        if not profile:
            raise ProfileNotFound("Profile not found.")
            
        return ProfileResponse(
            id=profile.id,
            identity_id=profile.identity_id,
            profile_type=profile.profile_type,
            display_name=profile.display_name,
            completeness_percentage=profile.completeness_percentage,
            bio=profile.bio,
            phone_number=profile.phone_number,
            avatar_url=profile.avatar_url,
            student_details=profile.student_details.to_dict() if profile.student_details else None, # type: ignore
            scout_details=profile.scout_details.to_dict() if profile.scout_details else None, # type: ignore
        )
