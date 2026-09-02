# API Rules

- Thin routers.
- Schema validation via Pydantic.
- Centralized error translation.
- Request correlation via `X-Request-ID`.
- Authenticated-caller extraction is a platform-level dependency (platform/security/authentication.py).
