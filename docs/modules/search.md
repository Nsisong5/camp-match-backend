# CAMP MATCH — MODULE 06: SEARCH & DISCOVERY

## Overview
Search & Discovery owns no facts of its own; every field in every result is sourced from other modules. Its purpose is to filter Housing listings, rank them based on relevance, and provide discovery feeds.

## Filtering Rules
A listing is eligible only if it is `PUBLISHED` and has `available_count > 0` (inherited from Housing).
- **campus_id:** Exact match. No `campus_id` in listing = no match.
- **price:** Price bounds inclusive. Billing period must match exactly.
- **accommodation_type:** Exact match.
- **amenities:** Intersection of requested vs listing amenities must equal requested set (all must match).
- **max_distance_km:** Applicable only if `campus_id` is present.
- **verified_only:** If true, only `VERIFIED` state matches.

## Ranking Formula
Weighted sum: `Score = w_p * P_p + w_b * P_b + w_v * P_v + w_f * P_f` (normalized)

| Factor | Weight | Formula |
|---|---|---|
| Proximity | 0.35 | `max(0, 1 - dist/10)` |
| Budget fit | 0.25 | `1 - (price / max_price)` (clamped) |
| Verification| 0.20 | 1.0 (verified) / 0.0 (else) |
| Freshness | 0.20 | `max(0, 1 - days/90)` |

### Haversine Formula
```
Δlat = radians(lat2 − lat1)
Δlon = radians(lon2 − lon1)
a = sin²(Δlat/2) + cos(radians(lat1)) · cos(radians(lat2)) · sin²(Δlon/2)
c = 2 · atan2(√a, √(1−a))
distance_km = R · c
```

## Discovery Strategies
1. **Recently Added:** Freshness weighted 1.0.
2. **Recommended For You:** Weighted sum of Preference match (0.5), Verification (0.25), Freshness (0.25). Fallback to RecentlyAdded if no profile exists.

## Cross-Module Dependencies
- **Housing:** Consumed via the `ListEligibleCandidates` port.
- **University & Location:** Consumed for campus coordinates only, once per request.
- **Profile:** Consumed for Discovery personalization only.
- **Verification:** Port real, data is a stub (`UNKNOWN`).
- **Security:** Authentication only, no permission.

## Housing Modifications
Added purely additive inbound port `ListEligibleCandidates` to Housing (no new API surface).

## Media Resolution
- Search results pass through listing media references sourced from Housing.
- Media items are returned as structured objects: `{ "type": "media", "media_id": "...", "stream_path": "..." }` for files stored in Module 06B, or `{ "type": "legacy_url", "url": "..." }` for legacy URL records.

## Known Limitations
- No campus-proximity discovery personalization (requires Profile `university_name` → `university_id` migration).
- Verification is stubbed pending Module 7.
- No search history or saved searches.
- `sort_by` options other than `RELEVANCE` bypass ranking entirely.
