---
name: e2e-testing
description: Guia de regras e padrões para escrever testes E2E no projeto zoppy-e2e-api (Playwright). Use esta skill sempre que o usuário quiser criar, editar ou revisar testes E2E de API, adicionar cobertura para um endpoint novo, escrever testes para a Partners API, webhooks, APIs internas (PVT) ou Segment. Acione também em frases como "cria o teste e2e", "adiciona cobertura e2e", "escreve o spec", "testa o endpoint X", "adiciona o e2e da partners api".
---

# E2E Testing Guidelines

Rules and patterns for end-to-end tests in `zoppy-e2e-api` (Playwright-based).

## Quando usar E2E

O `zoppy-e2e-api` é voltado para testar **endpoints que não são consumidos diretamente pelo nosso frontend**. Isso inclui:

-   **Partners API** — endpoints consumidos por integrações de parceiros via ExternalToken (`/customers`, `/orders`, `/coupons`, etc.)
-   **Webhooks** — endpoints públicos que recebem callbacks de serviços externos (WhatsApp, Wake Commerce, PDV, etc.)
-   **APIs internas (PVT)** — endpoints consumidos entre serviços internos
-   **Segment/OpenSearch** — endpoints de consulta analítica que precisam de paridade entre MySQL e OpenSearch

Para endpoints consumidos pelo frontend (zoppy-FE), os testes e2e ficam no próprio frontend com Cypress/Playwright browser-based. O `zoppy-e2e-api` testa **apenas a camada HTTP da API**, sem browser.

## Project Structure

```
zoppy-e2e-api/
├── src/
│   ├── shared/                    # Shared utilities
│   │   ├── auth/                  # Auth resolution (global login + refresh token)
│   │   ├── client/                # HTTP client (E2EApiClient)
│   │   └── fixtures/              # Base Playwright fixture
│   ├── zoppy-api/                 # Core API tests
│   │   ├── endpoints/             # E2eHttpApiBase + endpoint definitions
│   │   └── segment/              # Segment-specific tests
│   └── zoppy-partners/           # Partners API tests
│       ├── endpoints/             # PartnersApi endpoint definitions
│       ├── fixtures/              # Partners fixture (ExternalToken auth)
│       └── <entity>/             # One folder per entity
├── playwright.config.ts
└── .env.e2e
```

## Authentication

The e2e suite uses **global login** flow:

1. `POST /api/login/global` with `E2E_USER_EMAIL` / `E2E_USER_PASSWORD`
2. `PUT /api/refresh-token-company` with the global token + `E2E_COMPANY_ID`

Partners tests use a separate `E2E_PARTNERS_TOKEN` (ExternalToken) configured in `.env.e2e`.

## Writing Tests

### Partners API Tests

Use the `partners` fixture and `PartnersApi` helper class:

```typescript
import { test, expect } from '@zoppy-partners/fixtures/partners.fixture';
import { PartnersApi } from '@zoppy-partners/endpoints/partners-endpoints';
import type { APIRequestContext, APIResponse } from '@playwright/test';

test.describe('Entity API', () => {
    test.describe('GET /entity — list', () => {
        test('returns 200 with valid pagination', async ({ partners }: { partners: APIRequestContext }) => {
            const res: APIResponse = await PartnersApi.get(
                partners,
                'entities',
                {},
                {
                    after: '2020-01-01',
                    page: '1',
                    pageSize: '10'
                }
            );
            expect(res.status()).toBe(200);
            const body: any = await res.json();
            expect(Array.isArray(body.data)).toBe(true);
        });
    });
});
```

### Adding New Endpoints

1. Add the route to `src/zoppy-partners/endpoints/partners-endpoints.ts`:

```typescript
const ENDPOINTS: Record<string, string> = {
    // ...existing
    newEntity: '/new-entity',
    newEntityById: '/new-entity/:id'
};
```

2. Create the test folder and spec file:

```
src/zoppy-partners/new-entity/new-entity.spec.ts
```

### Test Categories

**Validation tests** — verify that invalid input returns the correct error status:

```typescript
test('returns 400 without required field', async ({ partners }) => {
    const res = await PartnersApi.post(partners, 'entities', {
        /* missing field */
    });
    expect(res.status()).toBe(400);
});
```

**Not found tests** — verify 404 for non-existent entities:

```typescript
test('returns 404 for non-existent id', async ({ partners }) => {
    const res = await PartnersApi.get(partners, 'entityById', { id: '00000000-0000-0000-0000-000000000000' });
    expect(res.status()).toBe(404);
});
```

**CRUD flow tests** — full lifecycle in a single test:

```typescript
test('creates, finds, updates and deletes', async ({ partners }) => {
    // Create
    const createRes = await PartnersApi.post(partners, 'entities', payload);
    expect(createRes.status()).toBe(200);
    const { id } = await createRes.json();

    // Find
    const findRes = await PartnersApi.get(partners, 'entityById', { id });
    expect(findRes.status()).toBe(200);

    // Update
    const updateRes = await PartnersApi.put(partners, 'entityById', updatedPayload, { id });
    expect(updateRes.status()).toBe(200);

    // Delete
    const deleteRes = await PartnersApi.delete(partners, 'entityById', { id });
    expect(deleteRes.status()).toBe(200);
});
```

**Smoke tests** — for endpoints that are hard to fully test (e.g., webhooks):

```typescript
test('returns expected status (endpoint is reachable)', async ({ partners }) => {
    const res = await PartnersApi.get(partners, 'webhookEndpoint', { id: 'dummy' });
    expect([400, 422].includes(res.status())).toBe(true);
});
```

### Serial Execution

If tests within a `describe` depend on execution order (e.g., create must run before duplicate check), mark the block as serial:

```typescript
test.describe('POST /entity — create', () => {
    test.describe.configure({ mode: 'serial' });

    test('creates entity', async ({ partners }) => { ... });
    test('returns 422 for duplicate', async ({ partners }) => { ... });
});
```

## Status Code Conventions

| Scenario                         | Expected Status |
| -------------------------------- | --------------- |
| Success                          | 200             |
| Missing required field           | 400             |
| Entity not found                 | 404             |
| Validation/business rule failure | 422             |
| Server error                     | 500             |

Do NOT expect 422 for "not found" scenarios — that's 404. Reserve 422 for validation failures (invalid data format, business rule violations, duplicate entries).

## Running Tests

```bash
# Full suite
npm run e2e

# Partners only
npx playwright test src/zoppy-partners/

# Specific entity
npx playwright test src/zoppy-partners/customers/

# With Allure report
npm run e2e:report
```

## Environment Variables

Required in `.env.e2e`:

| Variable                    | Description                         |
| --------------------------- | ----------------------------------- |
| `E2E_API_BASE_URL`          | Main API base URL                   |
| `E2E_API_PARTNERS_BASE_URL` | Partners API base URL               |
| `E2E_USER_EMAIL`            | Global user email for login         |
| `E2E_USER_PASSWORD`         | Global user password                |
| `E2E_COMPANY_ID`            | Target company ID for token refresh |
| `E2E_PARTNERS_TOKEN`        | ExternalToken for partners API      |
| `E2E_ZOPPY_ACCESS`          | Cloudflare Access header (optional) |
