---
name: architecture
description: >
    How to navigate and extend the layered architecture of zoppy-whatsapp-commerce
    (Python / FastAPI / async SQLAlchemy / LangGraph). Use this skill whenever
    creating a new feature, deciding where to put code, asking who can import
    whom, designing a new endpoint or service, or understanding multi-tenant
    scoping. Triggers on: "create new feature", "nova feature", "novo módulo",
    "nova camada", "where does this go", "onde colocar", "qual camada", "which
    layer", "layered architecture", "arquitetura em camadas", "application vs
    domain", "ApplicationService", "domain helper", "cross_cutting", "feature
    module", "bounded context", "camadas".
---

# Architecture — zoppy-whatsapp-commerce

The codebase is organized **per feature**, not per type. Both `application/`
and `domain/` mirror the same feature names, so a feature ends up looking
like a vertical slice across layers.

## Layer overview

```
src/
├── main.py            # FastAPI app, lifespan startup/shutdown
├── api/               # Presentation: routes, HTTP request/response schemas, webhooks
├── application/       # Use cases per feature: <feature>/<feature>_service.py
├── domain/            # Data only, per feature: <feature>/{model,repository,schemas}.py
├── ai/                # LangGraph agents, tools, orchestrator, parsers
├── infra/             # DB, Valkey, config, vectorstore, checkpointer, observability
├── utils/             # Stateless leaves: logger, context binding, phone normalization
└── worker/            # Celery tasks for background processing
```

`api/` is the equivalent of NestJS Controllers (thin facade), `application/`
is the equivalent of NestJS Application Services (use cases / orchestration),
and `domain/` is data-only (models, repositories, schemas).

## Per-feature layout

A typical feature ends up looking like this:

```
src/
├── application/company/
│   └── company_service.py        # CompanyService — use case orchestration
└── domain/
    ├── shared/
    │   └── base.py               # SQLAlchemy Base + TimestampMixin (only shared)
    └── company/
        ├── model.py              # Company (SQLAlchemy ORM)
        ├── repository.py         # CompanyRepository (async, scoped by company_id)
        ├── schemas.py            # CompanyConfig, CompanyContext, IntegrationConfig
        └── webhook_schemas.py    # CompanyData, CompanyActivatedPayload, …
```

Real features today: `agent_config`, `company`, `conversation_metric`,
`handoff`, `integration`, `knowledge`, `message`, plus `shared/`. Not every
feature has every file type — `message/` is schemas-only,
`conversation_metric/` has no schemas at all. Create only what the feature
needs.

## Layer dependency rules

A layer may only import from layers below it. Violations are bugs.

| Layer                            | May import from                                                                                                                                                                           |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api/`                           | `application/`, `domain/<feature>/`, `utils/`, `cross_cutting/`                                                                                                                           |
| `application/<feature>/`         | `application/<feature>/helpers/`, `domain/<any>/`, `infra/`, `utils/`, `cross_cutting/helpers/`, `worker/tasks/` (only to enqueue Celery jobs). **Never `application/<other_feature>/`.** |
| `application/<feature>/helpers/` | `domain/`, `infra/`, `utils/`, `cross_cutting/helpers/`                                                                                                                                   |
| `ai/`                            | `application/`, `domain/<feature>/`, `infra/`, `utils/`, `cross_cutting/`. **Never `api/`.**                                                                                              |
| `worker/`                        | `application/`, `domain/<feature>/`, `infra/`, `utils/`, `cross_cutting/`                                                                                                                 |
| `domain/<feature>/`              | `domain/shared/`, `domain/<other_feature>/` (only for legitimate business relationships — audit), `infra/` (DB session only), `utils/`                                                    |
| `domain/shared/`                 | Stdlib + SQLAlchemy only                                                                                                                                                                  |
| `cross_cutting/helpers/`         | `domain/`, `utils/`. Stateless, no I/O                                                                                                                                                    |
| `infra/`, `utils/`               | Strict leaves — no `from src.*` imports                                                                                                                                                   |

The cross-layer rule that matters most in practice:
**Application Service NEVER injects another Application Service.** This is
the same rule as zoppy-api. If two services need shared logic, see the
helper escape path below.

## Helpers — `utils/` × feature helpers × `cross_cutting/helpers/`

Helpers do **not** live in `domain/`. They live in one of three places,
chosen by reach and nature:

| Location                                                                     | For                                                                                                                                                                                     | Avoid                                                                                      |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `src/utils/`                                                                 | Cross-cutting stateless functions with **no business concept**: phone normalization, generic parsers, logger, `request_context`, constants. Depends only on stdlib / Pydantic / typing. | Anything that mentions Company, AgentConfig, Handoff, Knowledge, Conversation.             |
| `src/application/<feature>/helpers/<feature>.helper.py`                      | Logic shared between methods of the same feature's service or its sub-components. Lives next to the service that uses it.                                                               | Being called by another feature (promote to `cross_cutting/`).                             |
| `src/cross_cutting/helpers/<topic>.helper.py` _(created on first real need)_ | Business-concept logic shared by **2+ features** that doesn't fit `utils/`. Stateless, no I/O.                                                                                          | Single-feature use (move to feature helpers); pure technical utilities (move to `utils/`). |

`cross_cutting/` and `<feature>/helpers/` only get created on the first real
extraction — never empty scaffolding.

## Creating a new feature — checklist

1. **Pick a feature name** in snake_case. Use the same name in both
   `application/` and `domain/`.
2. **Domain side** (data only):
    ```
    src/domain/<feature>/
    ├── __init__.py            # empty
    ├── model.py               # SQLAlchemy ORM, inherit Base + TimestampMixin
    ├── repository.py          # async repository, scope by company_id
    ├── schemas.py             # Pydantic domain schemas (if needed)
    └── webhook_schemas.py     # Pydantic webhook payload schemas (if applicable)
    ```
    Add the model to `src/domain/__init__.py` so `Base.metadata` knows about it
    (integration tests rely on this for `Base.metadata.create_all`).
3. **Application side** (use case):
    ```
    src/application/<feature>/
    ├── __init__.py            # empty
    └── <feature>_service.py   # the use case
    ```
    The service can inject Repositories, Infra clients, helpers, but **never**
    another `<other>_service`.
4. **API side** (only if exposed via HTTP):
    - Endpoint in `src/api/endpoints/<feature>.py`
    - HTTP request/response schemas in `src/api/schemas/`
    - Register the new router in `src/api/router.py`
5. **Tests** mirror `src/`: `tests/unit/application/<feature>/test_<feature>_service.py`,
   `tests/integration/domain/repositories/test_<feature>.py`. See the `testing`
   skill for the conventions.

## Examples in the project

-   A feature with all four file types: `src/domain/company/` (`model.py`,
    `repository.py`, `schemas.py`, `webhook_schemas.py`) paired with
    `src/application/company/company_service.py`.
-   A feature with no model or repository, only schemas:
    `src/domain/message/schemas.py` (used by
    `src/application/message/message_preprocessor.py`).
-   A feature with no schemas at all:
    `src/domain/conversation_metric/{model,repository}.py`.
-   A feature with two service files because the domain naturally splits:
    `src/application/handoff/handoff_cooldown.py` (Valkey-backed module of
    free functions, not a class) and `handoff_event_service.py` (the class).

## Gotchas / anti-patterns

-   **Never recreate `domain/services/`, `domain/models/`, `domain/repositories/`
    or `domain/schemas/` as per-type folders.** Issues #58 and #59 removed
    them on purpose. New code goes per feature.
-   **Never inject one Application Service into another.** If you find yourself
    about to write `def __init__(self, other: OtherService)`, stop — extract
    a helper instead (see the helpers section).
-   **Never import from `api/` inside `ai/`, `application/`, `domain/` or
    `worker/`.** `api/` is a leaf of the dependency graph.
-   **Never put helpers under `domain/<feature>/`.** Domain is data only.
-   **`utils/` is a strict leaf.** No `from src.*` of any kind. If you need to
    reference a domain or application symbol, the helper belongs in
    `application/<feature>/helpers/` or `cross_cutting/helpers/`.
-   **All repository/service methods are `async`** (SQLAlchemy uses `asyncpg`).
-   **Every DB query MUST be scoped by `company_id`.** Multi-tenant leaks are
    the worst class of bug here. See the `multi-tenant-context` skill.

## Pre-PR checklist

-   [ ] New code follows per-feature layout (`<feature>/<file_type>.py`)
-   [ ] Application service does not inject another application service
-   [ ] No imports from `api/` inside `ai/`, `application/`, `domain/`, `worker/`
-   [ ] No imports from any `src.*` inside `utils/`
-   [ ] If a model was added, it's imported in `src/domain/__init__.py`
-   [ ] Tests live under `tests/unit/<layer>/<feature>/` mirroring `src/`
-   [ ] `uv run pytest tests/unit/ tests/integration/` is green
-   [ ] `CLAUDE.md` Architecture / Key Files sections still match reality if
        a new layer convention emerged
