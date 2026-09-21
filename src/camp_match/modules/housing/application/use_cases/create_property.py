"""Module Housing: create_property.py"""
"""Create property use case."""

from camp_match.modules.housing.application.errors import InvalidLocation
from camp_match.modules.housing.application.ports.inbound import CreatePropertyCommand
from camp_match.modules.housing.application.ports.outbound import (
    ProfileProvider,
    PropertyRepository,
    UniversityLocationProvider,
)
from camp_match.modules.housing.domain.entities import Property
from camp_match.modules.housing.domain.value_objects import Coordinates, PropertyStatus, PropertyType
from camp_match.shared_kernel.application.errors import ForbiddenError
from camp_match.shared_kernel.domain.identifiers import EntityId


from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

class CreatePropertyUseCase:
    def __init__(
        self,
        repo: PropertyRepository,
        profile_provider: ProfileProvider,
        uni_provider: UniversityLocationProvider,
        uow: UnitOfWork,
    ):
        self.repo = repo
        self.profile_provider = profile_provider
        self.uni_provider = uni_provider
        self.uow = uow

    async def __call__(self, command: CreatePropertyCommand) -> EntityId:
        profile_type = await self.profile_provider.get_profile_type(command.provider_id)
        if profile_type != "SCOUT":
            raise ForbiddenError("Only scouts can create properties")

        if command.campus_id and not await self.uni_provider.campus_exists(command.campus_id):
            raise InvalidLocation("Campus does not exist")

        property_id = EntityId.new()
        prop = Property(
            id=property_id,
            provider_id=command.provider_id,
            property_type=PropertyType(command.property_type),
            name=command.name,
            description=command.description,
            address=command.address,
            coordinates=Coordinates(latitude=command.latitude, longitude=command.longitude),
            campus_id=command.campus_id,
            status=PropertyStatus.ACTIVE,
        )

        await self.repo.add(prop)
        await self.uow.commit()
        return property_id
