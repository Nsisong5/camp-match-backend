from camp_match.modules.university_location.application.ports.inbound import (
    ListUniversities,
    ListUniversitiesRequest,
    UniversityResponse,
)
from camp_match.modules.university_location.application.ports.outbound import UniversityRepository
from camp_match.shared_kernel.application.pagination import Page


class ListUniversitiesUseCase(ListUniversities):
    def __init__(self, repository: UniversityRepository) -> None:
        self._repository = repository

    async def execute(self, request: ListUniversitiesRequest) -> Page[UniversityResponse]:
        page = await self._repository.list_universities(
            page_request=request.page_request,
            name_query=request.name_query,
            state_region=request.state_region,
            include_inactive=request.include_inactive,
        )
        
        items = [
            UniversityResponse(
                id=str(u.id),
                official_name=u.official_name,
                normalized_name=u.normalized_name,
                short_name=u.short_name,
                institution_type=u.institution_type.value,
                status=u.status.value,
                country=u.country,
                state_region=u.state_region,
                source=u.source,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in page.items
        ]
        
        return Page(
            items=items,
            total=page.total,
            page=page.page,
            page_size=page.page_size,
        )
