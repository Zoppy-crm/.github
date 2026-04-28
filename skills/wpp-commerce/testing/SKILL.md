---
name: testing
description: >
  How to write and run tests in zoppy-whatsapp-commerce (Python / pytest /
  pytest-asyncio / SQLite in-memory). Anchors to the in-project tests/TESTING.md
  for the long-form rules and adds: TDD red-green-refactor for async code,
  what's already covered vs the gaps, how to test LangGraph agents and tools,
  fixtures, mocking on the boundary, when to write unit vs integration vs slow
  tests. Use this skill whenever writing a new test, deciding what to mock,
  setting up fixtures, structuring describe/test classes, fixing a flaky test,
  testing an agent, testing a Celery task, or auditing a test for quality.
  Triggers on: "write a test", "add tests", "test this service", "test this
  agent", "test this tool", "como testar", "criar teste", "test conventions",
  "fixture", "conftest", "TestUtils", "in-memory database", "TDD",
  "red-green-refactor", "minimize mocks", "AsyncMock", "patch", "pytest",
  "@pytest.mark.unit", "@pytest.mark.integration", "test LangGraph",
  "mocking external services".
---

# Testing — zoppy-whatsapp-commerce

The long-form rules live in `tests/TESTING.md` (385 lines). This skill is
the entry point: it tells you what's there, anchors to the most-used parts,
and fills three gaps the file doesn't cover yet — TDD loop for async,
LangGraph agent/tool tests, and the working baseline.

## Where the rules already live

Always read `tests/TESTING.md` first when in doubt. It covers:

1. Directory structure (mirrors `src/`)
2. File and class naming
3. Internal file organization
4. Fixture hierarchy (global / layer / local)
5. Mocking on the boundary
6. Async tests
7. Parametrized tests
8. Markers (`unit`, `integration`, `slow`, `eval`)
9. Assertions (use bare `assert`, never `assertEqual`)
10. Docstrings (Portuguese for descriptions, English for symbols)
11. What to test vs what not to test
12. Pre-PR checklist
13. Useful commands

When a topic below conflicts with `tests/TESTING.md`, the file wins — open
a PR to update the file first.

## Layout — tests mirror src/

```
tests/
├── conftest.py
├── TESTING.md
├── fixtures/                            # JSON fixtures (e.g. sample_mcp_response.json)
├── integration/                         # SQLite in-memory + async session
│   ├── conftest.py                      # sqlite_engine + db_session fixtures
│   └── domain/repositories/test_<feature>.py
└── unit/                                # pure unit tests with mocks at the boundary
    ├── ai/
    │   ├── parsers/test_agent_response.py
    │   ├── agents/sales/test_*.py
    │   └── agents/subagents/<sub>/test_*.py
    ├── api/
    │   ├── endpoints/test_*.py
    │   └── webhooks/handlers/<feature>/test_webhooks.py
    ├── application/
    │   └── <feature>/test_<feature>_service.py
    ├── domain/schemas/test_<feature>.py
    ├── infra/test_*.py
    ├── utils/test_*.py
    └── worker/tasks/test_*.py
```

For each new file in `src/<layer>/<path>.py` add the matching test in
`tests/unit/<layer>/<path>` (or `tests/integration/<layer>/...`). New layout
introduced by issues #58 and #59 is already in place — `application/` and
`domain/` mirror per-feature.

## Running

```bash
make test                  # full unit + integration suite (gate)
make test-unit             # only @pytest.mark.unit
make test-integration      # only @pytest.mark.integration
make test-cov              # with coverage report (terminal + HTML + XML)
make test-watch            # re-run last failed on save

# Single file / function
uv run pytest tests/unit/application/company/test_company_service.py -v
uv run pytest tests/unit/application/company/test_company_service.py::TestGetById -v
```

Current baseline (post issues #58/#59): **460 passing**, 0 failing.

## Markers — when to use which

| Marker | When | Where it runs |
|---|---|---|
| `@pytest.mark.unit` | Pure logic tested with mocks at the I/O boundary (cache, DB, HTTP, S3). No external services. | `tests/unit/` |
| `@pytest.mark.integration` | Hits a real SQLite in-memory DB (via `sqlite_engine`/`db_session` fixtures). Other I/O is mocked. | `tests/integration/` |
| `@pytest.mark.slow` | Takes >2s. Excluded by default in dev (`pytest -m "not slow"`). | Any |
| `@pytest.mark.eval` | Langfuse evaluation experiments (separate flow, not in regular `make test`). | `tests/langfuse_eval/` (when present) |

Every unit test must have `@pytest.mark.unit`. Every integration test must
have `@pytest.mark.integration`. The marker can be on the class or on the
function — both are accepted.

## Async tests

`pyproject.toml` sets `asyncio_mode = "auto"` and
`asyncio_default_fixture_loop_scope = "function"`, so `async def` test
functions and async fixtures Just Work. Keep the explicit
`@pytest.mark.asyncio` decorator on test methods anyway — it's the project
convention and makes intent explicit:

```python
@pytest.mark.unit
class TestGetById:
    @pytest.mark.asyncio
    async def test_get_by_id_cache_hit_returns_config(self, service, sample_config):
        with patch("src.application.company.company_service.cache_client") as mock_cache:
            mock_cache.get = AsyncMock(return_value=sample_config.model_dump_json())
            result = await service.get_by_id("test-company")
            assert result is not None
            mock_cache.get.assert_called_once_with("company:test-company")
```

## TDD red-green-refactor for async code

The cycle is the same as anywhere — red, green, refactor — but a few
practicalities matter for this project:

1. **Red.** Write the failing test first. Pick the layer:
   - Pure logic (parsers, calculators, validators) → `tests/unit/<layer>/`.
   - Service that touches infra → `tests/unit/application/<feature>/`,
     mock the boundary (cache, DB, S3, HTTP) with `AsyncMock`.
   - Repository / data access → `tests/integration/domain/repositories/`,
     hit the SQLite in-memory engine.
2. **Green.** Write the minimum code in `src/` to make the test pass. Ruff
   rules enforce import order — running `uv run ruff check --fix` before
   the next iteration keeps the diff clean.
3. **Refactor.** Pull helpers out as the body grows. The escape paths for
   shared logic are the same as the `architecture` skill describes:
   `application/<feature>/helpers/` for same-feature, `cross_cutting/helpers/`
   for cross-feature, `utils/` for stateless purely-technical.

Watch out for:

- **Don't use `time.sleep` in async tests.** Use
  `await asyncio.sleep(...)` or freeze time with `jest`-style
  `freezegun` if needed.
- **Don't assert on error message strings** (locale-fragile, easy to drift).
  Assert on exception class instead: `with pytest.raises(ValueError, match="invalid")`.
- **Don't rely on test order.** Each test must set up and tear down its own
  state.

## Fixtures — hierarchy and conventions

| Scope | Lives in | Used by |
|---|---|---|
| Global | `tests/conftest.py` | Any test |
| Layer | `tests/<layer>/conftest.py` (e.g. `tests/integration/conftest.py`) | All tests in that subtree |
| Local | inside the `test_*.py` file itself | Only that file |

Project conventions:

- Fixture name = what it returns. `service` for the unit under test,
  `sample_company_config` for a Pydantic instance, `sample_company_dict`
  for a raw dict.
- Every fixture has a Portuguese docstring explaining what it returns.
- Integration fixtures live in `tests/integration/conftest.py`:
  `sqlite_engine` (SQLite in-memory async engine, schema created from
  `Base.metadata`), `db_session` (an `AsyncSession` ready to use).

```python
@pytest.fixture
def service():
    """Instância do CompanyService para testes."""
    return CompanyService()

@pytest.fixture
def sample_company_dict():
    """Dicionário representando uma empresa no cache/banco."""
    return {"company_id": "test-company", "company_name": "Test", ...}
```

## Mocking — on the boundary, not on logic

Mock external I/O — never internal logic. The boundary is:

- Cache (`src.infra.cache.cache_client`)
- DB session (`src.infra.database.get_session`) and Repository classes
- HTTP clients (`httpx.AsyncClient`)
- S3 (`boto3` via `src.infra.s3.S3Service`)
- Whisper / Vision / Embedding APIs
- Celery task `apply_async` calls

Patch by the **import path of the consumer**, not the source:

```python
# CORRECT — patches what company_service.py uses
with patch("src.application.company.company_service.cache_client") as mock_cache:
    ...

# WRONG — patches the source module, leaves the rebinding in
# company_service untouched
with patch("src.infra.cache.cache_client") as mock_cache:
    ...
```

Mocking pattern for an async context manager (e.g. `get_session()`):

```python
with patch("src.application.company.company_service.get_session") as mock_session:
    mock_session_instance = MagicMock()
    mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
    mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
    # then inject a mock repository on top:
    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=sample_company_config)
    MockRepoClass.return_value = mock_repo
```

When mocking external services, exercise the realistic failure modes:
success with expected payload, success with malformed payload, network
error, timeout, 4xx, 5xx.

## Integration tests — when and how

When the test exercises the data access layer end-to-end against a real
SQL engine. The fixtures already do the heavy lifting:

```python
@pytest.mark.integration
class TestCompanyRepository:
    async def test_crud_fluxo_basico(self, db_session):
        repo = CompanyRepository(db_session)
        company = await repo.upsert_full(...)
        assert company.id is not None
        # assert against the DB
        fetched = await repo.get_by_id(company.id)
        assert fetched.name == company.name
```

`Base.metadata.create_all` runs against SQLite by importing
`src.domain.__init__`, which in turn imports every model. If you add a new
model and forget to register it there, integration tests will silently
miss its table.

## Testing LangGraph agents and tools (gap area)

The current suite tests the `AgentManager` (TTL, snapshot, sliding TTL),
the orchestrator's handoff and usage extraction, prompts (golden),
sub-agent schemas, and tool-side compactors (e.g. `shopify` middleware).
Examples live in `tests/unit/ai/`.

The general posture for AI tests:

- **Don't call the real LLM.** Mock at the LangGraph / model boundary.
  When checking what messages get sent, build `AIMessage` / `HumanMessage`
  / `ToolMessage` instances directly (`from langchain_core.messages import ...`).
- **Test the deterministic parts.** Parsers (`shopify_response`,
  `agent_response_parser`), classifiers, prompt assembly (`style_renderer`,
  prompt golden tests), middleware compactors. These are the layers where
  bugs hurt the most.
- **Don't test prompt strings as opaque blobs.** Use golden snapshots
  (already done for sales prompt in
  `tests/unit/ai/agents/sales/test_prompt_golden.py`) so format drift
  surfaces as a small diff.
- **Tool tests** mock the underlying provider client and assert the
  function returns the right shape (see `tests/unit/ai/tools/test_*.py`).
- **Agent state** is checkpoint-based via Valkey. For unit tests, use the
  `RedisModuleMock` / `QueueModuleMock` patterns (see `tests/conftest.py`)
  rather than spinning up Valkey. For integration tests of the orchestrator,
  use the in-process checkpointer if available.

## What NOT to test

Carry over from `tests/TESTING.md`:

- Plain SQLAlchemy models (just declarations) — covered indirectly by
  integration tests of the repository.
- `Settings` / constants without logic.
- `__init__.py` re-exports.
- Third-party code.
- Private helpers in isolation — exercise them through the public API.

## Pre-PR checklist (test-side)

- [ ] File named `test_<module>.py` mirroring `src/`
- [ ] Tests grouped in classes with Portuguese docstrings
- [ ] Function names follow `test_<action>_<scenario>_<expected>`
- [ ] `@pytest.mark.unit` or `@pytest.mark.integration` present
- [ ] Mocks patch the consumer import path, not the source
- [ ] No assertions on error message strings — use exception class
- [ ] No `print()` calls or `import logging` — structlog is on
- [ ] If a new SQLAlchemy model was added, it's registered in
      `src/domain/__init__.py` so integration fixtures see the table
- [ ] `uv run pytest tests/unit/ tests/integration/ -q` is green
