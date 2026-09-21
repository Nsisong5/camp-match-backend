"""Module Housing: router.py"""
"""Router for housing module."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from camp_match.modules.housing.adapters.api import schemas, dependencies
from camp_match.modules.housing.application.ports.inbound import (
    CreatePropertyCommand, UpdatePropertyCommand, ArchivePropertyCommand,
    CreateUnitCommand, UpdateUnitCommand,
    CreateListingCommand, UpdateListingCommand, PublishListingCommand,
    UnpublishListingCommand, ArchiveListingCommand
)
from camp_match.modules.housing.application.use_cases.create_property import CreatePropertyUseCase
from camp_match.modules.housing.application.use_cases.property_management import UpdatePropertyUseCase, ArchivePropertyUseCase, ListPropertiesForProviderUseCase, GetPropertyUseCase
from camp_match.modules.housing.application.use_cases.unit_listing_management import (
    CreateUnitUseCase, UpdateUnitUseCase, CreateListingUseCase, UpdateListingUseCase,
    PublishListingUseCase, UnpublishListingUseCase, ArchiveListingUseCase,
    GetListingUseCase, GetUnitUseCase, ListActiveListingsUseCase
)
from camp_match.modules.housing.application.use_cases.check_availability import CheckAvailabilityUseCase
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.shared_kernel.application.pagination import PageRequest
from camp_match.modules.housing.adapters.api.schemas import PropertyResponseSchema
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Generic, TypeVar

T = TypeVar("T")

class PageSchema(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

from camp_match.modules.housing.application.ports.outbound import (
    PropertyRepository,
    UnitRepository,
    ListingRepository,
    AuthorizationService,
)
from camp_match.modules.housing.adapters.security.authorization import InProcessAuthorizationService
from camp_match.modules.housing.adapters.university_location.university_location_provider import InProcessUniversityLocationProvider
from camp_match.modules.housing.adapters.profile.profile_provider import InProcessProfileProvider

router = APIRouter(prefix="/api/v1", tags=["housing"])

@router.post("/properties", response_model=schemas.PropertyResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_property(
    request: schemas.CreatePropertySchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    profile_provider: Annotated[InProcessProfileProvider, Depends(dependencies.get_profile_provider)],
    uni_provider: Annotated[InProcessUniversityLocationProvider, Depends(dependencies.get_uni_provider)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.PropertyResponseSchema:
    use_case = CreatePropertyUseCase(repo, profile_provider, uni_provider, uow)

    campus_id = None
    if request.campus_id:
        campus_id = EntityId(request.campus_id)

    prop_id = await use_case(CreatePropertyCommand(
        provider_id=identity_id,
        property_type=request.property_type,
        name=request.name,
        description=request.description,
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
        campus_id=campus_id
    ))
    prop = await GetPropertyUseCase(repo)(prop_id)
    
    # Map entity to dict matching schema
    prop_data = {
        "id": prop.id.value,
        "provider_id": prop.provider_id.value,
        "property_type": prop.property_type.value,
        "name": prop.name,
        "description": prop.description,
        "address": prop.address,
        "latitude": prop.coordinates.latitude,
        "longitude": prop.coordinates.longitude,
        "campus_id": prop.campus_id.value if prop.campus_id else None,
        "status": prop.status.value
    }
    return schemas.PropertyResponseSchema.model_validate(prop_data)

@router.get("/properties/{property_id}", response_model=schemas.PropertyResponseSchema)
async def get_property(
    property_id: UUID,
    repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)]
) -> schemas.PropertyResponseSchema:
    prop = await GetPropertyUseCase(repo)(EntityId(property_id))
    
    # Map entity to dict matching schema
    prop_data = {
        "id": prop.id.value,
        "provider_id": prop.provider_id.value,
        "property_type": prop.property_type.value,
        "name": prop.name,
        "description": prop.description,
        "address": prop.address,
        "latitude": prop.coordinates.latitude,
        "longitude": prop.coordinates.longitude,
        "campus_id": prop.campus_id.value if prop.campus_id else None,
        "status": prop.status.value
    }
    return schemas.PropertyResponseSchema.model_validate(prop_data)

@router.patch("/properties/{property_id}", response_model=schemas.PropertyResponseSchema)
async def update_property(
    property_id: UUID,
    request: schemas.UpdatePropertySchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.PropertyResponseSchema:
    use_case = UpdatePropertyUseCase(repo, auth, uow)
    await use_case(UpdatePropertyCommand(identity_id=identity_id, property_id=EntityId(property_id), **request.model_dump()))
    prop = await GetPropertyUseCase(repo)(EntityId(property_id))
    
    # Map entity to dict matching schema
    prop_data = {
        "id": prop.id.value,
        "provider_id": prop.provider_id.value,
        "property_type": prop.property_type.value,
        "name": prop.name,
        "description": prop.description,
        "address": prop.address,
        "latitude": prop.coordinates.latitude,
        "longitude": prop.coordinates.longitude,
        "campus_id": prop.campus_id.value if prop.campus_id else None,
        "status": prop.status.value
    }
    return schemas.PropertyResponseSchema.model_validate(prop_data)

@router.post("/properties/{property_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_property(
    property_id: UUID,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> None:
    await ArchivePropertyUseCase(repo, auth, uow)(ArchivePropertyCommand(identity_id=identity_id, property_id=EntityId(property_id)))
    return None

@router.post("/properties/{property_id}/units", response_model=schemas.UnitResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_unit(
    property_id: UUID,
    request: schemas.CreateUnitSchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    unit_repo: Annotated[UnitRepository, Depends(dependencies.get_unit_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.UnitResponseSchema:
    use_case = CreateUnitUseCase(prop_repo, unit_repo, auth, uow)
    unit_id = await use_case(CreateUnitCommand(
        identity_id=identity_id,
        property_id=EntityId(property_id),
        **request.model_dump()
    ))
    unit = await GetUnitUseCase(unit_repo)(unit_id)
    
    unit_data = {
        "id": unit.id.value,
        "property_id": unit.property_id.value,
        "label": unit.label,
        "total_capacity": unit.total_capacity,
        "occupied_count": unit.occupied_count,
        "is_furnished": unit.is_furnished,
        "has_private_bathroom": unit.has_private_bathroom,
        "has_kitchen": unit.has_kitchen
    }
    return schemas.UnitResponseSchema.model_validate(unit_data)

@router.post("/listings", response_model=schemas.ListingResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_listing(
    request: schemas.CreateListingSchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    unit_repo: Annotated[UnitRepository, Depends(dependencies.get_unit_repository)],
    listing_repo: Annotated[ListingRepository, Depends(dependencies.get_listing_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.ListingResponseSchema:
    use_case = CreateListingUseCase(prop_repo, unit_repo, listing_repo, auth, uow)
    listing_id = await use_case(CreateListingCommand(
        identity_id=identity_id,
        property_id=EntityId(request.property_id),
        unit_id=EntityId(request.unit_id),
        title=request.title,
        description=request.description,
        price_amount_kobo=request.price_amount_kobo,
        price_currency=request.price_currency.value,
        price_period=request.price_period.value
    ))
    listing = await GetListingUseCase(listing_repo)(listing_id)
    
    listing_data = {
        "id": listing.id.value,
        "property_id": listing.property_id.value,
        "unit_id": listing.unit_id.value,
        "title": listing.title,
        "description": listing.description,
        "price": {
            "amount_kobo": listing.price.amount_kobo,
            "currency": listing.price.currency.value,
            "period": listing.price.period.value
        },
        "status": listing.status.value
    }
    return schemas.ListingResponseSchema.model_validate(listing_data)

@router.post("/listings/{listing_id}/publish", status_code=status.HTTP_204_NO_CONTENT)
async def publish_listing(
    listing_id: UUID,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    unit_repo: Annotated[UnitRepository, Depends(dependencies.get_unit_repository)],
    listing_repo: Annotated[ListingRepository, Depends(dependencies.get_listing_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> None:
    await PublishListingUseCase(prop_repo, listing_repo, unit_repo, auth, uow)(PublishListingCommand(identity_id=identity_id, listing_id=EntityId(listing_id)))
    return None

@router.get("/properties/list/mine", response_model=schemas.PropertyPageSchema)
async def list_my_properties(
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    page: int = 1,
    page_size: int = 20
) -> schemas.PropertyPageSchema:
    use_case = ListPropertiesForProviderUseCase(repo)
    page_request = PageRequest(page=page, page_size=page_size)
    prop_page = await use_case(identity_id, page_request)
    
    return schemas.PropertyPageSchema(
        items=[
            schemas.PropertyResponseSchema.model_validate({
                "id": p.id.value,
                "provider_id": p.provider_id.value,
                "property_type": p.property_type.value,
                "name": p.name,
                "description": p.description,
                "address": p.address,
                "latitude": p.coordinates.latitude,
                "longitude": p.coordinates.longitude,
                "campus_id": p.campus_id.value if p.campus_id else None,
                "status": p.status.value
            }) for p in prop_page.items
        ],
        total=prop_page.total,
        page=prop_page.page,
        page_size=prop_page.page_size
    )
