---
name: ai-agent
description: >
    How to create and modify LangGraph agents in zoppy-whatsapp-commerce —
    the supervisor "sales" agent + sub-agents (catalog, catalog_nuvemshop,
    knowledge). Covers the registry/factory split, AgentManager TTL cache,
    per-thread config snapshots, the AsyncValkeySaver checkpointer, the
    4-section XML system prompt (<system_rules>, <style_preferences>,
    <store_context>, <tools>), AgentStyle + presets + style_renderer, and
    the orchestrator pipeline that ties it all together. Use this skill
    whenever creating a new agent or subagent, modifying agent prompts,
    registering an agent type, debugging cache invalidation, adjusting the
    checkpointer TTL, or auditing how customer-tunable behavior maps to
    the prompt. Triggers on: "create agent", "novo agent", "novo subagent",
    "create subagent", "LangGraph", "create_agent", "AgentManager",
    "snapshot_config", "checkpointer", "AsyncValkeySaver", "system prompt",
    "<system_rules>", "<style_preferences>", "<store_context>", "<tools>",
    "AgentStyle", "preset", "style_renderer", "agent registry", "agent
    factory", "subagent", "wrap_subagent_as_tool", "supervisor", "sales
    agent", "catalog subagent", "knowledge subagent".
---

# AI Agents — zoppy-whatsapp-commerce

Agents are LangGraph `create_agent(...)` instances built per
`(company, agent_config)` pair, cached in memory by `AgentManager`, and
checkpointed in Valkey so conversations survive process restarts and
horizontal scaling.

The system has one **supervisor** ("sales") and three **sub-agents**:

-   `catalog_search` — Shopify catalog search via MCP
-   `catalog_search` — Nuvemshop variant (provider-routed)
-   `knowledge_search` — RAG over the company's knowledge base

The supervisor calls sub-agents through tool wrappers
(`wrap_subagent_as_tool`) — sub-agents are not chat participants,
they're agentic tools.

## Layer & file map

```
src/ai/
├── orchestrator.py             # entry point: run_conversation()
├── agent_manager.py            # in-memory cache + per-thread config snapshot
├── agents/
│   ├── registry.py             # agent_type → tool factory + agent factory
│   ├── factory.py              # composes tools + subagents into a final agent
│   ├── sales/                  # supervisor
│   │   ├── agent.py            # create_sales_agent()
│   │   ├── prompt.py           # 4-section XML prompt assembly
│   │   ├── style_renderer.py   # AgentStyle → <style_preferences> body
│   │   └── presets.py          # objetivo / consultivo / amigavel / agressivo
│   └── subagents/
│       ├── registry.py         # subagent_name → factory (provider-aware)
│       ├── catalog/agent.py             # Shopify catalog subagent
│       ├── catalog_nuvemshop/agent.py   # Nuvemshop catalog subagent
│       └── knowledge/agent.py           # KB / RAG subagent
├── tools/
│   ├── agent_wrappers.py       # wrap_subagent_as_tool
│   ├── registry.py             # company-wide tool registry
│   └── <provider/feature>.py   # actual tools — see ai-tool skill
├── middlewares/
│   ├── error_handler.py        # ToolCallErrorHandlerMiddleware
│   └── shopify.py              # ShopifyResponseCompactorMiddleware
├── parsers/
│   └── agent_response.py       # final messages → ResponseMessage list
└── prompts/
    └── presentation.py         # first-message presentation prompt
```

## The pipeline

When a chat request lands at `POST /chat`:

1. **`api/endpoints/chat.py`** validates, fetches `CompanyConfig`,
   delegates to `ai/orchestrator.py:run_conversation()`.
2. **`run_conversation`** binds the structlog context
   (`company_id`, `customer_phone`, `thread_id`) and resolves the
   `AgentConfig` for the receiving business phone.
3. **`AgentManager.snapshot_config(thread_id, current_config)`** freezes
   the config on the first message of the thread — DB edits to the
   config don't leak into a running session.
4. **Cooldown check** — if a recent handoff put the thread in cooldown,
   return early without invoking the agent.
5. **Message preprocessing** — `MessagePreprocessor` from
   `application/message/` transcribes audio (Whisper) and turns images
   into vision content blocks.
6. **`AgentManager.get_agent(company, agent_config)`** returns the
   compiled agent for `<company_id>:<agent_config_id>` (creates one on
   miss, refreshes TTL on hit). Includes the AsyncValkeySaver
   checkpointer.
7. **`agent.ainvoke(input, config)`** with `thread_id` in `configurable`.
   The checkpointer reads/writes state in Valkey under
   `checkpoint:{thread_id}:*`.
8. **`_handle_handoff`** scans tool outputs for `__transfer__` and
   persists a `HandoffEvent` if found.
9. **`parse_response_messages`** (from `ai/parsers/agent_response.py`)
   converts the raw final messages into typed `ResponseMessage[]`.
10. **`UsageCalculator.extract`** sums input/output tokens and computes
    cost.

Full breakdown of the orchestrator (preprocessing, langfuse tracing,
handoff persistence, usage accounting): `references/orchestrator.md`.

## The registry/factory split

Two registries, two responsibilities:

| Registry                                               | Purpose                                                          | File                                     |
| ------------------------------------------------------ | ---------------------------------------------------------------- | ---------------------------------------- |
| **agent registry** (`agents/registry.py`)              | `agent_type` (string) → `(get_agent_tools, agent_factory)`       | one supervisor type today: `"sales"`     |
| **subagent registry** (`agents/subagents/registry.py`) | `subagent_name` → factory, provider-aware (Shopify vs Nuvemshop) | `"catalog_search"`, `"knowledge_search"` |

The composition lives in **`agents/factory.py:create_agent_for_agent_config`**:

```python
async def create_agent_for_agent_config(
    company: CompanyConfig,
    agent_config: AgentConfigData,
    checkpointer: AsyncValkeySaver | None = None,
):
    # 1. base tools for the agent type (transfer_to_human, cart, giftback, …)
    agent_tools = get_agent_tools(
        agent_config.agent_type, company, agent_config.session_ttl_minutes
    )

    # 2. sub-agents wrapped as tools
    subagent_tools = await create_subagent_tools(company, agent_config)
    all_tools = agent_tools + subagent_tools

    # 3. the agent factory itself
    agent_factory = get_agent_factory(agent_config.agent_type)
    if not agent_factory:
        raise ValueError(f"Unknown agent type: {agent_config.agent_type}")

    return await agent_factory(company, agent_config, all_tools, checkpointer)
```

This split is what lets you toggle features per company (via
`agent_config.enabled_features` and `enabled_subagents`) without
changing prompt-level code.

## AgentManager — TTL cache + snapshot

`src/ai/agent_manager.py` is a process-local LRU-style cache:

| Key                              | Value                                 | TTL                                                                         |
| -------------------------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| `<company_id>:<agent_config_id>` | compiled LangGraph agent + metadata   | 30 min default (env: `agent_manager_ttl_minutes`), refreshed on each access |
| `<thread_id>`                    | per-thread `AgentConfigData` snapshot | same TTL, refreshed on access                                               |

The snapshot is the **invariant that protects ongoing conversations**.
The first message on a thread freezes the config; subsequent messages
within TTL see the same `AgentConfigData` even if the customer edits
the config in the playground. Without this, mid-conversation prompt
drift would break the user experience.

A background task (`start_background_cleanup`) sweeps expired entries
every `agent_manager_cleanup_interval_seconds`.

When something invalidates the config externally (webhook, playground
PUT), call:

```python
agent_manager.invalidate(company_id)                           # all configs for the company
agent_manager.invalidate(company_id, agent_config_id)          # one specific
```

Snapshots are not invalidated — they expire with TTL. That's
intentional: a running conversation should not see a config swap mid-flight.
See the `multi-tenant-context` skill.

## Checkpointer — AsyncValkeySaver

`src/infra/checkpointer.py` initializes one `AsyncValkeySaver` at app
startup (`CheckpointerManager.initialize()`). It writes LangGraph
state (messages, tool calls, intermediate state) under
`checkpoint:{thread_id}:*`, `writes:{thread_id}:*`,
`thread:{thread_id}:*`. Default TTL is 24 h; per-thread TTL can be
applied via `apply_session_ttl(thread_id, ttl_minutes)`.

Reset a session entirely with `clear_session(thread_id)` (used by
the handoff flow and the playground reset endpoint).

## Creating a sales-style supervisor agent

The canonical reference is `src/ai/agents/sales/agent.py`:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)
from langchain_openai import ChatOpenAI
from langfuse import observe
from langgraph_checkpoint_aws import AsyncValkeySaver

from src.ai.middlewares import ToolCallErrorHandlerMiddleware
from src.domain.agent_config.schemas import AgentConfigData
from src.domain.company.schemas import CompanyConfig
from src.infra.config import settings
from src.utils.logger import get_logger
from .prompt import get_sales_prompt

logger = get_logger(__name__)


@observe(name="create_sales_agent", as_type="span")
async def create_sales_agent(
    company: CompanyConfig,
    agent_config: AgentConfigData,
    tools: list,
    checkpointer: AsyncValkeySaver | None = None,
):
    system_prompt = get_sales_prompt(company, agent_config)

    model = ChatOpenAI(
        model=settings.supervisor_model,
        api_key=settings.openai_api_key,
        temperature=0.4,
        use_responses_api=True,
    )

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        middleware=[
            ModelRetryMiddleware(max_retries=2, on_failure="continue"),
            ToolRetryMiddleware(max_retries=2, backoff_factor=2.0, initial_delay=1.0),
            ToolCallErrorHandlerMiddleware(),
            ToolCallLimitMiddleware(run_limit=10),
        ],
    )

    return agent
```

Anatomy:

-   **`@observe(...)` from langfuse** wraps the factory so trace context
    flows. Always include it — it's how the team debugs production.
-   **`ChatOpenAI` from `langchain_openai`** with model from `settings`,
    `use_responses_api=True` (Responses API, not Chat Completions).
-   **`temperature=0.4`** for the supervisor (some creativity).
-   **Middleware stack**: model retry → tool retry → tool error handler →
    tool call limit. The tool call limit (`run_limit=10`) is the safety
    net against tool-loop bugs.
-   **`checkpointer` always passed in** for the supervisor. Sub-agents
    generally don't need a checkpointer (they execute as a subroutine
    inside the supervisor's turn).

## Creating a sub-agent

Reference: `src/ai/agents/subagents/knowledge/agent.py`. Differences vs
supervisor:

-   **`temperature=0.0`** — sub-agents must be deterministic.
-   **No checkpointer** — sub-agents are stateless from the orchestrator's
    view; their work happens inside the supervisor's turn.
-   **`settings.subagent_model`** — usually a smaller/cheaper model
    (gpt-4.1-mini at the time of writing).
-   **Tools come from `create_tools_for_company(...)`** rather than the
    agent registry, because the sub-agent's toolset is feature-specific
    (knowledge → KB tools, catalog → Shopify/Nuvemshop search tools).

## The 4-section XML system prompt (sales)

The supervisor system prompt is composed of four blocks in this order:

```
<system_rules>          rigid rules — invariants the agent must follow
                        (decision tree, tool orchestration, link rules,
                        formatting constraints)
</system_rules>

<style_preferences>     customer-tunable behavior rendered from AgentStyle
                        (10 fields: posture, objective, upsell, length,
                        framing, emoji, clarification budget, follow-up,
                        max_products, image_input_behavior)
</style_preferences>

<store_context>         per-company facts (brand_name, brand_tone,
                        brand_description, target_audience, integrations,
                        tone of voice)
</store_context>

<tools>                 tool orchestration rules + handoff reason codes
</tools>
```

Assembly happens in `src/ai/agents/sales/prompt.py:get_sales_prompt`.
See `references/prompts.md` for the full breakdown of each section,
how AgentStyle maps to `<style_preferences>`, and the four built-in
presets (`objetivo`, `consultivo`, `amigavel`, `agressivo`).

## Adding a new agent type (rare)

Most changes don't need a new agent type — toggling sub-agents,
features, or AgentStyle covers 90% of the customization surface. When
you do need one (e.g. "support" agent type that's not sales-shaped):

1. Create `src/ai/agents/<type>/agent.py` with `create_<type>_agent(...)`
   matching the `AgentFactory` signature.
2. Create `src/ai/agents/<type>/prompt.py` with `get_<type>_prompt(...)`.
3. Add the entry to `agents/registry.py`:
    - `_get_<type>_tools(company, session_ttl_minutes) -> list` — the
      base toolset
    - `AGENT_TOOLS_REGISTRY["<type>"] = _get_<type>_tools`
    - inside `get_agent_factory`: `registry["<type>"] = create_<type>_agent`
4. Add the new type as a valid value of `agent_config.agent_type` in
   the database (Alembic migration if there's a CHECK constraint).
5. Tests: a unit test that verifies the factory creates an agent with
   the expected tools + middleware stack, and a prompt-golden test for
   the system prompt assembly.

## Adding a new sub-agent

1. Create `src/ai/agents/subagents/<name>/agent.py` and `prompt.py`.
2. Register in `agents/subagents/registry.py`:
    - Add to the inner `registry` dict in `get_subagent_factory`.
    - Add a description under `SUBAGENT_DESCRIPTIONS` — the supervisor
      uses this when it decides whether to call the sub-agent. The
      description **is** the contract.
3. Provider-routing: if the sub-agent has provider variants (like
   catalog), route inside `get_subagent_factory` using
   `company_config.provider`.
4. The sub-agent surfaces to the supervisor as a tool via
   `wrap_subagent_as_tool(name=f"{subagent_name}_agent", description, agent)`.

## Customer-tunable behavior — `AgentStyle`

`src/domain/agent_config/agent_style.py` defines `AgentStyle`, a
Pydantic model with 10 fields:

| Field                   | Enum                                                    | Default               |
| ----------------------- | ------------------------------------------------------- | --------------------- |
| `sales_posture`         | `consultive`, `objective`, `supportive`, `aggressive`   | `consultive`          |
| `primary_objective`     | `conversion`, `information_first`, `mixed`              | `conversion`          |
| `upsell_intensity`      | `none`, `soft`, `active`, `proactive`                   | `soft`                |
| `response_length`       | `minimal`, `concise`, `detailed`                        | `concise`             |
| `product_framing`       | `name_price_only`, `+benefits`, `+features`, `+specs`   | `+benefits`           |
| `emoji_policy`          | `none`, `sparing`, `frequent`                           | `sparing`             |
| `clarification_budget`  | int 0..2                                                | 2                     |
| `follow_up_proactivity` | `never`, `when_interest_shown`, `always_offer_cart`     | `when_interest_shown` |
| `max_products`          | int 1..10                                               | 5                     |
| `image_input_behavior`  | `describe_and_suggest`, `search_similar`, `ask_context` | `ask_context`         |

Defaults reproduce the legacy hardcoded behavior (backward compat).
Presets (`src/ai/agents/sales/presets.py`) bundle a coherent set of
field values:

-   `objetivo` — direct, conversion-focused, minimal copy
-   `consultivo` — informative, longer responses, mixed objective
-   `amigavel` — warm, supportive, sparing emojis
-   `agressivo` — aggressive close, proactive upsell

The `<style_preferences>` block is rendered by
`src/ai/agents/sales/style_renderer.py`. See `references/prompts.md`.

## Tracing & observability

Every factory and the orchestrator are wrapped with
`@observe(name=..., as_type="span")` from langfuse. The orchestrator
also calls:

-   `langfuse.update_current_span(input=...)` to attach the user input
-   `propagate_attributes(session_id=thread_id, user_id=..., tags=...)` —
    the session id is the LangGraph thread id, so traces are grouped by
    conversation in the langfuse UI
-   `score_usage(...)` and `tag_handoff(...)` from
    `src.infra.observability` to score and tag traces post-hoc

`CallbackHandler()` from `langfuse.langchain` is passed in
`config["callbacks"]` so every LLM/tool call is traced automatically.

## Testing agents

See the `testing` skill for the full conventions. Agent tests live at:

```
tests/unit/ai/test_agent_manager.py             # cache + snapshot semantics
tests/unit/ai/test_agent_manager_snapshot.py
tests/unit/ai/test_agent_manager_sliding_ttl.py
tests/unit/ai/test_orchestrator.py              # handoff extraction, usage scoring
tests/unit/ai/agents/sales/test_prompt.py       # _build_* helpers
tests/unit/ai/agents/sales/test_prompt_golden.py # full prompt snapshot
tests/unit/ai/agents/sales/test_presets.py
tests/unit/ai/agents/sales/test_style_renderer.py
tests/unit/ai/agents/subagents/<name>/test_*.py
```

Posture:

-   **Don't call the real LLM.** Mock at the `ChatOpenAI` boundary, or
    test the deterministic pieces (prompt assembly, parsers,
    style_renderer, AgentManager state machine).
-   **Use prompt-golden snapshots** for the supervisor system prompt — the
    shape is large enough that diffs are the only sane review tool.
-   **Sub-agent factories** are mostly tested at the prompt + tool list
    level; full LangGraph execution is covered by the langfuse eval
    suite (separate from regular `make test`).

## Gotchas / anti-patterns

-   **Never instantiate `AgentManager` outside `agent_manager.py`.** The
    module-level `agent_manager = AgentManager(...)` at the bottom is the
    one and only instance.
-   **Never bypass `snapshot_config`.** Reading `agent_config` from the
    service at every message would break the "config is frozen mid-thread"
    contract.
-   **Never forget to invalidate `agent_manager` after a webhook updates
    `AgentConfig`.** New threads will compile against the new config;
    in-flight threads keep their snapshot until TTL.
-   **Never call sub-agent factories directly from the orchestrator.**
    The `factory.create_subagent_tools` path is the only correct one — it
    applies the `wrap_subagent_as_tool` envelope so the supervisor can
    invoke it as a tool.
-   **Never put feature-flag logic in the prompt.** Feature gates live in
    the registry (`_get_sales_tools`, `get_subagent_factory`). The prompt
    describes what the agent has access to, not what's allowed.
-   **Don't omit the `@observe(...)` decorator** on a new factory. Trace
    graphs lose context without it.
-   **Don't add direct `from src.api.*` imports to anything in `src/ai/`.**
    Layer rule.

## Pre-PR checklist

-   [ ] New agent / sub-agent file under `src/ai/agents/<...>/agent.py`
-   [ ] Registered in `agents/registry.py` (agent type) or
        `agents/subagents/registry.py` (subagent name + description)
-   [ ] `@observe(...)` on the factory
-   [ ] `temperature` chosen deliberately (supervisor: 0.4, sub-agents: 0.0)
-   [ ] Middleware stack matches the supervisor pattern (or documented
        deviation)
-   [ ] If a new agent type: `agent_config.agent_type` accepts the new
        value (Alembic migration if there's a CHECK constraint)
-   [ ] Prompt assembly uses the 4-section XML structure (sales-style) or
        a documented variant
-   [ ] AgentStyle field changes accompanied by `style_renderer.py`
        handlers and a preset value where applicable
-   [ ] Tests: prompt-golden, factory unit test, AgentManager state if
        affected
-   [ ] `uv run pytest tests/unit/ai/ -q` is green

## References

-   `references/prompts.md` — full breakdown of the 4 XML sections,
    `_build_*` helpers, AgentStyle → style_renderer mapping, presets
-   `references/orchestrator.md` — full breakdown of `run_conversation`:
    preprocessing, langfuse tracing, handoff persistence, usage accounting,
    cooldown semantics, broadcast context
