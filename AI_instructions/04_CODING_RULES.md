# Coding Rules

1. Do not redesign the architecture.
2. Do not invent requirements.
3. Do not introduce unauthorized libraries/tools.
4. Do not modify unauthorized modules/files.
5. Do not bypass ports.
6. Do not import internals of other modules.
7. Do not place business logic in API/adapters.
8. Do not import infrastructure libraries in domain code.
9. Do not delete/weaken tests.
10. Do not weaken input validation.
11. Do not silently change public interfaces.
12. Do not mark chunk complete without meeting Acceptance Criteria.
13. Do not claim test pass without running it.
14. Do not fabricate command output.
15. Do not refactor outside chunk scope.
16. Do not proceed without explicit instruction.
17. Do not leave architectural decisions undocumented.
18. Report ambiguity immediately.

Commands:
- Linting: `poetry run ruff check .`
- Formatting: `poetry run ruff format .`
- Type checking: `poetry run mypy src`
