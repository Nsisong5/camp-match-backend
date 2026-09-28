import math
from typing import Protocol
from camp_match.modules.search.domain.value_objects import (
    CandidateListing, SearchCriteria, ScoredCandidate, Coordinates, VerificationState
)

def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    R = 6371.0  # Earth's radius in km
    
    lat1_rad = math.radians(coord1.latitude)
    lon1_rad = math.radians(coord1.longitude)
    lat2_rad = math.radians(coord2.latitude)
    lon2_rad = math.radians(coord2.longitude)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

class RankingStrategy(Protocol):
    async def score(self, candidates: list[CandidateListing], criteria: SearchCriteria, verification_states: dict[str, VerificationState]) -> list[ScoredCandidate]:
        ...

class SearchRankingStrategy:
    async def score(self, candidates: list[CandidateListing], criteria: SearchCriteria, verification_states: dict[str, VerificationState]) -> list[ScoredCandidate]:
        scored_candidates = []
        
        for candidate in candidates:
            # Distance computation for proximity
            dist = None
            if criteria.campus_id is not None and candidate.coordinates is not None:
                # In a real system, we'd get campus coordinates from a service
                # Here, we assume the candidate or context might have them
                # For MVP, we need campus coordinates.
                pass
                
            # Weights
            weights = {
                "proximity": 0.35,
                "budget": 0.25,
                "verification": 0.20,
                "freshness": 0.20
            }
            
            # Identify active factors
            active_factors = []
            if criteria.campus_id is not None and dist is not None:
                active_factors.append("proximity")
            if criteria.max_price_kobo is not None:
                active_factors.append("budget")
            # Verification and freshness are always active
            active_factors.extend(["verification", "freshness"])
            
            # Renormalize weights
            total_active_weight = sum(weights[f] for f in active_factors)
            normalized_weights = {f: weights[f] / total_active_weight for f in active_factors}
            
            # Scoring
            score = 0.0
            
            # Proximity
            if "proximity" in normalized_weights and dist is not None:
                proximity_score = max(0.0, 1.0 - dist / 10.0)
                score += proximity_score * normalized_weights["proximity"]
                
            # Budget
            if "budget" in normalized_weights and criteria.max_price_kobo is not None:
                budget_score = max(0.0, min(1.0, 1.0 - (candidate.price_amount_kobo / criteria.max_price_kobo)))
                score += budget_score * normalized_weights["budget"]
                
            # Verification
            state = verification_states.get(str(candidate.listing_id), VerificationState.UNKNOWN)
            verif_score = 1.0 if state == VerificationState.VERIFIED else 0.0
            score += verif_score * normalized_weights["verification"]
            
            # Freshness
            # Simplification: assuming created_at is ISO string
            from datetime import datetime
            created_dt = datetime.fromisoformat(candidate.created_at.replace("Z", "+00:00"))
            days_since = (datetime.now(created_dt.tzinfo) - created_dt).days
            freshness_score = max(0.0, 1.0 - days_since / 90.0)
            score += freshness_score * normalized_weights["freshness"]
            
            scored_candidates.append(ScoredCandidate(candidate, score, dist))
            
        # Deterministic Sorting: Score (desc), Created (desc), ID (asc)
        # To achieve this in one sort, we use: (-score, inverted_created_at, listing_id)
        # Since we can't easily negate a timestamp string directly in the key,
        # we can convert to timestamp (float) and negate that.
        
        from datetime import datetime
        
        def sort_key(sc: ScoredCandidate):
            created_dt = datetime.fromisoformat(sc.listing.created_at.replace("Z", "+00:00"))
            return (-sc.score, -created_dt.timestamp(), sc.listing.listing_id.value)
            
        return sorted(scored_candidates, key=sort_key)
