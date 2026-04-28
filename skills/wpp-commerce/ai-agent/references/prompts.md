# Sales prompt internals

This reference complements the `ai-agent` skill. Read the main
`SKILL.md` first.

The supervisor (`sales`) system prompt is assembled in
`src/ai/agents/sales/prompt.py:get_sales_prompt`. The output is the
literal string passed as `system_prompt=` to LangGraph's `create_agent`.

## Assembly order

```
<system_rules>...</system_rules>
\n\n
<style_preferences>...</style_preferences>
\n\n
<store_context>...</store_context>
\n\n
<tools>...</tools>
\n
```

Blank lines between blocks are intentional — they make the structure
legible to the model.

The four `_build_*` helpers are all in the same file:

| Block | Helper | Roughly responsible for |
|---|---|---|
| `<system_rules>` | `_build_system_rules(caps, link_rule)` (l.214) | Decision tree, formatting rules, tool orchestration constraints, link policy, image rules |
| `<style_preferences>` | `_build_style_preferences(agent_config, product_example_extra)` (l.378) | Customer-tunable behavior — see `style_renderer` |
| `<store_context>` | `_build_store_context(company, agent_config)` (l.323) | Store facts: brand_name, brand_tone, brand_description, target_audience, integration metadata, tone of voice |
| `<tools>` | inline | `_build_tool_orchestration(caps)` (l.63) + `_build_handoff_reasons(reasons)` (l.17) |

## ToolCapabilities

`get_sales_prompt` first builds a `ToolCapabilities` dataclass:

```python
caps = ToolCapabilities(
    provider=provider,                                       # "shopify" / "nuvemshop" / ...
    has_cart=bool(company.integrations.url) and provider != "nuvemshop",
    has_giftback=bool(company.partners_token),
    has_knowledge_base="knowledge_search" in agent_config.enabled_subagents,
    has_order_status=bool(company.integrations.admin) and provider != "nuvemshop",
)
```

Each `_build_*` helper consumes `caps` to gate prompt sections by what
the company actually has. **The prompt only describes capabilities the
agent really has** — nothing wishful.

## `<system_rules>` block

Built by `_build_system_rules(caps, link_rule)`. Contents:

- The persona ("you are a sales assistant for an e-commerce store…")
- Decision tree: how to choose between answering directly, calling
  `catalog_agent`, calling `knowledge_agent`, or calling
  `transfer_to_human`
- Tool orchestration constraints (e.g. how many catalog searches before
  giving up; how to relax queries iteratively)
- Formatting constraints: link policy (`link_rule` differs between
  Shopify and Nuvemshop because Nuvemshop has no cart tools, so the
  agent must include the product page URL directly)
- Image rules: how to react to vision content blocks
- Output shape: how messages get split, when to use `[IMAGEM: <url>]`
  markers (parsed by `ai/parsers/agent_response.py`)

Most edits to "what the agent must always do" go here.

## `<style_preferences>` block

Built by `_build_style_preferences(agent_config, product_example_extra)`.
Body produced by `src/ai/agents/sales/style_renderer.py` based on the
`AgentStyle` Pydantic model on `agent_config.agent_style`.

### AgentStyle fields → prompt lines

`style_renderer.py` exposes per-field renderers that turn each enum
into a sentence. Examples:

```python
_OBJECTIVE_LINE: dict[PrimaryObjective, str] = {
    PrimaryObjective.CONVERSION: (
        "Help customers find products, build their shopping cart, and complete the sale.\n"
        "Your primary goal is conversion: guide the conversation naturally toward a "
        "completed purchase, without being pushy."
    ),
    PrimaryObjective.INFORMATION_FIRST: (
        "Help customers understand products and answer their questions clearly.\n"
        "Your primary goal is informed decision-making — recommend a purchase only "
        "when the customer has enough context."
    ),
    PrimaryObjective.MIXED: (
        "Help customers find products, answer their questions, and guide them toward "
        "a purchase when they're ready.\n"
        "Balance information and conversion equally."
    ),
}

_POSTURE_HINT: dict[SalesPosture, str] = {
    SalesPosture.CONSULTIVE: "",
    SalesPosture.OBJECTIVE: " Be direct and avoid unnecessary chatter.",
    SalesPosture.SUPPORTIVE: " Be warm, patient, and reassuring.",
    SalesPosture.AGGRESSIVE: " Push toward closing actively whenever there is buying intent.",
}
```

Adding a new AgentStyle field:

1. Add the enum and field to `src/domain/agent_config/agent_style.py`
   with a sane default (defaults reproduce legacy behavior).
2. Add a `_<field>_LINE` (or `_HINT`) dict in `style_renderer.py` mapping
   each enum value to a prompt fragment.
3. Render the fragment in `_build_style_preferences` (or in the
   relevant section of `style_renderer.py` if it exposes a builder).
4. Update any presets in `src/ai/agents/sales/presets.py` whose
   semantics include the new field.
5. Add a unit test in `tests/unit/ai/agents/sales/test_style_renderer.py`
   for each enum value.
6. Refresh the prompt golden:
   `tests/unit/ai/agents/sales/test_prompt_golden.py` — read the diff
   carefully.

### The 5 presets

`src/ai/agents/sales/presets.py`:

| Preset | sales_posture | primary_objective | upsell | length | emoji | follow-up |
|---|---|---|---|---|---|---|
| `objetivo` | objective | conversion | none | minimal | none | never |
| `consultivo` *(defaults)* | consultive | conversion | soft | concise | sparing | when_interest_shown |
| `amigavel` | supportive | mixed | soft | concise | frequent | when_interest_shown |
| `agressivo` | aggressive | conversion | proactive | concise | sparing | always_offer_cart |
| `custom` | (empty placeholder) | | | | | |

Customers select via `agent_config.preset` (and `preset_selected_at`
records when). Once selected, the preset values are copied onto
`agent_config.agent_style`; the customer can override individual
fields after that.

## `<store_context>` block

Built by `_build_store_context(company, agent_config)`. Contents:

- `Brand name: ...`
- `Brand description: ...`
- `Target audience: ...`
- `Provider: shopify | nuvemshop | ...`
- Integration metadata (URL, admin token presence — never the secret
  itself)
- `Tone of voice: <tone>` injected just before `</store_context>` from
  `agent_config.brand_tone` (see the helper's last replacement step in
  `get_sales_prompt`)

Store context is **per-company facts** — things that don't change
turn-to-turn. Anything that changes per-message belongs in
`<system_rules>` or `<style_preferences>`.

## `<tools>` block

Composed inline in `get_sales_prompt`:

```python
tool_orchestration = _build_tool_orchestration(caps)

if agent_config.handoff_reasons:
    handoff_reasons_section = _build_handoff_reasons(agent_config.handoff_reasons)
else:
    handoff_reasons_section = _build_handoff_reasons([])

tools_block = f"<tools>\n{tool_orchestration}{handoff_reasons_section}\n</tools>"
```

### `_build_tool_orchestration(caps)` (l.63)

Tells the agent which tools it has and *how* to use them — search
strategy, when to escalate to a sub-agent, what counts as enough info
to give an answer, the iterative search-relaxation strategy for
catalog queries (start exact → drop non-critical terms → expand
category, capped at 5 attempts).

### `_build_handoff_reasons(reasons)` (l.17)

Lists every available handoff reason code the agent can pass to
`transfer_to_human`:

- **System reasons** — built into `SYSTEM_HANDOFF_REASONS` in
  `src/domain/handoff/schemas.py` (always present)
- **Custom reasons** — provided by the customer via
  `agent_config.handoff_reasons` (list of `HandoffReason` rows)

Custom reasons that include a `description` also generate an
**Auto-transfer rule** appended to the prompt:

```
- <description> -> Call transfer_to_human with reason=`<code>`.
  Do NOT search the knowledge base or catalog first.
```

Auto-transfer rules take priority over the decision tree — the agent
must escalate immediately on these topics.

## Provider-specific quirks

The prompt branches in `get_sales_prompt`:

```python
if provider == "nuvemshop":
    link_rule = "- ALWAYS include the product Link for each product. ..."
    product_example_extra = "\nLink: https://loja.com/vestido-floral"
else:
    link_rule = "- Do NOT write product page URLs as text for the customer."
    product_example_extra = ""
```

Nuvemshop has no cart tool, so the agent has to include the product
page URL directly (the customer clicks through to Nuvemshop's
checkout). Shopify has the cart tool, so the agent **must not** spam
URLs in chat — the cart link comes from `cart_finalize` instead.

## Editing the prompt safely

The supervisor prompt is the highest-leverage code in the system.
Process:

1. **Always start from a prompt-golden test failure.** Edit the
   builder, run `make test`, read the golden diff, decide if every
   line is intentional.
2. **Don't add per-feature flags directly to the prompt text.** Add
   them to `ToolCapabilities` (or `agent_config`) and gate the prompt
   section on the flag.
3. **Don't write conditional grammar in the prompt** ("if X, ..., else
   ..."). Customers and models both struggle with conditionals.
   Pre-resolve in Python and emit a single, unconditional sentence.
4. **Don't put per-customer text outside `<store_context>` or
   `<style_preferences>`.** `<system_rules>` and `<tools>` should be
   identical across companies (gated only by capabilities).
5. **Run prompt-golden + presets + style_renderer tests** after any
   change.

## File pointers

- Assembly: `src/ai/agents/sales/prompt.py`
- Style rendering: `src/ai/agents/sales/style_renderer.py`
- Presets: `src/ai/agents/sales/presets.py`
- AgentStyle schema: `src/domain/agent_config/agent_style.py`
- Handoff reasons (system): `src/domain/handoff/schemas.py`
  (`SYSTEM_HANDOFF_REASONS`)
- Tests:
  `tests/unit/ai/agents/sales/test_prompt.py`,
  `test_prompt_golden.py`,
  `test_style_renderer.py`,
  `test_presets.py`
