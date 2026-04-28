---
name: ai-tool
description: >
  How to create and modify LangChain/LangGraph tools in
  zoppy-whatsapp-commerce. Covers the @tool decorator, the
  create_<feature>_tools(...) factory pattern with closure-captured
  config, the company-wide tools registry (create_tools_for_company),
  the wrap_subagent_as_tool envelope that exposes sub-agents as tools,
  feature-flag gating, return-shape conventions (the __transfer__ marker
  for handoff, JSON-stringified payloads), tenant-context propagation
  via request_context, and middleware that compacts tool responses
  before they hit the LLM. Use this skill whenever creating a new
  tool, gating one by company config, returning data the supervisor
  must see, troubleshooting a tool that breaks the agent loop, or
  registering a new tool in the company-wide registry. Triggers on:
  "create tool", "nova tool", "add tool", "@tool", "StructuredTool",
  "create_<provider>_tools", "register tool", "tools registry",
  "create_tools_for_company", "wrap_subagent_as_tool",
  "subagent as tool", "transfer_to_human", "__transfer__",
  "ToolCallLimitMiddleware", "ShopifyResponseCompactorMiddleware",
  "tool docstring", "tool description", "request_context tool",
  "_context_customer_phone".
---

# AI Tools — zoppy-whatsapp-commerce

Tools are how an agent acts on the world. In this codebase a tool is a
plain async function decorated with `@tool` from `langchain_core.tools`
(or built via `StructuredTool.from_function`). The supervisor and
sub-agents call them through LangGraph's standard tool node.

The system has three families of tools:

- **Common** — `transfer_to_human` (always present).
- **Provider tools** — Shopify (search + order status), Nuvemshop,
  Cart (Shopify-only), Knowledge (RAG retrieval), Giftback (Zoppy
  Partners API).
- **Sub-agents wrapped as tools** — `catalog_search_agent` and
  `knowledge_search_agent` from the `wrap_subagent_as_tool` envelope.

## Layer & file map

```
src/ai/tools/
├── __init__.py
├── registry.py              # create_tools_for_company(...) — company-wide registry
├── common.py                # transfer_to_human (@tool, always available)
├── agent_wrappers.py        # wrap_subagent_as_tool + subagent_usage_accumulator
├── giftback.py              # create_giftback_tools(partners_token)
├── shopify.py               # create_shopify_tools(...) + create_order_status_tool(...)
├── nuvemshop.py             # create_nuvemshop_tools(store_id, access_token)
├── cart.py                  # create_cart_tools(shop_domain, session_ttl_minutes)
└── knowledge.py             # create_knowledge_tools()
```

Two registries call into here:

- **`src/ai/agents/registry.py`** — supervisor-side: `_get_sales_tools`
  picks which provider tools the **sales** agent gets based on
  capabilities (provider, integrations, partners_token).
- **`src/ai/tools/registry.py`** — sub-agent-side:
  `create_tools_for_company` returns the full bag-of-tools grouped by
  category (`common`, `catalog`, `cart`, `support`). Sub-agents pick the
  group they need (knowledge agent picks `support`).

The split exists because the supervisor's toolset depends on the agent
type + capabilities, while sub-agents always need the same group.

## The canonical shape — `@tool` factory

`src/ai/tools/giftback.py:158`:

```python
def create_giftback_tools(partners_token: str) -> list:
    @tool
    async def giftback_check() -> str:
        """Consulta se o cliente possui giftback (cupom de desconto) ativo.

        Use esta ferramenta quando o cliente:
        - Perguntar sobre desconto, cupom, cashback, giftback ou beneficios
        - Quiser saber se tem algum credito disponivel

        A ferramenta consulta automaticamente pelo telefone do cliente.
        Nao e necessario fornecer nenhum parametro.

        Returns:
            Informacoes sobre giftbacks ativos do cliente, incluindo
            codigo, desconto, compra minima e validade.
        """
        customer_phone = _context_customer_phone.get()
        if not customer_phone:
            return "Nao foi possivel identificar o telefone do cliente."

        async with ZoppyPartnersClient(token=partners_token) as client:
            coupons = await client.get_active_giftbacks(customer_phone)

        return _format_multiple_giftbacks(coupons)

    return [giftback_check]
```

Anatomy:

1. **Outer `create_<feature>_tools(...)` factory** captures per-company
   config (tokens, shop domains) in a closure. The agent registry
   passes the `CompanyConfig` and reads what it needs to call this
   factory.
2. **Inner `@tool async def`** is what LangGraph actually invokes.
3. **`async def`** always — every tool touches I/O.
4. **Triple-quoted docstring** is the LLM-visible description.
   *Treat it as production code.*
5. **Args / Returns sections** in the docstring are how the LLM learns
   the tool's contract. Keep them concrete and short.
6. **`_context_customer_phone.get()`** pulls tenant context from the
   structlog contextvar that the orchestrator bound at the start of
   the request — see `multi-tenant-context` skill.
7. **Async context manager** for the HTTP client
   (`async with ClientClass(...) as client:`) so connections close
   deterministically.
8. **Return is a string.** Either a human-readable summary the LLM
   formats further, or a JSON-stringified payload (see "Return shapes"
   below).
9. **Factory returns `list`** of tools — even when there's only one,
   the registry expects a list.

## Tool docstrings — the contract

The docstring is the only thing the model sees about the tool. It
informs:

- **Whether to call it.** "Use esta ferramenta quando o cliente..." +
  concrete trigger phrases.
- **What to pass.** `Args:` section with one bullet per parameter,
  with examples.
- **What to expect back.** `Returns:` section.

Conventions in this codebase:

- Docstrings are in **Portuguese** when the tool is consumer-facing
  (giftback, cart, order_status). The model is multilingual; the
  customer's language wins.
- Use `Args:` and `Returns:` sections (NumPy-ish style).
- Include 1-3 example inputs in the param description when ambiguous
  values are possible (`order_number: "1001", "#1001", "BR1001"`).
- Don't over-constrain. Let the model decide when to call —
  one-paragraph description usually beats a checklist.
- Tools that don't take parameters (like `giftback_check`) make that
  explicit: "Nao e necessario fornecer nenhum parametro."

## Provider tools with multiple variants

Shopify's `create_shopify_tools` is the reference for "the basic tool
is always there, the optional one is gated":

```python
def create_shopify_tools(
    shop_domain: str, admin_token: str = "", store_context: str = ""
) -> list:
    @tool
    async def shopify_search_products(query: str) -> str:
        """..."""
        ...

    tools = [shopify_search_products]

    if admin_token:
        @tool
        async def order_status(order_number: str) -> str:
            """..."""
            ...
        tools.append(order_status)

    return tools
```

`order_status` only exists for companies that have an admin token (it
calls Shopify Admin API, not Storefront). The sales agent registry
calls a separate helper `create_order_status_tool(shop_domain, admin_token)`
so the supervisor can decide independently — but the same on/off
gating applies.

## Common tool — `transfer_to_human` and the `__transfer__` marker

`src/ai/tools/common.py`:

```python
@tool
def transfer_to_human(reason: str, detail: str = "") -> str:
    """
    Transfer the conversation to a human agent.

    Use this tool when:
    - The customer explicitly asks to speak with a human
    - The situation is too complex for the AI to handle
    - The customer is frustrated or upset
    - You need to escalate for authorization or special handling
    - Information is not available in the knowledge base
    - Repeated tool failures occur
    """
    return json.dumps({
        "__transfer__": True,
        "reason": reason,
        "detail": detail or None,
    })
```

The orchestrator scans tool outputs for the `__transfer__` marker
(`HandoffEventService.extract_transfer_info`). When present, it
short-circuits the response, persists a `HandoffEvent`, sets the
cooldown, and clears the LangGraph session. Two consequences:

- **The marker shape is load-bearing.** Don't change `__transfer__`,
  `reason`, `detail` keys without updating the extractor.
- **`reason` MUST be one of the codes the supervisor lists in
  `<tools>`.** The codes come from `SYSTEM_HANDOFF_REASONS` plus the
  customer's `agent_config.handoff_reasons`. See the `ai-agent` skill's
  `references/prompts.md` for the prompt section.

## Return shapes

Tools always return `str`. Two flavors are common:

| When | Shape | Why |
|---|---|---|
| Human-readable summary | Plain text formatted for the model to relay verbatim or rewrite | Catalog search results (after middleware compaction), giftback summary |
| Structured payload | `json.dumps({...})` with named fields | `transfer_to_human`, errors that carry codes, anything the orchestrator parses |

For structured payloads:

```python
return json.dumps({"error": "Erro inesperado ao consultar pedido."})
return json.dumps({"__transfer__": True, "reason": code, "detail": detail})
```

The LLM is fluent at extracting structured data from plain text, but
when downstream Python code needs to read it (the orchestrator scanning
for `__transfer__`, the parser detecting markers), JSON wins.

## Wrapping a sub-agent as a tool

`src/ai/tools/agent_wrappers.py:wrap_subagent_as_tool` produces a
`StructuredTool` that, when called, invokes a LangGraph agent and
returns its final message content as a string. The supervisor sees it
as a regular tool with the description provided by the
`SUBAGENT_DESCRIPTIONS` map in `agents/subagents/registry.py`.

```python
@observe(name=f"tool.{name}", as_type="tool")
async def subagent_tool(request: str) -> str:
    langfuse_handler = CallbackHandler()
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": request}]},
        config={"callbacks": [langfuse_handler]},
    )

    # Capture per-sub-agent token usage for the orchestrator's UsageCalculator
    for msg in result.get("messages", []):
        if isinstance(msg, AIMessage) and msg.usage_metadata:
            ...
            acc = subagent_usage_accumulator.get()
            if acc is not None:
                acc.append(usage_entry)
            else:
                subagent_usage_accumulator.set([usage_entry])

    raw_content = result["messages"][-1].content
    if isinstance(raw_content, list):
        from src.ai.parsers.agent_response import _normalize_content
        content = _normalize_content(raw_content)
    else:
        content = raw_content
    return content

return StructuredTool.from_function(
    coroutine=subagent_tool,
    name=name,
    description=description,
)
```

Key points:

- **`subagent_usage_accumulator`** is a contextvar reset by the
  orchestrator before each turn (`subagent_usage_accumulator.set([])`).
  Token usage from each sub-agent invocation gets appended; the
  `UsageCalculator` reads it back for cost accounting. Don't bypass
  this — if you call a sub-agent outside the wrapper, costs disappear
  from metrics.
- **`@observe(name=f"tool.{name}", as_type="tool")`** turns each
  sub-agent invocation into its own langfuse span, which is how we
  see "supervisor → catalog_agent → product results" trees in the UI.
- **`_normalize_content`** flattens content blocks (vision payloads)
  into a string.

## The company-wide registry — `create_tools_for_company`

`src/ai/tools/registry.py`:

```python
def create_tools_for_company(company_config: CompanyConfig) -> dict[str, list]:
    tools = {
        "common": [transfer_to_human],
        "catalog": [],
        "cart": [],
        "support": [],
    }

    provider = company_config.provider or "shopify"

    if provider == "nuvemshop" and company_config.integrations.key:
        tools["catalog"].extend(create_nuvemshop_tools(...))
    elif provider == "nuvemshop" and not company_config.integrations.key:
        logger.warning("tools_registry.nuvemshop_missing_key", ...)
    elif company_config.integrations.url:
        tools["catalog"].extend(create_shopify_tools(...))
        tools["cart"].extend(create_cart_tools(...))

    tools["support"].extend(create_knowledge_tools())
    return tools
```

Conventions:

- **Buckets are stable.** `common` / `catalog` / `cart` / `support` —
  sub-agent factories ask for one bucket. Don't rename or split without
  updating every caller.
- **Empty buckets stay empty.** If a company has no integration URL,
  `catalog` and `cart` lists are simply empty. Sub-agents handle that
  gracefully (the catalog sub-agent returns an "unavailable" message).
- **Logger when a config is partially set up.** `nuvemshop_missing_key`
  is exactly the kind of shape that helps debug a misconfigured
  company in production.

The supervisor doesn't use `create_tools_for_company` — it uses
`agents/registry.py:_get_sales_tools` which speaks in capability
terms. The two registries are intentional: supervisor toolsets are
agent-type-shaped, sub-agent toolsets are feature-shaped.

## Tenant context inside a tool

When a tool needs to know who the customer is, it reads from the
contextvars that the orchestrator bound at request entry:

```python
from src.utils.request_context import _context_customer_phone

customer_phone = _context_customer_phone.get()
if not customer_phone:
    return "Nao foi possivel identificar o telefone do cliente."
```

This is how `giftback_check` knows whose coupons to fetch without the
LLM having to pass the phone number as a parameter. Two consequences:

- **Tools called outside `run_conversation` won't see the context.**
  Test fixtures must `bind_context(...)` before invoking the tool, or
  the tool gets `None`.
- **Background tasks lose the context.** If a tool spawns a Celery
  job, re-bind in the worker (see `multi-tenant-context` skill).

## Middleware that touches tools

The supervisor stacks four middlewares (see `ai-agent` skill):

| Middleware | Purpose |
|---|---|
| `ModelRetryMiddleware` | Retry the LLM call on transient failures |
| `ToolRetryMiddleware` | Retry a failed tool call up to 2 times with backoff |
| `ToolCallErrorHandlerMiddleware` (project-local, `src/ai/middlewares/error_handler.py`) | Convert tool exceptions into model-readable error messages so the supervisor can recover |
| `ToolCallLimitMiddleware(run_limit=10)` | Hard cap on tool calls per turn — last-line defense against tool loops |

There's also a **response compactor** for Shopify
(`src/ai/middlewares/shopify.py:ShopifyResponseCompactorMiddleware`)
that runs *between* the tool returning and the LLM seeing the result.
It parses MCP catalog payloads (large) into a compact dict (small).
The compactor uses `parse_mcp_json_to_catalog` from the same file —
a pure parser exposed for tests.

When you write a tool whose response is large enough to threaten the
context window, write a paired compactor middleware. Don't push the
trim logic into the tool itself; the compactor stays optional and
deactivatable for debugging.

## Adding a new tool — checklist

1. **Pick the right file.** Provider tools live in
   `src/ai/tools/<provider>.py`. Cross-cutting tools (handoff,
   structured-data tools that aren't tied to a provider) live in
   `common.py` or get a dedicated file.
2. **Wrap in a factory** if the tool needs config: `def create_<feature>_tools(token, shop_domain, ...) -> list`. If it
   needs nothing beyond runtime context, decorate at module level
   like `transfer_to_human`.
3. **Write the docstring like production code.** Use, args, returns,
   examples for ambiguous types.
4. **Decide return shape.** Plain text vs JSON-stringified.
5. **Use the project HTTP client conventions.** `httpx.AsyncClient`
   inside an `async with Client(...) as client:` context manager.
   Set `timeout=15.0`/`30.0` based on upstream SLA.
6. **Log structured events.** `logger.info("<provider>.<action>.started", ...)`
   then `.completed` / `.failed` with relevant fields.
7. **Register**:
   - For supervisor tools: extend `_get_sales_tools` in
     `src/ai/agents/registry.py` with the gating condition that
     decides who gets it.
   - For sub-agent tools: extend `create_tools_for_company` in
     `src/ai/tools/registry.py` with the right bucket.
8. **Test.** Unit test in `tests/unit/ai/tools/test_<feature>.py`
   covering: happy path, error path (4xx, 5xx, timeout), missing
   tenant context, empty result.

## Gating tools by feature flag or capability

Three patterns coexist; pick whichever matches the gate:

| Gate | Where to check |
|---|---|
| **Per-company integration present** (token, shop domain) | Inside the registry function (`if company.integrations.url: ...`) |
| **Per-company partners_token present** (giftback) | Inside `_get_sales_tools` — only adds the tool if `company.partners_token` |
| **Per-company feature flag** (knowledge, catalog) | Inside the agent's `enabled_features` / `enabled_subagents` — checked at sub-agent registry time, not at tool time |

Don't gate inside the tool function itself with an `if not allowed:`
return-error pattern. The agent will see the tool listed and try to
call it; gating at registry time avoids the failed-call detour.

## Gotchas / anti-patterns

- **Never put business logic in `wrap_subagent_as_tool`.** It's a
  pass-through with usage capture. Logic belongs in the sub-agent's
  prompt + tools.
- **Never return raw exception objects** from a tool. Either return
  a friendly string or a JSON error payload — the LLM has to read it.
- **Never let a tool raise.** The retry/error middleware catches
  exceptions, but the model gets a generic error message and may try
  again. Catch internally, return a structured error string.
- **Never forget to register the tool.** A `@tool`-decorated function
  with no caller is dead code.
- **Never make a tool call out without an HTTP timeout.** Default to
  15-30 s; longer hangs the LangGraph node and burns the run_limit.
- **Don't add `from src.api.*` to a tool.** Layer rule.
- **Don't call `_context_customer_phone` directly inside a sync `@tool`.**
  Sync tools run on a different worker and the contextvar isn't
  guaranteed to propagate. All real tools in this codebase are async.
- **Don't change `transfer_to_human`'s return shape** (`__transfer__`
  / `reason` / `detail`). The orchestrator's extractor is brittle by
  design.

## Pre-PR checklist

- [ ] Tool lives in the right file (`tools/<provider>.py`,
      `tools/common.py`, or a new dedicated module)
- [ ] Async function with `@tool` decorator (or `StructuredTool` for
      composed tools)
- [ ] Docstring includes Use cases, Args, Returns
- [ ] Per-company config captured by closure in
      `create_<feature>_tools(...)` factory
- [ ] HTTP client wrapped in `async with` with explicit timeout
- [ ] Structured logger calls (`<feature>.<action>.started/completed/failed`)
- [ ] Registered in `_get_sales_tools` or `create_tools_for_company`
      (or both) with the correct gate
- [ ] Tenant context (if needed) read via `_context_customer_phone.get()`,
      with a fallback when it's missing
- [ ] Tests in `tests/unit/ai/tools/test_<feature>.py` covering happy
      path + error paths + missing-context path
- [ ] If response is large, paired compactor middleware (or documented
      decision not to)
- [ ] `uv run pytest tests/unit/ai/tools/ -q` is green
