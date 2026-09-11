from camp_match.modules.university_location.application.ports.inbound import (
    CampusResponse,
    ListCampuses,
    ListCampusesRequest,
)
from camp_match.modules.university_location.application.ports.outbound import CampusRepository
from camp_match.shared_kernel.application.pagination import Page


class ListCampusesUseCase(ListCampuses):
    def __init__(self, repository: CampusRepository) -> None:
        self._repository = repository

    async def execute(self, request: ListCampusesRequest) -> Page[CampusResponse]:
        page = await self._repository.list_campuses(
            page_request=request.page_request,
            name_query=request.name_query,
            state_region=request.state_region,
            include_inactive=request.include_inactive,
        )
        
        items = [
            CampusResponse(
                id=str(c.id),
                university_id=str(c.university_id),
                name=c.name,
                normalized_name=c.normalized_name,
                latitude=c.coordinates.latitude,
                longitude=c.coordinates.longitude,
                city=c.city,
                state_region=c.state_region,
                is_main_campus=c.is_main_campus,
                status=c.status.value,
                source=c.source,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in page.items
        ]
        
        return Page(
            items=items,
            total=page.total,
            page=page.page,
            page_size=page.page_size,
        )
