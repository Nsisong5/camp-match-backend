
import structlog

from camp_match.modules.university_location.application.errors import UniversityNotFound
from camp_match.modules.university_location.application.ports.inbound import (
    UniversityResponse,
    UpdateUniversity,
    UpdateUniversityRequest,
)
from camp_match.modules.university_location.application.ports.outbound import UniversityRepository
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()

class UpdateUniversityUseCase(UpdateUniversity):
    def __init__(self, repository: UniversityRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, request: UpdateUniversityRequest) -> UniversityResponse:
        university_id = EntityId.from_string(request.university_id)
        university = await self._repository.get_by_id(university_id)
        
        if not university:
            raise UniversityNotFound(f"University with id {request.university_id} not found.")

        updated_fields = []
        if request.official_name is not None and request.official_name != university.official_name:
            updated_fields.append("official_name")
        if request.short_name is not None and request.short_name != university.short_name:
            updated_fields.append("short_name")
        if request.institution_type is not None and request.institution_type != university.institution_type:
            updated_fields.append("institution_type")
        if request.status is not None and request.status != university.status:
            updated_fields.append("status")
        if request.country is not None and request.country != university.country:
            updated_fields.append("country")
        if request.state_region is not None and request.state_region != university.state_region:
            updated_fields.append("state_region")
        if request.source is not None and request.source != university.source:
            updated_fields.append("source")

        university.update(
            official_name=request.official_name,
            short_name=request.short_name,
            institution_type=request.institution_type,
            status=request.status,
            country=request.country,
            state_region=request.state_region,
            source=request.source,
        )
        
        async with self._unit_of_work:
            await self._repository.update(university)
            await self._unit_of_work.commit()
        
        logger.info("university_updated", id=str(university.id), updated_fields=updated_fields)
        
        return UniversityResponse(
            id=str(university.id),
            official_name=university.official_name,
            normalized_name=university.normalized_name,
            short_name=university.short_name,
            institution_type=university.institution_type.value,
            status=university.status.value,
            country=university.country,
            state_region=university.state_region,
            source=university.source,
            created_at=university.created_at,
            updated_at=university.updated_at,
        )
