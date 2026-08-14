# Architecture Rules

Modular Monolith: Hexagonal architecture (ports-and-adapters).

Layers:
- domain: Core entities, VO, business rules.
- application: Use cases, repository interfaces.
- ports: Interfaces (inbound/outbound).
- adapters: HTTP handlers, DB implementations.
- infrastructure: Framework setup, config, logging.

Dependency Rule: Dependencies point inward to the domain. Domain knows nothing of persistence, API, or infrastructure.
Good import: `src.camp_match.modules.housing.domain` -> `src.camp_match.shared_kernel.domain`
Bad import: `src.camp_match.modules.housing.domain` -> `src.camp_match.platform.db`
