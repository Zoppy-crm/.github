---
name: application-service
description: >
    How to create and modify Application Services in zoppy-whatsapp-commerce —
    the use-case orchestration layer that lives under
    src/application/<feature>/<feature>_service.py. Covers the file/class shape,
    the absolute "service does not inject another service" rule and its escape
    paths (feature helpers vs cross_cutting/helpers/ vs utils/), session
    management with get_session(), the read-through cache pattern, ValueError
    on input problems, structured logging, and where to put pure calculators
    vs services. Use this skill whenever creating a new service, adding a
    method to an existing one, deciding whether shared logic should be a
    helper, mapping infra failures to business outcomes, or auditing a
    service for layer violations. Triggers on: "create service", "novo
    service", "ApplicationService", "application service", "use case", "caso
    de uso", "service does not inject service", "service não injeta service",
    "feature helper", "cross_cutting helper", "get_session", "cache_client",
    "service-to-service", "application/<feature>", "service_calculator",
    "service vs calculator".
---

# Application Service — zoppy-whatsapp-commerce

Application Services live at `src/application/<feature>/<feature>_service.py`
and orchestrate one feature's use cases. They are the equivalent of the
NestJS `*.application.ts` files — the layer where business decisions are
made by composing Repositories, Infra clients, and helpers.

A service is the **only** layer allowed to:

-   Open DB sessions via `async with get_session() as session: ...`
-   Read/write the Valkey cache directly
-   Translate raw exceptions from infra into domain-meaningful failures
-   Decide what to do with the data the Repository returns

It is **not** allowed to:

-   Inject another Application Service (hard rule, see escape paths below)
-   Hold HTTP knowledge (`HTTPException`, FastAPI types — those belong in
    `api/`)
-   Define ORM models, Pydantic schemas, or raw SQL (those belong in
    `domain/<feature>/`)

## Layout

```
src/application/<feature>/
├── __init__.py              # empty — no re-exports
├── <feature>_service.py     # the use case (class)
└── helpers/                 # created on first real extraction, not before
    └── <feature>.helper.py
```

Real examples in the project:

-   `src/application/company/company_service.py` — read-through cache around
    a single repository
-   `src/application/agent_config/agent_config_service.py` — cache + `update_field`
    pattern with an `on_invalidate` callback so callers can clear the agent
    manager
-   `src/application/handoff/handoff_event_service.py` — mix of static
    helpers (`extract_transfer_info`, `resolve_reason_label`) and async
    methods that persist
-   `src/application/handoff/handoff_cooldown.py` — module of free functions
    (no class) because the feature is just Valkey-backed predicates
-   `src/application/usage/usage_calculator.py` — pure calculator (static
    methods, no I/O) — kept as a _calculator_, not named `_service`, to
    signal the difference

## When to write a Service vs a Calculator

| Shape                                                    | Filename                                                                       | Use case                                                                    |
| -------------------------------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| Class with I/O (DB, cache, S3, Celery enqueue)           | `<feature>_service.py`                                                         | The default — anything orchestrating real side effects                      |
| Class / module with **only static methods** and zero I/O | `<feature>_calculator.py` (or descriptive name like `message_preprocessor.py`) | Pure transforms (token usage math, message preprocessing, response parsing) |
| Free functions, no class, lightweight                    | `<topic>.py` (e.g. `handoff_cooldown.py`)                                      | When OOP overhead doesn't earn its keep — usually thin wrappers over Valkey |

When in doubt, default to `<feature>_service.py`. Calculators are an
optimization for code that's truly pure.

## Canonical service — `CompanyService`

The cleanest reference for a read-through cache:

```python
from src.domain.company.repository import CompanyRepository
from src.domain.company.schemas import CompanyConfig
from src.infra.cache import cache_client
from src.infra.config import settings
from src.infra.database import get_session


class CompanyService:
    CACHE_PREFIX = "company"

    async def get_by_id(self, company_id: str) -> CompanyConfig | None:
        cached = await self._get_from_cache(company_id)
        if cached:
            return cached

        async with get_session() as session:
            repo = CompanyRepository(session)
            config = await repo.get_by_id(company_id)

        if not config:
            return None

        await self._set_cache(company_id, config)
        return config

    async def list_active(self) -> list:
        async with get_session() as session:
            repo = CompanyRepository(session)
            return await repo.list_active()

    async def invalidate_cache(self, company_id: str) -> None:
        await cache_client.delete(self._cache_key(company_id))

    def _cache_key(self, company_id: str) -> str:
        return f"{self.CACHE_PREFIX}:{company_id}"

    async def _get_from_cache(self, company_id: str) -> CompanyConfig | None:
        key = self._cache_key(company_id)
        cached = await cache_client.get(key)
        if cached:
            return CompanyConfig.model_validate_json(cached)
        return None

    async def _set_cache(self, company_id: str, config: CompanyConfig) -> None:
        key = self._cache_key(company_id)
        await cache_client.set(
            key, config.model_dump_json(), settings.company_cache_ttl
        )
```

Anatomy:

1. **Constants at class level** (`CACHE_PREFIX`).
2. **Public methods first** — that's the API surface. List operations,
   then mutations, then cache management.
3. **Async everywhere** — never sync.
4. **DB access pattern** — `async with get_session() as session:` then
   `repo = SomeRepository(session)`. Never hold a session as an
   instance attribute.
5. **Cache pattern** — read-through on `get_by_id`, populate after miss,
   serialize via `model_dump_json` / `model_validate_json`. Never pickle.
6. **Private helpers at the end** with `_` prefix.

See the `multi-tenant-context` skill for the cache key convention
(`<topic>:<company_id>`) and TTL sourcing from `settings`.

## The hard rule — service does not inject service

**Never** write:

```python
# WRONG — service-to-service injection
class HandoffService:
    def __init__(self, agent_config_service: AgentConfigService):
        self._agent_config = agent_config_service
```

The same rule lives in `CLAUDE.md` and the `architecture` skill. When two
services need shared logic, use one of three escape paths:

| Logic shape                                                                              | Where it goes                                                                                          |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Pure stateless function with **no business concept** (formatting, parsing primitives)    | `src/utils/`                                                                                           |
| Logic shared between methods of the **same** service or the service + its sub-components | `src/application/<feature>/helpers/<feature>.helper.py`                                                |
| Business-concept logic shared by **2+ features**, stateless and no I/O                   | `src/cross_cutting/helpers/<topic>.helper.py` _(the folder is created on first real need, not before)_ |

If the shared logic needs I/O (DB, cache, etc.), the answer isn't a
helper — it's that you have a missing Domain or Repository method.
Promote the I/O into the right Repository, then the two services each
call the Repository directly.

## Session management

Always open a fresh session per logical unit of work:

```python
async with get_session() as session:
    repo = SomeRepository(session)
    result = await repo.some_method(...)
return result
```

Why per-method:

-   Sessions are short-lived. Holding one across many methods leaks
    connections and corrupts transaction boundaries.
-   Repository instances are cheap; recreate them.
-   Multiple sessions in one method are fine when you need transaction
    isolation between steps. Real example:
    `src/application/handoff/handoff_event_service.py:save` opens a session
    inside a `try/except` so a persist failure logs but doesn't crash the
    caller.

The shared dependency `get_db` (used in webhooks via `Depends(get_db)`)
returns a session managed by FastAPI's request lifecycle. Use it
when the service is short-circuited by a webhook handler. For everything
else, use `get_session()`.

## Returning Pydantic, not ORM

Repositories already convert ORM rows to Pydantic schemas (see
`repository-async` skill). Services should:

-   Accept Pydantic models (or primitives like `company_id: str`,
    `document_id: UUID`).
-   Return Pydantic models.

If you find yourself with a `Company` ORM instance inside a service,
either you're using the Repository wrong or the Repository is missing
the `_to_schema(...)` mapper.

## Errors

| Situation                                                   | What to do                                                                                        |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Input validation problem (file too big, unsupported format) | `raise ValueError("...")` — endpoints translate to 400/404                                        |
| Resource not found                                          | Return `None` from the read method; let endpoints translate to 404                                |
| Infra failure that is recoverable in this method            | `try/except`, `logger.error(...)` with structured context, return a sensible fallback (or `None`) |
| Infra failure that should bubble                            | Don't catch — let it propagate. The endpoint sees 500                                             |

Real example from `HandoffEventService.save`:

```python
async def save(self, ...) -> str | None:
    try:
        async with get_session() as session:
            repo = HandoffEventRepository(session)
            event = await repo.save(...)
            return str(event.id)
    except Exception as e:
        logger.error("handoff.persist_failed", error=str(e))
        return None
```

The service decided that a handoff event failing to persist must not
break the conversation. Other services would let the exception bubble.

## Logging

Every public method that does meaningful work emits at least one
structured log line — see `code-conventions` skill. Convention:

```python
logger.info(
    "knowledge.ingest.queued",
    document_id=str(doc_id),
    company_id=company_id,
    filename=filename,
)
```

If the orchestrator already bound `company_id` / `customer_phone` /
`thread_id` to the structlog context, you don't need to repeat them —
they appear automatically. For Celery tasks and CLI flows that don't
go through the orchestrator, pass `company_id=` explicitly.

## Static helpers on the service class

When a calculation belongs _semantically_ to the feature but doesn't
touch I/O, two options:

-   **`@staticmethod` on the service class** if the helper is small and
    used only by that service. Examples:
    `HandoffEventService.extract_transfer_info`,
    `HandoffEventService.resolve_reason_label`.
-   **Separate `<feature>_calculator.py` module** if the helpers add up to
    a coherent unit. Example: `usage/usage_calculator.py` — `extract`,
    `_resolve_pricing`, `_accumulate_tokens`, `_compute_breakdown`.

Don't mix the two. If the calculator grows past 3-4 static methods,
move to its own module.

## Testing services

See the `testing` skill for full conventions. Service tests live in
`tests/unit/application/<feature>/test_<feature>_service.py`. Mock at
the boundary:

```python
@pytest.mark.unit
class TestGetById:
    @pytest.mark.asyncio
    async def test_cache_hit_returns_config(self, service, sample_config):
        with patch(
            "src.application.company.company_service.cache_client"
        ) as mock_cache:
            mock_cache.get = AsyncMock(
                return_value=sample_config.model_dump_json()
            )
            result = await service.get_by_id("test-company")
            assert result.company_id == "test-company"
```

Patch the **consumer module path**, not the source module. See the
`testing` skill for the async context manager mocking pattern.

## Gotchas / anti-patterns

-   **Never inject one service into another.** First sign: a constructor
    with another `*Service` parameter. Stop and choose a helper escape path.
-   **Never open a long-lived session as `self.session`.** Sessions are
    per-call.
-   **Never hold ORM instances on the service.** Always pass / return
    Pydantic.
-   **Never `raise HTTPException`** — that's the endpoint's job.
-   **Never `from src.api.*` inside `application/`.** Layer rule
    (see `architecture` skill).
-   **Never mutate a domain schema in place after caching it** — Pydantic
    models are passed by reference, so cached state would change too. Build
    a new instance with `.model_copy(update=...)` if you need a tweaked
    variant.
-   **Don't call `repo.get_by_id(some_uuid)` without `company_id` when the
    call site has it.** Multi-tenant leak — see `multi-tenant-context`
    skill.
-   **Don't enqueue Celery tasks via raw `delay()` without `company_id`
    in the kwargs.** The worker re-binds the structlog context using these
    fields.

## Pre-PR checklist

-   [ ] Service file at `src/application/<feature>/<feature>_service.py`
-   [ ] Class name follows `<Feature>Service` (or `<Feature>Calculator` /
        `<Feature>Preprocessor` if pure)
-   [ ] Constructor takes only Repositories, Infra clients, helpers — never
        another `*Service`
-   [ ] All methods are `async def`
-   [ ] DB access uses `async with get_session() as session:` per method
-   [ ] If the service caches: prefix is `<topic>:<company_id>`, TTL from
        `settings`, serializes via `model_dump_json`
-   [ ] Public methods emit one structured log line at minimum
-   [ ] `ValueError` for input validation; `None` for not-found
-   [ ] No `HTTPException`, no `from src.api.*` imports
-   [ ] Tests in `tests/unit/application/<feature>/test_<feature>_service.py`
        cover happy path + cache hit + cache miss + error paths
-   [ ] `uv run pytest tests/unit/application/<feature>/ -q` is green
