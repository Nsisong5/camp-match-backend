from camp_match.modules.search.application.ports.outbound import VerificationProvider
from camp_match.modules.search.domain.value_objects import EntityId, VerificationState

class VerificationProviderAdapter(VerificationProvider):
    async def get_verification_states(self, listing_ids: list[EntityId]) -> dict[EntityId, VerificationState]:
        # Placeholder implementation
        return {lid: VerificationState.UNKNOWN for lid in listing_ids}
