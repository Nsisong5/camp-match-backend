"""Module Housing: property_management.py"""
"""Update property and archive property use cases."""

from camp_match.modules.housing.application.errors import PropertyNotFound
from camp_match.modules.housing.application.ports.inbound import (
    ArchivePropertyCommand,
    UpdatePropertyCommand,
)
from camp_match.modules.housing.application.ports.outbound import (
    AuthorizationService,
    PropertyRepository,
)
from camp_match.modules.housing.domain.value_objects import PropertyStatus
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import Page, PageRequest
from camp_match.modules.housing.domain.entities import Property


from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

class UpdatePropertyUseCase:
    def __init__(self, repo: PropertyRepository, auth: AuthorizationService, uow: UnitOfWork):
        self.repo = repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: UpdatePropertyCommand) -> None:
        # 1. Lookup
        prop = await self.repo.get_by_id(command.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {command.property_id} not found")
        
        # 2. Authorize
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        
        # 3. Update
        if command.name is not None:
            prop.name = command.name
        if command.description is not None:
            prop.description = command.description
        if command.address is not None:
            prop.address = command.address
        if command.has_water is not None:
            prop.has_water = command.has_water
        if command.has_electricity is not None:
            prop.has_electricity = command.has_electricity
        if command.has_security is not None:
            prop.has_security = command.has_security
        if command.has_parking is not None:
            prop.has_parking = command.has_parking
        if command.has_generator is not None:
            prop.has_generator = command.has_generator
        if command.has_cctv is not None:
            prop.has_cctv = command.has_cctv
        if command.has_wifi is not None:
            prop.has_wifi = command.has_wifi
        
        await self.repo.update(prop)
        await self.uow.commit()


class ArchivePropertyUseCase:
    def __init__(self, repo: PropertyRepository, auth: AuthorizationService, uow: UnitOfWork):
        self.repo = repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: ArchivePropertyCommand) -> None:
        # 1. Lookup
        prop = await self.repo.get_by_id(command.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {command.property_id} not found")
            
        # 2. Authorize
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        
        # 3. Archive
        if prop.status != PropertyStatus.ARCHIVED:
            prop.status = PropertyStatus.ARCHIVED
            await self.repo.update(prop)
            await self.uow.commit()


class ListPropertiesForProviderUseCase:
    def __init__(self, repo: PropertyRepository):
        self.repo = repo

    async def __call__(self, provider_id: EntityId, page: PageRequest) -> Page[Property]:
        return await self.repo.list_for_provider(provider_id, page)


class GetPropertyUseCase:
    def __init__(self, repo: PropertyRepository):
        self.repo = repo

    async def __call__(self, property_id: EntityId) -> Property:
        prop = await self.repo.get_by_id(property_id)
        if not prop:
            raise PropertyNotFound(f"Property {property_id} not found")
        return prop
