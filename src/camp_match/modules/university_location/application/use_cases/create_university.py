
import structlog

from camp_match.modules.university_location.application.errors import UniversityAlreadyExists
from camp_match.modules.university_location.application.ports.inbound import (
    CreateUniversity,
    CreateUniversityRequest,
    UniversityResponse,
)
from camp_match.modules.university_location.application.ports.outbound import UniversityRepository
from camp_match.modules.university_location.domain.entities import University
from camp_match.modules.university_location.domain.value_objects import normalize_name
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()

class CreateUniversityUseCase(CreateUniversity):
    def __init__(self, repository: UniversityRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateUniversityRequest) -> UniversityResponse:
        normalized_name = normalize_name(request.official_name)
        
        if await self._repository.get_by_normalized_name(normalized_name):
            raise UniversityAlreadyExists(f"University with normalized name '{normalized_name}' already exists.")

        university = University(
            id=EntityId.new(),
            official_name=request.official_name,
            institution_type=request.institution_type,
            short_name=request.short_name,
            status=request.status,
            country=request.country,
            state_region=request.state_region,
            source=request.source,
        )
        
        async with self._unit_of_work:
            await self._repository.add(university)
            await self._unit_of_work.commit()
        
        logger.info("university_created", id=str(university.id), official_name=university.official_name)
        
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
