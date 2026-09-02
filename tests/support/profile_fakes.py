
from camp_match.modules.profile.application.ports.outbound import (
    IdentityProvider,
    IdentitySummary,
    ProfileRepository,
)
from camp_match.modules.profile.domain.entities import Profile
from camp_match.shared_kernel.domain.identifiers import EntityId


class FakeProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self._profiles: dict[EntityId, Profile] = {}

    async def add(self, profile: Profile) -> None:
        if profile.identity_id in [p.identity_id for p in self._profiles.values()]:
            raise ValueError("Profile already exists")
        self._profiles[profile.id] = profile

    async def get_by_identity_id(self, identity_id: EntityId) -> Profile | None:
        for profile in self._profiles.values():
            if profile.identity_id == identity_id:
                return profile
        return None

    async def get_by_id(self, profile_id: EntityId) -> Profile | None:
        return self._profiles.get(profile_id)

    async def update_core(self, profile: Profile) -> None:
        if profile.id not in self._profiles:
            raise ValueError("Profile not found")
        self._profiles[profile.id] = profile

    async def update_student_extension(self, profile: Profile) -> None:
        await self.update_core(profile)

    async def update_scout_extension(self, profile: Profile) -> None:
        await self.update_core(profile)

class FakeIdentityProvider(IdentityProvider):
    def __init__(self) -> None:
        self._identities: dict[EntityId, IdentitySummary] = {}

    def set_identity(self, identity: IdentitySummary) -> None:
        self._identities[identity.id] = identity

    async def get_identity(self, identity_id: EntityId) -> IdentitySummary | None:
        return self._identities.get(identity_id)
