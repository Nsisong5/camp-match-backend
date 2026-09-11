
import structlog

from camp_match.modules.university_location.application.errors import (
    CampusNotFound,
    InvalidLocation,
)
from camp_match.modules.university_location.application.ports.inbound import (
    CampusResponse,
    UpdateCampus,
    UpdateCampusRequest,
)
from camp_match.modules.university_location.application.ports.outbound import CampusRepository
from camp_match.modules.university_location.domain.value_objects import Coordinates
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = structlog.get_logger()

class UpdateCampusUseCase(UpdateCampus):
    def __init__(self, repository: CampusRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    async def execute(self, request: UpdateCampusRequest) -> CampusResponse:
        campus_id = EntityId.from_string(request.campus_id)
        campus = await self._repository.get_by_id(campus_id)
        
        if not campus:
            raise CampusNotFound(f"Campus with id {request.campus_id} not found.")

        updated_fields = []
        if request.name is not None and request.name != campus.name:
            updated_fields.append("name")
        # Note: request.coordinates was not in the original request, using latitude/longitude directly
        # The update method in entities.py likely accepts Coordinates object or individual fields.
        # Original code used request.latitude/longitude to construct Coordinates.
        if request.latitude is not None and request.longitude is not None:
             updated_fields.append("coordinates")

        if request.city is not None and request.city != campus.city:
            updated_fields.append("city")
        if request.state_region is not None and request.state_region != campus.state_region:
            updated_fields.append("state_region")
        if request.is_main_campus is not None and request.is_main_campus != campus.is_main_campus:
            updated_fields.append("is_main_campus")
        if request.status is not None and request.status != campus.status:
            updated_fields.append("status")
        if request.source is not None and request.source != campus.source:
            updated_fields.append("source")

        coords = None
        if request.latitude is not None and request.longitude is not None:
            try:
                coords = Coordinates(latitude=request.latitude, longitude=request.longitude)
            except ValueError as e:
                raise InvalidLocation(str(e))

        campus.update(
            name=request.name,
            coordinates=coords,
            city=request.city,
            state_region=request.state_region,
            is_main_campus=request.is_main_campus,
            status=request.status,
            source=request.source,
        )
        
        async with self._unit_of_work:
            await self._repository.update(campus)
            await self._unit_of_work.commit()
        
        logger.info("campus_updated", id=str(campus.id), updated_fields=updated_fields)
        
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
