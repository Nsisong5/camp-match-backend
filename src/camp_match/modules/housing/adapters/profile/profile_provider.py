"""Module Housing: profile_provider.py"""
"""Housing Profile Provider adapter."""

from camp_match.modules.housing.application.ports.outbound import ProfileProvider
from camp_match.modules.profile.application.use_cases.get_current_user_profile import GetCurrentUserProfileUseCase
from camp_match.modules.profile.application.ports.inbound import GetProfileRequest
from camp_match.shared_kernel.domain.identifiers import EntityId

class InProcessProfileProvider(ProfileProvider):
    def __init__(self, get_profile_use_case: GetCurrentUserProfileUseCase):
        self._get_profile_use_case = get_profile_use_case

    async def get_profile_type(self, identity_id: EntityId) -> str | None:
        try:
            profile = await self._get_profile_use_case.execute(
                GetProfileRequest(identity_id=identity_id)
            )
            if profile:
                return profile.profile_type.name if hasattr(profile.profile_type, "name") else str(profile.profile_type)
            return None
        except Exception:
            return None
