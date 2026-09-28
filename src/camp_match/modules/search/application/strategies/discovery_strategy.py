from typing import Protocol
from camp_match.modules.search.domain.value_objects import ScoredCandidate
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import Page, PageRequest

class DiscoveryStrategy(Protocol):
    async def get_feed(self, identity_id: EntityId | None, page_request: PageRequest) -> Page[ScoredCandidate]:
        ...
