from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select, and_, update, func
from sqlalchemy.orm import selectinload

from camp_match.modules.housing.adapters.persistence.models import (
    ListingMediaModel,
    ListingModel,
    PropertyModel,
    UnitModel,
)
from camp_match.modules.housing.domain.entities import Listing, Property, Unit
from camp_match.modules.housing.domain.value_objects import (
    BillingPeriod,
    Coordinates,
    Currency,
    ListingStatus,
    Price,
    PropertyStatus,
    PropertyType,
)
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import Page, PageRequest

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyPropertyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, property_: Property) -> None:
        model = PropertyModel(
            id=property_.id.value,
            provider_id=property_.provider_id.value,
            property_type=property_.property_type.value,
            name=property_.name,
            description=property_.description,
            address=property_.address,
            latitude=property_.coordinates.latitude,
            longitude=property_.coordinates.longitude,
            campus_id=property_.campus_id.value if property_.campus_id else None,
            status=property_.status.value,
        )
        self._session.add(model)

    async def get_by_id(self, property_id: EntityId) -> Property | None:
        stmt = select(PropertyModel).where(PropertyModel.id == property_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_provider(self, provider_id: EntityId, page: PageRequest) -> Page[Property]:
        stmt = select(PropertyModel).where(PropertyModel.provider_id == provider_id.value)
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self._session.execute(count_stmt)
        total = total_res.scalar_one()

        # Apply pagination
        offset = (page.page - 1) * page.page_size
        stmt = stmt.offset(offset).limit(page.page_size)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        items = [self._to_domain(m) for m in models]
        return Page(items=items, total=total, page=page.page, page_size=page.page_size)

    list_for_provider = list_by_provider

    async def update(self, property_: Property) -> None:
        stmt = select(PropertyModel).where(PropertyModel.id == property_.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.name = property_.name
            model.description = property_.description
            model.address = property_.address
            model.latitude = property_.coordinates.latitude
            model.longitude = property_.coordinates.longitude
            model.campus_id = property_.campus_id.value if property_.campus_id else None
            model.status = property_.status.value

    def _to_domain(self, model: PropertyModel) -> Property:
        return Property(
            id=EntityId(model.id),
            provider_id=EntityId(model.provider_id),
            property_type=PropertyType(model.property_type),
            name=model.name,
            description=model.description,
            address=model.address,
            coordinates=Coordinates(latitude=model.latitude, longitude=model.longitude),
            campus_id=EntityId(model.campus_id) if model.campus_id else None,
            status=PropertyStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlAlchemyUnitRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, unit: Unit) -> None:
        model = UnitModel(
            id=unit.id.value,
            property_id=unit.property_id.value,
            label=unit.label,
            total_capacity=unit.total_capacity,
            occupied_count=unit.occupied_count,
            is_furnished=unit.is_furnished,
            has_private_bathroom=unit.has_private_bathroom,
            has_kitchen=unit.has_kitchen,
        )
        self._session.add(model)

    async def get_by_id(self, unit_id: EntityId) -> Unit | None:
        stmt = select(UnitModel).where(UnitModel.id == unit_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, unit: Unit) -> None:
        stmt = select(UnitModel).where(UnitModel.id == unit.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.label = unit.label
            model.total_capacity = unit.total_capacity
            model.occupied_count = unit.occupied_count
            model.is_furnished = unit.is_furnished
            model.has_private_bathroom = unit.has_private_bathroom
            model.has_kitchen = unit.has_kitchen

    async def try_reserve(self, unit_id: EntityId) -> bool:
        stmt = (
            update(UnitModel)
            .where(and_(UnitModel.id == unit_id.value, UnitModel.occupied_count < UnitModel.total_capacity))
            .values(occupied_count=UnitModel.occupied_count + 1)
        )
        result = await self._session.execute(stmt)
        if result.rowcount > 0: # type: ignore[attr-defined]
            await self._session.commit()
            return True
        return False

    async def try_release(self, unit_id: EntityId) -> bool:
        stmt = (
            update(UnitModel)
            .where(and_(UnitModel.id == unit_id.value, UnitModel.occupied_count > 0))
            .values(occupied_count=UnitModel.occupied_count - 1)
        )
        result = await self._session.execute(stmt)
        if result.rowcount > 0: # type: ignore[attr-defined]
            await self._session.commit()
            return True
        return False

    def _to_domain(self, model: UnitModel) -> Unit:
        return Unit(
            id=EntityId(model.id),
            property_id=EntityId(model.property_id),
            label=model.label,
            total_capacity=model.total_capacity,
            occupied_count=model.occupied_count,
            is_furnished=model.is_furnished,
            has_private_bathroom=model.has_private_bathroom,
            has_kitchen=model.has_kitchen,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlAlchemyListingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, listing: Listing) -> None:
        model = ListingModel(
            id=listing.id.value,
            property_id=listing.property_id.value,
            unit_id=listing.unit_id.value,
            title=listing.title,
            description=listing.description,
            price_amount_kobo=listing.price.amount_kobo,
            price_currency=listing.price.currency.value,
            price_period=listing.price.period.value,
            status=listing.status.value,
        )
        self._session.add(model)

    async def get_by_id(self, listing_id: EntityId) -> Listing | None:
        stmt = select(ListingModel).where(ListingModel.id == listing_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, listing: Listing) -> None:
        stmt = select(ListingModel).where(ListingModel.id == listing.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.title = listing.title
            model.description = listing.description
            model.price_amount_kobo = listing.price.amount_kobo
            model.status = listing.status.value

    async def get_by_unit_id(self, unit_id: EntityId) -> Listing | None:
        stmt = select(ListingModel).where(ListingModel.unit_id == unit_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def add_media(
        self,
        listing_id: EntityId,
        media_id: EntityId | None = None,
        media_url: str | None = None,
        display_order: int = 0,
    ) -> uuid.UUID:
        media_row_id = uuid.uuid4()
        model = ListingMediaModel(
            id=media_row_id,
            listing_id=listing_id.value,
            media_id=media_id.value if media_id else None,
            media_url=media_url,
            display_order=display_order,
        )
        self._session.add(model)
        await self._session.flush()
        return media_row_id

    async def get_media_for_listing(self, listing_id: EntityId) -> list[ListingMediaModel]:
        stmt = (
            select(ListingMediaModel)
            .where(ListingMediaModel.listing_id == listing_id.value)
            .order_by(ListingMediaModel.display_order.asc(), ListingMediaModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_active(
        self,
        campus_id: EntityId | None,
        property_type: PropertyType | None,
        page: PageRequest
    ) -> Page[Listing]:
        stmt = (
            select(ListingModel)
            .join(UnitModel, ListingModel.unit_id == UnitModel.id)
            .join(PropertyModel, ListingModel.property_id == PropertyModel.id)
            .where(
                and_(
                    ListingModel.status == ListingStatus.PUBLISHED.value,
                    UnitModel.occupied_count < UnitModel.total_capacity
                )
            )
        )

        if campus_id:
            stmt = stmt.where(PropertyModel.campus_id == campus_id.value)
        if property_type:
            stmt = stmt.where(PropertyModel.property_type == property_type.value)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self._session.execute(count_stmt)
        total = total_res.scalar_one()

        offset = (page.page - 1) * page.page_size
        stmt = stmt.offset(offset).limit(page.page_size)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        items = [self._to_domain(m) for m in models]
        return Page(items=items, total=total, page=page.page, page_size=page.page_size)

    def _to_domain(self, model: ListingModel) -> Listing:
        return Listing(
            id=EntityId(model.id),
            property_id=EntityId(model.property_id),
            unit_id=EntityId(model.unit_id),
            title=model.title,
            description=model.description,
            price=Price(
                amount_kobo=model.price_amount_kobo,
                currency=Currency(model.price_currency),
                period=BillingPeriod(model.price_period),
            ),
            status=ListingStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
