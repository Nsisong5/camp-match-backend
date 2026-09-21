"""Module Housing: release_slot.py"""
"""Release slot use case."""

import logging
from camp_match.modules.housing.application.ports.outbound import UnitRepository
from camp_match.shared_kernel.domain.identifiers import EntityId

logger = logging.getLogger(__name__)

class ReleaseSlotUseCase:
    def __init__(self, unit_repo: UnitRepository):
        self.unit_repo = unit_repo

    async def __call__(self, unit_id: EntityId) -> None:
        success = await self.unit_repo.try_release(unit_id)
        if not success:
            logger.warning("failed_to_release_slot: unit_id=%s (already at zero?)", unit_id)
        else:
            logger.info("slot_released: unit_id=%s", unit_id)
