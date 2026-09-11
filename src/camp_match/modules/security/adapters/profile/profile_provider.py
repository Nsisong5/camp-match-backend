from __future__ import annotations

from camp_match.modules.profile.application.errors import ProfileNotFound
from camp_match.modules.profile.application.ports.inbound import GetProfileRequest
from camp_match.modules.profile.application.use_cases.get_current_user_profile import (
    GetCurrentUserProfileUseCase,
)
from camp_match.modules.security.application.ports.outbound import ProfileProvider
from camp_match.modules.security.domain.value_objects import Role
from camp_match.shared_kernel.domain.identifiers import EntityId


class InProcessProfileProvider(ProfileProvider):
    def __init__(self, use_case: GetCurrentUserProfileUseCase) -> None:
        self._use_case = use_case

    async def get_profile_type(self, identity_id: EntityId) -> str | None:
        try:
            profile = await self._use_case.execute(GetProfileRequest(identity_id=identity_id))
            # Profile module returns type as a string
            profile_type = profile.profile_type
            if profile_type == "STUDENT":
                return Role.STUDENT.name
            elif profile_type == "SCOUT":
                return Role.SCOUT.name
            return None
        except ProfileNotFound:
            return None
