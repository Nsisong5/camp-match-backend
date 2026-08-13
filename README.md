# Camp Match

Camp Match backend — modular monolith, hexagonal architecture. Under construction.

## Testing
- Run all tests: `poetry run pytest`
- Run one layer: `poetry run pytest -m unit` (also `integration`, `api`, `architecture`)
- Run a single file: `poetry run pytest tests/api/test_health.py`

## Code Quality
- Linting: `poetry run ruff check .`
- Formatting: `poetry run ruff format .`
- Type checking: `poetry run mypy src`
