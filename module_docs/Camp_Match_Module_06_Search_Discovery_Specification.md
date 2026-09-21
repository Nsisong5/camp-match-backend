# CAMP MATCH — MODULE 06: SEARCH & DISCOVERY
**Specification prepared by: Claude (Technical Specification Engineer)**
**For: Gemini CLI (Implementation Agent) and Nsisong**
**Source directive: Chief Engineer → Claude, Search & Discovery Module handoff**

---

## HOW TO READ THIS DOCUMENT

Same conventions as the previous five module specs. This handoff asked for exactly thirteen numbered chunks, followed exactly, with my usual surrounding sections kept for consistency. Code stays minimal, with one exception: the distance formula in Chunk 4 is stated precisely, in full, because "roughly Haversine" leaves room for two implementations to disagree with each other in ways that are genuinely hard to notice in testing.

**On the "sieve" role — this is worth taking seriously, so here's exactly how I applied it:** I read this handoff against every previously shipped module's actual contracts, not just against the architecture diagram. That surfaced one real, significant gap (not a contradiction in this document itself, but a gap between what this module needs and what an *earlier* module actually delivers), and one place where this handoff's request required checking Housing's real, current interface rather than assuming it already exposes what's needed. Both are below, first, before any implementation content — not buried in a chunk where they'd be easy to miss.

---

## ARCHITECTURAL INTERPRETATION & FINDINGS [FOR NSISONG]

Search & Discovery is the first module that owns no facts of its own — every field in every result it returns is sourced from somewhere else. Its actual job is narrower and more precise than "search": decide which of Housing's eligible listings satisfy a request, put them in a defensible order, and say so without ever becoming a second source of truth for anything it's showing.

### FINDING 1 — a real gap, not a contradiction: Discovery can't do campus-proximity personalization yet

Discovery's whole value proposition includes "near your campus," inferred from the student's own profile. But Profile's Student record still stores `university_name` as free text (Module 2, ADR-029) — nobody has migrated it to a real `university_id` yet, even though University & Location has existed since Module 4 and its own spec explicitly flagged this as the natural next step (Module 4, ADR-051). **There is currently no reliable way to resolve "this student's profile" to "this student's campus coordinates."**

I considered fuzzy-matching Profile's free-text name against University & Location's directory as a workaround. I'm not doing that — string-matching two independently-typed names is exactly the kind of fragile, silently-wrong mechanism the whole project has been built to avoid, and it would quietly become a second, unreliable source of truth for something University & Location already owns correctly. Instead: **campus-proximity personalization is not implemented in this pass.** Explicit Search (Part 3's "search" case, where the *student* supplies `campus_id` directly in the request) is completely unaffected — that value comes from the frontend, sourced from University & Location's own directory, not from Profile at all. Only Discovery's *inferred* "near you" is blocked, and it's named as blocked, not silently worked around. See ADR-062.

**This is worth a decision from you, not just information:** the actual fix is small — migrate Profile's Student `university_name` to `university_id`, exactly as Module 4 already recommended. Say the word if you'd like that as a short standalone spec before or after this module ships.

### FINDING 2 — Housing needs one small, additive addition, exactly as its own spec predicted

This handoff (Part 9) asks Search to consume a rich per-listing contract from Housing — status, availability, price, amenities, location, campus reference, timestamps. Housing's *current* public surface doesn't quite offer that: `ListActiveListings`/`GET /listings` (Module 5) was built as a deliberately basic browse placeholder with only two filters and none of the raw fields Search needs to do its own filtering and ranking. Housing's own specification said this explicitly at the time: *"expect it to be wrapped or superseded once [Search] ships"* (Module 5, ADR-059). This module is that moment. Chunk 7 adds one new, small, purely additive inbound port to Housing — nothing about Housing's existing behavior changes. Flagged prominently because it's a real touch of another module's files, even though it's the expected, documented next step rather than a surprise.

No other contradictions were found between this handoff and the established architecture — the rest of it maps cleanly onto existing patterns.

### DECISIONS (ADR-061 … ADR-068) [FOR NSISONG]

Continuing the log from Phase 1–3 (001–013), Identity (014–023), Profile (024–034), Security (035–043), University & Location (044–051), Housing (052–060).

| ADR | Decision | Why |
|---|---|---|
| 061 | Housing's new port does **coarse, index-friendly pre-filtering only** (`campus_id`, `property_type`, a price ceiling) — Search owns every fine-grained filter and every ranking decision | Splits the work by what each module can actually do well: Housing has the indexes and the authoritative eligibility logic (published + available); Search has the cross-module context (distance, preferences, verification) Housing doesn't and shouldn't have. |
| 062 | Campus-proximity **discovery** personalization is not implemented this pass (Finding 1). Explicit **search** by `campus_id` is unaffected | Detailed above. |
| 063 | `VerificationQueryPort` is defined **and genuinely wired into ranking/filtering now**, backed by a `NullVerificationProvider` stub that reports "not verified" for everything until Module 7 ships | Different from every previous deferred port in this project: the *consumer* (this module's own ranking logic) exists today, only the real data source is pending. A conservative stub (never claim verification that hasn't happened) is safe to ship ahead of the real thing. |
| 064 | **No persistence of its own** — no search history, no saved searches | Nothing in the MVP needs it; the handoff itself asks me to decide rather than add it speculatively (Part 4). First module that's purely a stateless query/ranking layer. |
| 065 | Ranking is one documented, explicit weighted sum — every weight and formula given in full (Chunk 4). When an input is genuinely missing (no campus given, no price filter, no profile preferences), that factor is dropped and the remaining weights are **renormalized to sum to 1**, not defaulted to zero | A candidate should never be penalized for context the searcher simply didn't provide. Renormalizing keeps every returned score meaningfully comparable to every other score in the same result set. |
| 066 | A price filter requires an exact `billing_period` alongside it. Search never compares a yearly price to a monthly one — a price bound with no period is a validation error, not a guess | Directly required by Part 14. Silent cross-period comparison would be actively misleading, not just imprecise. |
| 067 | "Recommended for you" **degrades to the same behavior as "recently added"** when the caller has no profile yet, rather than erroring | A freshly registered student opening their feed for the first time shouldn't hit an error screen. |
| 068 | Distance is computed in Search's own domain layer with the Haversine formula on plain latitude/longitude — no PostGIS | Consistent with every prior module's choice (Housing, University & Location) not to introduce spatial database infrastructure nothing currently demands. |


---

## CHUNK 1 — CONTEXT AND ARCHITECTURAL CONTRACT
**[FOR YOU — GEMINI CLI]**

**Implementation instructions:**
1. Read `AI_instructions/` in full and `AI_state/CURRENT_STATE.md`, `ARCHITECTURE_STATE.md`, `DATABASE_STATE.md`, `API_STATE.md`.
2. Read `docs/modules/identity.md`, `profile.md`, `security.md`, `university_location.md`, `housing.md`.
3. Inspect Housing's `application/ports/inbound.py` and `ListActiveListings` — confirm it's as basic as this document assumes, since Chunk 7 replaces it as Search's data source with a new, richer port.
4. Inspect Profile's `student_profiles` table and confirm `university_name` is still free text — confirm Finding 1 is still accurate before building around it.
5. Confirm University & Location's `get_campus_location` and Security's `require_permission`/`get_current_principal` exact signatures.
6. Create the module's empty structure:
```
src/camp_match/modules/search/__init__.py
src/camp_match/modules/search/domain/__init__.py
src/camp_match/modules/search/domain/value_objects.py
src/camp_match/modules/search/domain/ranking.py
src/camp_match/modules/search/application/__init__.py
src/camp_match/modules/search/application/errors.py
src/camp_match/modules/search/application/ports/__init__.py
src/camp_match/modules/search/application/ports/inbound.py
src/camp_match/modules/search/application/ports/outbound.py
src/camp_match/modules/search/application/use_cases/__init__.py
src/camp_match/modules/search/application/strategies/__init__.py
src/camp_match/modules/search/adapters/__init__.py
src/camp_match/modules/search/adapters/housing/__init__.py
src/camp_match/modules/search/adapters/university_location/__init__.py
src/camp_match/modules/search/adapters/profile/__init__.py
src/camp_match/modules/search/adapters/verification/__init__.py
src/camp_match/modules/search/adapters/api/__init__.py
tests/unit/search/__init__.py
tests/unit/search/domain/__init__.py
tests/unit/search/application/__init__.py
tests/integration/search/__init__.py
tests/api/search/__init__.py
```
`domain/ranking.py` gets its own file, same reasoning as Security's `domain/policy.py` — the ranking formula is this module's one real piece of non-trivial domain logic and deserves a clearly-named home. `application/strategies/` is new — it holds the `RankingStrategy`/`DiscoveryStrategy` implementations from Chunks 4–5, kept separate from `use_cases/` since strategies are swappable policy objects, not orchestration.

**No database migration in this chunk or any other in this module** — per ADR-064, this module has no tables.

**Acceptance criteria:** written confirmation of steps 1–5; all files from step 6 importable.

---

## CHUNK 2 — SEARCH DOMAIN MODEL
**[FOR YOU — GEMINI CLI]**

**Files to modify:** `domain/value_objects.py`.

- **`AccommodationType`** (enum) — mirrors Housing's `PropertyType` values exactly (own copy, per the established cross-module discipline — see the System Reference doc's "one pattern" section if you haven't read it).
- **`Amenity`** (enum, 10 values) — mirrors Housing's ten boolean amenity fields by name (`WATER`, `ELECTRICITY`, `SECURITY`, `PARKING`, `GENERATOR`, `CCTV`, `WIFI`, `FURNISHED`, `PRIVATE_BATHROOM`, `KITCHEN`).
- **`BillingPeriod`** (enum) — mirrors Housing's exactly (`YEAR`, `SEMESTER`, `MONTH`).
- **`VerificationState`** (enum) — `VERIFIED`, `UNVERIFIED`, `UNKNOWN` (own copy, ready for Module 7 — `UNKNOWN` is what the stub adapter returns for everything today).
- **`Coordinates`** — own copy, same shape as every prior module's version.
- **`SortOption`** (enum) — `RELEVANCE`, `PRICE_ASC`, `PRICE_DESC`, `DISTANCE`, `NEWEST`.
- **`SearchCriteria`** — `campus_id` (`EntityId | None`), `min_price_kobo`/`max_price_kobo` (`int | None`, non-negative), `billing_period` (`BillingPeriod | None` — **must be set if either price bound is set**, raise `ValueError` at construction otherwise, per ADR-066), `accommodation_type` (`AccommodationType | None`), `amenities` (`frozenset[Amenity]`, defaults empty), `max_distance_km` (`float | None`, positive, only meaningful alongside `campus_id`), `verified_only` (`bool`, default `False`), `sort_by` (`SortOption`, default `RELEVANCE`).
- **`CandidateListing`** — the internal, post-translation shape Search works with once Housing's data has crossed the adapter boundary (Chunk 8): `listing_id`, `property_id`, `title`, `accommodation_type`, `price_amount_kobo`, `price_currency`, `price_period`, `coordinates`, `campus_id`, `amenities` (`frozenset[Amenity]`), `available_count`, `created_at`. This is a plain data holder, not an entity — it has no identity lifecycle of its own within Search, it's a read projection.
- **`ScoredCandidate`** — `CandidateListing` plus `score` (float, 0–1) and `distance_km` (`float | None`).

**Genuine domain logic that belongs here, not treated as a plain DTO:** the `SearchCriteria` price/period invariant above — that's a real business rule (Part 14's explicit requirement), not a transport concern, so it lives in the constructor, not in Pydantic.

**Tests you must write:** `tests/unit/search/domain/test_search_criteria.py` — a price bound with no `billing_period` raises `ValueError`; a price bound with a period constructs fine; negative price bounds and a non-positive `max_distance_km` each raise.

**Acceptance criteria:** new tests pass; no import beyond stdlib + shared-kernel `EntityId`.


---

## CHUNK 3 — FILTERING AND ELIGIBILITY RULES
**[FOR YOU — GEMINI CLI]**

**Files to create:** `application/use_cases/apply_filters.py` (a pure function/class, not a full use case — used internally by `SearchListings` and `GetDiscoveryFeed` alike, so it earns a shared home rather than being duplicated in both).

**Baseline eligibility, before any of Search's own filters apply — never re-derived, always inherited from Housing:** a `CandidateListing` only exists in Search's working set at all if Housing's new port (Chunk 7) already decided it's `PUBLISHED` and has `available_count > 0`. Search does not have, and must never invent, its own opinion about what "available" means.

**On top of that, Search's own filters — each one specified precisely, per Part 13's demand for no ambiguity:**
- `campus_id` — exact match against the candidate's `campus_id`. A candidate with no `campus_id` at all (Housing allows a null campus reference) never matches a `campus_id` filter — excluded, not treated as a wildcard.
- `min_price_kobo`/`max_price_kobo` — both are **inclusive** bounds (`>=`/`<=`, not strict). Only candidates whose `price_period` exactly equals the supplied `billing_period` are eligible for a price-filtered search at all — a candidate with a different period is excluded from the *results*, not silently compared (ADR-066). State this exact behavior in the docstring, since it's easy to misremember as "convert and compare."
- `accommodation_type` — exact match.
- `amenities` — a candidate must have **every** requested amenity (set intersection equals the requested set, not just a non-empty overlap) — "furnished AND has WiFi" means both, not either.
- `max_distance_km` — only applicable when `campus_id` is also set (if `campus_id` is absent, ignore this filter entirely rather than erroring — there's nothing to measure distance from). Requires the candidate's distance to have been computed already (Chunk 4 computes distance before this filter runs, since ranking needs it too — don't compute it twice).
- `verified_only` — when `True`, only `VerificationState.VERIFIED` candidates pass; `UNVERIFIED` and `UNKNOWN` are both excluded (a conservative reading — "unknown" never counts as verified).

**Tests you must write:** `tests/unit/search/application/test_apply_filters.py` — one test per filter above in isolation, plus at least one combination test (campus + price + amenities together) confirming filters compose with AND semantics, not OR. Specifically test: a candidate with no `campus_id` is excluded by a `campus_id` filter; a candidate with a mismatched `billing_period` is excluded from a price-filtered search even if its price would otherwise qualify; partial amenity overlap is rejected, not accepted.

**Acceptance criteria:** new tests pass.

---

## CHUNK 4 — RANKING SYSTEM
**[FOR YOU — GEMINI CLI]**

**Files to modify:** `domain/ranking.py`.

**The `RankingStrategy` port** (defined here in the domain file as a `Protocol`, even though it's conceptually an application-layer strategy — small enough not to need a separate ports file): `score(candidates: list[CandidateListing], criteria: SearchCriteria) -> list[ScoredCandidate]`.

**`SearchRankingStrategy` — the MVP implementation, four factors, explicit weights that sum to 1.0 when every factor is computable:**

| Factor | Weight | Formula | When excluded (input missing) |
|---|---|---|---|
| Proximity | 0.35 | `max(0, 1 - distance_km / 10)` — 10km is the point past which proximity stops contributing at all, not a hard cutoff, just diminishing to zero | `campus_id` not supplied |
| Budget fit | 0.25 | `1 - (price_amount_kobo / max_price_kobo)`, clamped to [0, 1] — cheaper relative to the ceiling scores higher | `max_price_kobo` not supplied |
| Verification | 0.20 | `1.0` if `VERIFIED`, else `0.0` | never excluded — always computable, defaults to `0.0` for `UNVERIFIED`/`UNKNOWN` since "unknown" is not a reason to boost a score |
| Freshness | 0.20 | `max(0, 1 - days_since_created / 90)` | never excluded |

**When a factor is excluded, renormalize the remaining weights to sum to 1** (ADR-065) — e.g. if proximity is excluded, budget fit becomes `0.25 / 0.65`, verification `0.20 / 0.65`, freshness `0.20 / 0.65`, preserving their *relative* weight to each other while still producing a score in [0, 1].

**Distance calculation — exact formula, Haversine, stated precisely so two implementations can't disagree:**
Given two points in decimal degrees (`lat1, lon1`) and (`lat2, lon2`), and Earth's radius `R = 6371` km:
```
Δlat = radians(lat2 − lat1)
Δlon = radians(lon2 − lon1)
a = sin²(Δlat/2) + cos(radians(lat1)) · cos(radians(lat2)) · sin²(Δlon/2)
c = 2 · atan2(√a, √(1−a))
distance_km = R · c
```
Implement this once, as a pure function in `domain/ranking.py`, taking two `Coordinates` and returning a `float`. If either coordinate is somehow out of the valid range (shouldn't happen — both sides already validate at their own boundary — but don't trust that blindly), log a WARNING and treat distance as uncomputable for that candidate (excluded from proximity scoring, not a crash).

**Ordering — deterministic, three levels (ADR / Part 24):** primary sort `score` descending; tie-break 1: `created_at` descending (newer first); tie-break 2: `listing_id` ascending. Implement this as the actual sort key, not an approximation — two candidates with identical scores and identical timestamps must still produce a stable, repeatable order across runs.

**Tests you must write:** `tests/unit/search/domain/test_ranking.py` — the Haversine formula against at least two known real-world distance pairs with a documented expected value (pick two Nigerian cities with a well-known approximate distance and assert within a small tolerance); weight renormalization when proximity is excluded (assert the remaining three weights actually sum to 1 and their *ratios* to each other are unchanged); the three-level deterministic tie-break, constructed with candidates deliberately sharing a score, then sharing a score and `created_at` too.

**Acceptance criteria:** new tests pass; manually verify the Haversine test's expected distance against a known reference (e.g. a mapping tool) rather than just trusting the formula was transcribed correctly.


---

## CHUNK 5 — DISCOVERY SYSTEM
**[FOR YOU — GEMINI CLI]**

**Files to create:** `application/strategies/discovery_strategy.py`, `application/strategies/recommended_for_you.py`, `application/strategies/recently_added.py`.

**`DiscoveryStrategy`** (`Protocol`): `get_feed(identity_id: EntityId | None, page_request: PageRequest) -> Page[ScoredCandidate]`. Takes `identity_id` as optional specifically so `RecentlyAdded` (which needs no user context at all) and `RecommendedForYou` (which does, when available) share one interface.

**Exactly two discovery experiences for MVP (ADR / Part 20's "small set"):**

**`RecentlyAdded`** — no personalization: all eligible candidates (same baseline as Chunk 3 — published + available, no other filters), scored by freshness alone (weight 1.0, the same formula as Chunk 4's freshness factor), tie-broken the same three-level way.

**`RecommendedForYou`** — steps:
1. If `identity_id` is `None`, or the identity has no profile (`ProfileProvider` returns nothing — Chunk 8), **delegate entirely to `RecentlyAdded`'s behavior** (ADR-067) — do not raise an error, do not return an empty result; log INFO (`"discovery_fallback_no_profile"`) so it's visible in the logs without being visible to the user as a failure.
2. Otherwise, fetch the caller's preferences via `ProfileProvider` — whichever of `preferred_accommodation_type`, `budget_min_naira`/`budget_max_naira`, `cleanliness_preference`, `sleep_schedule` are actually set (any or all may be unset; that's normal, not an error).
3. Baseline eligibility, same as always (published + available) — **no hard filtering on preferences** (ADR — ADR decision recorded in the ranking table below, not a new numbered one, since it follows directly from ADR-065's "missing input reduces weight, never excludes a candidate" principle extended to preferences too): every eligible candidate is scored, none are excluded just for not matching a preference.
4. Score with **`DiscoveryRankingStrategy`** — three factors:

| Factor | Weight | Formula | When excluded |
|---|---|---|---|
| Preference match | 0.50 | fraction of the student's *set* preference dimensions that this candidate matches (accommodation type equality; price within `[budget_min, budget_max]` if both set, or on the correct side of whichever bound is set) | student has no preferences set at all |
| Verification | 0.25 | same as Chunk 4 | never excluded |
| Freshness | 0.25 | same as Chunk 4 | never excluded |

No proximity factor at all in Discovery (Finding 1/ADR-062) — not weighted at zero, structurally absent from this table, so there's nothing to accidentally re-enable by copying Chunk 4's table without thinking.

**Tests you must write:** `tests/unit/search/application/test_recently_added.py` (pure freshness ordering) and `tests/unit/search/application/test_recommended_for_you.py` — a caller with no profile gets identical output to `RecentlyAdded` for the same candidate set (the actual fallback proof, not just "doesn't error"); a caller with only `preferred_accommodation_type` set scores a matching candidate higher than a non-matching one, with the weight redistributed correctly between the remaining two factors; a caller with a budget range scores an in-range candidate higher than an out-of-range one.

**Acceptance criteria:** new tests pass, all against fakes.

---

## CHUNK 6 — APPLICATION LAYER
**[FOR YOU — GEMINI CLI]**

**Files to create:** `application/use_cases/search_listings.py`, `application/use_cases/get_discovery_feed.py`.

**`SearchListings` — steps:** fetch candidates from `HousingProvider` (Chunk 8) using `SearchCriteria`'s coarse fields (`campus_id`, `accommodation_type`, `max_price_kobo` as a ceiling) as the pre-filter passed to Housing's new port; if `campus_id` is set, resolve its coordinates once via `UniversityLocationProvider` (**once per request, not once per candidate** — this matters, see Chunk 8) and compute each candidate's distance; resolve verification state for the candidate set via `VerificationProvider`; apply Chunk 3's fine filters; score via `SearchRankingStrategy` (or re-sort by a plain field if `sort_by` isn't `RELEVANCE` — `PRICE_ASC`/`PRICE_DESC`/`DISTANCE`/`NEWEST` bypass the weighted score entirely and sort directly on that field, still with the same three-level tie-break); paginate; log INFO (`"search_executed"`, filter summary, result count — not the full candidate list, just counts); return the page.

**`GetDiscoveryFeed` — steps:** resolve `identity_id` from the authenticated caller; select the strategy by the requested type (default `RECOMMENDED_FOR_YOU`); delegate to it; paginate; log INFO; return the page.

**Application errors this layer can raise:** `InvalidSearchCriteria` (a price bound without a period reaching this far — shouldn't happen if Chunk 9's DTOs are right, but the domain-level `ValueError` from Chunk 2 gets caught and translated here as defense in depth), `UnsupportedFilterCombination` (reserved — not triggered in this implementation; every documented filter combination is well-defined, so nothing currently raises this, same honesty note as every previous module's reserved-but-unused error types).

**Tests you must write:** `tests/unit/search/application/test_search_listings.py` and `test_get_discovery_feed.py`, against fakes for every outbound port — full orchestration: filters applied, ranking applied, pagination applied, the non-relevance sort options each produce correctly-ordered output, and a `campus_id`'s coordinates are fetched **exactly once** per search call regardless of candidate count (assert the fake `UniversityLocationProvider` was called exactly once, not once per candidate — this is the actual proof the N+1 concern from Chunk 8 doesn't exist).

**Acceptance criteria:** new tests pass, all against fakes — no real Housing/Profile/University & Location/Verification/Security code executed.


---

## CHUNK 7 — PORTS AND CROSS-MODULE CONTRACTS
**[FOR YOU — GEMINI CLI]**

**Files to modify (this module):** `application/ports/inbound.py`, `application/ports/outbound.py`.

**Inbound:** `SearchListings`, `GetDiscoveryFeed` — `Protocol`-with-`execute`, dataclass request/response, same convention as every previous module.

**Outbound (this module's own copies, each implemented by an adapter in Chunk 8):**
- **`HousingProvider`** — `list_eligible_candidates(campus_id: EntityId | None, accommodation_type: AccommodationType | None, max_price_kobo: int | None, limit: int = 500) -> list[CandidateListing]`.
- **`UniversityLocationProvider`** — `get_campus_coordinates(campus_id: EntityId) -> Coordinates | None`.
- **`ProfileProvider`** — `get_student_preferences(identity_id: EntityId) -> StudentPreferences | None` (a small dataclass carrying whichever of the four preference fields are set — returns `None` if no profile exists at all, distinct from a profile that exists with nothing set).
- **`VerificationProvider`** — `get_verification_states(listing_ids: list[EntityId]) -> dict[EntityId, VerificationState]` (batched — one call for the whole candidate set, not one per listing, same N+1 discipline as the coordinates lookup).

**The one cross-module addition — Housing's new inbound port (Finding 2 / ADR-061):**

**Files to create in `modules/housing/`:** `application/use_cases/list_eligible_candidates.py`.
**Files to modify in `modules/housing/`:** `application/ports/inbound.py` (add the new port), `adapters/api/router.py` — **no new HTTP route**, this port is for in-process consumption only, so nothing changes in Housing's API surface.

Housing's new use case, `ListEligibleCandidates`: same baseline eligibility as `ListActiveListings` (`PUBLISHED` + `available_count > 0` — reuse the existing repository method, do not duplicate that logic), accepting the three coarse filter parameters above, returning up to `limit` results with **no pagination metadata** (Search does its own pagination after filtering/ranking, so a paginated response here would be the wrong shape) and a richer field set than `ListActiveListings`'s response DTO: every field `CandidateListing` needs, listed in Chunk 2.

**Prohibition:** this is the *only* change to Housing anywhere in this module's chunks. Do not touch `ListActiveListings`, any existing endpoint, or any file not named above.

**Tests you must write:** `tests/unit/housing/application/test_list_eligible_candidates.py` (in Housing's own test folder, since this is Housing's use case) — confirms it returns the same eligibility set as `ListActiveListings` would (published + available), just with the richer field shape and the three coarse filters working correctly; confirm Housing's full pre-existing test suite is unaffected.

**Acceptance criteria:** `poetry run mypy` clean on every file above; `poetry run pytest tests/unit/housing tests/integration/housing tests/api/housing` shows the same results as before this chunk, plus the one new test.

---

## CHUNK 8 — PERSISTENCE/QUERY ADAPTER
**[FOR YOU — GEMINI CLI]**

**Objective:** the in-process adapters implementing Chunk 7's outbound ports — no Search-owned persistence (ADR-064), every one of these calls another module's use case directly.

**Files to create:** `adapters/housing/housing_provider.py`, `adapters/university_location/university_location_provider.py`, `adapters/profile/profile_provider.py`, `adapters/verification/verification_provider.py`.

**`InProcessHousingProvider`:** calls Housing's new `ListEligibleCandidates` use case (Chunk 7), maps its response into this module's own `CandidateListing` — translating Housing's `PropertyType`/amenity booleans/`Coordinates` into Search's own mirrored types, per the established boundary discipline. Never imports `modules.housing.adapters` or `modules.housing.domain`.

**`InProcessUniversityLocationProvider`:** calls University & Location's `get_campus_location`. **Performance note, worth stating explicitly since it's easy to get wrong by accident:** `SearchListings`/`GetDiscoveryFeed` (Chunk 6) call this **once per request** for the one `campus_id` in the criteria, never once per candidate — the adapter itself doesn't need internal caching to achieve this, since the *use case* only calls it once by construction; don't add a cache here to compensate for a use case calling it wrong, fix the use case instead if that's ever the actual problem.

**`InProcessProfileProvider`:** calls Profile's `GetCurrentUserProfile`, returns `None` if `ProfileNotFound` is raised (a normal state, not an error — same pattern as every previous `ProfileProvider` in this project), otherwise maps the four preference fields.

**`NullVerificationProvider`** (ADR-063): returns `VerificationState.UNKNOWN` for every listing id in the batch, unconditionally — no real call to anything, since Module 7 doesn't exist. Write it so that replacing it with a real adapter later is a one-line change in Chunk 9's dependency wiring, not a rewrite of anything that calls it.

**Tests you must write:** one unit test per adapter, using fakes for the use case each one calls — confirms the field mapping is correct in both directions (a Housing `PropertyType.LODGE` becomes Search's `AccommodationType.LODGE`, etc.) and that `None`/empty cases are handled without raising.

**Acceptance criteria:** new tests pass.


---

## CHUNK 9 — API/FASTAPI ADAPTERS
**[FOR YOU — GEMINI CLI]**

**Files to create:** `adapters/api/schemas.py`, `adapters/api/router.py`, `adapters/api/dependencies.py`.
**Files to modify:** `app.py`.

**Two endpoints, both under `/api/v1`, both requiring authentication only — no special permission, same reasoning as Profile's public view and Housing's browse endpoint:**

| Method | Path | Query parameters |
|---|---|---|
| GET | `/search` | `campus_id`, `min_price_kobo`, `max_price_kobo`, `billing_period`, `accommodation_type`, `amenities` (repeatable), `max_distance_km`, `verified_only`, `sort_by`, `page`, `page_size` |
| GET | `/discovery` | `strategy` (`RECOMMENDED_FOR_YOU` default, or `RECENTLY_ADDED`), `page`, `page_size` |

**Response shape (both endpoints, same `SearchResultItem` DTO, wrapped in the shared `Page` shape):** `listing_id`, `property_id`, `title`, `accommodation_type`, `price` (`{amount_kobo, currency, period}`), `location_summary` (city/state from the property), `distance_km` (nullable), `amenities` (list), `available_count`, `verification_state`, `media` (list of URLs), `relevance_score`.

**Validation:** Pydantic enforces primitive shape/range; the price/period pairing rule (ADR-066) is re-validated at the DTO layer too (fail fast, clear 422, before it would otherwise reach the domain constructor) — document this as intentional double-validation, same reasoning given in Housing/Profile's specs for why a genuine business rule sometimes deserves a check at both boundaries.

**Prohibition:** no business logic in `router.py`.

**Tests you must write:** placeholder only — real API tests arrive in Chunk 11.

**Acceptance criteria:** the app starts; both endpoints behave as described when exercised manually.

---

## CHUNK 10 — INTEGRATION
**[FOR YOU — GEMINI CLI]**

**Objective:** confirm, end to end, that every cross-module dependency actually works together — not new code, verification and explicit documentation of what's already been wired.

**Implementation instructions:** run a manual end-to-end pass (the Manual Testing Guide below has exact steps) confirming: a real listing created in Housing (Module 5) shows up in `GET /search` and `GET /discovery`; a real campus from University & Location affects `distance_km` and proximity ranking correctly; a real Profile's preferences measurably change `GET /discovery`'s ordering; Security correctly rejects an unauthenticated request to either endpoint.

Write the following into `docs/modules/search.md` (Chunk 12) plainly, as its own "Cross-Module Dependencies" section — this is required documentation, not optional color:
- **Housing:** consumed via the new `ListEligibleCandidates` port (Chunk 7) — the only module Search depends on for its actual result set.
- **University & Location:** consumed for campus coordinates only, once per request.
- **Profile:** consumed for Discovery personalization only — Search (the explicit-criteria path) never touches Profile at all.
- **Verification:** the port is real and wired; the data behind it is a stub (`UNKNOWN` for everything) until Module 7 ships.
- **Security:** authentication only, no permission — consistent with every other read-only, non-privileged endpoint in the project.

**Acceptance criteria:** the end-to-end manual pass succeeds; the "Cross-Module Dependencies" section exists and states the Verification stub plainly, not just implies it.

---

## CHUNK 11 — TESTING
**[FOR YOU — GEMINI CLI]**

**Files to create:** `tests/api/search/test_search_flow.py`, `tests/api/search/test_discovery_flow.py`, `tests/api/search/test_ranking_determinism.py`; extend the import-linter contract list.

**`test_search_flow.py`:** through real HTTP calls — create a Scout, a property with two listings at different prices and different distances from a seeded campus, publish both; search with a `campus_id` filter, confirm both appear, ordered by relevance with the closer one weighted appropriately; search with a price filter and a mismatched `billing_period`, confirm the correct one is excluded; search with `amenities` requiring two flags, confirm partial matches are excluded; confirm an unpublished/sold-out listing never appears regardless of filters.

**`test_discovery_flow.py`:** a Student with preferences set gets a feed reflecting them; a Student with no profile at all gets the same feed as `RECENTLY_ADDED` (the actual fallback proof, via real HTTP this time, not just the unit-level one from Chunk 5).

**`test_ranking_determinism.py`:** the specific proof the handoff asks for (Part 36) — construct three listings, A/B/C, with known, deliberately-chosen attributes, and assert the exact resulting order matches a documented expectation, in both directions (change one factor, confirm the order changes predictably).

**Extend import-linter:** `camp_match.modules.search.domain` and `.application` must not import `fastapi` or `sqlalchemy`; nothing outside `camp_match.modules.search` may import its `adapters.*` directly; the four cross-module adapters may each import their respective target module's `application.ports` only, never `adapters`/`domain`.

**Run everything:** `poetry run pytest`, `poetry run ruff check .`, `poetry run mypy src`, `poetry run lint-imports` — the whole project, all six modules and the foundation, green.

**Acceptance criteria:** every scenario above passes; the ranking determinism test specifically demonstrates a *predictable* change in order when a *specific* factor changes, not just "some order came out."

---

## CHUNK 12 — DOCUMENTATION AND AI STATE
**[FOR YOU — GEMINI CLI]**

See "Module Documentation Requirements" and "AI State Requirements" below. Set `AI_state/CURRENT_TASK.md` to the standard format (per the session-protocol update from the last resumed session) reflecting Search & Discovery complete, next module pending.

---

## CHUNK 13 — FINAL VERIFICATION
**[FOR YOU — GEMINI CLI]**

Confirm every item in the Completion Checklist below, run the full six-module suite one final time from a clean state, and specifically re-confirm Housing's own suite is unaffected apart from the one new test from Chunk 7 — this module touched another module's files, and that's the check that proves it didn't break anything there.


---

## FRONTEND DOCUMENTATION [FOR NSISONG — copy into your Front End Doc]

**Applies to both endpoints below:** results are not a booking guarantee. A listing can sell out or change between when it's shown and when a student tries to act on it — the future Booking module performs the real, final availability check. Design the UI accordingly (e.g. handle a "no longer available" response gracefully at booking time, don't treat search results as reserved).

### GET /api/v1/search
**Authentication:** required. **Authorization:** none.
**Query parameters:** `campus_id`, `min_price_kobo`, `max_price_kobo`, `billing_period` (`YEAR`/`SEMESTER`/`MONTH` — **required if either price bound is set**, omit entirely otherwise), `accommodation_type`, `amenities` (repeat the parameter for each one, all must match), `max_distance_km` (only meaningful with `campus_id`), `verified_only` (default `false`), `sort_by` (`RELEVANCE` default, or `PRICE_ASC`/`PRICE_DESC`/`DISTANCE`/`NEWEST`), `page`, `page_size`.
**Success — 200:** paginated `SearchResultItem` list.
**Errors:** 422 `invalid_search_criteria` (most commonly: a price bound with no `billing_period`).
**Frontend notes:** `distance_km` is `null` whenever `campus_id` wasn't supplied — don't display a distance the user didn't ask to filter/sort by unless you want it purely informational, in which case supply `campus_id`.

### GET /api/v1/discovery
**Authentication:** required. **Authorization:** none.
**Query parameters:** `strategy` (`RECOMMENDED_FOR_YOU` default, `RECENTLY_ADDED`), `page`, `page_size`.
**Success — 200:** paginated `SearchResultItem` list, same shape as search.
**Frontend notes:** a brand-new user with no profile yet gets a perfectly reasonable, non-personalized feed here (same content as `RECENTLY_ADDED`) — no special "empty state" handling needed for that case specifically, it looks like a normal feed. `relevance_score` is present but not something to display raw to a student — it's ordering information, not a number that means anything to them on its own.

---

## MANUAL TESTING GUIDE [FOR NSISONG]

**Preconditions:** `scripts/db_start.sh` running; the app running; at minimum one seeded university/campus (Module 4), one Scout with two published listings at different prices/distances from that campus (Module 5), one Student account with a profile and at least one preference set (Module 2).

1. **Plain search:** `GET /search?campus_id={id}` — confirm both listings appear, closer one ranked first (all else equal).
2. **Price filter without a period:** `GET /search?max_price_kobo=600000` (no `billing_period`) — expect `422`.
3. **Price filter with a mismatched period:** `GET /search?max_price_kobo=600000&billing_period=MONTH` where your seeded listings are priced yearly — expect the listings to be excluded, not converted.
4. **Amenity filter:** request two amenities only one listing actually has — confirm only that one appears.
5. **Sold-out exclusion:** reserve every slot on one listing (directly via Housing's `AvailabilityPort`, same simulate-Booking approach as Module 5's guide) — confirm it disappears from search results, same "derived, not stored" behavior Housing itself demonstrated.
6. **Discovery, personalized:** `GET /discovery` as the Student with preferences set — confirm the ordering reflects them (a matching listing ranks above a non-matching one, all else equal).
7. **Discovery, no profile:** register a brand-new account, log in, call `GET /discovery` before creating any profile — expect a normal, non-error response, equivalent to `GET /discovery?strategy=RECENTLY_ADDED`.
8. **Unauthenticated:** call either endpoint with no token — expect `401`.

**Failure interpretation:** if step 3's listings show up anyway, the price/period rule isn't actually enforced and Search is silently comparing incompatible units — treat this as a correctness bug serious enough to block sign-off, not a cosmetic issue. If step 7 errors instead of degrading gracefully, the fallback (ADR-067) isn't wired correctly.

---

## AUTOMATED TESTING GUIDE [FOR NSISONG]

- Just Search: `poetry run pytest tests/unit/search tests/integration/search tests/api/search`
- Domain only (fast, no database, no other module involved): `poetry run pytest tests/unit/search -v`
- The ranking determinism test specifically: `poetry run pytest tests/api/search/test_ranking_determinism.py -v`
- Full verification: `poetry run pytest && poetry run ruff check . && poetry run mypy src && poetry run lint-imports`
- After this module specifically, re-run Housing's suite in isolation (`poetry run pytest tests/unit/housing tests/integration/housing tests/api/housing`) and confirm it's unchanged apart from the one new test — this module touched Housing's files, and that's the check that proves nothing else there broke.


---

## MODULE DOCUMENTATION REQUIREMENTS [FOR YOU — GEMINI CLI, part of Chunk 12]

Write `docs/modules/search.md`. Cover: purpose/ownership/non-ownership (this document's Architectural Interpretation, condensed); the filtering rules from Chunk 3, verbatim enough to be a real reference; the ranking formula and weight table from Chunk 4, in full, plus the Discovery table from Chunk 5 — this is the part most likely to be revisited when tuning search quality later, so it needs to actually be usable, not just present; the Haversine formula; the two discovery strategies and the no-profile fallback; the "Cross-Module Dependencies" section from Chunk 10; the one change made to Housing and why (point back to Finding 2 rather than re-explaining); known limitations — explicitly, in a clearly labeled list: no campus-proximity discovery (Finding 1, with the exact unblock condition — Profile's migration), verification is stubbed pending Module 7, no search history/saved searches, `sort_by` options other than `RELEVANCE` bypass ranking entirely (state this so nobody's surprised `PRICE_ASC` isn't "relevance, but price-weighted").

## AI STATE REQUIREMENTS [FOR YOU — GEMINI CLI, part of Chunk 12]

Update `CURRENT_STATE.md`, `PROGRESS.md`, `COMPLETED_WORK.md`, `ARCHITECTURE_STATE.md` (note this is the first module with zero tables of its own, and the first to touch Housing's files after Housing shipped), `DATABASE_STATE.md` (no change — say so explicitly rather than leaving the entry stale), `API_STATE.md`, `TEST_STATE.md`, `DECISIONS.md` (append ADR-061–068), `SESSION_HANDOFF.md`. Housing's own `ARCHITECTURE_STATE.md`/`API_STATE.md` should note the new in-process-only port. Use the standard `CURRENT_TASK.md` status-block format from the last session's documentation fix — don't regress to prose.

---

## COMPLETION CHECKLIST [FOR NSISONG]

- [ ] Search correctly filters on every documented criterion, with AND semantics across filters.
- [ ] A price filter without a matching `billing_period` is rejected (422), and a mismatched-period listing is excluded, never silently compared.
- [ ] Sold-out/unpublished listings never appear in either endpoint, verified by the same derived-availability test pattern Housing itself used.
- [ ] Ranking is deterministic and explainable — verified by the specific known-order test, not just "results came back in some order."
- [ ] Weight renormalization actually happens when an input is missing — verified, not assumed.
- [ ] Discovery personalizes when a profile exists and gracefully degrades to `RECENTLY_ADDED` when it doesn't — both paths tested via real HTTP.
- [ ] Distance calculation matches a known reference value within a small tolerance.
- [ ] `campus_id` coordinates are fetched once per search request, not once per candidate — verified by the specific call-count assertion in Chunk 6.
- [ ] Housing's new port is additive only — Housing's pre-existing suite passes unchanged apart from the one new test.
- [ ] No Search-owned database tables exist.
- [ ] No cross-module database access in any direction; every adapter imports only its target's `application.ports`.
- [ ] Unit, integration, API, and architecture tests all pass — every module together.
- [ ] `docs/modules/search.md` exists and covers everything above, especially the ranking tables in a genuinely reusable form.
- [ ] All `AI_state/` files updated, including Housing's, using the standard status-block format.
- [ ] Known limitations (no campus-proximity discovery, stubbed verification, no search history) documented plainly, with Finding 1's exact unblock condition stated, not just "future work."

