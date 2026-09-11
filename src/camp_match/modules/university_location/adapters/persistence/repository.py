from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.university_location.adapters.persistence.models import (
    CampusModel,
    UniversityModel,
)
from camp_match.modules.university_location.application.errors import (
    CampusAlreadyExists,
    UniversityAlreadyExists,
)
from camp_match.modules.university_location.application.ports.outbound import (
    CampusRepository,
    UniversityRepository,
)
from camp_match.modules.university_location.domain.entities import Campus, University
from camp_match.modules.university_location.domain.value_objects import (
    Coordinates,
    InstitutionStatus,
    InstitutionType,
)
from camp_match.shared_kernel.application.pagination import Page, PageRequest
from camp_match.shared_kernel.domain.identifiers import EntityId


class SqlAlchemyUniversityRepository(UniversityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, university: University) -> None:
        model = UniversityModel(
            id=university.id.value,
            official_name=university.official_name,
            normalized_name=university.normalized_name,
            short_name=university.short_name,
            institution_type=university.institution_type.value,
            status=university.status.value,
            country=university.country,
            state_region=university.state_region,
            source=university.source,
            created_at=university.created_at,
            updated_at=university.updated_at,
        )
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError:
            raise UniversityAlreadyExists(f"University with normalized name {university.normalized_name} already exists.")

    async def get_by_id(self, university_id: EntityId) -> University | None:
        model = await self._session.get(UniversityModel, university_id.value)
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_normalized_name(self, normalized_name: str) -> University | None:
        stmt = select(UniversityModel).where(UniversityModel.normalized_name == normalized_name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, university: University) -> None:
        model = await self._session.get(UniversityModel, university.id.value)
        if not model:
            raise UniversityAlreadyExists(f"University {university.id} not found.")
        
        model.official_name = university.official_name
        model.normalized_name = university.normalized_name
        model.short_name = university.short_name
        model.institution_type = university.institution_type.value
        model.status = university.status.value
        model.country = university.country
        model.state_region = university.state_region
        model.source = university.source
        model.updated_at = university.updated_at
        
        try:
            await self._session.flush()
        except IntegrityError:
            raise UniversityAlreadyExists(f"University with normalized name {university.normalized_name} already exists.")

    async def list_universities(
        self,
        page_request: PageRequest,
        name_query: str | None = None,
        state_region: str | None = None,
        include_inactive: bool = False,
    ) -> Page[University]:
        stmt = select(UniversityModel)
        
        if not include_inactive:
            stmt = stmt.where(UniversityModel.status == InstitutionStatus.ACTIVE.value)
        if name_query:
            stmt = stmt.where(UniversityModel.normalized_name.ilike(f"%{name_query}%"))
        if state_region:
            stmt = stmt.where(UniversityModel.state_region == state_region)
            
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Apply pagination
        stmt = stmt.offset((page_request.page - 1) * page_request.page_size).limit(page_request.page_size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        universities = [self._to_domain(m) for m in models]
        return Page(
            items=universities,
            total=total,
            page=page_request.page,
            page_size=page_request.page_size
        )

    def _to_domain(self, model: UniversityModel) -> University:
        return University(
            id=EntityId(model.id),
            official_name=model.official_name,
            institution_type=InstitutionType(model.institution_type),
            short_name=model.short_name,
            status=InstitutionStatus(model.status),
            country=model.country,
            state_region=model.state_region,
            source=model.source,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlAlchemyCampusRepository(CampusRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, campus: Campus) -> None:
        model = CampusModel(
            id=campus.id.value,
            university_id=campus.university_id.value,
            name=campus.name,
            normalized_name=campus.normalized_name,
            latitude=campus.coordinates.latitude,
            longitude=campus.coordinates.longitude,
            city=campus.city,
            state_region=campus.state_region,
            is_main_campus=campus.is_main_campus,
            status=campus.status.value,
            source=campus.source,
            created_at=campus.created_at,
            updated_at=campus.updated_at,
        )
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError:
            raise CampusAlreadyExists(f"Campus with normalized name {campus.normalized_name} already exists in university {campus.university_id}.")

    async def get_by_id(self, campus_id: EntityId) -> Campus | None:
        model = await self._session.get(CampusModel, campus_id.value)
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_university_and_normalized_name(
        self, university_id: EntityId, normalized_name: str
    ) -> Campus | None:
        stmt = select(CampusModel).where(
            CampusModel.university_id == university_id.value,
            CampusModel.normalized_name == normalized_name,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, campus: Campus) -> None:
        model = await self._session.get(CampusModel, campus.id.value)
        if not model:
            raise CampusAlreadyExists(f"Campus {campus.id} not found.")
        
        model.name = campus.name
        model.normalized_name = campus.normalized_name
        model.latitude = campus.coordinates.latitude
        model.longitude = campus.coordinates.longitude
        model.city = campus.city
        model.state_region = campus.state_region
        model.is_main_campus = campus.is_main_campus
        model.status = campus.status.value
        model.source = campus.source
        model.updated_at = campus.updated_at
        
        try:
            await self._session.flush()
        except IntegrityError:
            raise CampusAlreadyExists(f"Campus with normalized name {campus.normalized_name} already exists.")

    async def list_campuses(
        self,
        page_request: PageRequest,
        name_query: str | None = None,
        state_region: str | None = None,
        include_inactive: bool = False,
    ) -> Page[Campus]:
        stmt = select(CampusModel).join(UniversityModel)
        
        if not include_inactive:
            stmt = stmt.where(CampusModel.status == InstitutionStatus.ACTIVE.value)
            stmt = stmt.where(UniversityModel.status == InstitutionStatus.ACTIVE.value)
            
        if name_query:
            stmt = stmt.where(CampusModel.normalized_name.ilike(f"%{name_query}%"))
        if state_region:
            stmt = stmt.where(CampusModel.state_region == state_region)
            
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Apply pagination
        stmt = stmt.offset((page_request.page - 1) * page_request.page_size).limit(page_request.page_size)
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        campuses = [self._to_domain(m) for m in models]
        return Page(
            items=campuses,
            total=total,
            page=page_request.page,
            page_size=page_request.page_size
        )

    def _to_domain(self, model: CampusModel) -> Campus:
        return Campus(
            id=EntityId(model.id),
            university_id=EntityId(model.university_id),
            name=model.name,
            coordinates=Coordinates(latitude=float(model.latitude), longitude=float(model.longitude)),
            city=model.city,
            state_region=model.state_region,
            is_main_campus=model.is_main_campus,
            status=InstitutionStatus(model.status),
            source=model.source,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
