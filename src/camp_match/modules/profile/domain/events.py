from dataclasses import dataclass

from camp_match.modules.profile.domain.value_objects import ProfileType
from camp_match.shared_kernel.domain.events import DomainEvent
from camp_match.shared_kernel.domain.identifiers import EntityId


@dataclass(frozen=True)
class ProfileCreated(DomainEvent):
    profile_id: EntityId
    identity_id: EntityId
    profile_type: ProfileType
