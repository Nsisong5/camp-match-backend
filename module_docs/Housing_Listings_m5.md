# CAMP MATCH — MODULE 05: HOUSING & LISTINGS
**Specification prepared by: Claude (Technical Specification Engineer)**
**For: Gemini CLI (Implementation Agent) and Nsisong**
**Source directive: Chief Engineer → Claude, Housing & Listings Module handoff**

---

## HOW TO READ THIS DOCUMENT

Same conventions as the previous four module specs. This handoff asked for exactly thirteen numbered chunks — followed exactly below — with my usual surrounding sections kept for consistency. This is the largest module yet: real domain modeling decisions, real money handling, real concurrency. Code stays minimal everywhere except the one place precision matters more than brevity — the atomic reservation technique in Chunk 7, which gets an exact, unambiguous description since getting it subtly wrong is the one mistake in this whole module that's genuinely hard to notice until it's too late.

---

## ARCHITECTURAL INTERPRETATION [FOR NSISONG]

This is the first module that models a real physical/marketplace hierarchy rather than a single flat concept, and the first with a genuine concurrency problem to solve (two students can't both successfully claim the last available room). It's also the first real, non-synthetic test of Security's ownership-based authorization — Module 3 built that mechanism and could only prove it against a made-up example permission, because nothing existed yet that had "resources someone specifically owns." Housing is that thing.

**The core modeling decision, explained plainly:** a `Property` is the physical building. A `Unit` is a *category* of rentable space within it — not necessarily one physical room. A 20-room lodge where every room is identical and interchangeable is **one** `Unit` with a capacity of 20, not twenty separate rows — the same mechanism that represents "20 identical private rooms" also represents "a shared room with 4 bed spaces," just with a smaller number. Only genuinely different room types (different price, different size) become separate `Unit`s. A `Listing` is the marketplace-facing offer for exactly one `Unit` — title, description, price, and whether it's currently discoverable. This is the smallest model that satisfies every scenario in the handoff's own example without needing a special case for any of them.

No contradictions were found with the existing foundation. A genuine number of modeling and boundary decisions were mine to make — see below.

### DECISIONS (ADR-052 … ADR-060) [FOR NSISONG]

Continuing the log from Phase 1–3 (001–013), Identity (014–023), Profile (024–034), Security (035–043), University & Location (044–051).

| ADR | Decision | Why |
|---|---|---|
| 052 | Three-tier model — `Property` → `Unit` (capacity-based, not one-row-per-room) → `Listing` (1:1 with `Unit`, enforced by a unique constraint) | Explained above. One mechanism (`total_capacity`/`occupied_count`) covers "many identical rooms" and "shared bed spaces" without needing two different modeling approaches for what's structurally the same fact: how many interchangeable slots exist and how many are taken. |
| 053 | Amenities split **property-wide** (water, electricity, security, parking, generator, CCTV, Wi-Fi) vs **unit-specific** (furnished, private bathroom, kitchen) | A lodge's generator doesn't change room to room; editing it once beats duplicating the same fact across twenty `Unit` rows and risking them drifting out of sync. |
| 054 | "Is this listing currently bookable" is **computed** (`status == PUBLISHED AND unit.available_count > 0`), never a stored, cascading write | The exact same "derive, don't cascade" pattern University & Location used for inactive-university-hides-its-campuses (ADR-046). Inventory changing shouldn't require a listener that goes and flips a status field somewhere else — the fact is already fully knowable at query time. |
| 055 | Housing defines its **own** `Coordinates` value object and its own `ProfileProvider` outbound port, structurally identical to University & Location's and Security's respective versions, rather than importing them | The rule has held since Module 3: a module's domain types are private. Every cross-module integration duplicates the *pattern*, never the *code* — this is the fourth time that exact discipline has come up, which is a good sign it's a real project convention, not an accident. |
| 056 | `reserve_slot`/`release_slot` are single atomic `UPDATE ... WHERE ...` statements, success determined by **affected-row-count**, never a `SELECT` followed by a conditional `UPDATE`. They commit independently — a future Booking module compensates with `release_slot` if its own next step fails after a successful reservation | This is the actual fix for the double-booking scenario the handoff describes, explained precisely in Chunk 7. The compensating-action note is important, honest information for whoever specs Booking next — Housing can't hold a transaction open across a call from another module, so Booking has to handle its own half of the failure case. |
| 057 | **Creating** a property or listing needs no Security permission check — only Housing's own "is this identity currently a Scout" check via its `ProfileProvider`. `HOUSING_MANAGE` (ownership-scoped, granted to `SCOUT` and `ADMIN`) governs every mutation on an *existing* resource | You can't violate anyone's ownership by creating something new — whatever you create, you own by definition. Security's ownership check only makes sense once a resource with a real owner already exists to compare against. |
| 058 | `HOUSING_MANAGE` is the **first real exercise of Security's ownership-scoped path** — Module 3 could only prove that mechanism against a synthetic example (its own ADR-042, flagged honestly at the time) | Worth knowing this module is what actually retires that flagged gap, not just another consumer of Security. |
| 059 | `GET /listings` is a **deliberately basic browse endpoint** — plain filters, no ranking, no personalization | It exists only because Search & Discovery doesn't exist yet. Expect it to be wrapped or superseded once that module ships — it's a placeholder with real value today, not a feature Housing is meant to keep growing indefinitely. |
| 060 | `DuplicateProperty` and `UnauthorizedListingOperation`, both named in the handoff's own error list, are **not independently implemented** | `Property` has no real uniqueness rule in this design (two properties can coincidentally share a name), so nothing would ever raise the former. Housing reuses Security's existing `Forbidden` directly for the latter rather than wrapping it in a second, redundant class — the entire point of centralizing authorization was exactly this kind of reuse. |

**One item worth your attention specifically:** ADR-056's compensating-action note. It's not a gap in this module — it's a real constraint on how Booking will eventually have to be built, and worth remembering when that spec comes around so it isn't rediscovered the hard way.


---

## CHUNK 1 — CONTEXT, ARCHITECTURE, AND MODULE BOUNDARIES
**[FOR YOU — GEMINI CLI]**

**Implementation instructions:**
1. Read `AI_instructions/` in full and `AI_state/CURRENT_STATE.md`, `ARCHITECTURE_STATE.md`, `DATABASE_STATE.md`, `API_STATE.md`.
2. Read `docs/modules/identity.md`, `profile.md`, `security.md`, `university_location.md`.
3. Inspect Security's `domain/value_objects.py`/`policy.py` (Chunk 9 adds `HOUSING_MANAGE`), Profile's `GetCurrentUserProfile` (Chunk 5's `ProfileProvider` adapter calls it), and University & Location's `UniversityLocationQueryPort` (Chunk 10 uses it to validate `campus_id`).
4. Create the module's empty structure:
```
src/camp_match/modules/housing/__init__.py
src/camp_match/modules/housing/domain/__init__.py
src/camp_match/modules/housing/domain/value_objects.py
src/camp_match/modules/housing/domain/entities.py
src/camp_match/modules/housing/application/__init__.py
src/camp_match/modules/housing/application/errors.py
src/camp_match/modules/housing/application/ports/__init__.py
src/camp_match/modules/housing/application/ports/inbound.py
src/camp_match/modules/housing/application/ports/outbound.py
src/camp_match/modules/housing/application/use_cases/__init__.py
src/camp_match/modules/housing/adapters/__init__.py
src/camp_match/modules/housing/adapters/persistence/__init__.py
src/camp_match/modules/housing/adapters/profile/__init__.py
src/camp_match/modules/housing/adapters/university_location/__init__.py
src/camp_match/modules/housing/adapters/api/__init__.py
tests/unit/housing/__init__.py
tests/unit/housing/domain/__init__.py
tests/unit/housing/application/__init__.py
tests/integration/housing/__init__.py
tests/api/housing/__init__.py
```

**Acceptance criteria:** written confirmation of steps 1–3; all files from step 4 importable.

---

## CHUNK 2 — DOMAIN MODEL
**[FOR YOU — GEMINI CLI]**

**Files to modify:** `domain/value_objects.py`, `domain/entities.py`.

**`value_objects.py`:**
- **`Coordinates`** — same shape and validation as University & Location's (own copy, per ADR-055): latitude −90..90, longitude −180..180.
- **`PropertyType`** (enum) — `SELF_CONTAINED_HOUSE`, `LODGE`, `APARTMENT_BUILDING`, `HOSTEL`, `OTHER`. A distinct enum from Profile's `AccommodationTypePreference` — one describes what a Student wants, this describes what a property physically is; don't merge them.
- **`PropertyStatus`** (enum) — `ACTIVE`, `ARCHIVED`.
- **`ListingStatus`** (enum) — `DRAFT`, `PUBLISHED`, `UNAVAILABLE`, `ARCHIVED`.
- **`Currency`** (enum) — `NGN` only, for now.
- **`BillingPeriod`** (enum) — `YEAR`, `SEMESTER`, `MONTH`. (No `WEEK`/`ONE_TIME` — not a real MVP need for student housing; add later without restructuring if that changes.)
- **`Price`** — `amount_kobo` (non-negative integer — **kobo, not naira**, name it exactly that so nobody divides or multiplies by the wrong factor later), `currency` (`Currency`), `period` (`BillingPeriod`). Raise `ValueError` on a negative amount.

**`entities.py`:**
- **`Property`** — `id`, `provider_id` (`EntityId`, permanent), `property_type`, `name`, `description`, `address` (free text), `coordinates` (`Coordinates`), `campus_id` (`EntityId | None` — validated against University & Location in the application layer, not here), `has_water`/`has_electricity`/`has_security`/`has_parking`/`has_generator`/`has_cctv`/`has_wifi` (booleans), `status` (`PropertyStatus`), `created_at`/`updated_at`.
- **`Unit`** — `id`, `property_id` (`EntityId`, permanent), `label` (e.g. "Self-contained room", required), `total_capacity` (positive integer), `occupied_count` (non-negative integer, never exceeds `total_capacity` — enforce as a constructor/update invariant, not just a database constraint, so a bug surfaces immediately in a unit test rather than only at the database layer), `is_furnished`/`has_private_bathroom`/`has_kitchen` (booleans), `created_at`/`updated_at`. Expose a read-only `available_count` property (`total_capacity - occupied_count`) — never stored, always derived.
- **`Listing`** — `id`, `property_id`, `unit_id` (both `EntityId`, permanent), `title`, `description`, `price` (`Price`), `status` (`ListingStatus`), `created_at`/`updated_at`. Expose a read-only `is_bookable` property that a *caller* evaluates by combining `status` with the referenced `Unit.available_count` (ADR-054) — the `Listing` entity itself doesn't hold a `Unit` reference in memory, so this composition happens in the application layer (Chunk 4), not inside the entity. Document that clearly rather than trying to make the entity self-sufficient for something it structurally can't know alone.

**Listing state machine, exactly:**
```
DRAFT        → PUBLISHED, ARCHIVED
PUBLISHED    → UNAVAILABLE, ARCHIVED
UNAVAILABLE  → PUBLISHED, ARCHIVED
ARCHIVED     → (terminal — no transitions out)
```
Implement this as an explicit table/method on `Listing`, not scattered `if` statements — any transition not in the table above raises `ValueError` at the domain level (translated to `InvalidListingStateTransition` in the application layer).

**Tests you must write:** `tests/unit/housing/domain/test_price.py` (negative amount rejected), `tests/unit/housing/domain/test_unit.py` (`occupied_count` can never exceed `total_capacity`, `available_count` derives correctly), `tests/unit/housing/domain/test_listing_transitions.py` (every valid transition from the table succeeds, every invalid one — including anything out of `ARCHIVED` — raises).

**Acceptance criteria:** new tests pass; no import beyond stdlib + shared-kernel `EntityId`.

---

## CHUNK 3 — DOMAIN INVARIANTS AND LIFECYCLE STATE MACHINES
**[FOR YOU — GEMINI CLI]**

**Objective:** this chunk is verification, not new code — Chunk 2 already implemented the state machine and capacity invariant as part of building the entities (small, cohesive modules don't benefit from artificially separating "the model" from "its rules" into two chunks that touch the same files). Confirm both are actually enforced, not just described.

**Implementation instructions:** write two additional tests that don't fit neatly in Chunk 2's files because they're about *combinations* of rules: `tests/unit/housing/domain/test_invariants.py` — attempting to construct a `Unit` with `occupied_count > total_capacity` directly (not through the normal increment path) raises at construction, not just when incremented; attempting every one of the six invalid `Listing` transitions individually (not just "some invalid transition") each raises with a message identifying which transition was attempted, useful for debugging later.

**Acceptance criteria:** new tests pass, and running them alone (`poetry run pytest tests/unit/housing/domain/test_invariants.py -v`) shows every case listed above as an individually named, passing test — not one combined test hiding six assertions.


---

## CHUNK 4 — APPLICATION USE CASES
**[FOR YOU — GEMINI CLI]**

**Files to create:** one file per use case under `application/use_cases/`.

**Governing rule, same as every previous module:** Pydantic (Chunk 8) handles transport validation. This layer handles cross-record rules Pydantic can't: ownership, state transitions, capacity math, and the two real cross-module checks (is this identity a Scout; does this `campus_id` actually exist).

**`CreateProperty` — steps:** confirm the caller is currently a Scout via `ProfileProvider.get_profile_type` (raise `Forbidden` — Security's class, reused directly, ADR-060 — if not); if `campus_id` was supplied, confirm it resolves via the University & Location adapter (Chunk 10) or raise `InvalidLocation`; construct and persist the `Property` (`provider_id` = the caller); log INFO (`"property_created"`, id, provider id); return the response.

**`UpdateProperty` — steps:** look up by id (`PropertyNotFound` if absent); call `AuthorizationService.authorize(identity_id, Permission.HOUSING_MANAGE, resource_owner_id=property.provider_id)` — anything but `ALLOWED` raises the matching Security exception; apply only supplied fields; persist; log INFO with changed field names.

**`ArchiveProperty` — steps:** same lookup-and-authorize pattern as above; sets `status = ARCHIVED` (idempotent — archiving an already-archived property is a harmless no-op, same discipline as every previous module's idempotent operations); log INFO.

**`ListPropertiesForProvider` — steps:** paginated, scoped to the *caller's own* `provider_id` only (no target parameter — same structural self-scoping Profile used for `/me`, ADR-030's precedent) — this is the Scout's own dashboard view, not a public "browse this provider's properties" endpoint.

**`CreateUnit` — steps:** look up the parent property (`PropertyNotFound`); authorize via `HOUSING_MANAGE` against the property's `provider_id`; construct and persist; log INFO.

**`UpdateUnit` — steps:** look up (`UnitNotFound`); authorize via the *parent property's* `provider_id` (a `Unit` doesn't carry its own owner — resolve it by loading the property); apply supplied fields, re-checking the capacity invariant if `total_capacity` changes downward below the current `occupied_count` (reject with `InvalidPrice`... no — define this as a new, honestly-named check: raising `InvalidListingStateTransition` doesn't fit either; use `InventoryUnavailable` for this case too, since it's the same underlying fact — capacity can't shrink below what's currently occupied); persist; log INFO.

**`CreateListing` — steps:** look up the referenced property and unit, confirming the unit actually belongs to that property (`UnitNotFound` otherwise); authorize via `HOUSING_MANAGE`; confirm the unit isn't already attached to a non-archived listing (the 1:1 relationship, ADR-052 — raise a clear error if it is, reusing `InventoryUnavailable` as the closest fit rather than inventing a new class for one edge case); construct in `DRAFT`; persist; log INFO.

**`UpdateListing` — steps:** look up (`ListingNotFound`), authorize, reject if `status == ARCHIVED` (nothing about an archived listing should be editable — raise `InvalidListingStateTransition`), apply supplied fields (title/description/price), persist, log INFO.

**`PublishListing` — steps:** look up, authorize; call the entity's transition method (`ARCHIVED`/invalid-source raises `InvalidListingStateTransition`); additionally validate *readiness to publish*, beyond just the state machine being legal: `price.amount_kobo > 0` and the referenced unit's `available_count > 0` — both raise `InvalidListingStateTransition` too, with a message distinguishing "wrong state" from "not ready to publish" for anyone debugging later; persist; log INFO.

**`UnpublishListing`/`ArchiveListing` — steps:** look up, authorize, transition, persist, log INFO — same pattern, no additional readiness checks needed for these directions.

**`GetProperty`/`GetUnit`/`GetListing` — steps:** direct id lookup, no authorization required (reading isn't privileged) — not found raises the matching `*NotFound`.

**`ListActiveListings`** (ADR-059) **— steps:** paginated, filterable by `campus_id` and `property_type`; returns only listings where `status == PUBLISHED` **and** the referenced unit's `available_count > 0` — computed at query time (Chunk 6's repository does the join), never a stored flag.

**`CheckAvailability`/`ReserveSlot`/`ReleaseSlot`** — covered in full in Chunk 7, since their correctness is really about the persistence-layer technique, not the use-case shell around it.

**Tests you must write:** shared fakes under `tests/support/housing_fakes.py` (fake repositories, fake `ProfileProvider`, fake `AuthorizationService`, fake University & Location adapter). Cover every use case above: success paths, not-found paths, unauthorized paths (both "not a Scout" for creation and "not the owner" for mutation), the publish-readiness checks (zero price, zero availability), and the state-machine rejection path for update/publish/unpublish/archive attempted from `ARCHIVED`.

**Acceptance criteria:** new tests pass, all against fakes — no real database, no real Profile/Security/University & Location code executed.


---

## CHUNK 5 — PORTS AND CROSS-MODULE CONTRACTS
**[FOR YOU — GEMINI CLI]**

**Files to modify:** `application/ports/inbound.py`, `application/ports/outbound.py`.

**Inbound:**
- The administrative surface — one `Protocol`/dataclass-pair per Chunk 4 use case, same convention as every previous module.
- **`AvailabilityPort`** (ADR-056, detailed fully in Chunk 7) — `check_availability(unit_id) -> int`, `reserve_slot(unit_id) -> bool`, `release_slot(unit_id) -> None`. This is the module's real deliverable — the one a future Booking module actually depends on.

**Outbound:**
- **`PropertyRepository`**, **`UnitRepository`**, **`ListingRepository`** — methods mirroring Chunk 4's needs (`add`, `get_by_id`, `update`, `list` with the relevant filters/pagination). `ListingRepository.list_active` implements the `PUBLISHED`-and-available join.
- **`ProfileProvider`** (own copy, ADR-055) — `get_profile_type(identity_id) -> Role | None`, same shape as Security's own version, implemented independently in Chunk 9.
- **`UniversityLocationProvider`** — one method, `campus_exists(campus_id) -> bool`, implemented in Chunk 10.
- Reused directly: shared-kernel `Clock`, `EntityId`, `Page`/`PageRequest`, `UnitOfWork`.

**Acceptance criteria:** `poetry run mypy` clean; every method above exists with a matching signature.

---

## CHUNK 6 — DATABASE MODELS, MIGRATIONS, CONSTRAINTS, INDEXES, REPOSITORIES
**[FOR YOU — GEMINI CLI]**

**Files to create:** `adapters/persistence/models.py`, `adapters/persistence/repository.py`.

**`properties`**

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | primary key |
| `provider_id` | UUID | not null, **no foreign key** (cross-module, same reasoning as every prior module's identity references) — indexed |
| `property_type` | text | not null, `CHECK` restricted |
| `name` | text | not null |
| `description` | text | nullable |
| `address` | text | not null |
| `latitude`, `longitude` | `NUMERIC(9,6)` | not null |
| `campus_id` | UUID | nullable, **no foreign key** — indexed |
| `has_water`…`has_wifi` | boolean | not null, default `false`, one column each (seven total) |
| `status` | text | not null, `CHECK` restricted, default `ACTIVE` |
| `created_at`/`updated_at` | timestamptz | server defaults |

**`units`**

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | primary key |
| `property_id` | UUID | not null, **foreign key → `properties.id`** (same module — a real FK is correct here) — indexed |
| `label` | text | not null |
| `total_capacity` | integer | not null, `CHECK (total_capacity > 0)` |
| `occupied_count` | integer | not null, default 0, `CHECK (occupied_count >= 0 AND occupied_count <= total_capacity)` — the invariant enforced at the database level too, not just in the domain layer |
| `is_furnished`, `has_private_bathroom`, `has_kitchen` | boolean | not null, default `false` |
| `created_at`/`updated_at` | timestamptz | server defaults |

**`listings`**

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | primary key |
| `property_id` | UUID | not null, foreign key → `properties.id` — indexed |
| `unit_id` | UUID | not null, foreign key → `units.id`, **unique** (the 1:1 relationship, ADR-052) |
| `title` | text | not null |
| `description` | text | nullable |
| `price_amount_kobo` | bigint | not null, `CHECK (price_amount_kobo >= 0)` |
| `price_currency` | text | not null, `CHECK` restricted to `NGN` |
| `price_period` | text | not null, `CHECK` restricted |
| `status` | text | not null, `CHECK` restricted, default `DRAFT` — **indexed** (this is the module's hottest filter, per the handoff's own performance note) |
| `created_at`/`updated_at` | timestamptz | server defaults |

**`listing_media`**

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | primary key |
| `listing_id` | UUID | not null, foreign key → `listings.id` — indexed |
| `media_url` | text | not null |
| `display_order` | integer | not null, default 0 |
| `created_at` | timestamptz | server default |

**Repositories:** translate unique-constraint violations (the `units.id`-unique-per-listing case) into the matching application error, same pattern as every prior module. `ListingRepository.list_active` joins `listings` to `units` and filters `status = 'PUBLISHED' AND units.occupied_count < units.total_capacity` in one query — do not fetch listings and units separately and filter in Python; that defeats the index on `listings.status` and doesn't scale.

**Migration:** `poetry run alembic revision --autogenerate -m "add housing tables"`, read before applying — this one is worth reading closely, given four tables and several `CHECK` constraints in one migration.

**Tests you must write:** `tests/integration/housing/test_repositories.py` (marked `integration`) — CRUD for all three entities; the `occupied_count <= total_capacity` constraint rejects a direct attempt to violate it at the database level (bypass the application layer deliberately to prove this, same verification discipline as University & Location's partial-unique-index test); the one-listing-per-unit uniqueness; `list_active` correctly excludes a `PUBLISHED` listing whose unit has zero `available_count`.

**Acceptance criteria:** new tests pass against local Termux Postgres; migration applies cleanly.


---

## CHUNK 7 — AVAILABILITY AND CONCURRENCY IMPLEMENTATION
**[FOR YOU — GEMINI CLI]**

**Objective:** the one chunk in this module where precision matters more than anything else — this is what stops two students from both successfully claiming the same room.

**Files to create:** `application/use_cases/check_availability.py`, `application/use_cases/reserve_slot.py`, `application/use_cases/release_slot.py`.
**Files to modify:** `adapters/persistence/repository.py` — add the two atomic methods below to `UnitRepository`.

**The problem, stated exactly:** two requests arrive at nearly the same instant, both wanting the last available slot in a unit with `total_capacity = 5`, `occupied_count = 4`. A naive implementation reads `occupied_count` (sees 4, thinks "room for one more"), then writes `occupied_count = 5` — and if both requests do their *read* before either does its *write*, both conclude there's room, and both write `5`, silently double-booking the last slot. Wrapping this in a transaction does **not** fix it by itself — the transaction doesn't stop two separate read-then-write sequences from interleaving unless something also locks the row between the read and the write.

**The fix — a single atomic statement, not a read followed by a write:**

`UnitRepository.try_reserve(unit_id) -> bool`: issue exactly one `UPDATE` statement —
```sql
UPDATE units
SET occupied_count = occupied_count + 1
WHERE id = :unit_id AND occupied_count < total_capacity
```
— and check how many rows it affected. **One row affected means the reservation succeeded** (and the database guaranteed nobody else could have squeezed in between the check and the write, because the check and the write are the *same* statement, evaluated atomically by Postgres). **Zero rows affected means either the unit doesn't exist or there was genuinely no room left** — the repository method returns `False` either way; the use case (below) is responsible for telling those two cases apart if it needs to (a separate existence check only when the result is `False`, never as part of deciding whether to reserve).

`UnitRepository.try_release(unit_id) -> bool` is the mirror image:
```sql
UPDATE units
SET occupied_count = occupied_count - 1
WHERE id = :unit_id AND occupied_count > 0
```

**`ReserveSlot` (the use case wrapping `try_reserve`) — steps:** call `try_reserve`; if it returns `False`, look the unit up separately to decide whether to raise `UnitNotFound` or `InventoryUnavailable` (this order — try first, explain the failure after — is deliberate: it means the common, fast path never pays for an extra lookup); if `True`, log INFO (`"slot_reserved"`, unit id, new `occupied_count`) and return success.

**`ReleaseSlot` — steps:** call `try_release`; log INFO either way (a `False` here — releasing a slot that's already at zero — is worth a WARNING instead, since it suggests a caller released something it shouldn't have, e.g. calling release twice for one booking).

**`CheckAvailability` — steps:** a plain read (`available_count` from the current row) — explicitly **not** safe to use as the basis for a reservation decision; its only legitimate purpose is display ("3 spaces left"). State this directly in the docstring, since it's exactly the kind of thing that's tempting to misuse later ("just check first, then reserve") in a way that quietly reintroduces the race condition this chunk exists to prevent.

**What this chunk does *not* do:** wrap `try_reserve` in the caller's transaction. It commits on its own, immediately (ADR-056). A future Booking module calling `reserve_slot` and then failing a later step of its own must call `release_slot` itself to undo it — Housing has no way to know Booking's later steps failed, and shouldn't be designed as if it could.

**Tests you must write:** `tests/integration/housing/test_concurrency.py` (marked `integration`) — the actual proof. Create a unit with `total_capacity = 1`. Launch two concurrent `reserve_slot` calls against it (using `asyncio.gather` or equivalent real concurrency, not two sequential calls that only *look* like a concurrency test) — assert exactly one succeeds and the other returns `False`/raises `InventoryUnavailable`, and that `occupied_count` ends at exactly `1`, never `2`. Repeat with `total_capacity = 5` and ten concurrent reservation attempts — assert exactly 5 succeed. Also test `release_slot` bringing `occupied_count` back down and a subsequent `reserve_slot` succeeding again.

**Acceptance criteria:** the concurrency test genuinely exercises simultaneous requests (not sequential ones dressed up as concurrent) and passes reliably, not just once by luck — run it several times in a row if there's any doubt.


---

## CHUNK 8 — FASTAPI ADAPTERS, DTOS, ENDPOINTS, VALIDATION
**[FOR YOU — GEMINI CLI]**

**Files to create:** `adapters/api/schemas.py`, `adapters/api/router.py`, `adapters/api/dependencies.py`.
**Files to modify:** `app.py`.

**Endpoints, all under `/api/v1`:**

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/properties` | Scout only (no permission, ADR-057) | create |
| GET | `/properties/{id}` | authenticated | direct lookup |
| PATCH | `/properties/{id}` | `HOUSING_MANAGE` | partial update |
| POST | `/properties/{id}/archive` | `HOUSING_MANAGE` | idempotent |
| GET | `/properties/mine` | authenticated | caller's own, paginated |
| POST | `/properties/{property_id}/units` | `HOUSING_MANAGE` | create |
| GET | `/properties/{property_id}/units` | authenticated | list |
| PATCH | `/units/{unit_id}` | `HOUSING_MANAGE` | partial update |
| POST | `/listings` | `HOUSING_MANAGE` | create (references property + unit) |
| GET | `/listings/{id}` | authenticated | direct lookup |
| PATCH | `/listings/{id}` | `HOUSING_MANAGE` | partial update |
| POST | `/listings/{id}/publish` | `HOUSING_MANAGE` | |
| POST | `/listings/{id}/unpublish` | `HOUSING_MANAGE` | |
| POST | `/listings/{id}/archive` | `HOUSING_MANAGE` | |
| GET | `/listings` | authenticated | public browse, `PUBLISHED`-and-available only, filterable by `campus_id`/`property_type` |
| GET | `/listings/{id}/availability` | authenticated | `CheckAvailability` — display use only |
| GET | `/providers/me/listings` | authenticated | Scout's own, every status |

No `DELETE` anywhere — archiving only, consistent with every previous module's "no hard delete" discipline.

**Validation:** Pydantic enforces primitive shape and range (e.g. `total_capacity >= 1`, `price_amount_kobo >= 0`) at the boundary; everything ownership/state/capacity-related is Chunk 4/7's job, not this chunk's.

**Prohibition, same as every module before this one:** no business logic in `router.py` — every route is parse → call use case → serialize.

**Tests you must write:** placeholder only — the real API tests come together in Chunk 11.

**Acceptance criteria:** the app starts; each endpoint behaves as described when exercised manually.

---

## CHUNK 9 — SECURITY & AUTHORIZATION INTEGRATION
**[FOR YOU — GEMINI CLI]**

**Objective:** add `HOUSING_MANAGE`, using Security's own documented extension recipe (Module 3, Section 5) — the same two-line touch University & Location made for `UNIVERSITY_MANAGE`.

**Files to modify:** `modules/security/domain/value_objects.py` (add `HOUSING_MANAGE` to `Permission`, mapped to `"housing.manage"`, declared **ownership-scoped** — the first ownership-scoped permission with a real consumer, per ADR-058), `modules/security/domain/policy.py` (grant it to both `SCOUT` and `ADMIN`).

**Prohibition:** exactly those two files, exactly the permission-registration lines — nothing else in Security changes.

**Files to create:** `adapters/profile/profile_provider.py` — Housing's own `InProcessProfileProvider`, same pattern as Security's Module 3 version and Profile's Module 2 `IdentityProvider`: constructed with a reference to Profile's `GetCurrentUserProfile` use case, maps its response to Housing's own `Role`-shaped result (or reuse Security's already-defined `Role` type via its `application.ports` surface if that's cleaner — your call, document which in the Completion Report), never importing Profile's `adapters`/`domain`.

**Tests you must write:** `tests/unit/housing/adapters/test_profile_provider.py` (mirrors Module 3's equivalent test exactly); extend `tests/unit/security/domain/test_policy.py` with two lines confirming `HOUSING_MANAGE` is granted to both `SCOUT` and `ADMIN`; `tests/api/housing/test_authorization.py` — a Scout can manage their own property/listing; a different Scout gets 403 attempting to; an Admin can manage anyone's; an unauthenticated request gets 401 before any of this module's logic runs.

**Acceptance criteria:** new tests pass; Security's, Identity's, Profile's, and University & Location's full suites are unaffected apart from the two-line policy addition.

---

## CHUNK 10 — INTEGRATION WITH UNIVERSITY & LOCATION, VERIFICATION, SEARCH, AND BOOKING
**[FOR YOU — GEMINI CLI]**

**University & Location — the one real integration in this chunk.** **Files to create:** `adapters/university_location/university_location_provider.py` — `InProcessUniversityLocationProvider` implementing `UniversityLocationProvider`, constructed with a reference to University & Location's `GetCampus` (or the `UniversityLocationQueryPort`) use case, mapping "found" to `True` and "not found" to `False` for `campus_exists`. Same import discipline as every prior adapter: `application.ports` only, never `adapters`/`domain`.

**Verification, Search, Booking — none of these modules exist yet, so there is nothing to wire up.** Confirm the following are true and will remain true without further work once those modules do exist, and say so explicitly in `docs/modules/housing.md` (Chunk 12) rather than leaving it implicit:
- **Verification** will consume Housing through direct id lookups (`GetProperty`/`GetListing`/`GetUnit`) — nothing new needed here; those use cases already exist and already don't require the caller to be the resource's owner (reading isn't privileged).
- **Search** will consume `ListActiveListings`'s underlying data, most likely wrapping or replacing `GET /listings` (ADR-059) rather than adding a new port to this module.
- **Booking** will consume `AvailabilityPort` (Chunk 7) exactly as built — this is the one contract genuinely designed with Booking specifically in mind, and it needs no changes once Booking exists to call it.

**Acceptance criteria:** the University & Location adapter test passes (see Chunk 4's test list); `docs/modules/housing.md`'s eventual "cross-module dependencies" section (Chunk 12) states the three points above plainly.

---

## CHUNK 11 — TESTING
**[FOR YOU — GEMINI CLI]**

**Objective:** consolidate and complete — most tests already exist from Chunks 2–10; this chunk fills the remaining gaps and runs everything together.

**Files to create:** `tests/api/housing/test_property_flow.py`, `tests/api/housing/test_listing_flow.py`.

**`test_property_flow.py`:** register/login a Scout → create a property → create two units (one capacity 1, one capacity 4) → confirm `GET /properties/mine` shows it → attempt to create a property as a Student account, confirm 403 → attempt to update the Scout's property using a *different* Scout's token, confirm 403.

**`test_listing_flow.py`:** create a listing for one of the units above (still `DRAFT`) → confirm it does **not** appear in `GET /listings` → attempt to publish with `price_amount_kobo = 0`, confirm rejection → set a real price, publish → confirm it **does** now appear in `GET /listings` → reserve every available slot via `AvailabilityPort` directly (simulating Booking, since Booking doesn't exist yet) → confirm the listing **disappears** from `GET /listings` again without its `status` field ever changing (ADR-054 — assert `status` is still `"PUBLISHED"` even though it's no longer bookable) → release one slot → confirm it reappears → archive it → confirm any further update attempt is rejected.

**Extend import-linter:** `camp_match.modules.housing.domain` and `.application` must not import `fastapi` or `sqlalchemy`; nothing outside the module may import its `adapters.persistence`, `.profile`, or `.university_location` directly.

**Run everything:** `poetry run pytest`, `poetry run ruff check .`, `poetry run mypy src`, `poetry run lint-imports` — the whole project, all five modules and the foundation, green.

**Independent testability note (per the handoff's own Part 34-equivalent):** everything in this module is fully testable today except the *real* Booking/Verification/Search integrations, which have no module to integrate with yet — state this plainly in `docs/modules/housing.md` rather than leaving it to be discovered later, same discipline as Security's and Module 4's equivalent notes.

**Acceptance criteria:** every scenario above passes, including the specific assertion that `status` doesn't change when availability hits zero.

---

## CHUNK 12 — DOCUMENTATION AND AI STATE
**[FOR YOU — GEMINI CLI]**

See "Module Documentation Requirements" and "AI State Requirements" below. Set `AI_state/CURRENT_TASK.md` to "Housing & Listings complete. Awaiting Module 6 specification from Claude."

---

## CHUNK 13 — FINAL VERIFICATION AND DEFINITION OF DONE
**[FOR YOU — GEMINI CLI]**

Confirm every item in the Completion Checklist below is genuinely true, run the full project suite one final time from a clean state, and re-run the concurrency test (Chunk 7) at least three times in a row before reporting this module complete — a race condition test that passes once is weaker evidence than one that passes reliably.


---

## FRONTEND DOCUMENTATION [FOR NSISONG — copy into your Front End Doc]

**Money note that applies to every endpoint below:** `price_amount_kobo` is always in kobo (1 Naira = 100 kobo) — divide by 100 to display Naira. This is deliberate (see the module's decision log) — don't "fix" it by sending Naira directly.

### POST /api/v1/properties
**Authorization:** caller must currently be a Scout (Profile-level check, no permission needed).
**Request body:** `property_type`, `name`, `address`, `latitude`, `longitude` (required); `description`, `campus_id` (optional).
**Success — 201.** **Errors:** 403 if not a Scout; 422 for malformed input or an unresolvable `campus_id`.

### GET /api/v1/properties/{id} / PATCH /api/v1/properties/{id} / POST /api/v1/properties/{id}/archive
Standard direct-lookup / owner-only-partial-update / owner-only-idempotent-archive pattern. `PATCH`/`archive` need `housing.manage` **and** ownership — a 403 here means either.

### GET /api/v1/properties/mine
Paginated, every status, Scout's own properties only.

### POST /api/v1/properties/{property_id}/units / GET .../units / PATCH /api/v1/units/{unit_id}
**Request body (create):** `label`, `total_capacity` (required); the three unit-level amenity flags (optional). **Errors on `PATCH`:** 409 `inventory_unavailable` if shrinking `total_capacity` below the currently `occupied_count`.

### POST /api/v1/listings
**Request body:** `property_id`, `unit_id`, `title`, `price_amount_kobo`, `price_currency`, `price_period` (required); `description` (optional). Starts in `DRAFT`. **Errors:** 404 if the unit doesn't belong to the property; 409 if the unit already has a listing.

### GET /api/v1/listings/{id} / PATCH /api/v1/listings/{id}
Standard pattern. `PATCH` rejected with 422 `invalid_listing_state_transition` if the listing is `ARCHIVED`.

### POST /api/v1/listings/{id}/publish
**Errors:** 422 `invalid_listing_state_transition` if the current state doesn't allow it, **or** if price is zero, **or** if the unit has no available capacity — same error code for all three; check the message for which.

### POST /api/v1/listings/{id}/unpublish, POST /api/v1/listings/{id}/archive
Standard transition endpoints.

### GET /api/v1/listings
**Query parameters:** `campus_id`, `property_type` (both optional filters), `page`, `page_size`.
**Success — 200:** paginated, `PUBLISHED`-and-currently-available listings only.
**Frontend notes:** this is a plain browse endpoint, not a search/recommendation feature — no ranking, no personalization. Expect a real search endpoint from a future module to eventually take over primary discovery; this one stays useful as a simple fallback either way.

### GET /api/v1/listings/{id}/availability
**Success — 200:** `{ "available_count": <int> }`.
**Frontend notes:** display only — don't use this to decide whether to let a user attempt a booking; the booking attempt itself (a future module) is what actually enforces availability atomically.

### GET /api/v1/providers/me/listings
Paginated, Scout's own listings, every status — the provider's management dashboard view.

---

## MANUAL TESTING GUIDE [FOR NSISONG]

**Preconditions:** `scripts/db_start.sh` running; the app running; two Scout accounts and one Student account, all registered/logged in, with profiles created (Module 2).

1. **Create a property** as Scout A, with a `campus_id` from Module 4's data if you have any seeded, otherwise omit it.
2. **Add two units:** one `total_capacity: 1`, one `total_capacity: 3`.
3. **Create a listing** for the capacity-1 unit. Confirm `GET /listings` does **not** show it yet (still `DRAFT`).
4. **Try publishing with no price set correctly** (`price_amount_kobo: 0`) — expect `422`.
5. **Update the price**, then publish. Confirm it **now appears** in `GET /listings`.
6. **Ownership check:** try updating this listing using Scout B's token. Expect `403`. Try with the Student's token. Expect `403` too — Students were never granted `housing.manage`.
7. **Simulate a booking** by calling `reserve_slot` directly (no HTTP endpoint exists yet — this proves the mechanism, standing in for the future Booking module): the capacity-1 unit's only slot gets taken. Confirm `GET /listings` no longer shows this listing, **and** confirm via a direct `GET /listings/{id}` that its `status` is still `"PUBLISHED"` — it's the *derived* bookability that changed, not the stored status.
8. **Concurrency, the real test:** with the capacity-3 unit's listing published, fire off several booking attempts against it at once (a short script hitting `reserve_slot` concurrently is the honest way to do this — two browser tabs clicked quickly won't actually prove anything). Confirm exactly 3 succeed, no more, no matter how many were attempted simultaneously.
9. **Archive the listing.** Confirm any further update attempt returns `422`.

**Failure interpretation:** step 8 is the one that matters most in this whole module. If more than 3 succeed even once, out of any number of attempts or any number of repeated runs, that's a real double-booking bug and should block everything downstream (Booking, Payment) until it's fixed — this is exactly the kind of bug that can hide for months under low traffic and then cause real financial/trust damage the first busy day.

---

## AUTOMATED TESTING GUIDE [FOR NSISONG]

- Just Housing: `poetry run pytest tests/unit/housing tests/integration/housing tests/api/housing`
- Domain only (fast, no database): `poetry run pytest tests/unit/housing -v`
- **The concurrency test specifically, run several times in a row:** `for i in 1 2 3; do poetry run pytest tests/integration/housing/test_concurrency.py -v; done`
- Full verification: `poetry run pytest && poetry run ruff check . && poetry run mypy src && poetry run lint-imports`
- After this module, re-run Security's suite in isolation to confirm the `HOUSING_MANAGE` addition didn't disturb anything else there.


---

## MODULE DOCUMENTATION REQUIREMENTS [FOR YOU — GEMINI CLI, part of Chunk 12]

Write `docs/modules/housing.md`. Cover, specifically: the three-tier Property/Unit/Listing model and why (point to this document's Architectural Interpretation rather than re-deriving); the capacity/`available_count` mechanism explained clearly enough that nobody "simplifies" it into a boolean later; the Listing state machine table, verbatim; the concurrency technique from Chunk 7, in full — this is the one part of this module's documentation that most needs to survive contact with a future engineer who's never seen atomic `UPDATE...WHERE` reservation before; `AvailabilityPort`'s exact contract and the compensating-action note for Booking; the amenity split (property-wide vs unit-specific) and why; every use case and endpoint; the three cross-module integration points from Chunk 10, stated plainly, including the two that don't exist yet; known limitations (no media upload, just URL storage; `GET /listings` is a placeholder, not real search; no `DuplicateProperty`/`UnauthorizedListingOperation` triggers in practice).

## AI STATE REQUIREMENTS [FOR YOU — GEMINI CLI, part of Chunk 12]

Update `CURRENT_STATE.md`, `PROGRESS.md`, `COMPLETED_WORK.md`, `ARCHITECTURE_STATE.md` (note this is the first module with a real concurrency-critical operation, and describe the technique in one paragraph), `DATABASE_STATE.md`, `API_STATE.md`, `TEST_STATE.md`, `DECISIONS.md` (append ADR-052–060), `SESSION_HANDOFF.md`. Security's own state should note its fifth permission.

---

## COMPLETION CHECKLIST [FOR NSISONG]

- [ ] Property → Unit → Listing model works end to end, including a unit representing multiple identical interchangeable spaces via `total_capacity`.
- [ ] Listing state machine rejects every transition not explicitly in the table, including everything out of `ARCHIVED`.
- [ ] Publishing is blocked by zero price or zero availability, with a clear distinction in the error message.
- [ ] "Bookable" is computed, never stored — verified by the specific test asserting `status` doesn't change when availability hits zero.
- [ ] `HOUSING_MANAGE` correctly gates every mutation, and ownership is enforced (a different Scout, and a Student, both correctly rejected).
- [ ] **The concurrency test passes reliably across multiple runs, not once** — this is the single most important item on this checklist.
- [ ] `reserve_slot`/`release_slot` use the atomic `UPDATE...WHERE` technique, confirmed by reading the repository code, not just by the test passing (a test can pass by luck; a code review confirms the mechanism is actually right).
- [ ] No cross-module database access in any direction.
- [ ] Unit, integration, API, and architecture tests all pass — every module together.
- [ ] `docs/modules/housing.md` exists and covers everything above, especially the concurrency technique in enough detail to actually be useful to a future reader.
- [ ] All `AI_state/` files updated, including Security's new permission.
- [ ] Known limitations documented, not silently left implicit.

