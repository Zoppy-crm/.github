# Orchestrator pipeline

This reference complements the `ai-agent` skill. Read the main
`SKILL.md` first.

`src/ai/orchestrator.py:run_conversation` is the entry point for every
chat turn. It glues together: tenant context binding, AgentConfig
resolution, cooldown gating, message preprocessing (audio + images),
agent retrieval (cached), LangGraph invocation, parsing, usage
accounting, handoff handling, and conversation metrics.

## Top-level shape

```python
@observe(name="run_conversation")
async def run_conversation(
    messages: list[MessageInput],
    customer_phone: str,
    business_phone: str,
    company: CompanyConfig,
    broadcast_context: str | None = None,
) -> dict:
    customer_phone = normalize_br_phone(customer_phone)
    thread_id = f"{company.company_id}:{customer_phone}"

    bind_context(
        company_id=company.company_id,
        customer_phone=customer_phone,
        thread_id=thread_id,
    )
    try:
        ...  # the pipeline below
        return {
            "messages": response_messages,
            "thread_id": thread_id,
            "agent_config_id": str(agent_config.id),
            "usage": usage,
            "transfer_info": transfer_info,
        }
    finally:
        clear_context()
```

`thread_id = "<company_id>:<customer_phone>"` is the load-bearing
identifier. The LangGraph checkpointer keys state under
`checkpoint:{thread_id}:*`; the cart and any session-scoped Valkey
data follow the same pattern.

`bind_context` writes the tenant fields onto structlog's contextvars
so every `logger.info(...)` downstream picks them up automatically —
see the `multi-tenant-context` skill.

## Step 1 — Resolve AgentConfig + snapshot

```python
service = AgentConfigService()
agent_config_response = await service.get_by_phone_number(business_phone)
if not agent_config_response:
    raise ValueError(f"No agent_config configured for phone {business_phone}")

if agent_config_response.company_id != company.company_id:
    raise ValueError(...)  # cross-tenant guard

agent_config = await service.get_config_for_agent(agent_config_response.id)
agent_config = agent_manager.snapshot_config(thread_id, agent_config)
```

The `business_phone` is the WABA / WhatsApp Business number that
received the message. We look up the AgentConfig that owns that
phone, then guard against it belonging to another company. Always.

`snapshot_config` is the freeze point — see the main `ai-agent` skill.

## Step 2 — Cooldown gate

```python
if await is_in_cooldown(company.company_id, customer_phone):
    return {
        "messages": [],
        "thread_id": thread_id,
        "agent_config_id": str(agent_config.id),
        "usage": None,
        "transfer_info": None,
        "in_handoff_cooldown": True,
    }
```

After a handoff, the customer is in cooldown for
`agent_config.handoff_cooldown_minutes` (default 60). During cooldown
the bot stays silent so the human takeover isn't interrupted.
`is_in_cooldown` and `set_cooldown` live in
`src/application/handoff/handoff_cooldown.py` (Valkey-backed
predicates, key `handoff_cooldown:<company_id>:<customer_phone>`).

## Step 3 — Tracing setup

```python
tags = build_trace_tags(company.company_id, messages, broadcast_context)

input_data = [
    {"content": m.content, "is_audio": m.is_audio, "is_image": m.is_image,
     "timestamp": m.timestamp.isoformat()}
    for m in messages
]
langfuse = get_client()
langfuse.update_current_span(input=input_data)

with propagate_attributes(
    session_id=thread_id,
    user_id=f"{company.company_id}:{customer_phone}",
    tags=tags,
    metadata={"company_id": company.company_id, ...},
):
    ...  # everything from here on shares the trace
```

`session_id=thread_id` is what groups conversations in the langfuse UI.
`tags` distinguishes broadcast contexts, audio/image/text inputs, etc.

## Step 4 — Message preprocessing

```python
preprocessor = MessagePreprocessor()
content_blocks = await preprocessor.process(messages)
```

`MessagePreprocessor` (in `src/application/message/message_preprocessor.py`):

- Audio messages → Whisper transcription → `TextContentBlock`
- Image messages → vision content blocks (OpenAI vision format)
- Text messages → `TextContentBlock` as-is

The output is a list of LangChain content blocks ready to drop into a
`HumanMessage(content=content_blocks)`.

## Step 5 — First-message presentation

```python
is_first = await checkpointer_manager.is_first_message(thread_id)
if is_first and agent_config.agent_name:
    presentation = get_presentation_prompt(agent_config.agent_name)
    content_blocks.insert(0, {"type": "text", "text": presentation})
```

When the conversation starts (no checkpoint state yet), prepend the
agent's self-introduction so the model has context for who it is.
`get_presentation_prompt` lives in `src/ai/prompts/presentation.py`.

## Step 6 — Broadcast context

```python
if broadcast_context:
    await checkpointer_manager.initialize_broadcast(
        thread_id=thread_id, broadcast_message=broadcast_context
    )
```

When the chat is replying to a marketing broadcast (the API caller
passes `broadcast_context`), seed the LangGraph state with the broadcast
body so the supervisor can reference it when answering "is this still
on?" type messages.

## Step 7 — Get the agent

```python
agent = await agent_manager.get_agent(company, agent_config)
langfuse_handler = CallbackHandler()
config = {
    "configurable": {"thread_id": thread_id},
    "recursion_limit": 25,
    "callbacks": [langfuse_handler],
}
```

`AgentManager.get_agent` returns the cached compiled LangGraph
`StateGraph` for `<company_id>:<agent_config_id>` (or compiles a new
one). `recursion_limit=25` is the LangGraph node-execution cap;
combined with `ToolCallLimitMiddleware(run_limit=10)` on the agent
itself, this is the safety net against infinite tool loops.

`CallbackHandler()` from `langfuse.langchain` is a per-invocation
callback so every model/tool span is captured.

## Step 8 — Invoke

```python
subagent_usage_accumulator.set([])

result = await agent.ainvoke(
    {"messages": [HumanMessage(content=content_blocks)]},
    config=config,
)
```

`subagent_usage_accumulator` is a contextvar (see
`src/ai/tools/agent_wrappers.py`) that sub-agent tool wrappers append
their token usage into. We reset it before each turn and read it back
during usage accounting.

`agent.ainvoke(...)` runs the supervisor's compiled graph. The graph
invokes tools (including sub-agents wrapped as tools); the
checkpointer persists each step.

## Step 9 — Apply session TTL

```python
await checkpointer_manager.apply_session_ttl(
    thread_id=thread_id, ttl_minutes=agent_config.session_ttl_minutes
)
await CartManager.apply_ttl(
    thread_id=thread_id,
    ttl_seconds=agent_config.session_ttl_minutes * 60,
)
```

After every successful turn, refresh the TTL on the LangGraph
checkpoint keys and the cart key. `agent_config.session_ttl_minutes`
defaults to 5 — short, because each new turn extends it. If the
customer goes silent, the conversation expires and the next message
starts fresh.

## Step 10 — Parse the response

```python
response_content = result["messages"][-1].content
response_messages = parse_response_messages(response_content)

langfuse.update_current_span(output=response_messages)
```

`parse_response_messages` lives in `src/ai/parsers/agent_response.py`.
It transforms the supervisor's final `AIMessage.content` (a string or
list of blocks) into the typed `ResponseMessage[]` the API returns.
The parser handles the `[IMAGEM: <url>]` markers — every line that
matches `_IMAGE_MARKER_RE` becomes an `image` ResponseMessage and
preceding text becomes its caption.

## Step 11 — Usage accounting

```python
usage = UsageCalculator.extract(
    result["messages"],
    model=settings.supervisor_model,
    subagent_usage=subagent_usage_accumulator.get(),
)

if usage:
    asyncio.create_task(
        ConversationMetricService().save(
            company_id=...,
            agent_config_id=...,
            thread_id=...,
            ...
            model_breakdown=usage.get("model_breakdown", []),
        )
    )
score_usage(usage)
```

`UsageCalculator.extract` (in `src/application/usage/usage_calculator.py`)
sums input/output tokens across the supervisor turn + each sub-agent
invocation that wrote into the accumulator. It computes per-model cost
using `MODEL_PRICING` from `src/infra/config.py`.

The `ConversationMetricService.save(...)` call is wrapped in
`asyncio.create_task(...)` — the response doesn't wait on the metric
write. The save lives in `src/application/conversation_metric/`.

`score_usage` (in `src/infra/observability.py`) attaches the cost to
the langfuse trace so dashboards can surface per-message economics.

## Step 12 — Handoff detection

```python
handoff_messages, transfer_info = await _handle_handoff(
    result["messages"], agent_config, company.company_id, thread_id, customer_phone,
)
if handoff_messages is not None:
    response_messages = handoff_messages

if transfer_info:
    tag_handoff(transfer_info["reason_code"])
```

`_handle_handoff` (top of `orchestrator.py`):

1. Calls `HandoffEventService.extract_transfer_info(result_messages)`
   to look for a `__transfer__` marker in any tool output.
2. If a transfer is found, resolves the reason label
   (system reasons + customer-defined custom reasons).
3. Resolves the actual handoff message via `resolve_handoff_message`
   (`src/domain/handoff/schemas.py`) — supports per-reason overrides
   from `agent_config.handoff_message_overrides`.
4. Sets the cooldown via `set_cooldown(company_id, customer_phone, ttl_seconds)`.
5. Persists a `HandoffEvent` via `HandoffEventService().save(...)`.
6. Calls `checkpointer_manager.clear_session(thread_id)` so the next
   message starts fresh once cooldown expires.
7. Returns the handoff message as the response (replacing whatever the
   supervisor produced) plus the `transfer_info` payload.

`tag_handoff` adds a langfuse tag so handoff traces are filterable.

## Final return

```python
return {
    "messages": response_messages,
    "thread_id": thread_id,
    "agent_config_id": str(agent_config.id),
    "usage": usage,
    "transfer_info": transfer_info,
}
```

The endpoint (`api/endpoints/chat.py`) shapes this into the
`ChatResponse` HTTP schema.

The `finally: clear_context()` removes the bound contextvars so the
next request in the same worker doesn't inherit them.

## Editing the orchestrator safely

`run_conversation` is the load-bearing function in this codebase.
Process when changing it:

1. Add a unit test in `tests/unit/ai/test_orchestrator.py` for the new
   behavior **before** editing.
2. The orchestrator has no integration test (it would require Valkey +
   real LLM). Rely on:
   - The handoff extraction + label resolution unit tests
   - The cooldown gate logic
   - The langfuse evaluation suite (separate from `make test`) for
     end-to-end verification
3. Don't add business logic here — push it into `application/<feature>/`
   or `ai/agents/<feature>/` and call from the orchestrator.
4. Don't add new entries to the return dict without updating
   `src/api/schemas/response.py:ChatResponse` and the chat endpoint.
5. Don't change `thread_id` shape — too many things key on it
   (LangGraph checkpoints, cart, langfuse session_id, downstream
   metrics).

## File pointers

- Orchestrator: `src/ai/orchestrator.py`
- AgentManager: `src/ai/agent_manager.py`
- CheckpointerManager: `src/infra/checkpointer.py`
- MessagePreprocessor: `src/application/message/message_preprocessor.py`
- Response parser: `src/ai/parsers/agent_response.py`
- Usage calculator: `src/application/usage/usage_calculator.py`
- Handoff service: `src/application/handoff/handoff_event_service.py`
- Handoff cooldown: `src/application/handoff/handoff_cooldown.py`
- Cart manager: `src/ai/tools/cart.py`
- Sub-agent wrapper: `src/ai/tools/agent_wrappers.py`
  (`subagent_usage_accumulator`)
- Langfuse helpers: `src/infra/observability.py`
  (`build_trace_tags`, `score_usage`, `tag_handoff`)
- Tests:
  `tests/unit/ai/test_orchestrator.py`,
  `tests/unit/ai/test_agent_manager*.py`
