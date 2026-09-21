"""Module Housing: authorization.py"""
"""Housing Authorization Service adapter."""

from camp_match.modules.housing.application.ports.outbound import AuthorizationService
from camp_match.modules.security.application.use_cases.authorize_action import AuthorizeActionUseCase
from camp_match.modules.security.application.ports.inbound import AuthorizationRequest
from camp_match.modules.security.domain.value_objects import AuthorizationOutcome, Permission
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.errors import ForbiddenError

class InProcessAuthorizationService(AuthorizationService):
    def __init__(self, authorize_use_case: AuthorizeActionUseCase):
        self._authorize_use_case = authorize_use_case

    async def authorize(
        self,
        identity_id: EntityId,
        permission: Permission,
        resource_owner_id: EntityId | None = None
    ) -> None:
        request = AuthorizationRequest(
            identity_id=identity_id,
            permission=permission,
            resource_owner_id=resource_owner_id
        )
        decision = await self._authorize_use_case.execute(request)
        if decision.outcome != AuthorizationOutcome.ALLOWED:
            raise ForbiddenError(decision.reason)
