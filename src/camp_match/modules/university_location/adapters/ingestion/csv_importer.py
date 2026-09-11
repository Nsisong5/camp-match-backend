import csv

import structlog

from camp_match.modules.university_location.application.ports.inbound import (
    CreateCampus,
    CreateCampusRequest,
    CreateUniversity,
    CreateUniversityRequest,
)
from camp_match.modules.university_location.domain.value_objects import InstitutionType

logger = structlog.get_logger()

# Documentation of CSV format:
# Columns: type,name,institution_type,university_id,latitude,longitude
# type: 'university' or 'campus'
# For 'university': name, institution_type (must match InstitutionType enum values)
# For 'campus': university_id, name, latitude, longitude

async def import_from_csv(
    file_path: str, create_university: CreateUniversity, create_campus: CreateCampus
) -> None:
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if row["type"] == "university":
                    await create_university.execute(
                        CreateUniversityRequest(
                            official_name=row["name"],
                            institution_type=InstitutionType(row["institution_type"]),
                        )
                    )
                elif row["type"] == "campus":
                    await create_campus.execute(
                        CreateCampusRequest(
                            university_id=row["university_id"],
                            name=row["name"],
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                        )
                    )
            except Exception as e:
                logger.warning("csv_import_skip_row", row=row, error=str(e))
