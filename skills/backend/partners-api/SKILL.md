---
name: partners-api
description: >
  Partners API specifics for zoppy-api: port 8082, ExternalToken authentication, no /api prefix,
  separate Swagger. Use this skill whenever working on the Partners API environment, creating or
  modifying partners endpoints, or asked about external partner integrations. Triggers on:
  "partners API", "Partners environment", "PARTNERS service", "external token", "ExternalToken",
  "port 8082", "partners endpoint", "api parceiros", "autenticação parceiros", "partners swagger",
  "PartnersExternalAuthMiddleware", "initializePartnersSwagger".
---

# Partners API

The Partners API runs as a separate service environment (`API_SERVICE_ENVIRONMENT=PARTNERS`) on **port 8082**.

## Key Differences from the Main API

| | Main API | Partners API |
|---|---|---|
| Port | 8080 | 8082 |
| URL prefix | `/api/...` | `/` (no prefix) |
| Authentication | JWT Bearer token | `ExternalToken` lookup |
| Validation pipe | Strict (whitelist, forbidNonWhitelisted) | Permissive (no whitelist) |
| Swagger | `/api/docs` | `/docs` |

## Endpoints

Partners endpoints are at the root — no `/api` prefix:

```
GET  /customers        (not /api/customers)
POST /coupons
GET  /orders
```

## Authentication

Partners authenticate via `PartnersExternalAuthMiddleware`, which looks up an `ExternalToken` record (not a JWT). The token is passed in the request header and resolved to a company context.

```typescript
// The middleware handles auth — controllers don't need @UseGuards(RoleGuard(...))
// for partners endpoints, but do need @IsPublic() to bypass JWT guard
@IsPublic()
@Get('customers')
public async list(): Promise<CustomerResponse[]> { ... }
```

## Swagger

The Partners API has its own Swagger instance initialized via `initializePartnersSwagger()` (separate from the main API Swagger). It's available at `/docs` on port 8082.

## Important Notes

- **SysMiddle endpoints were intentionally removed** (partnership cancelled) — do not re-add them
- The more permissive validation pipe means partners can send extra fields without a 400 error — this is intentional for forward compatibility
- Partners controllers live in `src/access/http/controllers/partners/` (or similar) — keep them separate from main API controllers
