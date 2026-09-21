from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select, and_, update, func
from sqlalchemy.orm import selectinload

from camp_match.modules.housing.adapters.persistence.models import (
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

    async def add(self, prop: Property) -> None:
        model = PropertyModel(
            id=prop.id.value,
            provider_id=prop.provider_id.value,
            property_type=prop.property_type.value,
            name=prop.name,
            description=prop.description,
            address=prop.address,
            latitude=prop.coordinates.latitude,
            longitude=prop.coordinates.longitude,
            campus_id=prop.campus_id.value if prop.campus_id else None,
            has_water=prop.has_water,
            has_electricity=prop.has_electricity,
            has_security=prop.has_security,
            has_parking=prop.has_parking,
            has_generator=prop.has_generator,
            has_cctv=prop.has_cctv,
            has_wifi=prop.has_wifi,
            status=prop.status.value,
        )
        self._session.add(model)

    async def get_by_id(self, property_id: EntityId) -> Property | None:
        stmt = select(PropertyModel).where(PropertyModel.id == property_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, prop: Property) -> None:
        stmt = select(PropertyModel).where(PropertyModel.id == prop.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.name = prop.name
            model.description = prop.description
            model.address = prop.address
            model.status = prop.status.value
            model.has_water = prop.has_water
            model.has_electricity = prop.has_electricity
            model.has_security = prop.has_security
            model.has_parking = prop.has_parking
            model.has_generator = prop.has_generator
            model.has_cctv = prop.has_cctv
            model.has_wifi = prop.has_wifi

    def _to_domain(self, model: PropertyModel) -> Property:
        return Property(
            id=EntityId(model.id),
            provider_id=EntityId(model.provider_id),
            property_type=PropertyType(model.property_type),
            name=model.name,
            description=model.description,
            address=model.address,
            coordinates=Coordinates(latitude=float(model.latitude), longitude=float(model.longitude)),
            campus_id=EntityId(model.campus_id) if model.campus_id else None,
            has_water=model.has_water,
            has_electricity=model.has_electricity,
            has_security=model.has_security,
            has_parking=model.has_parking,
            has_generator=model.has_generator,
            has_cctv=model.has_cctv,
            has_wifi=model.has_wifi,
            status=PropertyStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_for_provider(self, provider_id: EntityId, page: PageRequest) -> Page[Property]:
        stmt = select(PropertyModel).where(PropertyModel.provider_id == provider_id.value)
        
        # Count total for pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.scalar(count_stmt) or 0

        # Apply pagination
        stmt = stmt.offset((page.page - 1) * page.page_size).limit(page.page_size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return Page(
            items=[self._to_domain(m) for m in models],
            total=total,
            page=page.page,
            page_size=page.page_size
        )



# ... (other imports)

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

    async def list_active(
        self,
        campus_id: EntityId | None,
        property_type: PropertyType | None,
        page: PageRequest
    ) -> Page[Listing]:
        # Join with UnitModel to check availability (occupied_count < total_capacity)
        # Join with PropertyModel to filter by campus_id and property_type
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

        # Count total for pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.scalar(count_stmt) or 0

        # Apply pagination
        stmt = stmt.offset((page.page - 1) * page.page_size).limit(page.page_size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return Page(
            items=[self._to_domain(m) for m in models],
            total=total,
            page=page.page,
            page_size=page.page_size
        )

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
