"""Module Housing: unit_listing_management.py"""
"""Unit and listing management use cases."""

from camp_match.modules.housing.application.errors import (
    InventoryUnavailable,
    InvalidListingStateTransition,
    ListingNotFound,
    PropertyNotFound,
    UnitNotFound,
)
from camp_match.modules.housing.application.ports.inbound import (
    ArchiveListingCommand,
    CreateListingCommand,
    CreateUnitCommand,
    PublishListingCommand,
    UnpublishListingCommand,
    UpdateListingCommand,
    UpdateUnitCommand,
)
from camp_match.modules.housing.application.ports.outbound import (
    AuthorizationService,
    ListingRepository,
    PropertyRepository,
    UnitRepository,
)
from camp_match.modules.housing.domain.entities import Listing, Unit
from camp_match.modules.housing.domain.value_objects import (
    BillingPeriod,
    Currency,
    ListingStatus,
    Price,
    PropertyType,
)
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import Page, PageRequest


from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

class CreateUnitUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        unit_repo: UnitRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.unit_repo = unit_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: CreateUnitCommand) -> EntityId:
        prop = await self.prop_repo.get_by_id(command.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {command.property_id} not found")
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        unit = Unit(
            id=EntityId.new(),
            property_id=command.property_id,
            label=command.label,
            total_capacity=command.total_capacity,
            is_furnished=command.is_furnished,
            has_private_bathroom=command.has_private_bathroom,
            has_kitchen=command.has_kitchen,
        )
        await self.unit_repo.add(unit)
        await self.uow.commit()
        return unit.id


class UpdateUnitUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        unit_repo: UnitRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.unit_repo = unit_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: UpdateUnitCommand) -> None:
        unit = await self.unit_repo.get_by_id(command.unit_id)
        if not unit:
            raise UnitNotFound(f"Unit {command.unit_id} not found")
        
        prop = await self.prop_repo.get_by_id(unit.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {unit.property_id} not found")
        
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        
        if command.label:
            unit.label = command.label
        if command.total_capacity is not None:
            if command.total_capacity < unit.occupied_count:
                raise InventoryUnavailable("Cannot decrease capacity below occupied count")
            unit.total_capacity = command.total_capacity
        if command.is_furnished is not None:
            unit.is_furnished = command.is_furnished
        if command.has_private_bathroom is not None:
            unit.has_private_bathroom = command.has_private_bathroom
        if command.has_kitchen is not None:
            unit.has_kitchen = command.has_kitchen
            
        await self.unit_repo.update(unit)
        await self.uow.commit()


class CreateListingUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        unit_repo: UnitRepository,
        listing_repo: ListingRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.unit_repo = unit_repo
        self.listing_repo = listing_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: CreateListingCommand) -> EntityId:
        prop = await self.prop_repo.get_by_id(command.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {command.property_id} not found")
        
        unit = await self.unit_repo.get_by_id(command.unit_id)
        if not unit or unit.property_id != command.property_id:
            raise UnitNotFound(f"Unit {command.unit_id} not found in property {command.property_id}")
            
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )

        existing = await self.listing_repo.get_by_unit_id(command.unit_id)
        if existing and existing.status != ListingStatus.ARCHIVED:
            raise InventoryUnavailable("Unit already has a non-archived listing")

        listing = Listing(
            id=EntityId.new(),
            property_id=command.property_id,
            unit_id=command.unit_id,
            title=command.title,
            description=command.description,
            price=Price(
                amount_kobo=command.price_amount_kobo,
                currency=Currency(command.price_currency),
                period=BillingPeriod(command.price_period),
            ),
        )
        await self.listing_repo.add(listing)
        await self.uow.commit()
        return listing.id


class UpdateListingUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        listing_repo: ListingRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.listing_repo = listing_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: UpdateListingCommand) -> None:
        listing = await self.listing_repo.get_by_id(command.listing_id)
        if not listing:
            raise ListingNotFound(f"Listing {command.listing_id} not found")
        
        prop = await self.prop_repo.get_by_id(listing.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {listing.property_id} not found")
        
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )

        if listing.status == ListingStatus.ARCHIVED:
            raise InvalidListingStateTransition("Cannot update an archived listing")

        if command.title:
            listing.title = command.title
        if command.description:
            listing.description = command.description
        if command.price_amount_kobo is not None:
            listing.price = Price(
                amount_kobo=command.price_amount_kobo,
                currency=listing.price.currency,
                period=listing.price.period
            )
        
        await self.listing_repo.update(listing)
        await self.uow.commit()


class GetListingUseCase:
    def __init__(self, repo: ListingRepository):
        self.repo = repo

    async def __call__(self, listing_id: EntityId) -> Listing:
        listing = await self.repo.get_by_id(listing_id)
        if not listing:
            raise ListingNotFound(f"Listing {listing_id} not found")
        return listing
class ListActiveListingsUseCase:
    def __init__(self, repo: ListingRepository):
        self.repo = repo

    async def __call__(
        self,
        campus_id: EntityId | None,
        property_type: PropertyType | None,
        page: PageRequest
    ) -> Page[Listing]:
        return await self.repo.list_active(campus_id, property_type, page)


class GetUnitUseCase:
    def __init__(self, repo: UnitRepository):
        self.repo = repo

    async def __call__(self, unit_id: EntityId) -> Unit:
        unit = await self.repo.get_by_id(unit_id)
        if not unit:
            raise UnitNotFound(f"Unit {unit_id} not found")
        return unit


class PublishListingUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        listing_repo: ListingRepository,
        unit_repo: UnitRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.listing_repo = listing_repo
        self.unit_repo = unit_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: PublishListingCommand) -> None:
        listing = await self.listing_repo.get_by_id(command.listing_id)
        if not listing:
            raise ListingNotFound(f"Listing {command.listing_id} not found")
        
        prop = await self.prop_repo.get_by_id(listing.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {listing.property_id} not found")
        
        # Logging to debug identity mismatch
        import logging
        logger = logging.getLogger(__name__)
        logger.info("authorizing_publish_listing", 
                    identity=str(command.identity_id), 
                    owner=str(prop.provider_id),
                    match=(command.identity_id == prop.provider_id))
        
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        
        unit = await self.unit_repo.get_by_id(listing.unit_id)
        if not unit:
            raise UnitNotFound(f"Unit {listing.unit_id} not found")
            
        if listing.price.amount_kobo <= 0:
            raise InvalidListingStateTransition("Listing must have a price > 0 to publish")
        if unit.available_count <= 0:
            raise InvalidListingStateTransition("Listing unit has no availability")
            
        listing.transition_to(ListingStatus.PUBLISHED)
        await self.listing_repo.update(listing)
        await self.uow.commit()


class UnpublishListingUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        listing_repo: ListingRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.listing_repo = listing_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: UnpublishListingCommand) -> None:
        listing = await self.listing_repo.get_by_id(command.listing_id)
        if not listing:
            raise ListingNotFound(f"Listing {command.listing_id} not found")
        
        prop = await self.prop_repo.get_by_id(listing.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {listing.property_id} not found")
        
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        
        listing.transition_to(ListingStatus.UNAVAILABLE)
        await self.listing_repo.update(listing)
        await self.uow.commit()


class ArchiveListingUseCase:
    def __init__(
        self,
        prop_repo: PropertyRepository,
        listing_repo: ListingRepository,
        auth: AuthorizationService,
        uow: UnitOfWork,
    ):
        self.prop_repo = prop_repo
        self.listing_repo = listing_repo
        self.auth = auth
        self.uow = uow

    async def __call__(self, command: ArchiveListingCommand) -> None:
        listing = await self.listing_repo.get_by_id(command.listing_id)
        if not listing:
            raise ListingNotFound(f"Listing {command.listing_id} not found")
            
        prop = await self.prop_repo.get_by_id(listing.property_id)
        if not prop:
            raise PropertyNotFound(f"Property {listing.property_id} not found")
        
        await self.auth.authorize(
            command.identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id
        )
        
        listing.transition_to(ListingStatus.ARCHIVED)
        await self.listing_repo.update(listing)
        await self.uow.commit()
