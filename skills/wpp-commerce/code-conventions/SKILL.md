---
name: code-conventions
description: >
  Coding conventions for zoppy-whatsapp-commerce (Python 3.13 / FastAPI / async
  SQLAlchemy / structlog). Covers ruff/mypy rules, the uv package manager,
  import order, async/await usage, the WHATSAPP_COMMERCE_ env prefix,
  structured logging with bound context, exception handling, and Pydantic v2
  conventions. Use this skill whenever writing new code, choosing how to log
  something, deciding which exception to raise, configuring a setting, or
  reviewing whether code follows the project's style. Triggers on: "how to log",
  "structlog", "request_context", "ruff", "mypy", "uv", "pyproject.toml",
  "WHATSAPP_COMMERCE_", "settings", "env var", "exception", "raise",
  "Pydantic", "model_dump", "model_validate", "async def", "logging", "logger",
  "convenções", "convention", "estilo", "code style".
---

# Code Conventions — zoppy-whatsapp-commerce

## Tooling

| Tool | Version source | Purpose |
|---|---|---|
| `uv` | system | Package manager + venv resolver |
| `ruff` | dev dep | Lint + format (line-length 88, target py313) |
| `mypy` | dev dep | Type check (`strict=false`, `warn_return_any=true`, ignores missing imports) |
| `pytest` + `pytest-asyncio` | dev dep | Tests (`asyncio_mode=auto`) |

Always invoke through `uv` so the right venv is used:

```bash
uv run ruff check          # lint
uv run ruff check --fix    # auto-fix imports + simple issues
uv run ruff format         # format
uv run mypy src/           # type check (src only — tests/ excluded)
uv run pytest tests/unit/ tests/integration/ -q
```

`make lint`, `make type-check`, `make test`, `make check` (all of them) and
`make format` wrap the same commands.

## Ruff rules in effect

The lint set is in `pyproject.toml`:

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008", "B904"]

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

Practical consequences:

- **Imports** are sorted automatically (`I001`). When you change an import,
  run `uv run ruff check --fix <file>` instead of hand-formatting.
- **`src` is first-party** — internal imports group separately from third-party.
- **`ARG`** flags unused function arguments. In tests with mass `@patch()`
  decorators where mock fixtures must exist on the signature, prefix the unused
  ones with `_` (e.g. `_mock_settings`) instead of suppressing the warning.
- **`UP`** keeps types modern — write `list[int]`, `dict[str, Any]`,
  `str | None` (no `Optional`, no `List`).
- **`B904`** is intentionally ignored: `raise XError(...)` without `from` is OK
  inside `except` blocks. Use `from e` only when the chained context adds value.

## Type hints

- Add type hints on **public** functions/methods (parameters and return type).
- Optional internals: not enforced by `mypy` (`disallow_untyped_defs=false`),
  but encouraged.
- Modern syntax only: `str | None` over `Optional[str]`, `list[T]` over
  `List[T]`. Imports from `typing` shrink to what's still needed
  (`Any`, `TypeVar`, `Callable`, `Literal`, etc.).
- Async functions get hints too: `async def foo(...) -> CompanyConfig | None`.

## `uv` and dependencies

- The lockfile is `uv.lock`. Don't edit by hand.
- `uv add <pkg>` to add runtime deps, `uv add --group dev <pkg>` for dev.
- The Python pin is `>=3.13` and there is a `.python-version` file. Don't
  bump unless the team agrees.

## Async / await

Everything that touches I/O is async — SQLAlchemy uses `asyncpg`, the
HTTP client is `httpx.AsyncClient`, Valkey is async, the FastAPI handlers
are async.

- Repository methods: `async def`.
- Application service methods that call repositories or infra: `async def`.
- Tools (LangGraph) follow the framework's async contract.
- Use `asyncio.to_thread(blocking_call, ...)` to bridge legacy sync APIs
  (e.g. `boto3` S3 client). See
  `src/application/knowledge/knowledge_service.py` for a real example.
- Don't mix `time.sleep` with async code; use `await asyncio.sleep(...)`.

## Configuration & environment variables

All settings live in `src/infra/config.py` as a `pydantic-settings`
`Settings` class loaded from `.env`. Convention:

- **Env vars are prefixed `WHATSAPP_COMMERCE_`**, e.g.
  `WHATSAPP_COMMERCE_DATABASE_URL`, `WHATSAPP_COMMERCE_OPENAI_API_KEY`.
- New setting → add a typed field on `Settings` with a default when safe,
  expose it via `settings.<field>`. Never read `os.environ` directly outside
  `config.py`.
- Feature flags with their human-readable name go in `src/utils/constants.py`
  (e.g. `FEATURE_KB_PROCESSING`, `FEATURE_CATALOG_SEARCH`,
  `AVAILABLE_FEATURES`). The toggle itself is per-company in
  `agent_config.enabled_features`.

## Logging

Use the project's structlog wrapper, never `print` or stdlib `logging`
directly.

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.info(
    "knowledge.ingest.queued",
    document_id=str(doc_id),
    company_id=company_id,
    filename=filename,
    file_type=extension,
)
```

Conventions:

- **Event name** is the first positional arg. Use `dot.case` namespaces
  (`<area>.<action>` or `<area>.<action>.<state>`):
  `knowledge.ingest.queued`, `worker.process_document.completed`,
  `agent_manager.cache_hit`, `shopify_parser.parse_success`.
- **Structured fields** as kwargs. Don't interpolate into the message —
  pass values as named keys so logs are queryable.
- **Severity**:
  - `info` for normal lifecycle events worth keeping
  - `debug` for fine-grained tracing
  - `warning` for recoverable / unexpected-but-not-fatal
  - `error` for failures (always include `error=str(e)` and
    `error_type=type(e).__name__`)
- **Tenant context comes for free.** At request entry the orchestrator calls
  `bind_context(company_id=..., customer_phone=..., thread_id=...)` from
  `src.utils.request_context`. Every subsequent `logger.info(...)` inside the
  same async task automatically carries those fields.
- For helpers that need extra context not yet bound, use
  `get_contextualized_logger(...)` from `src.utils.logger`.

## Exceptions

- Raise `ValueError` for input validation problems inside services
  (e.g. invalid file type in `KnowledgeService.ingest_document`).
- Let domain repositories surface SQLAlchemy errors as-is to the application
  layer.
- HTTP-facing endpoints translate domain failures to `HTTPException` (with
  the right status code) inside `api/endpoints/`. Don't raise `HTTPException`
  from inside `application/` or `domain/`.
- Never swallow exceptions silently. Either re-raise (often `from e` to
  preserve chain) or `logger.error(...)` with structured context, then
  decide what to return.

Pattern in Celery tasks (see `src/worker/tasks/document_processing.py`):

```python
try:
    ...
except ValueError as e:
    logger.error("worker.process_document.validation_error", error=str(e))
    _update_document_status(doc_uuid, DocumentStatus.FAILED, error_message=str(e))
    return {...}
except Exception as e:
    logger.error(
        "worker.process_document.error",
        error=str(e),
        error_type=type(e).__name__,
    )
    if self.request.retries < self.max_retries:
        raise self.retry(exc=e)
    ...
```

## Pydantic v2

- Use `BaseModel` (not v1 `BaseSettings` for non-config models).
- Validation: `Model.model_validate(data)`, NOT v1 `parse_obj`.
- Serialization: `Model.model_dump()` and `Model.model_dump_json()`.
- Field with default factory:
  `field: list[str] = Field(default_factory=list)`.
- Optional with default: `name: str | None = None`.
- Domain schemas live in `src/domain/<feature>/schemas.py`. HTTP request /
  response schemas live in `src/api/schemas/`. Webhook payload schemas live
  in `src/domain/<feature>/webhook_schemas.py`. See the `architecture` skill
  for which goes where.

## Imports

- Order: stdlib → third-party → first-party (`src.*`). Ruff/isort enforces.
- One symbol per line is fine — readability over compactness.
- Prefer absolute imports: `from src.application.company.company_service import CompanyService`.
  No relative imports inside `src/`.
- Re-exports through `__init__.py` are kept minimal; usually empty. Don't add
  re-exports just for shorthand.

## Naming

- Modules: `snake_case` (`agent_config_service.py`, `message_preprocessor.py`).
- Classes: `PascalCase` (`CompanyService`, `KnowledgeDocument`).
- Functions / methods / variables: `snake_case`.
- Constants: `SCREAMING_SNAKE_CASE`
  (`FEATURE_KB_PROCESSING`, `MODEL_PRICING`, `CACHE_PREFIX`).
- Async vs sync: don't suffix names with `_async`. The `async def` keyword
  already says it.

## Method complexity

Hard cap is taste, not lint, but use the same rule of thumb as zoppy-api:

- Keep public methods focused on one verb. If a method body grows past
  ~40 lines or 4-5 levels of nesting, extract private helpers.
- Private helpers go on the same class with `_underscore_prefix`.
- If extraction would require knowing about another feature, that's the
  signal to promote the helper to `application/<feature>/helpers/` or
  `cross_cutting/helpers/` — see the `architecture` skill.

## Pre-PR checklist

- [ ] `uv run ruff check src/ tests/` clean (or only pre-existing baseline)
- [ ] `uv run mypy src/` clean (or only pre-existing baseline)
- [ ] `uv run pytest tests/unit/ tests/integration/` green
- [ ] No `print()` calls, no stdlib `logging` directly
- [ ] No raw `os.environ` reads outside `src/infra/config.py`
- [ ] Public functions/methods have type hints
- [ ] Async functions are `async def` and awaited correctly
- [ ] No new env var without prefix `WHATSAPP_COMMERCE_`
- [ ] No `from typing import List/Dict/Optional/Tuple` — use `list/dict/| None/tuple`
