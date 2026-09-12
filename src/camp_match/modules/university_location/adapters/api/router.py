from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from camp_match.modules.security.adapters.api.dependencies import require_permission
from camp_match.modules.security.domain.value_objects import Permission
from camp_match.modules.university_location.adapters.api import dependencies, schemas
from camp_match.modules.university_location.application.ports.inbound import (
    CreateCampusRequest,
    CreateUniversityRequest,
    ListCampusesRequest,
    ListUniversitiesRequest,
    UpdateCampusRequest,
    UpdateUniversityRequest,
)
from camp_match.modules.university_location.application.ports.outbound import (
    CampusRepository,
    UniversityRepository,
)
from camp_match.modules.university_location.application.use_cases.create_campus import (
    CreateCampusUseCase,
)
from camp_match.modules.university_location.application.use_cases.create_university import (
    CreateUniversityUseCase,
)
from camp_match.modules.university_location.application.use_cases.get_campus import GetCampusUseCase
from camp_match.modules.university_location.application.use_cases.get_university import (
    GetUniversityUseCase,
)
from camp_match.modules.university_location.application.use_cases.list_campuses import (
    ListCampusesUseCase,
)
from camp_match.modules.university_location.application.use_cases.list_universities import (
    ListUniversitiesUseCase,
)
from camp_match.modules.university_location.application.use_cases.update_campus import (
    UpdateCampusUseCase,
)
from camp_match.modules.university_location.application.use_cases.update_university import (
    UpdateUniversityUseCase,
)
from camp_match.shared_kernel.application.pagination import PageRequest
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

router = APIRouter(prefix="/api/v1", tags=["university_location"])

# --- University Endpoints ---

@router.post("/universities", response_model=schemas.UniversityResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[require_permission(Permission.UNIVERSITY_MANAGE)])
async def create_university(
    request: schemas.CreateUniversitySchema,
    repo: Annotated[UniversityRepository, Depends(dependencies.get_university_repository)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.UniversityResponseSchema:
    use_case = CreateUniversityUseCase(repo, uow)
    resp = await use_case.execute(CreateUniversityRequest(**request.model_dump()))
    return schemas.UniversityResponseSchema.model_validate(resp)

@router.get("/universities", response_model=schemas.UniversityListResponseSchema)
async def list_universities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name_query: str | None = None,
    state_region: str | None = None,
    include_inactive: bool = False,
    repo: UniversityRepository = Depends(dependencies.get_university_repository),
) -> schemas.UniversityListResponseSchema:
    use_case = ListUniversitiesUseCase(repo)
    request = ListUniversitiesRequest(
        page_request=PageRequest(page=page, page_size=page_size),
        name_query=name_query,
        state_region=state_region,
        include_inactive=include_inactive,
    )
    resp = await use_case.execute(request)
    print(f"DEBUG: Use case returned {len(resp.items)} items.")
    return schemas.UniversityListResponseSchema.model_validate(resp)


@router.get("/universities/{university_id}", response_model=schemas.UniversityResponseSchema)
async def get_university(
    university_id: str,
    repo: Annotated[UniversityRepository, Depends(dependencies.get_university_repository)]
) -> schemas.UniversityResponseSchema:
    use_case = GetUniversityUseCase(repo)
    resp = await use_case.execute(university_id)
    return schemas.UniversityResponseSchema.model_validate(resp)

@router.patch("/universities/{university_id}", response_model=schemas.UniversityResponseSchema, dependencies=[require_permission(Permission.UNIVERSITY_MANAGE)])
async def update_university(
    university_id: str,
    request: schemas.UpdateUniversitySchema,
    repo: Annotated[UniversityRepository, Depends(dependencies.get_university_repository)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.UniversityResponseSchema:
    use_case = UpdateUniversityUseCase(repo, uow)
    resp = await use_case.execute(UpdateUniversityRequest(university_id=university_id, **request.model_dump(exclude_unset=True)))
    return schemas.UniversityResponseSchema.model_validate(resp)

# --- Campus Endpoints ---

@router.post("/universities/{university_id}/campuses", response_model=schemas.CampusResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[require_permission(Permission.UNIVERSITY_MANAGE)])
async def create_campus(
    university_id: str,
    request: schemas.CreateCampusSchema,
    campus_repo: Annotated[CampusRepository, Depends(dependencies.get_campus_repository)],
    uni_repo: Annotated[UniversityRepository, Depends(dependencies.get_university_repository)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.CampusResponseSchema:
    use_case = CreateCampusUseCase(campus_repo, uni_repo, uow)
    resp = await use_case.execute(CreateCampusRequest(university_id=university_id, **request.model_dump()))
    return schemas.CampusResponseSchema.model_validate(resp)

@router.get("/universities/{university_id}/campuses", response_model=schemas.CampusListResponseSchema)
async def list_campuses_for_university(
    university_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name_query: str | None = None,
    state_region: str | None = None,
    include_inactive: bool = False,
    campus_repo: CampusRepository = Depends(dependencies.get_campus_repository),
) -> schemas.CampusListResponseSchema:
    use_case = ListCampusesUseCase(campus_repo)
    request = ListCampusesRequest(
        page_request=PageRequest(page=page, page_size=page_size),
        name_query=name_query,
        state_region=state_region,
        include_inactive=include_inactive,
    )
    resp = await use_case.execute(request)
    return schemas.CampusListResponseSchema.model_validate(resp)

@router.get("/campuses/{campus_id}", response_model=schemas.CampusResponseSchema)
async def get_campus(
    campus_id: str,
    repo: Annotated[CampusRepository, Depends(dependencies.get_campus_repository)]
) -> schemas.CampusResponseSchema:
    use_case = GetCampusUseCase(repo)
    resp = await use_case.execute(campus_id)
    return schemas.CampusResponseSchema.model_validate(resp)

@router.patch("/campuses/{campus_id}", response_model=schemas.CampusResponseSchema, dependencies=[require_permission(Permission.UNIVERSITY_MANAGE)])
async def update_campus(
    campus_id: str,
    request: schemas.UpdateCampusSchema,
    repo: Annotated[CampusRepository, Depends(dependencies.get_campus_repository)],
    uow: Annotated[UnitOfWork, Depends(dependencies.get_uow)]
) -> schemas.CampusResponseSchema:
    use_case = UpdateCampusUseCase(repo, uow)
    resp = await use_case.execute(UpdateCampusRequest(campus_id=campus_id, **request.model_dump(exclude_unset=True)))
    return schemas.CampusResponseSchema.model_validate(resp)

