import structlog

from camp_match.modules.profile.application.errors import ProfileNotFound, UnsupportedProfileType
from camp_match.modules.profile.application.ports.inbound import (
    ProfileResponse,
    UpdateScoutProfileRequest,
)
from camp_match.modules.profile.application.ports.outbound import ProfileRepository
from camp_match.modules.profile.domain.value_objects import ScoutProfileDetails
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

logger = structlog.get_logger()

class UpdateScoutProfileUseCase:
    def __init__(self, repository: ProfileRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, request: UpdateScoutProfileRequest) -> ProfileResponse:
        profile = await self._repository.get_by_identity_id(request.identity_id)
        if not profile:
            raise ProfileNotFound("Profile not found.")
        
        if not profile.scout_details:
            raise UnsupportedProfileType("Not a scout profile")
            
        current = profile.scout_details
        new_details = ScoutProfileDetails(
            business_name=request.business_name if request.business_name is not None else current.business_name,
            business_description=request.business_description if request.business_description is not None else current.business_description,
            years_active=request.years_active if request.years_active is not None else current.years_active,
            availability_status=request.availability_status if request.availability_status is not None else current.availability_status,
        )
        
        profile.update_scout_details(new_details)
        await self._repository.update_scout_extension(profile)
        await self._uow.commit()
        
        logger.info("scout_profile_updated", identity_id=str(request.identity_id), profile_id=str(profile.id))
        
        return ProfileResponse(
            id=profile.id,
            identity_id=profile.identity_id,
            profile_type=profile.profile_type,
            display_name=profile.display_name,
            completeness_percentage=profile.completeness_percentage,
            bio=profile.bio,
            phone_number=profile.phone_number,
            avatar_url=profile.avatar_url,
            avatar_media_id=profile.avatar_media_id,
            student_details=profile.student_details.to_dict() if profile.student_details else None, # type: ignore
            scout_details=profile.scout_details.to_dict() if profile.scout_details else None, # type: ignore
        )
