"""Module Housing: router.py"""
"""Router for housing module."""

from typing import Annotated, List, Generic, TypeVar, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, UploadFile, HTTPException
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

from camp_match.modules.media.adapters.api.dependencies import (
    get_upload_media,
    get_get_authorized_access,
)
from camp_match.modules.media.application.ports.inbound import (
    UploadMediaRequest,
    GetAuthorizedAccessRequest,
)
from camp_match.modules.media.domain.value_objects import MediaPurpose
from camp_match.modules.media.application.use_cases.upload_media import UploadMediaUseCase
from camp_match.modules.media.application.use_cases.get_authorized_access import GetAuthorizedAccessUseCase
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.shared_kernel.application.errors import ForbiddenError

T = TypeVar("T")

class PageSchema(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

router = APIRouter(prefix="/api/v1", tags=["housing"])


async def _build_listing_media_response(listing_id: EntityId, listing_repo, get_access_uc=None):
    media_models = await listing_repo.get_media_for_listing(listing_id)
    media_list = []
    for item in media_models:
        if item.media_id:
            stream_path = f"/api/v1/media/{item.media_id}/stream"
            if get_access_uc:
                try:
                    grant = await get_access_uc.execute(GetAuthorizedAccessRequest(media_id=EntityId(item.media_id)))
                    stream_path = f"{stream_path}?token={grant.token}"
                except Exception:
                    pass
            media_list.append({
                "type": "media",
                "media_id": str(item.media_id),
                "stream_path": stream_path,
            })
        elif item.media_url:
            media_list.append({
                "type": "legacy_url",
                "url": item.media_url,
            })
    return media_list


def _build_listing_response(listing, media_list):
    return schemas.ListingResponseSchema.model_validate({
        "id": listing.id.value,
        "property_id": listing.property_id.value,
        "unit_id": listing.unit_id.value,
        "title": listing.title,
        "description": listing.description,
        "price": {
            "amount_kobo": listing.price.amount_kobo,
            "currency": listing.price.currency.value,
            "period": listing.price.period.value,
        },
        "status": listing.status.value,
        "media": media_list,
    })


@router.post("/properties", response_model=schemas.PropertyResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_property(
    request: schemas.CreatePropertySchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    profile_provider: Annotated[InProcessProfileProvider, Depends(dependencies.get_profile_provider)],
    univ_provider: Annotated[InProcessUniversityLocationProvider, Depends(dependencies.get_university_location_provider)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.PropertyResponseSchema:
    use_case = CreatePropertyUseCase(prop_repo, profile_provider, univ_provider, uow)
    prop_id = await use_case(CreatePropertyCommand(
        provider_id=identity_id,
        property_type=request.property_type,
        name=request.name,
        description=request.description,
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
        campus_id=EntityId(request.campus_id) if request.campus_id else None
    ))
    prop = await GetPropertyUseCase(prop_repo)(prop_id)
    return schemas.PropertyResponseSchema.model_validate({
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
    })


@router.get("/properties/{property_id}", response_model=schemas.PropertyResponseSchema)
async def get_property(
    property_id: UUID,
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)]
) -> schemas.PropertyResponseSchema:
    prop = await GetPropertyUseCase(prop_repo)(EntityId(property_id))
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return schemas.PropertyResponseSchema.model_validate({
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
    })


@router.put("/properties/{property_id}", response_model=schemas.PropertyResponseSchema)
async def update_property(
    property_id: UUID,
    request: schemas.UpdatePropertySchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.PropertyResponseSchema:
    use_case = UpdatePropertyUseCase(prop_repo, auth, uow)
    await use_case(UpdatePropertyCommand(
        identity_id=identity_id,
        property_id=EntityId(property_id),
        name=request.name,
        description=request.description,
        address=request.address,
    ))
    prop = await GetPropertyUseCase(prop_repo)(EntityId(property_id))
    return schemas.PropertyResponseSchema.model_validate({
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
    })


@router.post("/properties/{property_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_property(
    property_id: UUID,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    listing_repo: Annotated[ListingRepository, Depends(dependencies.get_listing_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> None:
    use_case = ArchivePropertyUseCase(prop_repo, listing_repo, auth, uow)
    await use_case(ArchivePropertyCommand(identity_id=identity_id, property_id=EntityId(property_id)))
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
        label=request.label,
        total_capacity=request.total_capacity,
        is_furnished=request.is_furnished,
        has_private_bathroom=request.has_private_bathroom,
        has_kitchen=request.has_kitchen
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


@router.put("/units/{unit_id}", response_model=schemas.UnitResponseSchema)
async def update_unit(
    unit_id: UUID,
    request: schemas.UpdateUnitSchema,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    unit_repo: Annotated[UnitRepository, Depends(dependencies.get_unit_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.UnitResponseSchema:
    use_case = UpdateUnitUseCase(prop_repo, unit_repo, auth, uow)
    await use_case(UpdateUnitCommand(
        identity_id=identity_id,
        unit_id=EntityId(unit_id),
        label=request.label,
        total_capacity=request.total_capacity,
        is_furnished=request.is_furnished,
        has_private_bathroom=request.has_private_bathroom,
        has_kitchen=request.has_kitchen
    ))
    unit = await GetUnitUseCase(unit_repo)(EntityId(unit_id))
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
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)],
    get_access_uc: Annotated[GetAuthorizedAccessUseCase, Depends(get_get_authorized_access)],
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
    media_list = await _build_listing_media_response(listing.id, listing_repo, get_access_uc)
    return _build_listing_response(listing, media_list)


@router.get("/listings/{listing_id}", response_model=schemas.ListingResponseSchema)
async def get_listing_detail(
    listing_id: UUID,
    listing_repo: Annotated[ListingRepository, Depends(dependencies.get_listing_repository)],
    get_access_uc: Annotated[GetAuthorizedAccessUseCase, Depends(get_get_authorized_access)],
) -> schemas.ListingResponseSchema:
    listing = await GetListingUseCase(listing_repo)(EntityId(listing_id))
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    media_list = await _build_listing_media_response(listing.id, listing_repo, get_access_uc)
    return _build_listing_response(listing, media_list)


@router.post("/listings/{listing_id}/media", response_model=schemas.ListingResponseSchema)
async def upload_listing_media(
    listing_id: UUID,
    file: UploadFile,
    identity_id: Annotated[EntityId, Depends(get_current_identity_id)],
    prop_repo: Annotated[PropertyRepository, Depends(dependencies.get_property_repository)],
    listing_repo: Annotated[ListingRepository, Depends(dependencies.get_listing_repository)],
    auth: Annotated[InProcessAuthorizationService, Depends(dependencies.get_auth_service)],
    upload_media_uc: Annotated[UploadMediaUseCase, Depends(get_upload_media)],
    get_access_uc: Annotated[GetAuthorizedAccessUseCase, Depends(get_get_authorized_access)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)],
) -> schemas.ListingResponseSchema:
    listing = await GetListingUseCase(listing_repo)(EntityId(listing_id))
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    prop = await prop_repo.get_by_id(listing.property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    try:
        await auth.authorize(identity_id, Permission.HOUSING_MANAGE, resource_owner_id=prop.provider_id)
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))

    data = await file.read()
    upload_res = await upload_media_uc.execute(UploadMediaRequest(
        purpose=MediaPurpose.LISTING_PHOTO,
        data=data,
        content_type=file.content_type or "image/jpeg",
        original_filename=file.filename or "photo.jpg",
        uploaded_by=identity_id,
    ))

    await listing_repo.add_media(
        listing_id=listing.id,
        media_id=upload_res.media_id,
        media_url=None,
    )
    async with uow:
        await uow.commit()

    media_list = await _build_listing_media_response(listing.id, listing_repo, get_access_uc)
    return _build_listing_response(listing, media_list)


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
