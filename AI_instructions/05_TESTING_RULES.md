# Testing Rules

Layers:
- unit: Pure logic, no I/O (Marker: `unit`)
- integration: Real adapters (DB, systems) (Marker: `integration`)
- api: HTTP-level tests against FastAPI (Marker: `api`)
- architecture: Import/dependency checks (Marker: `architecture`)

Commands:
- All: `poetry run pytest`
- By layer: `poetry run pytest -m <marker>`
- Single file: `poetry run pytest <path>`
