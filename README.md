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
- Architectural boundaries: `poetry run lint-imports`

## Contributing / Commit Convention
This project uses [Conventional Commits](https://www.conventionalcommits.org/).
Please use one of the following types for your commit messages:
- `feat`: A new feature
- `fix`: A bug fix
- `chore`: Build process or auxiliary tool changes
- `docs`: Documentation changes
- `test`: Adding missing tests
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
