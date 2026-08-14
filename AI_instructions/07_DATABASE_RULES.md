# Database Rules

- One module owns one set of tables.
- No direct cross-module table queries.
- Migrations only via Alembic.
- Audit timestamps (created_at/updated_at) use DB defaults for persistence, Clock port for domain logic.
