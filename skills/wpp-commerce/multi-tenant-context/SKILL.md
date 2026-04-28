---
name: multi-tenant-context
description: >
  How multi-tenancy works in zoppy-whatsapp-commerce — every record is scoped
  by company_id, every query filters by it, every cache key is namespaced by
  it, and every log line carries it. Use this skill whenever you write a
  query, add a cache layer, design a webhook, instantiate an agent, write
  tests for a tenant-aware service, or audit code for tenant leaks. Triggers
  on: "company_id", "multi-tenant", "multitenant", "tenant", "isolation",
  "scoping", "scope by company", "cache key", "Valkey cache", "cache TTL",
  "invalidate cache", "webhook invalidation", "request_context", "bind
  context", "Company cache", "AgentConfig cache", "thread_id",
  "AgentManager", "snapshot_config", "tenant leak", "isolamento por tenant".
---

# Multi-Tenant Context — zoppy-whatsapp-commerce

The whole system is multi-tenant by `company_id`. There is no per-tenant
database — tenants share schema, tables, Valkey keyspace and Celery
queues, and the only thing that keeps them apart is consistent scoping.
Every leak is a security incident. Treat `company_id` as a load-bearing
invariant.

## The four places `company_id` shows up

1. **Database — every domain table has a `company_id` UUID FK.** Every
   query MUST filter on it. Repositories under `src/domain/<feature>/repository.py`
   are the right place to enforce this — no other layer should be writing
   raw SQL.
2. **Cache — every Valkey key is prefixed by `<topic>:<company_id>`.**
   Examples:
   - `company:<company_id>` — cached `CompanyConfig`
   - `agent_config:<agent_config_id>` — cached `AgentConfigData`
     (note: keyed by `agent_config_id`, but agent_config rows themselves
     belong to a single company)
   - `handoff_cooldown:<company_id>:<customer_phone>` — handoff cooldown
   - `cart:<thread_id>` — cart, where `thread_id = "<company_id>:<customer_phone>"`
   - LangGraph checkpoint keys derived from `thread_id`, same shape
3. **Logs — `company_id` is bound to the structlog context for the whole
   request lifecycle** (plus `customer_phone` and `thread_id` when relevant).
   Once `bind_context(...)` runs, every `logger.info(...)` carries those
   fields automatically.
4. **Agent state — the `AgentManager` cache key is `<company_id>:<agent_config_id>`,**
   and the conversation `thread_id` is `<company_id>:<customer_phone>`.
   Tenant separation in conversation state falls out of these two keys.

## Where each piece lives

| Concern | File |
|---|---|
| Cache client | `src/infra/cache.py` |
| Valkey client | `src/infra/valkey.py` |
| Async DB session | `src/infra/database.py` (`get_session`, `get_db`) |
| Request-scoped context (logger contextvars) | `src/utils/request_context.py` |
| Logger that picks up the context | `src/utils/logger.py` |
| Per-thread agent + frozen config | `src/ai/agent_manager.py` |
| Webhook handlers (where invalidation happens) | `src/api/webhooks/handlers/<feature>/` |
| Cooldown after handoff | `src/application/handoff/handoff_cooldown.py` |

## Repository scoping — the absolute rule

Every read or write through `src/domain/<feature>/repository.py` filters
by `company_id`. Real example from `src/domain/company/repository.py`:

```python
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

For features whose primary key is the `company_id` itself (like `Company`),
the filter is the lookup. For features keyed by their own UUID
(`AgentConfig`, `KnowledgeDocument`, `ConversationMetric`), the lookup must
**still** include `company_id` whenever the call site has it — never trust
a UUID alone to scope reads:

```python
# WRONG — leak path: an attacker who guesses an agent_config_id can read
# someone else's row.
await repo.get_by_id(agent_config_id)

# RIGHT — explicit tenant guard.
await repo.get_by_id(agent_config_id, company_id=company_id)
```

Application services know the company at call time (it's threaded through
from the webhook, the chat request, or the playground call). Pass it down.

## Service-level cache pattern

The canonical example is `src/application/company/company_service.py` —
copy this shape for any new tenant-scoped cache:

```python
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

    async def invalidate_cache(self, company_id: str) -> None:
        await cache_client.delete(self._cache_key(company_id))

    def _cache_key(self, company_id: str) -> str:
        return f"{self.CACHE_PREFIX}:{company_id}"
```

Conventions:

- Prefix every key by `<topic>:` then the tenant id. Never derive cache
  keys without the tenant in them.
- TTL comes from `settings` (`settings.company_cache_ttl`,
  `settings.agent_config_cache_ttl`, `CACHE_TTL`). Don't hard-code seconds
  in the service.
- Cache on read-after-miss, not on write. Writes invalidate; the next read
  re-populates.
- Serialize through the Pydantic model: `config.model_dump_json()` on set,
  `Model.model_validate_json(cached)` on get. Don't pickle.

## Webhook invalidation contract

External systems push to `/webhooks/*` whenever the upstream company /
agent config / integration changes. Every handler:

1. Persists the change through the repository.
2. **Invalidates the relevant Valkey key(s)** so the next read fetches
   fresh data.

Real example from `src/api/webhooks/handlers/company/synced.py`:

```python
@router.post("/company/synced")
async def handle_company_synced(
    payload: CompanySyncedPayload,
    db: AsyncSession = Depends(get_db),
):
    company_repo = CompanyRepository(db)
    await company_repo.sync_from_platform(
        company_id=payload.company_id,
        company_data=payload.company,
        attributes_data=payload.attributes,
    )
    await cache_client.delete(f"company:{payload.company_id}")
    return {"status": "success", ...}
```

Rules:

- The cache key string must match what the service writes. If you change
  the prefix in one place, change it in both — there's no shared
  constant yet (consider promoting to one if a third caller appears).
- For `AgentConfig` updates that affect live conversations, also clear the
  `AgentManager` cache via `agent_manager.invalidate(company_id)` so the
  agent gets recompiled on the next message — see
  `src/api/webhooks/handlers/agent_config/updated.py`.
- Webhook handlers are a `controller` layer in disguise — they may import
  from `application/`, `domain/`, `infra/`, `utils/`. They must not contain
  business logic that other features will need; if they do, lift it into an
  application service.

## Request lifecycle — binding the tenant context

At the start of every chat request, `src/ai/orchestrator.py:run_conversation`
binds the tenant context to structlog's contextvars. From that point on,
**every `logger.info(...)` call inside the same async task carries
`company_id`, `customer_phone`, `thread_id` automatically.**

```python
from src.utils.request_context import bind_context, clear_context

bind_context(
    company_id=company.company_id,
    customer_phone=customer_phone,
    thread_id=thread_id,
)
try:
    ...
finally:
    clear_context()
```

For background work (Celery tasks, scheduled jobs) that doesn't run inside
a chat request, bind the context manually at the top of the task using the
inputs (`company_id`, `document_id`, etc.). For helpers that need extra
fields not yet bound, use `get_contextualized_logger(...)` from
`src/utils/logger.py`.

## Agent state — the two keys you need to know

`src/ai/agent_manager.py` keeps a per-tenant cache of compiled LangGraph
agents and a per-thread snapshot of the agent config:

- **Agent cache key:** `<company_id>:<agent_config_id>`. TTL defaults to
  30 min. Compiled agents are reused across messages of the same tenant.
- **Thread id:** `<company_id>:<customer_phone>` — used by the LangGraph
  Valkey checkpointer. Conversations are isolated per tenant by virtue
  of this key.
- **`AgentManager.snapshot_config(thread_id, current_config)`** freezes
  `AgentConfigData` on the first message of a thread so a config edit
  mid-conversation doesn't leak into a running session. The snapshot
  expires alongside the agent cache TTL.

When a webhook updates an `AgentConfig`, call
`agent_manager.invalidate(company_id)` so future threads get the fresh
compiled agent. Existing threads keep their snapshot — by design.

## Test posture

- Unit tests of services should patch `cache_client` on the **consumer
  module path** (`src.application.company.company_service.cache_client`,
  not `src.infra.cache.cache_client`) — see the `testing` skill for the
  pattern.
- Integration tests of repositories run against SQLite in-memory and
  exercise the `company_id` filter explicitly. There must be at least one
  test per repository that proves a query for company A doesn't see rows
  from company B.
- For multi-tenant cache, write a paired test: `set` for company A,
  `get` for company B, expect None. Cheap and catches prefix drift early.

## Gotchas / anti-patterns

- **Never query by the entity's own UUID alone** when the call site knows
  the tenant. Pass `company_id=` and use it as an extra `WHERE` clause.
- **Never share a Valkey key without the tenant in it** unless it is truly
  global (model pricing, feature flag definitions, etc.).
- **Never cache a Pydantic model with shared mutable references** — always
  serialize via `model_dump_json` so the cached state is independent.
- **Never log raw `customer_phone` outside the bound context.** Phones are
  PII; the structured logger is configured to handle them, but ad-hoc
  `logger.info(f"phone is {phone}")` strings escape redaction.
- **Never write a webhook handler that updates a cached entity without
  invalidating the cache.** The next chat request will run with stale
  config and the bug is hard to spot in production.
- **Never trust `request_context` in fan-out.** Once you spawn a Celery
  task or a background `asyncio.create_task`, the contextvars don't
  propagate. Re-bind at the top of the new task.
- **Never omit `company_id` from a fresh log call.** If `bind_context`
  hasn't run (a CLI script, a Celery task, a fixture), pass it explicitly
  as a kwarg: `logger.info("event", company_id=company_id, ...)`.

## Pre-PR checklist

- [ ] Every new repository method takes `company_id` (or an entity that
      already carries it) and filters on it
- [ ] Every new cache key includes `<topic>:<company_id>` (or
      `<thread_id>`, which already encodes it)
- [ ] If a write affects a cached entity, the corresponding webhook /
      mutation invalidates the cache
- [ ] If an `AgentConfig` is touched, `agent_manager.invalidate(company_id)`
      is called
- [ ] Background tasks and Celery jobs `bind_context(...)` at the top
- [ ] Test for the negative path: another tenant cannot read the new row
- [ ] Logs carry `company_id` (either bound via `request_context` or
      passed explicitly)
