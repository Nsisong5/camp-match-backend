# Housing & Listings Module

## Architecture
The Housing module follows a three-tier model:
- `Property`: The physical building.
- `Unit`: A category of rentable space within a property, defined by capacity (not one-row-per-room).
- `Listing`: The marketplace-facing offer for exactly one `Unit`, enforced by a unique constraint (ADR-052).

## Capacity & Availability
- `Unit` maintains `total_capacity` and `occupied_count`.
- `available_count` is a derived property (`total_capacity - occupied_count`), never stored.
- `Listing.is_bookable` is computed at query time by the application layer based on `Listing.status` and `Unit.available_count` (ADR-054).

## Listing State Machine
| From | To (Allowed) |
|---|---|
| DRAFT | PUBLISHED, ARCHIVED |
| PUBLISHED | UNAVAILABLE, ARCHIVED |
| UNAVAILABLE | PUBLISHED, ARCHIVED |
| ARCHIVED | (terminal) |

## Concurrency Technique
To prevent double-booking, the module uses atomic `UPDATE` statements at the persistence layer (`SqlAlchemyUnitRepository.try_reserve`):
```sql
UPDATE units
SET occupied_count = occupied_count + 1
WHERE id = :unit_id AND occupied_count < total_capacity
```
This ensures the check and write happen atomically in the database, preventing race conditions between concurrent requests.

## AvailabilityPort
The `AvailabilityPort` provides the contract for other modules (like Booking) to interact with slot availability:
- `check_availability(unit_id: EntityId) -> int`: Returns current available count (display only).
- `reserve_slot(unit_id: EntityId) -> bool`: Attempts to atomically reserve a slot.
- `release_slot(unit_id: EntityId) -> None`: Releases a slot (compensating action if Booking fails).

## Amenity Split
- **Property-wide**: Water, electricity, security, parking, generator, CCTV, Wi-Fi.
- **Unit-specific**: Furnished, private bathroom, kitchen.

## Future Cross-Module Integration
- **Verification**: Will consume Housing through direct id lookups (`GetProperty`/`GetListing`/`GetUnit`).
- **Search**: Will consume `ListActiveListings`'s underlying data.
- **Booking**: Will consume `AvailabilityPort` directly.

## Known Limitations
- Media storage is limited to URLs.
- `GET /listings` is a basic browse endpoint; advanced search is not implemented.
- No direct `DuplicateProperty` or `UnauthorizedListingOperation` independent error triggers exist (uses standard errors).
