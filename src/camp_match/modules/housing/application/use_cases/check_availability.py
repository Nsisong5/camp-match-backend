"""Module Housing: check_availability.py"""
"""Check availability use case."""

from camp_match.modules.housing.application.errors import UnitNotFound
from camp_match.modules.housing.application.ports.outbound import UnitRepository
from camp_match.shared_kernel.domain.identifiers import EntityId


class CheckAvailabilityUseCase:
    def __init__(self, unit_repo: UnitRepository):
        self.unit_repo = unit_repo

    async def __call__(self, unit_id: EntityId) -> int:
        """
        Return available count. 
        Note: Not safe for reservation decisions due to race conditions.
        """
        unit = await self.unit_repo.get_by_id(unit_id)
        if not unit:
            raise UnitNotFound(f"Unit {unit_id} not found")
        return unit.available_count
