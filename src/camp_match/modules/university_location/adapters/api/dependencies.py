from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.university_location.adapters.persistence.repository import (
    SqlAlchemyCampusRepository,
    SqlAlchemyUniversityRepository,
)
from camp_match.modules.university_location.application.ports.outbound import (
    CampusRepository,
    UniversityRepository,
)
from camp_match.platform.db.session import get_db_session
from camp_match.platform.db.unit_of_work import SqlAlchemyUnitOfWork
from camp_match.shared_kernel.application.unit_of_work import UnitOfWork


def get_uow(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)

def get_university_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UniversityRepository:
    return SqlAlchemyUniversityRepository(session)

def get_campus_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CampusRepository:
    return SqlAlchemyCampusRepository(session)
