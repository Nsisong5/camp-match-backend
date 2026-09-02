from camp_match.modules.profile.application.ports.inbound import UpdateStudentProfileRequest, ProfileResponse
from camp_match.modules.profile.application.ports.outbound import ProfileRepository
from camp_match.modules.profile.application.errors import ProfileNotFound, UnsupportedProfileType
from camp_match.modules.profile.domain.value_objects import StudentProfileDetails
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
import structlog

logger = structlog.get_logger()

class UpdateStudentProfileUseCase:
    def __init__(self, repository: ProfileRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, request: UpdateStudentProfileRequest) -> ProfileResponse:
        profile = await self._repository.get_by_identity_id(request.identity_id)
        if not profile:
            raise ProfileNotFound("Profile not found.")
        
        if not profile.student_details:
            raise UnsupportedProfileType("Not a student profile")
            
        current = profile.student_details
        new_details = StudentProfileDetails(
            university_name=request.university_name if request.university_name is not None else current.university_name,
            department=request.department if request.department is not None else current.department,
            budget_min_naira=request.budget_min_naira if request.budget_min_naira is not None else current.budget_min_naira,
            budget_max_naira=request.budget_max_naira if request.budget_max_naira is not None else current.budget_max_naira,
            preferred_accommodation_type=request.preferred_accommodation_type if request.preferred_accommodation_type is not None else current.preferred_accommodation_type,
            cleanliness_preference=request.cleanliness_preference if request.cleanliness_preference is not None else current.cleanliness_preference,
            sleep_schedule=request.sleep_schedule if request.sleep_schedule is not None else current.sleep_schedule,
        )
        
        profile.update_student_details(new_details)
        await self._repository.update_student_extension(profile)
        await self._uow.commit()
        
        logger.info("student_profile_updated", identity_id=str(request.identity_id), profile_id=str(profile.id))
        
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
