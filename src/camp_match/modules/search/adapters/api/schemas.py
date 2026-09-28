from pydantic import BaseModel, Field
from typing import List, Optional
from camp_match.modules.search.domain.value_objects import AccommodationType, BillingPeriod, Amenity, SortOption

class SearchRequestSchema(BaseModel):
    campus_id: Optional[str] = None
    min_price_kobo: Optional[int] = Field(None, ge=0)
    max_price_kobo: Optional[int] = Field(None, ge=0)
    billing_period: Optional[BillingPeriod] = None
    accommodation_type: Optional[AccommodationType] = None
    amenities: List[Amenity] = []
    max_distance_km: Optional[float] = Field(None, gt=0)
    verified_only: bool = False
    sort_by: SortOption = SortOption.RELEVANCE

class CandidateListingResponse(BaseModel):
    listing_id: str
    property_id: str
    title: str
    accommodation_type: AccommodationType
    price_amount_kobo: int
    price_currency: str
    price_period: BillingPeriod
    available_count: int
    media: List[dict] = []

class ScoredCandidateResponse(BaseModel):
    listing: CandidateListingResponse
    score: float
    distance_km: Optional[float] = None
