from camp_match.modules.search.application.strategies.discovery_strategy import DiscoveryStrategy
from camp_match.modules.search.domain.value_objects import ScoredCandidate
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import Page, PageRequest

class GetDiscoveryFeed:
    def __init__(self, strategies: dict[str, DiscoveryStrategy]):
        self._strategies = strategies

    async def execute(self, identity_id: EntityId | None, strategy_type: str, page_request: PageRequest) -> Page[ScoredCandidate]:
        strategy = self._strategies.get(strategy_type)
        if not strategy:
            raise ValueError(f"Unknown discovery strategy: {strategy_type}")
            
        return await strategy.get_feed(identity_id, page_request)
