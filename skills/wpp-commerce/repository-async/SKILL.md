---
name: repository-async
description: >
  How to create and modify async Repositories in zoppy-whatsapp-commerce
  (SQLAlchemy 2.0 + asyncpg). Covers placement under
  src/domain/<feature>/repository.py, the constructor that takes an
  AsyncSession, query patterns with select() / update() / selectinload(),
  the absolute company_id scoping rule, ORM→Pydantic mapping via _to_schema,
  upsert patterns, soft delete, flush vs commit semantics, and what does
  NOT belong in a Repository (business decisions, cache reads, HTTP). Use
  this skill whenever creating a new Repository, adding a query method to
  an existing one, deciding flush vs commit, mapping a row to a domain
  schema, designing an upsert, or auditing a query for tenant scoping.
  Triggers on: "create repository", "novo repository", "Repository",
  "AsyncSession", "session.execute", "select()", "selectinload",
  "scalar_one_or_none", "scope by company_id", "scoping", "tenant scope",
  "upsert", "soft delete", "_to_schema", "flush", "commit", "data access",
  "SQLAlchemy", "asyncpg", "pgvector", "domain repository".
---

# Repository (async) — zoppy-whatsapp-commerce

Repositories live at `src/domain/<feature>/repository.py` and are the
**only** place where the codebase touches SQL. They:

- Wrap an `AsyncSession` (passed in by the caller)
- Run typed queries against the ORM models in
  `src/domain/<feature>/model.py`
- Convert ORM rows to Pydantic domain schemas before returning
- Enforce `company_id` scoping on every read/write tied to a tenant

They do **not**:

- Decide what to do with the data (that's the Application Service)
- Read or write the cache (cache lives in services / webhook handlers)
- Speak HTTP, FastAPI, or Pydantic-Settings
- Commit transactions on writes that compose with sibling writes
  (the Application Service / webhook handler decides commit boundary)

## Layout

```
src/domain/<feature>/
├── __init__.py          # empty
├── model.py             # SQLAlchemy ORM (inherits Base + TimestampMixin)
├── repository.py        # async Repository class
├── schemas.py           # Pydantic domain schemas (CompanyConfig, ...)
└── webhook_schemas.py   # Pydantic webhook payload schemas (when applicable)
```

Real repositories you can crib from:

- `src/domain/knowledge/repository.py` (84 l) — small, full CRUD, good
  starting point
- `src/domain/company/repository.py` (161 l) — read-with-eager-load,
  upsert, soft delete, `_to_schema` mapper for a complex aggregate
- `src/domain/conversation_metric/repository.py` (257 l) — heavier
  feature with reporting queries and aggregations
- `src/domain/handoff/repository.py` (128 l) — joins across
  `HandoffEvent` and `ConversationMetric` (legitimate cross-feature
  read; see `architecture` skill on the rule)

## Canonical shape

```python
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.<feature>.model import <Feature>
from src.domain.<feature>.schemas import <FeatureConfig>
from src.utils.logger import get_logger

logger = get_logger(__name__)


class <Feature>Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, <feature>_id: UUID, company_id: str | None = None
    ) -> <FeatureConfig> | None:
        query = select(<Feature>).where(<Feature>.id == <feature>_id)
        if company_id is not None:
            query = query.where(<Feature>.company_id == company_id)
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        if not row:
            return None
        return self._to_schema(row)

    def _to_schema(self, row: <Feature>) -> <FeatureConfig>:
        return <FeatureConfig>(...)
```

Anatomy:

1. **Constructor takes `AsyncSession`** — never `get_session()` inside the
   repo. The caller (Service / webhook) controls the session lifecycle.
2. **`select()` for reads, `update()` / `delete()` for writes.** Prefer
   typed Core API over `session.query(...)` (legacy v1 style).
3. **`scalar_one_or_none()` for single-row reads** that may miss.
   `scalar_one()` only when a missing row is a programming error.
4. **`list(result.scalars().all())`** for collections — the explicit
   `list(...)` makes typing happy.
5. **`_to_schema(row)`** maps the ORM instance to a Pydantic schema.
   Every public read returns Pydantic, never the ORM row.
6. **Logger only on writes / state changes**, not on every read. Reads
   are too noisy to log.

## The absolute rule — scope by `company_id`

Every read/write tied to a tenant filters on `company_id`. There are
three shapes you'll see in practice:

**Shape 1 — the entity is the company.** Filter is just the lookup:

```python
# src/domain/company/repository.py
async def get_by_id(self, company_id: str) -> CompanyConfig | None:
    result = await self.session.execute(
        select(Company)
        .options(selectinload(Company.integrations))
        .where(Company.id == company_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    return self._to_schema(row)
```

**Shape 2 — entity has its own UUID, but always belongs to a company.**
Always include `company_id`:

```python
# src/domain/knowledge/repository.py
async def get_by_id(
    self, document_id: UUID, company_id: str | None = None
) -> KnowledgeDocument | None:
    query = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    if company_id is not None:
        query = query.where(KnowledgeDocument.company_id == company_id)
    result = await self.session.execute(query)
    return result.scalar_one_or_none()
```

`company_id` is `Optional` here because some background flows (the Celery
worker processing a document) only know the `document_id`. Application
Services and endpoint paths that **do** know the tenant must pass it.

**Shape 3 — list endpoints scope by `company_id` from the start.**

```python
# src/domain/knowledge/repository.py
async def list_by_company(
    self, company_id: str, status: str | None = None
) -> list[KnowledgeDocument]:
    query = select(KnowledgeDocument).where(
        KnowledgeDocument.company_id == company_id
    )
    if status:
        query = query.where(KnowledgeDocument.status == status)
    query = query.order_by(KnowledgeDocument.created_at.desc())
    result = await self.session.execute(query)
    return list(result.scalars().all())
```

See the `multi-tenant-context` skill for the negative tests that prove
isolation works.

## Eager loading with `selectinload`

When the schema needs related rows (e.g. `Company` + its `integrations`),
eager-load them in the same query. Otherwise SQLAlchemy raises
`MissingGreenlet` errors when async code tries to lazy-load.

```python
result = await self.session.execute(
    select(Company)
    .options(selectinload(Company.integrations))
    .where(Company.id == company_id)
)
```

`selectinload` is the right choice for one-to-many. Use `joinedload`
sparingly (only for one-to-one with predictable size) — it inflates
result rows.

## Insert / Update — `flush` vs `commit`

Two patterns coexist; pick based on transaction scope:

| Pattern | When | Example |
|---|---|---|
| `await self.session.flush()` then `refresh(...)` | The caller owns the transaction (typical Application Service flow) | `KnowledgeDocumentRepository.create` |
| `await self.session.commit()` then `refresh(...)` | The repository is the unit of work — no other write is composed with this one | `CompanyRepository.create_from_onboarding` |

When in doubt, **flush, not commit.** Letting the Service control commit
makes it possible to compose writes (e.g. create the Company *and* the
default AgentConfig in one transaction). The pattern across the codebase
is mixed; new code should prefer `flush` and document any deviation.

After flush/commit, call `await self.session.refresh(<entity>)` to load
DB-assigned values (created_at, server defaults, sequences).

## Upsert pattern

The codebase uses an explicit "look up, then insert or update" pattern
rather than DB-level `INSERT ... ON CONFLICT`:

```python
async def upsert_from_onboarding(
    self,
    company_data: CompanyData,
    attributes_data: CompanyAttributesData,
) -> Company:
    result = await self.session.execute(
        select(Company).where(Company.id == company_data.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.name = company_data.name
        existing.provider = company_data.provider
        ...
        existing.synced_at = datetime.utcnow()
        existing.deleted_at = None  # un-delete on re-onboard
        await self.session.commit()
        await self.session.refresh(existing)
        return existing

    return await self.create_from_onboarding(company_data, attributes_data)
```

This is fine for low-write rates. For high-write rates (metrics,
events) we'd switch to `INSERT ... ON CONFLICT` or a partial unique
index — but that decision should be paired with a benchmark.

## Selective field update via `update()`

When you only want to update a few fields without loading the row, use
the SQLAlchemy `update()` Core construct:

```python
async def sync_from_platform(
    self, company_id: str, company_data: dict, attributes_data: dict
) -> None:
    updates = {}
    if "name" in company_data:
        updates["name"] = company_data["name"]
    ...
    updates["synced_at"] = datetime.utcnow()
    updates["updated_at"] = datetime.utcnow()

    if updates:
        stmt = update(Company).where(Company.id == company_id).values(**updates)
        await self.session.execute(stmt)
        await self.session.commit()
```

Cheaper than load-mutate-save when the row is large or you have many
fields and only a subset arrives in the payload.

## Soft delete

Add a nullable `deleted_at` column on the model and a `soft_delete`
method:

```python
async def soft_delete(self, company_id: str, _reason: str) -> None:
    stmt = (
        update(Company)
        .where(Company.id == company_id)
        .values(deleted_at=datetime.utcnow(), updated_at=datetime.utcnow())
    )
    await self.session.execute(stmt)
    await self.session.commit()
```

Reads should filter `WHERE deleted_at IS NULL` when "active" is the
expected default:

```python
async def list_active(self) -> list[Company]:
    result = await self.session.execute(
        select(Company)
        .options(selectinload(Company.agent_configs))
        .where(Company.deleted_at.is_(None))
        .order_by(Company.name)
    )
    return list(result.scalars().all())
```

The unique constraint on a soft-deleted row may need partial-index
treatment in the migration — see the `alembic-migration` skill.

## ORM ↔ Pydantic mapping (`_to_schema`)

Public methods return Pydantic, not ORM. Map at the repository boundary:

```python
def _to_schema(self, row: Company) -> CompanyConfig:
    integration = row.integrations[0] if row.integrations else None
    return CompanyConfig(
        company_id=row.id,
        company_name=row.name,
        provider=row.provider,
        partners_token=row.partners_token,
        context=CompanyContext(
            brand_tone=row.brand_tone,
            brand_name=row.brand_name,
            brand_description=row.brand_description,
            target_audience=row.target_audience,
        ),
        integrations=IntegrationConfig(...),
    )
```

Why a method instead of `Schema.model_validate(row, from_attributes=True)`:

- We routinely shape nested aggregates (Company → first IntegrationConfig)
  that don't match the ORM relationship 1:1.
- Future-proof against ORM column renames — the mapper is the seam.

For simple cases without reshape, `model_validate` with
`from_attributes=True` is fine — but keep the call inside the repository
so the Application Service never sees an ORM instance.

## Logging

Repositories log **state-changing** events, not every read:

```python
logger.info(
    "knowledge_document.created",
    document_id=str(document.id),
    company_id=document.company_id,
    filename=document.filename,
)
```

Event names follow `<feature>.<state>` (`knowledge_document.created`,
`company.synced`, `handoff_event.persisted`). Reads with cache misses
are logged at the Application Service level, not here.

## Testing

Repository tests are **integration tests**:

```
tests/integration/domain/repositories/test_<feature>.py
```

They run against SQLite in-memory via the `db_session` fixture in
`tests/integration/conftest.py`. The base test pattern:

```python
@pytest.mark.integration
class TestKnowledgeDocumentRepository:
    async def test_knowledge_document_crud(self, db_session):
        repo = KnowledgeDocumentRepository(db_session)
        doc = KnowledgeDocument(...)
        created = await repo.create(doc)
        assert created.id is not None

        fetched = await repo.get_by_id(created.id, company_id=created.company_id)
        assert fetched is not None
```

Always include at least one **negative tenant test**: company A inserts
a row, company B queries by id, expects `None`. See the
`multi-tenant-context` skill.

## Gotchas / anti-patterns

- **Never call `cache_client` from a Repository.** Cache is the
  Application Service's responsibility.
- **Never raise `HTTPException` from a Repository.** Layer rule.
- **Never mix `session.query(...)` (v1) with `select(...)` (v2)** in the
  same file. The codebase uses 2.0-style throughout.
- **Never forget to `await` an `execute()`.** Async ORM, async result.
- **Never trigger lazy loads after the session closes.** Use
  `selectinload` / `joinedload` upfront.
- **Never query by entity UUID alone when the call site has the tenant.**
  Multi-tenant leak.
- **Never commit inside a method that's part of a larger transaction.**
  If the caller needs to compose writes, your `commit` will tear the
  transaction in half.
- **Never put cross-feature joins in a Repository unless the relationship
  is real business** (e.g. `handoff/repository.py` joining
  `HandoffEvent` with `ConversationMetric` is fine because every
  handoff annotates a metric). Auditable on next layer review.
- **Never let `_to_schema` access the DB.** The mapper is in-memory; if
  you need extra rows, load them in the same query (`selectinload`).

## Pre-PR checklist

- [ ] Repository at `src/domain/<feature>/repository.py`
- [ ] Class name follows `<Feature>Repository`
- [ ] Constructor takes `session: AsyncSession` only
- [ ] Every public method is `async def`
- [ ] Every tenant-scoped method filters by `company_id`
- [ ] Reads use `select(...)`; writes use `update()` / direct attr
      mutation; never `session.query(...)` v1 style
- [ ] Public methods return Pydantic via `_to_schema(...)` — no ORM
      leaks
- [ ] Eager-loading set up with `selectinload(...)` for relationships
- [ ] State-changing methods emit a structured log line
- [ ] Integration test in `tests/integration/domain/repositories/test_<feature>.py`
      covers happy path + negative tenant scoping
- [ ] If a new model column was added, an Alembic migration exists
      (see `alembic-migration` skill)
- [ ] `uv run pytest tests/integration/domain/repositories/test_<feature>.py -q`
      is green
