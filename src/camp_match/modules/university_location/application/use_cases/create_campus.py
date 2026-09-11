
import structlog

from camp_match.modules.university_location.application.errors import (
    CampusAlreadyExists,
    InactiveInstitution,
    InvalidLocation,
    UniversityNotFound,
)
from camp_match.modules.university_location.application.ports.inbound import (
    CampusResponse,
    CreateCampus,
    CreateCampusRequest,
)
from camp_match.modules.university_location.application.ports.outbound import (
    CampusRepository,
    UniversityRepository,
)
from camp_match.modules.university_location.domain.entities import Campus
from camp_match.modules.university_location.domain.value_objects import (
    Coordinates,
    InstitutionStatus,
    normalize_name,
)
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()

class CreateCampusUseCase(CreateCampus):
    def __init__(
        self,
        campus_repo: CampusRepository,
        university_repo: UniversityRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._campus_repo = campus_repo
        self._university_repo = university_repo
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateCampusRequest) -> CampusResponse:
        university_id = EntityId.from_string(request.university_id)
        university = await self._university_repo.get_by_id(university_id)
        
        if not university:
            raise UniversityNotFound(f"University with id {request.university_id} not found.")
        
        if university.status != InstitutionStatus.ACTIVE:
            raise InactiveInstitution(f"Cannot add campus to inactive university {university_id}")
            
        normalized_name = normalize_name(request.name)
        
        if await self._campus_repo.get_by_university_and_normalized_name(university_id, normalized_name):
            raise CampusAlreadyExists(f"Campus with normalized name '{normalized_name}' already exists in university {university_id}")
            
        try:
            coords = Coordinates(latitude=request.latitude, longitude=request.longitude)
        except ValueError as e:
            raise InvalidLocation(str(e))
            
        campus = Campus(
            id=EntityId.new(),
            university_id=university_id,
            name=request.name,
            coordinates=coords,
            city=request.city,
            state_region=request.state_region,
            is_main_campus=request.is_main_campus,
            status=request.status,
            source=request.source,
        )
        
        async with self._unit_of_work:
            await self._campus_repo.add(campus)
            await self._unit_of_work.commit()
        
        logger.info("campus_created", id=str(campus.id), name=campus.name, university_id=str(university_id))
        
        return CampusResponse(
            id=str(campus.id),
            university_id=str(campus.university_id),
            name=campus.name,
            normalized_name=campus.normalized_name,
            latitude=campus.coordinates.latitude,
            longitude=campus.coordinates.longitude,
            city=campus.city,
            state_region=campus.state_region,
            is_main_campus=campus.is_main_campus,
            status=campus.status.value,
            source=campus.source,
            created_at=campus.created_at,
            updated_at=campus.updated_at,
        )
