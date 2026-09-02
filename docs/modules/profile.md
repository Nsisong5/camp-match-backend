# Profile Module

The Profile module handles user profile management, including personal details, student-specific information (budget, preferences), and scout-specific information (business details, availability).

## Design Overview
- **Modular Monolith**: Follows hexagonal architecture (domain, application, ports, adapters).
- **Core Entities**: `Profile`.
- **Value Objects**: `ProfileType`, `StudentProfileDetails`, `ScoutProfileDetails`.

## API Endpoints
- `POST /api/v1/profiles`: Create a new profile (linked to an Identity ID).
- `GET /api/v1/profiles/me`: Get current user's full profile.
- `GET /api/v1/profiles/{profile_id}`: Get a public profile view (limited data).
- `PATCH /api/v1/profiles/me`: Update core profile info.
- `PATCH /api/v1/profiles/me/student`: Update student-specific details.
- `PATCH /api/v1/profiles/me/scout`: Update scout-specific details.

## Persistence
- SQLAlchemy-backed repository using three tables: `profiles`, `student_profiles`, `scout_profiles`.
