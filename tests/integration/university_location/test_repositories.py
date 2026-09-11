import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.university_location.adapters.persistence.repository import (
    SqlAlchemyCampusRepository,
    SqlAlchemyUniversityRepository,
)
from camp_match.modules.university_location.domain.entities import Campus, University
from camp_match.modules.university_location.domain.value_objects import (
    Coordinates,
    InstitutionType,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_add_and_get(db_session: AsyncSession):
    uni_repo = SqlAlchemyUniversityRepository(db_session)
    campus_repo = SqlAlchemyCampusRepository(db_session)
    
    uni_id = EntityId.new()
    uni = University(id=uni_id, official_name="Uni", institution_type=InstitutionType.UNIVERSITY)
    await uni_repo.add(uni)
    
    campus_id = EntityId.new()
    coords = Coordinates(latitude=0.0, longitude=0.0)
    campus = Campus(id=campus_id, university_id=uni_id, name="Main", coordinates=coords)
    await campus_repo.add(campus)
    await db_session.commit()
    
    retrieved_uni = await uni_repo.get_by_id(uni_id)
    assert retrieved_uni is not None
    assert retrieved_uni.official_name == "Uni"
    
    retrieved_campus = await campus_repo.get_by_id(campus_id)
    assert retrieved_campus is not None
    assert retrieved_campus.name == "Main"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_campus_main_campus_constraint(db_session: AsyncSession):
    # This requires direct DB manipulation to test the partial unique index
    # We will try to add two main campuses to the same university
    from sqlalchemy import text
    
    uni_id = EntityId.new()
    # Manual setup bypassing repo
    await db_session.execute(text("INSERT INTO universities (id, official_name, normalized_name, institution_type, status, country) VALUES (:id, 'Uni', 'uni', 'UNIVERSITY', 'ACTIVE', 'Nigeria')"), {"id": uni_id.value})
    
    # First main campus
    await db_session.execute(text("INSERT INTO campuses (id, university_id, name, normalized_name, latitude, longitude, is_main_campus, status) VALUES (:id, :u_id, 'C1', 'c1', 0, 0, true, 'ACTIVE')"), {"id": EntityId.new().value, "u_id": uni_id.value})
    
    # Second main campus should fail
    with pytest.raises(Exception): # Postgres IntegrityError
        await db_session.execute(text("INSERT INTO campuses (id, university_id, name, normalized_name, latitude, longitude, is_main_campus, status) VALUES (:id, :u_id, 'C2', 'c2', 0, 0, true, 'ACTIVE')"), {"id": EntityId.new().value, "u_id": uni_id.value})
        await db_session.commit()
