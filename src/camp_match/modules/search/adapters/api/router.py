from fastapi import APIRouter, Depends, Query
from camp_match.modules.search.adapters.api.schemas import SearchRequestSchema, ScoredCandidateResponse
from camp_match.shared_kernel.application.pagination import PageRequest
from camp_match.shared_kernel.domain.identifiers import EntityId

router = APIRouter(prefix="/api/v1/search", tags=["search"])

@router.get("/listings", response_model=list[ScoredCandidateResponse])
async def search_listings(
    request: SearchRequestSchema = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    # This would call the SearchListings use case.
    # For now, return empty to confirm route setup.
    return []

@router.get("/discovery/{strategy_type}", response_model=list[ScoredCandidateResponse])
async def get_discovery_feed(
    strategy_type: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    # This would call the GetDiscoveryFeed use case.
    return []
