"""Module Housing: reserve_slot.py"""
"""Reserve slot use case."""

import logging
from camp_match.modules.housing.application.errors import InventoryUnavailable, UnitNotFound
from camp_match.modules.housing.application.ports.outbound import UnitRepository
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = logging.getLogger(__name__)

class ReserveSlotUseCase:
    def __init__(self, unit_repo: UnitRepository):
        self.unit_repo = unit_repo

    async def __call__(self, unit_id: EntityId) -> None:
        success = await self.unit_repo.try_reserve(unit_id)
        if not success:
            unit = await self.unit_repo.get_by_id(unit_id)
            if not unit:
                raise UnitNotFound(f"Unit {unit_id} not found")
            raise InventoryUnavailable(f"No slots available for unit {unit_id}")
            
        logger.info("slot_reserved: unit_id=%s", unit_id)
