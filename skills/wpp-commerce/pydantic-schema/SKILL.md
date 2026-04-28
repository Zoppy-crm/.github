---
name: pydantic-schema
description: >
  How and where to define Pydantic v2 schemas in zoppy-whatsapp-commerce.
  Schemas live in three distinct locations and choosing the right one
  matters: src/api/schemas/ for HTTP request/response (presentation),
  src/domain/<feature>/schemas.py for domain values that flow through the
  application + repository layers, src/domain/<feature>/webhook_schemas.py
  for webhook payload contracts. Covers the v2 idioms (model_dump,
  model_validate, model_validate_json, Field, default_factory, validators,
  computed_field), modern type hints, and how schemas serialize for cache
  / wire / DB. Use this skill whenever creating a new schema, deciding
  which folder to place it in, validating input, serializing to cache,
  adding computed properties, or migrating a v1 schema to v2 idioms.
  Triggers on: "create schema", "novo schema", "Pydantic", "BaseModel",
  "model_dump", "model_dump_json", "model_validate", "model_validate_json",
  "Field", "default_factory", "validator", "field_validator",
  "computed_field", "schema HTTP", "domain schema", "webhook schema",
  "request schema", "response schema", "Pydantic v2", "from_attributes".
---

# Pydantic Schemas — zoppy-whatsapp-commerce

The project is on **Pydantic v2** — use only v2 idioms. There is no v1
fallback shimming: `model_dump`, `model_validate`, `Field`, with the new
type hints (`str | None`, `list[T]`).

## The three locations and how to choose

| Location | Used by | What lives here |
|---|---|---|
| `src/api/schemas/` | HTTP layer (`api/endpoints/`) | Request/response DTOs that match the REST contract for chat, knowledge, metrics, playground. Re-shape data for clients; may hide internal fields. |
| `src/domain/<feature>/schemas.py` | Application services + repositories + AI layer | Domain truth — the canonical shape of a feature's data as the system thinks of it. Cached, persisted, passed across layers. |
| `src/domain/<feature>/webhook_schemas.py` | Webhook handlers (`api/webhooks/handlers/`) + repositories | The contract of incoming webhook payloads from upstream platforms (company-sync, agent_config-updated, integration-synced). |

If the same field appears in two of these folders, that's intentional.
The HTTP shape may differ from the domain shape; the webhook shape is
what the upstream sends, which may differ from both.

> Webhook payloads live under `domain/<feature>/` (not `api/`) because
> they are pure DTOs without HTTP semantics — they are the contract a
> Repository understands when persisting a sync. See issue #59 for the
> rationale.

## Decision tree

```
Is it the body / query / response of an HTTP endpoint exposed to clients?
└── yes → src/api/schemas/{request,response,playground}.py

Is it the payload an upstream platform pushes via /webhooks/*?
└── yes → src/domain/<feature>/webhook_schemas.py

Otherwise it's domain truth (cached, persisted, returned by services):
└──       src/domain/<feature>/schemas.py
```

## Domain schema — the canonical reference

`src/domain/company/schemas.py`:

```python
from pydantic import BaseModel, Field


class CompanyContext(BaseModel):
    brand_tone: str | None = None
    brand_name: str | None = None
    brand_description: str | None = None
    target_audience: str | None = None
    segment_statistics: dict | None = None


class IntegrationConfig(BaseModel):
    key: str | None = None
    secret: str | None = None
    url: str | None = None
    admin: str | None = None
    name: str | None = None


class CompanyConfig(BaseModel):
    company_id: str
    company_name: str
    provider: str | None = None
    partners_token: str | None = None

    context: CompanyContext
    integrations: IntegrationConfig = Field(default_factory=IntegrationConfig)

    @property
    def brand_tone(self) -> str | None:
        return self.context.brand_tone

    @property
    def integration_url(self) -> str | None:
        return self.integrations.url
```

Anatomy:

1. **Inherits `BaseModel`.** No `BaseSettings` here — that's only for
   `infra/config.py`.
2. **Modern type hints.** `str | None` (not `Optional[str]`),
   `list[T]` (not `List[T]`), `dict` (not `Dict`). The `code-conventions`
   skill has the full list.
3. **Composition.** Aggregates split into smaller schemas
   (`CompanyConfig` aggregates `CompanyContext` + `IntegrationConfig`).
4. **`Field(default_factory=...)`** for mutable defaults — never
   `= []` or `= {}` directly.
5. **`@property` for derived values** — read-only convenience accessors
   that don't change serialization. For computed values that should
   appear in `model_dump()`, use `@computed_field`.

## Webhook schema

`src/domain/company/webhook_schemas.py`:

```python
class CompanyData(BaseModel):
    id: str
    name: str
    provider: str
    partners_token: str | None = None


class CompanyAttributesData(BaseModel):
    brand_name: str | None = None
    brand_tone: str | None = None
    ...


class AgentConfigData(BaseModel):
    agent_name: str = Field(...)
    phone_number: str | None = Field(default=None)
    custom_prompt: str | None = Field(None)
    session_ttl_minutes: int = Field(default=5)
    handoff_cooldown_minutes: int | None = Field(default=None)
    enabled_features: list[str] = Field(default_factory=lambda: ["catalog_search"])
```

The naming convention is `<Entity>Data` for the data part, and
`<Event>Payload` for the full webhook envelope:

```python
class CompanySyncedPayload(BaseModel):
    company_id: str
    company: CompanyData
    attributes: CompanyAttributesData
```

Cross-feature webhook references are allowed inside `domain/`:
`agent_config/webhook_schemas.py` imports `AgentConfigData` from
`company/webhook_schemas.py` because the upstream company webhook
embeds agent config data. This is a real business relationship — see
the `architecture` skill for the rule.

## API HTTP schema

`src/api/schemas/request.py`:

```python
from pydantic import BaseModel, Field

from src.domain.message.schemas import MessageInput


class ChatRequest(BaseModel):
    company_id: str
    customer_phone: str
    business_phone: str
    messages: list[MessageInput] = Field(..., min_length=1)
    broadcast_context: str | None = Field(None, max_length=2000)
```

`src/api/schemas/response.py`:

```python
class ChatResponse(BaseModel):
    messages: list[ResponseMessage] = Field(
        ..., description="Messages to send sequentially"
    )
    agent_config_id: str
    transfer_to_human: bool = False
    handoff: HandoffInfo | None = None
    usage: TokenUsage | None = None
    in_handoff_cooldown: bool = False
```

API schemas may **import** domain schemas (`MessageInput`, `HandoffInfo`)
to avoid duplicating the shape. They must **never** be imported in the
opposite direction — `domain/` doesn't know `api/` exists.

The `description=` and length/format constraints (`min_length=`,
`max_length=`, `pattern=`) feed both Pydantic validation and the
auto-generated OpenAPI / Swagger docs. Use them.

## Pydantic v2 idioms

### Construction & validation

```python
# From a dict
config = CompanyConfig.model_validate(payload_dict)

# From a JSON string (e.g. cache read)
config = CompanyConfig.model_validate_json(cached_string)

# From an ORM row (when columns map 1:1)
config = CompanyConfig.model_validate(orm_row, from_attributes=True)
```

`model_validate` runs validators. Don't bypass it via `__init__` for
inputs from the wire / cache.

### Serialization

```python
config.model_dump()                        # dict
config.model_dump(exclude={"created_at"})  # drop fields
config.model_dump(exclude_none=True)       # omit None values

config.model_dump_json()                   # str
config.model_dump_json(indent=2)           # pretty
```

`exclude_none=True` is useful for HTTP responses where omitted fields
should be missing rather than `null`. For cache writes we generally
keep all fields so the round-trip is symmetric.

### `Field(...)`

```python
class Foo(BaseModel):
    name: str = Field(..., description="Required name")           # required, with metadata
    count: int = Field(default=0, ge=0)                            # bounded
    tags: list[str] = Field(default_factory=list)                  # mutable default
    profile: dict = Field(default_factory=lambda: {"v": 1})        # complex default
```

Constraints: `min_length`, `max_length`, `min_items`, `max_items`,
`ge`, `le`, `gt`, `lt`, `pattern`, `multiple_of`. Use them on
**request schemas** especially — input validation is cheap at the door.

### Validators

For business rules that don't fit constraints:

```python
from pydantic import field_validator

class Foo(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def must_be_known(cls, v: str) -> str:
        if v not in {"PENDING", "PROCESSING", "ACTIVE", "FAILED"}:
            raise ValueError(f"unknown status: {v}")
        return v
```

For cross-field validation use `@model_validator(mode="after")`.

### `@computed_field`

When you want a derived value to appear in `model_dump()` (clients see
it), use `@computed_field` instead of plain `@property`:

```python
from pydantic import computed_field

class Order(BaseModel):
    items: list[Item]

    @computed_field
    @property
    def total(self) -> Decimal:
        return sum(i.price for i in self.items)
```

## Where each shape ends up

| Schema | Goes through |
|---|---|
| API request | Endpoint handler → Application Service input |
| Domain schema | Application Service ↔ Repository ↔ cache (Valkey) |
| Webhook schema | Webhook handler → Repository |
| API response | Application Service output → Endpoint handler returns it |

The repository's `_to_schema(row)` mapper (see `repository-async` skill)
is the seam between ORM rows and Pydantic. Once you have a Pydantic
instance, every layer above repository speaks Pydantic only.

## Caching

Domain schemas are cached via Valkey. The pattern (see
`multi-tenant-context` skill) is:

```python
# Write to cache
await cache_client.set(key, config.model_dump_json(), settings.company_cache_ttl)

# Read from cache
cached = await cache_client.get(key)
if cached:
    return CompanyConfig.model_validate_json(cached)
```

`model_dump_json()` is the only acceptable cache serialization. Never
pickle Pydantic models — version drift breaks pickle in painful ways.

## When to use Enum

Use `enum.Enum` (or `enum.StrEnum` on Python 3.11+) for closed sets
that the schema reads / writes:

```python
from enum import StrEnum

class DocumentStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"

class IngestStatusResponse(BaseModel):
    id: UUID
    status: DocumentStatus
    ...
```

Pydantic serializes enums to their `.value` by default. Keep the enum
in the same `schemas.py` (or `model.py` if it's also used by the ORM —
`KnowledgeDocument` does that).

## Testing schemas

Schema tests live in:

```
tests/unit/domain/schemas/test_<feature>.py
tests/unit/api/schemas/test_<feature>.py   (if you add HTTP-shape tests)
```

Cover:

- Successful construction with happy-path data
- Validation errors for missing required fields and out-of-bounds values
- Round-trip: `model_validate(model_dump())` returns equivalent instance
- For computed fields / properties: derived value matches expectation
- For schemas with validators: each rule has a positive and negative case

## Gotchas / anti-patterns

- **Never put a domain schema in `src/api/schemas/`.** The domain
  doesn't depend on the wire format.
- **Never put an HTTP-only field in `domain/<feature>/schemas.py`.**
  If clients see it but services don't care, it's API-only.
- **Don't use `Optional[str]` / `Union[A, B]` / `List[T]` / `Dict[K, V]`.**
  Use `str | None`, `A | B`, `list[T]`, `dict[K, V]`. Ruff's `UP` rules
  flag this.
- **Don't default mutable values inline** (`= []`, `= {}`). Always
  `default_factory=...`.
- **Don't use v1 `parse_obj` / `dict()` / `json()`.** Those are gone
  in v2.
- **Don't bypass validators by constructing via `__init__` with raw
  values from the wire.** Always go through `model_validate(...)`.
- **Don't return ORM instances from a service** — see `repository-async`
  skill. The schema mapping must happen at the repository.
- **Don't import from `src/api/` inside `src/domain/`.** Layer rule.

## Pre-PR checklist

- [ ] New schema is in the correct folder (`api/schemas/`,
      `domain/<feature>/schemas.py`, or
      `domain/<feature>/webhook_schemas.py`)
- [ ] Class extends `BaseModel`
- [ ] Type hints are modern (`str | None`, `list[T]`, etc.)
- [ ] Mutable defaults use `Field(default_factory=...)`
- [ ] Required fields use `Field(...)` with `description=` and
      length/format constraints when applicable
- [ ] Validators (`@field_validator`, `@model_validator`) for business
      rules that don't fit constraints
- [ ] No v1 idioms (`parse_obj`, `.dict()`, `.json()`)
- [ ] If used in cache: `model_dump_json` / `model_validate_json` round
      trip exercised in a test
- [ ] Tests in `tests/unit/domain/schemas/test_<feature>.py` cover happy
      path + each validation rule
- [ ] `uv run pytest tests/unit/domain/schemas/ -q` is green
