---
name: alembic-migration
description: >
  How to create and apply Alembic database migrations in
  zoppy-whatsapp-commerce (PostgreSQL 16 + pgvector + asyncpg). Covers
  the migrations/ folder layout, the make migration / make migrate
  workflow, the autogenerate cycle (always read before applying),
  per-feature model imports in env.py, the pgvector extension setup,
  multi-tenant FK conventions (company_id), data migrations vs schema
  migrations, downgrade discipline, partial unique indexes for soft
  delete, and how to keep migrations passing on the SQLite in-memory
  test DB. Use this skill whenever adding a new model, adding/altering/
  dropping a column, creating an index or constraint, registering a new
  model in env.py, or troubleshooting an Alembic head/branch issue.
  Triggers on: "create migration", "nova migration", "alembic", "make
  migrate", "make migration", "autogenerate", "--autogenerate",
  "downgrade", "alembic revision", "alembic upgrade", "Alembic head",
  "merge migrations", "data migration", "pgvector", "create table",
  "add column", "drop column", "constraint", "index", "FK company_id",
  "soft delete index".
---

# Alembic Migrations — zoppy-whatsapp-commerce

The project uses Alembic for schema evolution against PostgreSQL 16
(with the `pgvector` extension). All migrations live under
`migrations/versions/`. The `make` targets wrap the alembic CLI so the
correct env / venv is used.

## Layout

```
migrations/
├── env.py                # Alembic environment (target_metadata, model imports)
├── README
├── script.py.mako        # template for new migrations
└── versions/
    ├── fb801f698202_initial_schema.py
    ├── 80fc4916a49a_add_handoff_events_and_agent_handoff_.py
    ├── a8d67c1b549a_add_handoff_cooldown_minutes_to_agent_.py
    ├── 39969ff83e97_add_handoff_message_overrides_to_agent_.py
    └── c4f1a2e93b51_add_agent_style_and_preset_to_agent_.py
```

`alembic.ini` lives at the repo root. The DB URL is read from the
`WHATSAPP_COMMERCE_DATABASE_URL` env var (override) and falls back to
the value in `alembic.ini` for local dev.

## Daily commands

```bash
# Create a new migration from current model diff
make migration m="add example column to company"

# Apply pending migrations
make migrate

# Reset DB (down + up + migrate) — destroys local data
make db-reset
```

Behind the scenes:

- `make migration` runs
  `uv run alembic revision --autogenerate -m "<message>"`
- `make migrate` runs `uv run alembic upgrade head`

You can drop down to alembic directly when you need finer control:

```bash
uv run alembic current             # show current revision
uv run alembic history             # full history
uv run alembic heads               # show heads (multiple == branch problem)
uv run alembic upgrade <rev>       # upgrade to specific revision
uv run alembic downgrade -1        # one step back
uv run alembic downgrade <rev>     # go to specific revision
```

## The autogenerate cycle — always review before applying

`--autogenerate` produces a draft. **Always read it before `make migrate`.**
Common things autogen gets wrong:

| Pitfall | What to do |
|---|---|
| Detects an Enum change as drop+create | Manually rewrite as `ALTER TYPE` |
| Misses CHECK constraints with custom names | Add `name=` consistently on the model and re-run |
| Reorders index name unexpectedly | Inspect, rename to match existing if needed |
| Drops a column you only renamed | Use `op.alter_column(..., new_column_name=...)` |
| pgvector `Vector(N)` columns | Confirm dialect import and dimensions match the model |
| Soft-delete unique constraints | Replace with partial unique index (see below) |

The rhythm:

1. Edit `src/domain/<feature>/model.py` — add the column / constraint /
   index.
2. Make sure the new model file is imported in `migrations/env.py` so
   autogen sees it (see the `env.py` section).
3. `make migration m="<short imperative description>"` — generates a file
   under `migrations/versions/`.
4. **Open the file**, read upgrade/downgrade. Fix anything autogen got
   wrong. Add a docstring describing why the migration exists if the
   `m=` message isn't enough.
5. `make migrate` to apply locally.
6. Run `uv run pytest tests/integration/ -q` — integration tests run
   against SQLite in-memory and use `Base.metadata.create_all`, so they
   don't replay migrations, but they do confirm the model + repository
   still match.
7. Commit the migration file together with the model + repository
   changes.

## Registering a new model in `migrations/env.py`

`env.py` builds `target_metadata` from `Base.metadata`. For autogen to
detect a new table, the model has to be imported somewhere that runs
before `target_metadata = Base.metadata` is read.

Today the project imports each feature's model explicitly:

```python
# migrations/env.py — head of file
from src.domain.shared.base import Base
from src.domain.company.model import Company
from src.domain.agent_config.model import AgentConfig
from src.domain.knowledge.model import KnowledgeDocument
# ... etc

target_metadata = Base.metadata
```

When you add a feature:

1. Import its model in `env.py` immediately after the existing block.
2. If `src/domain/__init__.py` already imports the model (it does, for
   the integration test bootstrap), you can also do
   `import src.domain  # noqa: F401` once at the top — both paths are
   acceptable, but be explicit and consistent within the file.

> **Heads up — env.py paths may lag the refactor.** Issue #59 moved
> models from `src/domain/models/<feature>.py` to
> `src/domain/<feature>/model.py`. If `migrations/env.py` still
> references the old paths, fix that import before generating any new
> migration. The integration test bootstrap (`src/domain/__init__.py`)
> already uses the new paths and is the source of truth for which
> models exist.

## File anatomy

```python
"""initial schema

Revision ID: fb801f698202
Revises:
Create Date: 2026-03-03 15:25:58.331947
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'fb801f698202'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(...)
    op.create_index(...)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(...)
    op.drop_table(...)
```

Conventions:

- The docstring is the only place to write longer rationale. The `m=`
  message becomes the file slug and the first docstring line.
- Always implement `downgrade()`. Even if the team rarely runs it, the
  symmetry is the test of whether your `upgrade` is reversible.
- `op.execute("CREATE EXTENSION IF NOT EXISTS vector")` lives in the
  initial schema and any migration that adds a `pgvector` column to a
  freshly-cloned environment.
- Use `postgresql` types (`postgresql.UUID`, `postgresql.JSONB`) when the
  model uses them. SQLite tests have compatibility shims in
  `tests/integration/conftest.py`.

## Multi-tenant — `company_id` FK convention

Every domain table that belongs to a tenant declares:

```python
sa.Column('company_id', sa.String(length=36), nullable=False),
sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_<table>_company'),
sa.Index('idx_<table>_company', 'company_id'),
```

Rules:

- `company_id` must be **NOT NULL** for tenant-scoped tables. If it
  could be null, the row escapes scoping in repository queries.
- Always add an index on `company_id`. Tenant queries will scan this
  column on every read.
- Use a stable name for the index (`idx_<table>_company`) so future
  autogens don't churn.
- Cross-table queries that join a tenant-scoped table to another should
  preserve `company_id` in both — never lose the scope mid-join.

## Data migrations

For changes that need to backfill data, do schema + data in the same
migration when possible:

```python
def upgrade() -> None:
    op.add_column('agent_configs', sa.Column('preset', sa.String(50), nullable=True))

    # Backfill from existing custom_prompt
    bind = op.get_bind()
    bind.execute(sa.text(
        "UPDATE agent_configs SET preset = 'objetivo' WHERE preset IS NULL"
    ))

    # Tighten constraint after backfill
    op.alter_column('agent_configs', 'preset', nullable=False)
```

For large backfills (millions of rows), split into two migrations:

1. Add the column nullable. Deploy. Backfill out of band (script).
2. In a second migration, set NOT NULL after the backfill is verified.

This avoids holding write locks during a big update.

## Soft delete — partial unique indexes

The codebase soft-deletes (sets `deleted_at = now()`) instead of
DELETEing. A unique constraint that includes `deleted_at` would prevent
re-inserting a "deleted" row. The right shape is a **partial unique
index**:

```python
def upgrade() -> None:
    op.create_index(
        'uq_companies_provider_external',
        'companies',
        ['provider', 'external_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
    )

def downgrade() -> None:
    op.drop_index('uq_companies_provider_external', table_name='companies')
```

Autogen will sometimes propose a regular `UniqueConstraint` — flip it
to a partial index when the table has `deleted_at`.

## Branch / merge problems

If two PRs land migrations against the same `down_revision`, you get
two heads and `make migrate` complains:

```bash
uv run alembic heads
# prints two revision ids
```

Fix by creating a merge migration:

```bash
uv run alembic merge -m "merge feature-x and feature-y heads" <rev1> <rev2>
```

Read the generated file. The `upgrade()` / `downgrade()` are usually
empty — the merge file just declares the new single head.

## Testing migrations

There is no migration replay in the integration suite — it uses
`Base.metadata.create_all` directly against SQLite. That means:

- Schema diffs are caught by autogen, not by a CI replay.
- It's easy for a migration to be wrong without integration tests
  noticing. Always run `make migrate` against a clean local DB and run
  `uv run pytest tests/integration/ -q` to confirm the model + repo
  still match.
- For risky migrations (data backfill, constraint tightening), run them
  twice in dev: once cold, once after a downgrade, to validate
  reversibility.

## Gotchas / anti-patterns

- **Never edit a migration that's already in `master` / `staging`.**
  Roll a new migration that fixes the previous one. Editing in place
  diverges environments.
- **Never `make migrate` without reading the generated file.** Autogen
  is a draft.
- **Never delete a migration file without coordinating** — if it's been
  applied somewhere, the only safe path is a new migration that
  inverts it.
- **Don't import production code directly inside `upgrade()`.** Use raw
  SQL via `bind.execute(sa.text(...))` and ORM Core constructs. Domain
  Pydantic schemas drift faster than DB schema; the migration shouldn't
  break when you rename a service.
- **Don't forget pgvector.** New environments need
  `CREATE EXTENSION IF NOT EXISTS vector` before `knowledge_embeddings`
  becomes valid.
- **Don't put unique constraints on tables with `deleted_at`** — use a
  partial unique index (`postgresql_where=sa.text('deleted_at IS NULL')`).
- **Don't leave `down_revision = None`** unless you're authoring the
  initial migration. Autogen sets this correctly; don't manually break
  the chain.
- **Don't use `nullable=True` on `company_id`** — multi-tenant leak.

## Pre-PR checklist

- [ ] Model change in `src/domain/<feature>/model.py` is committed
- [ ] New model imported in `migrations/env.py` (or `src/domain/__init__.py`
      already imports it and `env.py` defers there)
- [ ] Generated with `make migration m="<imperative message>"`
- [ ] Migration file read end-to-end and edits applied where autogen is
      wrong (Enums, partial indexes, custom constraint names)
- [ ] `downgrade()` is implemented and reversible
- [ ] `company_id` columns are `NOT NULL` and have an `idx_<table>_company`
      index when applicable
- [ ] Data backfills use `bind = op.get_bind(); bind.execute(sa.text(...))`,
      not the ORM
- [ ] `make migrate` runs clean against a fresh local DB
- [ ] `uv run alembic downgrade -1 && uv run alembic upgrade head` round-trips
      cleanly for risky migrations
- [ ] `uv run pytest tests/integration/ -q` is green
- [ ] Migration file + model change + repository change land in the same
      commit / PR
