import structlog

from camp_match.modules.profile.application.errors import ProfileNotFound
from camp_match.modules.profile.application.ports.inbound import (
    GetPublicProfileRequest,
    ProfileResponse,
)
from camp_match.modules.profile.application.ports.outbound import ProfileRepository
from camp_match.modules.profile.domain.value_objects import ProfileType

logger = structlog.get_logger()

class GetPublicProfileUseCase:
    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    async def execute(self, request: GetPublicProfileRequest) -> ProfileResponse:
        profile = await self._repository.get_by_id(request.profile_id)
        if not profile:
            raise ProfileNotFound("Profile not found.")
            
        logger.info("public_profile_viewed", profile_id=str(profile.id))
        
        student_details = None
        scout_details = None
        
        if profile.profile_type == ProfileType.SCOUT and profile.scout_details:
            scout_details = {
                "business_name": profile.scout_details.business_name,
                "business_description": profile.scout_details.business_description,
            }
            
        return ProfileResponse(
            id=profile.id,
            identity_id=profile.identity_id,
            profile_type=profile.profile_type,
            display_name=profile.display_name,
            completeness_percentage=profile.completeness_percentage,
            bio=profile.bio,
            phone_number=None, # Public: No phone number
            avatar_url=profile.avatar_url,
            avatar_media_id=profile.avatar_media_id,
            student_details=student_details,
            scout_details=scout_details,
        )
