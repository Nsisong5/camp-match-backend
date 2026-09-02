from camp_match.modules.profile.application.ports.inbound import UpdateProfileRequest, ProfileResponse
from camp_match.modules.profile.application.ports.outbound import ProfileRepository
from camp_match.modules.profile.application.errors import ProfileNotFound
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
import structlog

logger = structlog.get_logger()

class UpdateProfileUseCase:
    def __init__(self, repository: ProfileRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, request: UpdateProfileRequest) -> ProfileResponse:
        profile = await self._repository.get_by_identity_id(request.identity_id)
        if not profile:
            raise ProfileNotFound("Profile not found.")
            
        profile.update_core(
            display_name=request.display_name,
            bio=request.bio,
            phone_number=request.phone_number,
            avatar_url=request.avatar_url,
        )
        
        await self._repository.update_core(profile)
        await self._uow.commit()
        
        logger.info("profile_updated", identity_id=str(request.identity_id), profile_id=str(profile.id))
        
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
