from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, status

from camp_match.modules.profile.adapters.api import schemas
from camp_match.modules.profile.adapters.api.dependencies import (
    get_create_profile,
    get_get_current_user_profile,
    get_get_public_profile,
    get_update_profile,
    get_update_scout_profile,
    get_update_student_profile,
)
from camp_match.modules.profile.application.ports.inbound import (
    CreateProfileRequest,
    GetProfileRequest,
    GetPublicProfileRequest,
    UpdateProfileRequest,
    UpdateScoutProfileRequest,
    UpdateStudentProfileRequest,
)
from camp_match.platform.security.authentication import get_current_identity_id
from camp_match.shared_kernel.domain.identifiers import EntityId

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])

@router.post("", response_model=schemas.ProfileResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: Annotated[schemas.ProfileCreateRequest, Body(...)],
    identity_id: Annotated[UUID, Depends(get_current_identity_id)],
    use_case=Depends(get_create_profile),
) -> schemas.ProfileResponseSchema:
    request = CreateProfileRequest(
        identity_id=EntityId(identity_id),
        **data.model_dump(),
    )
    result = await use_case.execute(request)
    return schemas.ProfileResponseSchema(
        id=str(result.id.value),
        identity_id=str(result.identity_id.value),
        profile_type=result.profile_type,
        display_name=result.display_name,
        completeness_percentage=result.completeness_percentage,
        bio=result.bio,
        phone_number=result.phone_number,
        avatar_url=result.avatar_url,
        student_details=result.student_details,
        scout_details=result.scout_details,
    )

@router.get("/me", response_model=schemas.ProfileResponseSchema)
async def get_current_user_profile(
    identity_id: Annotated[UUID, Depends(get_current_identity_id)],
    use_case=Depends(get_get_current_user_profile),
) -> schemas.ProfileResponseSchema:
    request = GetProfileRequest(identity_id=EntityId(identity_id))
    result = await use_case.execute(request)
    return schemas.ProfileResponseSchema(
        id=str(result.id.value),
        identity_id=str(result.identity_id.value),
        profile_type=result.profile_type,
        display_name=result.display_name,
        completeness_percentage=result.completeness_percentage,
        bio=result.bio,
        phone_number=result.phone_number,
        avatar_url=result.avatar_url,
        student_details=result.student_details,
        scout_details=result.scout_details,
    )

@router.get("/{profile_id}", response_model=schemas.PublicProfileResponseSchema)
async def get_public_profile(
    profile_id: UUID,
    use_case=Depends(get_get_public_profile),
) -> schemas.PublicProfileResponseSchema:
    request = GetPublicProfileRequest(profile_id=EntityId(profile_id))
    result = await use_case.execute(request)
    return schemas.PublicProfileResponseSchema(
        id=str(result.id.value),
        profile_type=result.profile_type,
        display_name=result.display_name,
        completeness_percentage=result.completeness_percentage,
        bio=result.bio,
        avatar_url=result.avatar_url,
        student_details=result.student_details,
        scout_details=result.scout_details,
    )

@router.patch("/me", response_model=schemas.ProfileResponseSchema)
async def update_profile(
    data: Annotated[schemas.ProfileUpdateRequest, Body(...)],
    identity_id: Annotated[UUID, Depends(get_current_identity_id)],
    use_case=Depends(get_update_profile),
) -> schemas.ProfileResponseSchema:
    request = UpdateProfileRequest(identity_id=EntityId(identity_id), **data.model_dump(exclude_unset=True))
    result = await use_case.execute(request)
    return schemas.ProfileResponseSchema(
        id=str(result.id.value),
        identity_id=str(result.identity_id.value),
        profile_type=result.profile_type,
        display_name=result.display_name,
        completeness_percentage=result.completeness_percentage,
        bio=result.bio,
        phone_number=result.phone_number,
        avatar_url=result.avatar_url,
        student_details=result.student_details,
        scout_details=result.scout_details,
    )

@router.patch("/me/student", response_model=schemas.ProfileResponseSchema)
async def update_student_profile(
    data: Annotated[schemas.StudentProfileUpdateRequest, Body(...)],
    identity_id: Annotated[UUID, Depends(get_current_identity_id)],
    use_case=Depends(get_update_student_profile),
) -> schemas.ProfileResponseSchema:
    request = UpdateStudentProfileRequest(identity_id=EntityId(identity_id), **data.model_dump(exclude_unset=True))
    result = await use_case.execute(request)
    return schemas.ProfileResponseSchema(
        id=str(result.id.value),
        identity_id=str(result.identity_id.value),
        profile_type=result.profile_type,
        display_name=result.display_name,
        completeness_percentage=result.completeness_percentage,
        bio=result.bio,
        phone_number=result.phone_number,
        avatar_url=result.avatar_url,
        student_details=result.student_details,
        scout_details=result.scout_details,
    )

@router.patch("/me/scout", response_model=schemas.ProfileResponseSchema)
async def update_scout_profile(
    data: Annotated[schemas.ScoutProfileUpdateRequest, Body(...)],
    identity_id: Annotated[UUID, Depends(get_current_identity_id)],
    use_case=Depends(get_update_scout_profile),
) -> schemas.ProfileResponseSchema:
    request = UpdateScoutProfileRequest(identity_id=EntityId(identity_id), **data.model_dump(exclude_unset=True))
    result = await use_case.execute(request)
    return schemas.ProfileResponseSchema(
        id=str(result.id.value),
        identity_id=str(result.identity_id.value),
        profile_type=result.profile_type,
        display_name=result.display_name,
        completeness_percentage=result.completeness_percentage,
        bio=result.bio,
        phone_number=result.phone_number,
        avatar_url=result.avatar_url,
        student_details=result.student_details,
        scout_details=result.scout_details,
    )
