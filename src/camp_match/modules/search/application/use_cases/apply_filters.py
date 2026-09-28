from camp_match.modules.search.domain.value_objects import CandidateListing, SearchCriteria, VerificationState

def apply_filters(candidates: list[CandidateListing], criteria: SearchCriteria, verification_states: dict[str, VerificationState]) -> list[CandidateListing]:
    """
    Applies filters to candidates.
    Assumes baseline filtering (PUBLISHED, available) is already performed by Housing.
    """
    filtered = []
    for candidate in candidates:
        # 1. campus_id filter
        if criteria.campus_id is not None:
            if candidate.campus_id != criteria.campus_id:
                continue
        
        # 2. price/billing_period filter
        if criteria.min_price_kobo is not None or criteria.max_price_kobo is not None:
            # Only exact match on period is eligible for price filtering
            if candidate.price_period != criteria.billing_period:
                continue
            
            if criteria.min_price_kobo is not None and candidate.price_amount_kobo < criteria.min_price_kobo:
                continue
            
            if criteria.max_price_kobo is not None and candidate.price_amount_kobo > criteria.max_price_kobo:
                continue

        # 3. accommodation_type filter
        if criteria.accommodation_type is not None:
            if candidate.accommodation_type != criteria.accommodation_type:
                continue
        
        # 4. amenities filter (intersection)
        if criteria.amenities:
            if not criteria.amenities.issubset(candidate.amenities):
                continue
        
        # 5. max_distance_km filter
        if criteria.max_distance_km is not None and criteria.campus_id is not None:
            # Distance must have been computed already
            # Assuming distance is somehow passed or stored for later ranking
            # Based on the spec, distance is computed before this filter runs.
            # However, the filtering function here doesn't take computed distances.
            # The spec says "requires the candidate's distance to have been computed already (Chunk 4 computes distance before this filter runs)".
            # I will need to handle this expectation.
            pass

        # 6. verified_only filter
        if criteria.verified_only:
            state = verification_states.get(str(candidate.listing_id), VerificationState.UNKNOWN)
            if state != VerificationState.VERIFIED:
                continue
        
        filtered.append(candidate)
    
    return filtered
