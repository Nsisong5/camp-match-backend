from camp_match.modules.university_location.application.errors import UniversityNotFound
from camp_match.modules.university_location.application.ports.inbound import (
    GetUniversity,
    UniversityResponse,
)
from camp_match.modules.university_location.application.ports.outbound import UniversityRepository
from camp_match.shared_kernel.domain.identifiers import EntityId


class GetUniversityUseCase(GetUniversity):
    def __init__(self, repository: UniversityRepository) -> None:
        self._repository = repository

    async def execute(self, university_id: str) -> UniversityResponse:
        u_id = EntityId.from_string(university_id)
        university = await self._repository.get_by_id(u_id)
        
        if not university:
            raise UniversityNotFound(f"University with id {university_id} not found.")
        
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
