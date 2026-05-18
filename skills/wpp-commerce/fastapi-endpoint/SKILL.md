---
name: fastapi-endpoint
description: >
    How to create HTTP endpoints in zoppy-whatsapp-commerce (FastAPI). Covers
    endpoint placement under src/api/endpoints/, the thin-facade rule (no
    business logic in handlers), Depends() dependency injection, response_model,
    HTTPException mapping from domain errors, file uploads, async handlers,
    registering new routers in src/api/router.py, and webhook handlers under
    src/api/webhooks/handlers/. Use this skill whenever exposing a new use
    case via REST API, adding an endpoint to an existing controller, deciding
    between Depends() and direct instantiation, mapping a service exception
    to an HTTP status, or registering a new webhook handler. Triggers on:
    "create endpoint", "novo endpoint", "novo controller", "FastAPI", "rota",
    "route", "APIRouter", "Depends", "response_model", "HTTPException",
    "status_code", "register router", "registrar router", "include_router",
    "webhook handler", "novo webhook", "Query()", "File()", "UploadFile",
    "request body", "feature flag check", "controller layer", "thin facade".
---

# FastAPI Endpoints — zoppy-whatsapp-commerce

The `src/api/` layer plays the role of Controllers in the NestJS sense:
thin facades that receive HTTP, validate input through Pydantic, delegate
to an Application Service, and shape the response. **Zero business logic
lives in `api/`.** If you find yourself writing a `for` loop or an
`if status == ...` chain in an endpoint, you're in the wrong layer —
push it down into `application/<feature>/<feature>_service.py`.

## Layout

```
src/api/
├── dependencies.py              # Depends() factories, e.g. get_company_service
├── router.py                    # Top-level APIRouter that includes everything
├── endpoints/
│   ├── chat.py                  # POST /chat (canonical thin example)
│   ├── health.py                # GET /health
│   ├── knowledge.py             # KB ingest + crawl + status (file upload + Query)
│   ├── metrics.py               # GET /playground/metrics/{company_id}
│   └── playground.py            # admin / operational endpoints
├── schemas/
│   ├── request.py               # ChatRequest
│   ├── response.py               # ChatResponse, ResponseMessage, TokenUsage
│   └── playground.py            # all playground schemas
└── webhooks/
    ├── router.py                # webhooks APIRouter
    └── handlers/
        ├── company/{activated,synced,deactivated}.py
        ├── agent_config/{updated,deactivated}.py
        └── integration/synced.py
```

## The canonical thin endpoint

`src/api/endpoints/chat.py` is the cleanest reference. It does only what
a controller is supposed to do:

```python
from fastapi import APIRouter, Depends, HTTPException

from src.ai.orchestrator import run_conversation
from src.api.dependencies import get_company_service
from src.api.schemas.request import ChatRequest
from src.api.schemas.response import ChatResponse
from src.application.company.company_service import CompanyService
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    company_service: CompanyService = Depends(get_company_service),
):
    company = await company_service.get_by_id(request.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    logger.info(
        "chat.request",
        company_id=request.company_id,
        customer_phone=request.customer_phone,
        message_count=len(request.messages),
    )

    result = await run_conversation(...)
    return ChatResponse(messages=result["messages"], ...)
```

Anatomy:

1. **`router = APIRouter()`** at module level.
2. **`@router.<method>(<path>, response_model=<Schema>)`** on every handler.
3. **`async def`** every handler (we touch async I/O).
4. **Pydantic Request schema** as the body / query parameter (auto-validated
   by FastAPI).
5. **`Depends(get_<service>)`** for services that should be reused across
   endpoints.
6. **One structured log line** describing the request — the orchestrator
   binds `company_id`, `customer_phone`, `thread_id` to context for
   subsequent calls (see `multi-tenant-context` skill).
7. **Delegate** to the Application Service / orchestrator.
8. **Shape the response** through the Pydantic Response schema.
9. **Map domain errors to HTTP status** with `HTTPException(...)`.

## Dependency injection — `Depends()` vs direct instantiation

Two patterns coexist today; the team is converging on `Depends()`. Use
the rule below for new code.

| When                                                 | Use                              | Why                                                                                 |
| ---------------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------- |
| Service is stateless / lightweight (most cases)      | `Depends(get_<service>)`         | Composable, mockable in tests via `app.dependency_overrides`, follows FastAPI idiom |
| One-off small endpoint where DI ceremony is overhead | `service = SomeService()` inline | Fine — but if you'd reuse it, lift to `dependencies.py`                             |

The factory lives in `src/api/dependencies.py`:

```python
from functools import lru_cache
from src.application.company.company_service import CompanyService

@lru_cache
def get_company_service() -> CompanyService:
    return CompanyService()
```

`@lru_cache` makes the factory return a singleton — fine because services
are stateless. If the service holds per-request state (rare), drop the
cache.

When you need a DB session inside a webhook handler, use `Depends(get_db)`
from `src.infra.database`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.infra.database import get_db

async def handle(payload: SomePayload, db: AsyncSession = Depends(get_db)):
    repo = SomeRepository(db)
    ...
```

## Path / Query / Body parameters

```python
from uuid import UUID
from fastapi import Query, Path, Body

# Path parameter (typed)
@router.get("/status/{document_id}", response_model=IngestStatusResponse)
async def get_document_status(document_id: UUID, ...):
    ...

# Query string
@router.get("/documents", response_model=list[IngestStatusResponse])
async def list_documents(
    company_id: str = Query(..., description="Company ID"),
    status: str | None = Query(None, description="Filter by status"),
):
    ...

# Request body — always a Pydantic schema from src/api/schemas/
@router.post("/crawl", response_model=CrawlResponse, status_code=202)
async def crawl_url(body: CrawlRequest, company_id: str = Query(...)):
    ...
```

`UUID`, `int`, `bool`, `Literal[...]` types are parsed by FastAPI
automatically. Add `description=` for OpenAPI/Swagger clarity.

## File upload

```python
from fastapi import File, UploadFile

@router.post("/ingest", response_model=IngestResponse, status_code=202)
async def ingest_document(
    company_id: str = Query(..., description="Company ID"),
    file: UploadFile = File(..., description="File to ingest (PDF, DOCX, TXT)"),
):
    knowledge_service = KnowledgeService()
    try:
        return await knowledge_service.ingest_document(company_id, file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

Real example: `src/api/endpoints/knowledge.py:23`. Pass `UploadFile`
straight into the service — never read the bytes inside the controller.

## response_model and status codes

Always set `response_model=` on routes that return data. Default status
is 200; override only when semantics demand it:

| Operation                     | Status                                      |
| ----------------------------- | ------------------------------------------- |
| GET (resource found)          | 200 (default)                               |
| POST that creates inline      | 200 or 201                                  |
| POST that enqueues async work | **202** (`status_code=202`)                 |
| DELETE that succeeded         | 204 if empty body, else 200                 |
| Validation failure            | 400                                         |
| Not found                     | 404                                         |
| Forbidden / feature flag off  | 403                                         |
| Internal error                | 500 (let FastAPI handle / structured raise) |

Real `202`s in this codebase: `POST /v1/knowledge/ingest`,
`POST /v1/knowledge/crawl`, `POST /v1/knowledge/refresh/{id}` — all
return immediately and the heavy work runs in a Celery task.

## Mapping domain errors to HTTP

Application services raise `ValueError` for input problems. Catch at the
endpoint and translate:

```python
@router.post("/refresh/{document_id}", response_model=CrawlResponse, status_code=202)
async def refresh_url(document_id: UUID, company_id: str = Query(...)):
    try:
        return await knowledge_service.refresh_url(document_id, company_id)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
```

Rules:

-   **Never raise `HTTPException` from `application/` or `domain/`.** Those
    layers don't know about HTTP. Endpoints translate.
-   **Don't swallow exceptions.** If you can't translate, let it bubble —
    FastAPI returns 500 and the structured logger captures the trace.
-   For idiomatic FastAPI handling, `HTTPException(status_code=..., detail=...)`
    is enough — no custom exception classes for the basics.

## Feature flag checks

Pattern from `src/api/endpoints/knowledge.py`:

```python
async def _check_feature_flag(
    company_id: str,
    flag: str = FEATURE_FLAG,
    label: str = "Knowledge base processing",
) -> None:
    service = AgentConfigService()
    if not await service.has_feature(company_id, flag):
        raise HTTPException(
            status_code=403,
            detail=f"{label} is not enabled for this company",
        )
```

The flag list lives in `src/utils/constants.py` (`FEATURE_KB_PROCESSING`,
`FEATURE_KB_CRAWLER`, `FEATURE_CATALOG_SEARCH`); per-company toggles live
in `agent_config.enabled_features`.

## Registering a new endpoints module

Two-step:

1. Create the file under `src/api/endpoints/<feature>.py` with its own
   `router = APIRouter(prefix="/v1/<feature>", tags=["<feature>"])`.
2. Register in `src/api/router.py`:

```python
from src.api.endpoints import (
    chat,
    health,
    knowledge,
    metrics,
    playground,
)

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(chat.router, tags=["chat"])
router.include_router(playground.router)
router.include_router(knowledge.router)
router.include_router(metrics.router)
router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
```

Order matters when paths could collide; otherwise alphabetize by feature.

## Webhook handlers

Webhooks live in `src/api/webhooks/handlers/<feature>/<event>.py`. Each
file owns one `router = APIRouter()` and one POST handler. The contract:

1. **Persist the change** through the Repository.
2. **Invalidate caches** (Valkey) tied to the entity. See
   `multi-tenant-context` skill.
3. **Return a small JSON ack** with `status` and the entity id.

Real example, `src/api/webhooks/handlers/company/synced.py`:

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
    return {"status": "success", "company_id": payload.company_id, ...}
```

To register the handler, add it to `src/api/webhooks/router.py`:

```python
from src.api.webhooks.handlers.company import activated, deactivated, synced

router.include_router(activated.router, tags=["webhooks:company"])
router.include_router(synced.router, tags=["webhooks:company"])
router.include_router(deactivated.router, tags=["webhooks:company"])
```

The webhook payload schemas are **domain webhook schemas**, not HTTP
schemas: `src/domain/<feature>/webhook_schemas.py`. See the
`pydantic-schema` skill for the rationale.

## Logging

One log line per request, at the entry, with the structured fields
relevant to the operation. The orchestrator (called by `chat`) binds
`company_id`/`customer_phone`/`thread_id` so downstream logs carry the
context automatically. For non-chat endpoints, pass `company_id`
explicitly:

```python
logger.info(
    "knowledge.ingest.requested",
    company_id=company_id,
    filename=file.filename,
    file_size=file.size,
)
```

Event names follow the `code-conventions` skill:
`<area>.<action>` or `<area>.<action>.<state>` in `dot.case`.

## Testing endpoints

See the `testing` skill. Endpoint tests live under
`tests/unit/api/endpoints/test_<feature>.py` (using FastAPI `TestClient`)
and `tests/unit/api/webhooks/handlers/<feature>/test_webhooks.py` for
webhook handlers. Mock services / repositories on the boundary; don't
spin up real Valkey or DB at this layer.

## Gotchas / anti-patterns

-   **No business logic in endpoints.** `for` loops over domain objects,
    `if` chains on enums, conditional cache reads — all push down to
    `application/<feature>/`.
-   **Never instantiate domain classes (Repositories) inside an endpoint
    unless it's a webhook.** Endpoints call services; only webhook handlers
    may inject `Repository` directly because their job is to persist +
    invalidate.
-   **Always set `response_model=`.** Without it, FastAPI returns whatever
    the service emits, OpenAPI loses the contract, and clients break
    silently when the service shape drifts.
-   **Never return ORM models.** Always Pydantic. `_to_schema` mappers
    belong in the Repository (see `repository-async` skill).
-   **Don't reuse `endpoints/<feature>.py` for unrelated routes.** Feature
    drift makes routers hard to maintain. New feature → new file.
-   **Don't create new `Settings` env vars without the `WHATSAPP_COMMERCE_`
    prefix.** See `code-conventions` skill.

## Pre-PR checklist

-   [ ] Endpoint lives in `src/api/endpoints/<feature>.py` (or
        `webhooks/handlers/<feature>/<event>.py`)
-   [ ] `response_model=` set on every route that returns data
-   [ ] Status code matches semantics (202 for enqueued async work)
-   [ ] Pydantic request/response schemas live under `src/api/schemas/`
-   [ ] Feature flag checked when applicable (`_check_feature_flag` pattern)
-   [ ] Domain errors mapped to `HTTPException(...)` — no `ValueError`
        escaping to FastAPI
-   [ ] No business logic in the handler — only validate, delegate, shape
-   [ ] Router registered in `src/api/router.py` (or `webhooks/router.py`)
-   [ ] One structured log line at request entry
-   [ ] Tests in `tests/unit/api/endpoints/test_<feature>.py` cover happy
        path + 4xx error paths
-   [ ] `uv run pytest tests/unit/api/ -q` is green
