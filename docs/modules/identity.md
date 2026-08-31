# Identity Module

The Identity module handles user registration, authentication, session management, and profile retrieval for Camp Match.

## Overview

- **Purpose**: Manage identities and provide secure access.
- **Scope**: User accounts, credentials, session tokens.

## Architecture

The module follows hexagonal architecture:

- **Domain**: Pure business logic (entities like `UserAccount`, value objects, domain errors).
- **Application**: Ports and use cases (e.g., `RegisterAccountUseCase`, `AuthenticateUserUseCase`).
- **Adapters**:
  - **API**: FastAPI routers and schemas.
  - **Persistence**: SQLAlchemy repositories.
  - **Security**: JWT authentication, Scrypt password hashing.

## Use Cases

- Register Account
- Authenticate User
- Refresh Session
- Logout
- Get Identity

## Domain Model

- `UserAccount` entity.
- `EmailAddress` value object.
- `Password` value object.

## Testing Strategy

- **Unit**: Domain logic, use cases (mocks for infrastructure).
- **Integration**: Database operations, session adapter logic.
- **API**: HTTP-level tests against the FastAPI router.
