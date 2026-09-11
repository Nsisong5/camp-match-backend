from camp_match.modules.university_location.application.errors import CampusNotFound
from camp_match.modules.university_location.application.ports.inbound import (
    CampusResponse,
    GetCampus,
)
from camp_match.modules.university_location.application.ports.outbound import CampusRepository
from camp_match.shared_kernel.domain.identifiers import EntityId


class GetCampusUseCase(GetCampus):
    def __init__(self, repository: CampusRepository) -> None:
        self._repository = repository

    async def execute(self, campus_id: str) -> CampusResponse:
        c_id = EntityId.from_string(campus_id)
        campus = await self._repository.get_by_id(c_id)
        
        if not campus:
            raise CampusNotFound(f"Campus with id {campus_id} not found.")
        
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
