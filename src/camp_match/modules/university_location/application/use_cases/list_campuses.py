from camp_match.modules.university_location.application.ports.inbound import (
    CampusResponse,
    ListCampuses,
    ListCampusesRequest,
)
from camp_match.modules.university_location.application.ports.outbound import CampusRepository
from camp_match.modules.university_location.domain.value_objects import clean_name, normalize_name
from camp_match.shared_kernel.application.pagination import Page


class ListCampusesUseCase(ListCampuses):
    def __init__(self, repository: CampusRepository) -> None:
        self._repository = repository

    async def execute(self, request: ListCampusesRequest) -> Page[CampusResponse]:
        name_query = normalize_name(request.name_query) if request.name_query else None
        state_region = clean_name(request.state_region) if request.state_region else None

        page = await self._repository.list_campuses(
            page_request=request.page_request,
            name_query=name_query,
            state_region=state_region,
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
