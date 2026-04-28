---
name: ecommerce-provider
description: >
  How to add a new e-commerce provider integration to
  zoppy-whatsapp-commerce (Shopify is the reference implementation;
  Nuvemshop is the second variant). Covers the full surface a provider
  needs: HTTP client class with async context manager, @tool factory,
  optional admin/order-status tool, two-registry registration, the
  catalog sub-agent (shared CatalogSearchResult schema), provider-aware
  routing in the sub-agent registry, optional response-compactor
  middleware, prompt branches for provider quirks (Nuvemshop has no
  cart, link rule differs), and the AgentConfig.provider CHECK
  constraint. Use this skill whenever onboarding a new platform
  (Shopify, VTEX, WooCommerce, NuvemShop, Dooca, Tray, Yampi, …),
  adding catalog search to an existing provider, splitting a provider's
  toolset, or troubleshooting why an agent ends up with no catalog
  tools. Triggers on: "add provider", "novo provider", "new e-commerce
  provider", "Shopify integration", "Nuvemshop integration", "VTEX",
  "WooCommerce", "Dooca", "Tray", "Yampi", "create_<provider>_tools",
  "<Provider>Client", "catalog search", "search products", "iterative
  search", "MCP catalog", "storefront API", "admin API", "provider
  registry", "provider routing", "company.provider", "integrations.url",
  "integrations.key", "integrations.admin", "response compactor".
---

# E-commerce Provider — zoppy-whatsapp-commerce

Adding a new platform integration touches multiple layers because the
catalog search surface is wide. The good news is the project has a
**reference implementation (Shopify)** and a **second variant
(Nuvemshop)** that prove the seams, so the work is mostly cookie-cutter
once you know the contract.

## What "provider" means in this codebase

The `Company.provider` column (`src/domain/company/model.py`) holds a
short identifier:

```
shopify | vtex | woocommerce | nuvemshop | dooca | tray
```

The CHECK constraint in the initial migration enforces this set
(`migrations/versions/fb801f698202_initial_schema.py`):

```python
sa.CheckConstraint(
    "provider IN ('shopify', 'vtex', 'woocommerce', 'nuvemshop', 'dooca', 'tray') "
    "OR provider IS NULL",
    name='check_valid_provider',
)
```

**Adding a new provider value requires an Alembic migration** to update
that CHECK. See the `alembic-migration` skill.

The `Company.integrations` aggregate
(`src/domain/company/schemas.py:IntegrationConfig`) carries the
per-provider credentials in a flat shape:

| Field | Shopify uses | Nuvemshop uses | Notes |
|---|---|---|---|
| `url` | shop domain (`my-shop.myshopify.com`) | — | "do they have an integration?" gate |
| `admin` | Shopify Admin API token | — | Optional — gates order_status tool |
| `key` | — | OAuth access token | "do they have an integration?" gate |
| `secret` | — | store_id | Provider-specific use |
| `name` | display name | display name | UI |

When you add a provider, decide which of these fields you'll consume.
**Don't add new columns** unless absolutely required — repurpose
existing ones to avoid migration churn.

## The full surface a provider needs

A complete provider integration consists of (Shopify as reference):

```
src/ai/tools/<provider>.py
├── <Provider>StorefrontClient (or <Provider>Client)  # main HTTP client
├── <Provider>AdminClient                             # optional, for admin API
└── create_<provider>_tools(...)                      # @tool factory

src/ai/middlewares/<provider>.py        # optional, response compactor
src/ai/agents/subagents/catalog[_<provider>]/
├── agent.py                            # only when the prompt or tools differ
└── prompt.py                           # provider-specific iterative-search rules

src/domain/company/model.py             # the CHECK constraint includes the new value (via Alembic)
src/ai/agents/registry.py               # _get_sales_tools branches per provider
src/ai/agents/subagents/registry.py     # get_subagent_factory routes per provider
src/ai/tools/registry.py                # create_tools_for_company routes per provider
src/ai/agents/sales/prompt.py           # link_rule + product_example_extra for the new provider
```

Not every step is needed every time — read the "Decide what to write"
table below before coding.

## Reference implementation — Shopify

Shopify is the canonical reference because:

- It has both a **Storefront** (catalog search via Shopify MCP) and an
  **Admin** API (order_status), so it exercises the full split.
- It has a **response compactor** middleware
  (`ShopifyResponseCompactorMiddleware`) — the canonical pattern for
  trimming large tool responses.
- It uses the shared catalog sub-agent (no `_nuvemshop`-style fork) —
  the canonical sub-agent path.
- It supports **cart tools** (`create_cart_tools` in `src/ai/tools/cart.py`)
  with checkout permalinks. Most providers will not have this.

When you add a provider, model your work on Shopify first, then
diverge only where the upstream API forces you to.

### `src/ai/tools/shopify.py` — the reference file

The shape (see the file for the full code):

```python
class ShopifyStorefrontClient:
    def __init__(self, shop_domain: str):
        # Strip protocol + trailing slash, normalize the host
        if shop_domain.startswith(("http://", "https://")):
            parsed = urlparse(shop_domain)
            shop_domain = parsed.netloc or parsed.path
        self.shop_domain = shop_domain.rstrip("/")
        self.base_url = f"https://{self.shop_domain}/api/mcp"
        self.timeout = 30.0  # catalog search is long-running

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def search_products(self, query: str, intent: str = "") -> str:
        # 1. Build provider-specific payload
        # 2. POST with logger.info("<provider>.search.started", ...)
        # 3. Map upstream errors to friendly strings
        # 4. Return either a JSON string or a friendly message
        ...


class ShopifyAdminClient:
    # GraphQL (Admin API) for order_status — optional, gated by admin_token
    ...


def create_shopify_tools(
    shop_domain: str, admin_token: str = "", store_context: str = ""
) -> list:
    @tool
    async def shopify_search_products(query: str) -> str:
        """..."""
        async with ShopifyStorefrontClient(shop_domain) as client:
            return await client.search_products(query=query, intent=...)

    tools = [shopify_search_products]
    if admin_token:
        @tool
        async def order_status(order_number: str) -> str:
            """..."""
            async with ShopifyAdminClient(shop_domain, admin_token) as client:
                return await client.get_order_by_name(order_number)
        tools.append(order_status)
    return tools
```

Anatomy you must replicate:

1. **Dedicated client class** with `__aenter__` / `__aexit__` — managed
   by `async with` from inside the `@tool`. Connections close
   deterministically.
2. **Domain normalization** — accept whatever the customer typed
   (`my-shop.com`, `https://my-shop.com/`, `my-shop.myshopify.com`) and
   normalize to a host. The client constructor is the seam.
3. **Timeouts.** `30.0` for search (long upstream), `15.0` for admin /
   small ops. Never `None`.
4. **Structured logger calls** at each step:
   `<provider>.<action>.started/completed/failed/<error_type>`.
5. **Map every upstream error class to a user-friendly string.**
   `httpx.HTTPStatusError` (404 / 401 specific), `httpx.RequestError`,
   bare `Exception`. The model has to read the return string — strip
   stack traces.
6. **Optional admin tool gated by token.** The factory pattern returns
   a `list`; conditionally append the second tool if the credential is
   present.
7. **Return strings** — see `ai-tool` skill. JSON-stringified for
   structured payloads (errors, order_status), plain text for
   model-rewritable content (catalog).

See the `ai-tool` skill for tool-level conventions and the
`code-conventions` skill for HTTP / async / logging idioms.

## Provider-aware routing — three registries

Three places route based on `company.provider`:

### 1. `_get_sales_tools` in `src/ai/agents/registry.py`

The supervisor's toolset for the **sales** agent type. Dispatches per
provider with explicit branches:

```python
provider = company.provider or "shopify"
has_integration = (
    company.integrations.key
    if provider == "nuvemshop"
    else company.integrations.url
)

if has_integration:
    if provider == "nuvemshop":
        pass  # Nuvemshop has no cart tools — links go directly in prompt
    else:
        from src.ai.tools.cart import create_cart_tools
        from src.ai.tools.shopify import create_order_status_tool

        tools.extend(
            create_cart_tools(
                shop_domain=company.integrations.url or "",
                session_ttl_minutes=session_ttl_minutes,
            )
        )
        order_tool = create_order_status_tool(
            shop_domain=company.integrations.url or "",
            admin_token=company.integrations.admin or "",
        )
        if order_tool:
            tools.append(order_tool)
```

When adding a provider, decide:

- **Does the supervisor itself need a tool from this provider?**
  Order status, cart, giftback — likely yes. Push them here.
- **Or is everything sub-agent territory?** (catalog search is always
  sub-agent.) If so, this file doesn't change.

### 2. `get_subagent_factory` in `src/ai/agents/subagents/registry.py`

Decides which sub-agent factory handles `catalog_search` for a given
provider:

```python
if name == "catalog_search":
    provider = (company_config.provider if company_config else None) or "shopify"
    if provider == "nuvemshop":
        return create_catalog_nuvemshop_subagent
    return create_catalog_subagent
```

When adding a provider, choose:

- **Reuse `create_catalog_subagent`** (Shopify path) when your tool
  returns the same shape as Shopify and the search-relaxation strategy
  in `agents/subagents/catalog/prompt.py` works as-is. Default choice.
- **Fork to `create_catalog_<provider>_subagent`** only when prompt
  rules genuinely differ (e.g. Nuvemshop forks because there's no
  cart, the agent has to emit product page URLs directly, and the
  search shape is different enough).

### 3. `create_tools_for_company` in `src/ai/tools/registry.py`

Sub-agent toolsets, bucketed:

```python
provider = company_config.provider or "shopify"

if provider == "nuvemshop" and company_config.integrations.key:
    tools["catalog"].extend(
        create_nuvemshop_tools(
            store_id=company_config.integrations.secret or "",
            access_token=company_config.integrations.key,
        )
    )
elif provider == "nuvemshop" and not company_config.integrations.key:
    logger.warning("tools_registry.nuvemshop_missing_key", company_id=...)
elif company_config.integrations.url:
    tools["catalog"].extend(create_shopify_tools(...))
    tools["cart"].extend(create_cart_tools(...))

tools["support"].extend(create_knowledge_tools())
```

Always add a `logger.warning("tools_registry.<provider>_missing_<credential>", ...)`
branch — it's how production debugging starts when a company is
half-onboarded.

## The shared catalog schema

All catalog providers should map their upstream payloads to the same
Pydantic shape:

```
src/ai/agents/subagents/catalog/schemas.py
├── PriceRange
├── ProductVariant         # variant_id, title, price, currency, image_url, available
├── Product                # product_id, title, description, url, image_url,
│                          # price_range, product_type, tags, variants
│   └── has_available_variants  (computed)
├── AvailableFilter
├── Pagination
├── CatalogSearchResult    # products, message, pagination, available_filters,
│                          # query, total_products, has_results
│   └── available_products (computed: products with at least one available variant)
└── CatalogErrorResponse   # error_type, message, query, suggestion
```

This shape is **shared across providers** so the supervisor (and
downstream parsers) can speak one language regardless of the upstream
platform. Nuvemshop builds `Product` instances directly from the API
response; Shopify parses an MCP JSON blob into the same shape via
`src/ai/middlewares/shopify.py:parse_mcp_json_to_catalog`.

When adding a provider, write a parser that targets these classes —
do not invent a parallel shape. The supervisor's prompt and the
response compactor both depend on this contract.

## Response compactor middleware (when output is large)

Catalog responses tend to be huge — full product objects with all
variants, descriptions, and available_filters. Without compaction,
they blow the context window or starve the model of attention.

`src/ai/middlewares/shopify.py:ShopifyResponseCompactorMiddleware`:

1. Reads the raw tool output
2. Parses it into a `CatalogSearchResult` via `parse_mcp_json_to_catalog`
3. Trims to the fields the supervisor actually consumes (drops verbose
   variant attributes, keeps id + title + price + image)
4. Re-serializes into a compact JSON string
5. Logs the size delta (`shopify_middleware.search_optimized`)

The catalog sub-agent factory adds the middleware conditionally
(`src/ai/agents/subagents/catalog/agent.py:_build_middleware`):

```python
def _build_middleware(company_config: CompanyConfig) -> list:
    provider = company_config.provider or "shopify"
    middleware = [
        ModelRetryMiddleware(max_retries=2, on_failure="continue"),
        ToolRetryMiddleware(max_retries=2, backoff_factor=2.0, initial_delay=1.0),
        ToolCallErrorHandlerMiddleware(),
    ]
    if provider != "nuvemshop":
        middleware.append(ShopifyResponseCompactorMiddleware())
    middleware.append(ToolCallLimitMiddleware(run_limit=10))
    return middleware
```

Nuvemshop's tool already returns compact data, so it's exempt.

When adding a provider:

- If the upstream returns large payloads, write a paired compactor
  middleware (`src/ai/middlewares/<provider>.py`) and add it to the
  catalog sub-agent's middleware stack.
- The compactor must produce the same `CatalogSearchResult` shape so
  the parser stays portable.

## Prompt quirks per provider

`src/ai/agents/sales/prompt.py:get_sales_prompt` branches on
`provider`:

```python
if provider == "nuvemshop":
    link_rule = "- ALWAYS include the product Link for each product. ..."
    product_example_extra = "\nLink: https://loja.com/vestido-floral"
else:
    link_rule = "- Do NOT write product page URLs as text for the customer."
    product_example_extra = ""
```

The branch is structural: providers without cart tools (Nuvemshop) need
the agent to surface URLs directly so the customer can click through.
Providers with cart tools (Shopify) suppress URLs because cart_finalize
emits the link.

When adding a provider:

- **Has a cart-equivalent flow?** Default `link_rule` (suppress URLs).
- **No cart-equivalent flow?** Fork like Nuvemshop: instruct the agent
  to include product page URLs directly.

The catalog sub-agent prompt (`agents/subagents/catalog/prompt.py` or
`catalog_<provider>/prompt.py`) carries the iterative-search rules:

```
Maximum tool calls: 5
Strategy:
1. Short query first — 2-4 keywords ("blusa vermelha", "mesa madeira")
2. If < 3 results: Remove one non-critical attribute ("blusa", "mesa")
3. If still insufficient: Try related categories
4. If still insufficient: Broaden to general category
5. Last resort: Try synonym or alternative terms
```

Most providers should reuse Shopify's prompt as-is. Fork only if the
upstream search semantics are wildly different (Nuvemshop forked
because category-based search is the natural Nuvemshop API path,
whereas Shopify uses MCP-style natural language).

## Decide what to write — quick reference

| Question | Yes | No |
|---|---|---|
| Does the upstream provide catalog search? | Write `<Provider>Client.search_products` | You're not really adding a provider — you're adding a different kind of tool |
| Does the upstream have an admin / order-status API? | Write a second client class + tool, gate by token field on `IntegrationConfig` | Skip the admin client |
| Does the upstream have cart / checkout? | Reuse `create_cart_tools` if Shopify-shape; otherwise document why not | Branch in `_get_sales_tools` like Nuvemshop |
| Are catalog responses > ~5 KB typical? | Write a response compactor middleware | Skip; the raw payload is fine |
| Does iterative search (the relaxation strategy) work as-is? | Reuse `agents/subagents/catalog/` | Fork to `agents/subagents/catalog_<provider>/` |
| Need to expose URLs in the chat (no cart)? | Branch `link_rule` in `get_sales_prompt` like Nuvemshop | Default Shopify behavior |
| Existing IntegrationConfig fields cover the credentials? | Repurpose `url` / `key` / `admin` / `secret` | Add the field via Alembic — discuss before |

## End-to-end checklist for a new provider

1. **`Company.provider` accepts the new value.**
   - Update the CHECK constraint in a new Alembic migration.
   - Update `src/domain/company/model.py` if it has a literal /
     enum (it currently uses a free-form string, so the migration is
     enough).
2. **Decide which `IntegrationConfig` fields you'll consume.**
3. **Write `src/ai/tools/<provider>.py`** with:
   - `<Provider>Client` (storefront / catalog search)
   - Optional `<Provider>AdminClient` (order status, account ops)
   - `create_<provider>_tools(...)` factory
   - Helper `create_<provider>_order_status_tool(...)` if you want
     supervisor-level access
4. **Catalog mapping**: parse the upstream payload into
   `src/ai/agents/subagents/catalog/schemas.py:CatalogSearchResult`.
5. **Response compactor (optional)** at
   `src/ai/middlewares/<provider>.py`. Add to the catalog sub-agent
   middleware stack.
6. **Sub-agent factory**: reuse `create_catalog_subagent` if possible.
   Fork to `src/ai/agents/subagents/catalog_<provider>/agent.py` only
   if necessary.
7. **Register** in three places:
   - `src/ai/agents/registry.py:_get_sales_tools` — supervisor tool
     dispatch
   - `src/ai/agents/subagents/registry.py:get_subagent_factory` —
     sub-agent dispatch (only if forking)
   - `src/ai/tools/registry.py:create_tools_for_company` — sub-agent
     buckets, with a `logger.warning` for half-onboarded companies
8. **Prompt branches**:
   - `src/ai/agents/sales/prompt.py:get_sales_prompt` — `link_rule` +
     `product_example_extra` if the provider has no cart
   - `src/ai/agents/subagents/catalog<_provider>/prompt.py` — only if
     you forked the sub-agent
9. **Tests**:
   - `tests/unit/ai/tools/test_<provider>.py` — happy path, 4xx, 5xx,
     timeout, empty result, malformed payload
   - `tests/unit/ai/agents/subagents/catalog<_provider>/test_*.py` if
     forked
   - Update `tests/unit/ai/agents/sales/test_prompt_golden.py` to
     cover the new provider's prompt variant
10. **Webhook handler (optional)** — if the platform pushes updates to
    `/webhooks/integration/synced`, decide whether the existing
    handler covers it or you need a per-provider one. See the
    `webhook-handler` skill (Wave 4, future) for the contract.

## Gotchas / anti-patterns

- **Don't invent a new product shape.** Map upstream → existing
  `CatalogSearchResult`. Parallel shapes break the supervisor prompt
  and the parser.
- **Don't add `Company.provider` values without an Alembic CHECK
  update.** The DB will reject the row.
- **Don't put credentials in `Company` columns.** They live on
  `IntegrationConfig` (and the upstream OAuth flow writes them via the
  `integration/synced` webhook).
- **Don't read tokens out of env vars inside tools.** Tokens are
  per-tenant — they come from `CompanyConfig.integrations.*` via the
  registry closures. Env vars only hold global secrets (OpenAI key,
  Langfuse key).
- **Don't forget the `logger.warning` for half-onboarded companies.**
  Production support relies on it.
- **Don't add cart tools for a provider that has no checkout API.**
  The supervisor will offer a non-existent flow. Branch like
  Nuvemshop and route the customer to the product page URL.
- **Don't bypass the response compactor for large payloads.** Context
  window pain is silent until it isn't. If output is large, write a
  compactor.
- **Don't hardcode `provider == "shopify"` as a fallback elsewhere.**
  The `provider or "shopify"` pattern is intentional and lives only in
  the three registries. Other code reads from `company.provider`
  directly.

## Pre-PR checklist

- [ ] New provider value documented in
      `src/domain/company/model.py` comments and added to the CHECK
      constraint via a new Alembic migration
- [ ] `src/ai/tools/<provider>.py` exists with
      `<Provider>Client` + `create_<provider>_tools`
- [ ] Optional admin client + factory only if upstream has an admin API
- [ ] Catalog responses parsed into `CatalogSearchResult`
- [ ] Response compactor at `src/ai/middlewares/<provider>.py` (or
      documented decision not to)
- [ ] Sub-agent reuse vs fork decided and justified in the PR
      description
- [ ] Three registries updated:
      `agents/registry.py`, `agents/subagents/registry.py`,
      `tools/registry.py`, with `logger.warning` for missing
      credentials
- [ ] Prompt: `link_rule` + `product_example_extra` branched in
      `agents/sales/prompt.py` if no cart-equivalent flow
- [ ] Tests in `tests/unit/ai/tools/test_<provider>.py` covering
      happy + 4xx/5xx/timeout/malformed/no-tenant-context
- [ ] Prompt-golden tests updated for the new provider variant
- [ ] `uv run pytest tests/unit/ai/ -q` is green
- [ ] One real company in staging migrated to verify the end-to-end
      flow before merging
