from camp_match.modules.search.application.ports.outbound import ProfileProvider
from camp_match.modules.profile.application.use_cases.get_current_user_profile import GetCurrentUserProfile
from camp_match.shared_kernel.domain.identifiers import EntityId

class ProfileProviderAdapter(ProfileProvider):
    def __init__(self, get_profile_use_case: GetCurrentUserProfile):
        self._get_profile_use_case = get_profile_use_case

    async def get_student_preferences(self, identity_id: EntityId) -> dict | None:
        profile = await self._get_profile_use_case.execute(identity_id)
        if not profile or not profile.student_details:
            return None
        return {
            "budget_min": profile.student_details.budget_min_naira,
            "budget_max": profile.student_details.budget_max_naira,
            "accommodation_type": profile.student_details.preferred_accommodation_type,
        }
