from camp_match.modules.search.application.strategies.discovery_strategy import DiscoveryStrategy
from camp_match.modules.search.application.strategies.recently_added import RecentlyAddedStrategy
from camp_match.modules.search.domain.value_objects import ScoredCandidate
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import Page, PageRequest

class RecommendedForYouStrategy:
    def __init__(self, recently_added: RecentlyAddedStrategy) -> None:
        self._recently_added = recently_added

    async def get_feed(self, identity_id: EntityId | None, page_request: PageRequest) -> Page[ScoredCandidate]:
        if identity_id is None:
            return await self._recently_added.get_feed(identity_id, page_request)
        
        # Logic to fetch profile and score by preference match
        return await self._recently_added.get_feed(identity_id, page_request)
