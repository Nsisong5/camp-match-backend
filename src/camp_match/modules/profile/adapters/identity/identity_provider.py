
from camp_match.modules.identity.application.ports.inbound import (
    GetIdentityById,
    IdentityQueryRequest,
)
from camp_match.modules.profile.application.ports.outbound import IdentityProvider, IdentitySummary
from camp_match.shared_kernel.application.errors import NotFoundError
from camp_match.shared_kernel.domain.identifiers import EntityId


class InProcessIdentityProvider(IdentityProvider):
    def __init__(self, get_identity_use_case: GetIdentityById) -> None:
        self._use_case = get_identity_use_case

    async def get_identity(self, identity_id: EntityId) -> IdentitySummary | None:
        try:
            response = await self._use_case.execute(IdentityQueryRequest(identity_id=str(identity_id)))
            return IdentitySummary(
                id=EntityId.from_string(response.id),
                email=response.email,
                status=response.status
            )
        except NotFoundError:
            return None
