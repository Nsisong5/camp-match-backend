from camp_match.modules.search.application.ports.outbound import HousingProvider
from camp_match.modules.housing.application.ports.outbound import ListingRepository
from camp_match.modules.search.domain.value_objects import CandidateListing, Coordinates
from camp_match.shared_kernel.domain.identifiers import EntityId

class HousingProviderAdapter(HousingProvider):
    def __init__(self, listing_repository: ListingRepository):
        self._listing_repository = listing_repository

    async def list_eligible_candidates(
        self, campus_id: EntityId | None, accommodation_type: None, max_price_kobo: int | None
    ) -> list[CandidateListing]:
        # Implementation to call listing_repository.list_active and transform
        # For this chunk, I will prepare the structure.
        return []
