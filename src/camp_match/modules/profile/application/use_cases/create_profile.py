import structlog

from camp_match.modules.profile.application.errors import (
    ProfileAlreadyExists,
    UnauthorizedProfileAccess,
)
from camp_match.modules.profile.application.ports.inbound import (
    CreateProfileRequest,
    ProfileResponse,
)
from camp_match.modules.profile.application.ports.outbound import (
    IdentityProvider,
    ProfileRepository,
)
from camp_match.modules.profile.domain.entities import Profile
from camp_match.modules.profile.domain.events import ProfileCreated
from camp_match.modules.profile.domain.value_objects import (
    ProfileType,
    ScoutProfileDetails,
    StudentProfileDetails,
)
from camp_match.shared_kernel.application.event_bus import EventBus
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.clock import Clock
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()

class CreateProfileUseCase:
    def __init__(
        self,
        repository: ProfileRepository,
        identity_provider: IdentityProvider,
        event_bus: EventBus,
        clock: Clock,
        uow: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._identity_provider = identity_provider
        self._event_bus = event_bus
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CreateProfileRequest) -> ProfileResponse:
        identity = await self._identity_provider.get_identity(request.identity_id)
        if not identity or identity.status != "ACTIVE":
            logger.warning("profile_creation_blocked", reason="invalid_identity", identity_id=str(request.identity_id))
            raise UnauthorizedProfileAccess("Profile creation blocked.")
        
        existing = await self._repository.get_by_identity_id(request.identity_id)
        if existing:
            raise ProfileAlreadyExists("Profile already exists.")
            
        profile_id = EntityId.new()
        
        student_details = None
        scout_details = None
        
        if request.profile_type == ProfileType.STUDENT:
            student_data = request.student_details or {}
            student_details = StudentProfileDetails(**student_data) # type: ignore
        else:
            scout_data = request.scout_details or {}
            scout_details = ScoutProfileDetails(**scout_data) # type: ignore

        profile = Profile(
            id=profile_id,
            identity_id=request.identity_id,
            display_name=request.display_name,
            student_details=student_details,
            scout_details=scout_details,
            bio=request.bio,
            phone_number=request.phone_number,
            avatar_url=request.avatar_url,
        )
        
        await self._repository.add(profile)
        await self._event_bus.publish(ProfileCreated(
            profile_id=profile_id,
            identity_id=request.identity_id,
            profile_type=request.profile_type,
            occurred_at=self._clock.now()
        ))
        
        await self._uow.commit()
        
        logger.info("profile_created", identity_id=str(request.identity_id), profile_id=str(profile_id), profile_type=request.profile_type.name)
        
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
