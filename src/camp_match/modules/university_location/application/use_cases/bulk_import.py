import csv

import structlog

from camp_match.modules.university_location.application.ports.inbound import (
    BulkImport,
    BulkImportRequest,
    BulkImportResponse,
    CreateCampus,
    CreateCampusRequest,
    CreateUniversity,
    CreateUniversityRequest,
    ImportRowResult,
)
from camp_match.modules.university_location.domain.value_objects import (
    InstitutionType,
)

logger = structlog.get_logger()

class BulkImportUseCase(BulkImport):
    def __init__(
        self,
        create_university: CreateUniversity,
        create_campus: CreateCampus,
    ) -> None:
        self._create_university = create_university
        self._create_campus = create_campus

    async def execute(self, request: BulkImportRequest) -> BulkImportResponse:
        results = []
        created_count = 0
        processed_count = 0
        
        with open(request.file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                processed_count += 1
                try:
                    # Logic to determine if row is University or Campus based on columns
                    # Assuming CSV format defined in docs (Chunk 9)
                    if row.get("type") == "university":
                        await self._create_university.execute(
                            CreateUniversityRequest(
                                official_name=row["name"],
                                institution_type=InstitutionType(row["institution_type"]),
                            )
                        )
                    elif row.get("type") == "campus":
                        await self._create_campus.execute(
                            CreateCampusRequest(
                                university_id=row["university_id"],
                                name=row["name"],
                                latitude=float(row["latitude"]),
                                longitude=float(row["longitude"]),
                            )
                        )
                    created_count += 1
                    results.append(ImportRowResult(row_index=i, success=True))
                except Exception as e:
                    logger.warning("bulk_import_skipped_row", row=i, reason=str(e))
                    results.append(ImportRowResult(row_index=i, success=False, error_reason=str(e)))
                    
        logger.info("bulk_import_summary", processed=processed_count, created=created_count, skipped=processed_count - created_count)
        
        return BulkImportResponse(
            processed_count=processed_count,
            created_count=created_count,
            skipped_count=processed_count - created_count,
            errors=[r for r in results if not r.success],
        )
