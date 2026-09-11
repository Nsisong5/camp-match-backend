import asyncio
from sqlalchemy import select
from camp_match.modules.university_location.adapters.persistence.models import UniversityModel
from camp_match.modules.university_location.domain.value_objects import InstitutionStatus

def main():
    stmt = select(UniversityModel)
    stmt = stmt.where(UniversityModel.status == InstitutionStatus.ACTIVE.value)
    print("SQL:", stmt)

if __name__ == "__main__":
    main()
