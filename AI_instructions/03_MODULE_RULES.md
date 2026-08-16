# Module Rules

Template for `src/camp_match/modules/<module_name>/`:
- domain/ (entities, VO, errors, events — no framework imports)
- application/
    - ports/ (inbound.py, outbound.py — interfaces)
    - use_cases/
- adapters/
    - api/ (router.py, schemas.py, dependencies.py)
    - persistence/ (models.py, repository.py)
    - security/ (optional: password hashing, token issuance, credentials)
    - external/ (if needed)

Tests: `tests/unit/<module_name>/`, `tests/integration/<module_name>/`, `tests/api/<module_name>/`.
Docs: `docs/modules/<module_name>.md`.
