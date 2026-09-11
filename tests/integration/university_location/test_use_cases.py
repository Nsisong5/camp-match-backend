import pytest

from camp_match.modules.university_location.application.errors import (
    CampusAlreadyExists,
    InactiveInstitution,
    InvalidLocation,
    UniversityAlreadyExists,
    UniversityNotFound,
)
from camp_match.modules.university_location.application.ports.inbound import (
    CreateCampusRequest,
    CreateUniversityRequest,
)
from camp_match.modules.university_location.application.use_cases.create_campus import (
    CreateCampusUseCase,
)
from camp_match.modules.university_location.application.use_cases.create_university import (
    CreateUniversityUseCase,
)
from camp_match.modules.university_location.domain.value_objects import (
    InstitutionStatus,
    InstitutionType,
)
from camp_match.shared_kernel.domain.identifiers import EntityId
from tests.support.university_location_fakes import FakeCampusRepository, FakeUniversityRepository
from tests.support.university_location_fakes_uow import FakeUnitOfWork


@pytest.fixture
def uni_repo():
    return FakeUniversityRepository()

@pytest.fixture
def campus_repo():
    return FakeCampusRepository()

@pytest.fixture
def uow():
    return FakeUnitOfWork()

@pytest.fixture
def create_uni_use_case(uni_repo, uow):
    return CreateUniversityUseCase(uni_repo, uow)

@pytest.fixture
def create_campus_use_case(campus_repo, uni_repo, uow):
    return CreateCampusUseCase(campus_repo, uni_repo, uow)

@pytest.mark.asyncio
async def test_university_creation_success(create_uni_use_case):
    req = CreateUniversityRequest(official_name="Unilag", institution_type=InstitutionType.UNIVERSITY)
    resp = await create_uni_use_case.execute(req)
    assert resp.official_name == "Unilag"

@pytest.mark.asyncio
async def test_university_creation_duplicate_rejected(create_uni_use_case):
    req = CreateUniversityRequest(official_name="Unilag", institution_type=InstitutionType.UNIVERSITY)
    await create_uni_use_case.execute(req)
    with pytest.raises(UniversityAlreadyExists):
        await create_uni_use_case.execute(req)

@pytest.mark.asyncio
async def test_campus_creation_success(create_uni_use_case, create_campus_use_case, uni_repo):
    uni_req = CreateUniversityRequest(official_name="Unilag", institution_type=InstitutionType.UNIVERSITY)
    uni_resp = await create_uni_use_case.execute(uni_req)
    
    campus_req = CreateCampusRequest(university_id=uni_resp.id, name="Main", latitude=0.0, longitude=0.0)
    resp = await create_campus_use_case.execute(campus_req)
    assert resp.name == "Main"

@pytest.mark.asyncio
async def test_campus_creation_nonexistent_university_rejected(create_campus_use_case):
    campus_req = CreateCampusRequest(university_id=str(EntityId.new()), name="Main", latitude=0.0, longitude=0.0)
    with pytest.raises(UniversityNotFound):
        await create_campus_use_case.execute(campus_req)

@pytest.mark.asyncio
async def test_campus_creation_inactive_university_rejected(create_uni_use_case, create_campus_use_case):
    uni_req = CreateUniversityRequest(official_name="Unilag", institution_type=InstitutionType.UNIVERSITY, status=InstitutionStatus.INACTIVE)
    uni_resp = await create_uni_use_case.execute(uni_req)
    
    campus_req = CreateCampusRequest(university_id=uni_resp.id, name="Main", latitude=0.0, longitude=0.0)
    with pytest.raises(InactiveInstitution):
        await create_campus_use_case.execute(campus_req)

@pytest.mark.asyncio
async def test_campus_creation_duplicate_within_university_rejected(create_uni_use_case, create_campus_use_case):
    uni_req = CreateUniversityRequest(official_name="Unilag", institution_type=InstitutionType.UNIVERSITY)
    uni_resp = await create_uni_use_case.execute(uni_req)
    
    campus_req = CreateCampusRequest(university_id=uni_resp.id, name="Main", latitude=0.0, longitude=0.0)
    await create_campus_use_case.execute(campus_req)
    with pytest.raises(CampusAlreadyExists):
        await create_campus_use_case.execute(campus_req)

@pytest.mark.asyncio
async def test_campus_creation_invalid_coordinates_rejected(create_uni_use_case, create_campus_use_case):
    uni_req = CreateUniversityRequest(official_name="Unilag", institution_type=InstitutionType.UNIVERSITY)
    uni_resp = await create_uni_use_case.execute(uni_req)
    
    campus_req = CreateCampusRequest(university_id=uni_resp.id, name="Main", latitude=100.0, longitude=0.0)
    with pytest.raises(InvalidLocation):
        await create_campus_use_case.execute(campus_req)
