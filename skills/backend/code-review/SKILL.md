---
name: code-review
description: >
    Code review checklist for the zoppy-api NestJS project covering architecture, PII/security, and
    performance. Use this skill whenever reviewing a PR, auditing new code, checking a controller or
    service for correctness, or verifying that sensitive data is not being exposed. Triggers on:
    "review this", "check this PR", "audit this code", "is this correct", "does this expose PII",
    "check for security issues", "review my controller", "review my service", or any code review request.
---

# Code Review Checklist

## Role

You are a code reviewer for the zoppy-api NestJS project. Apply every section of this checklist to the code under review. Group findings by severity. Reference exact file paths and line numbers. Propose a concrete fix for every BLOCKER.

---

## Severity Levels

| Level          | Meaning               | Examples                                                |
| -------------- | --------------------- | ------------------------------------------------------- |
| **BLOCKER**    | Must fix before merge | PII leak, arch violation, N+1 query, missing auth guard |
| **WARNING**    | Should fix soon       | Missing test, unhandled promise, hardcoded value        |
| **SUGGESTION** | Optional improvement  | Naming, simplification, readability                     |

---

## 1. Architecture Checklist

### Controllers (`src/access/http/`)

-   [ ] Controller is a thin facade — zero business logic inside it
-   [ ] Every endpoint has `@ExceptionInterceptor()`
-   [ ] Every non-public endpoint has `@UseGuards(RoleGuard([...]))` and `@UseGuards(BlockFreeTierGuard())`
-   [ ] Every endpoint has `@ApiOperation` and `@ApiResponse` Swagger decorators
-   [ ] Response is a typed Response DTO — never a raw Sequelize model or `Promise<any>`
-   [ ] Write endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) have `@UsingTransaction()`

```typescript
// CORRECT controller signature
@Post('campaigns')
@UseGuards(RoleGuard([RoleEnum.MASTER, RoleEnum.ADMIN]), BlockFreeTierGuard())
@ExceptionInterceptor()
@ApiOperation({ summary: 'Create campaign' })
@ApiResponse({ status: 201, type: CampaignResponse })
@UsingTransaction()
public async create(@Body() request: CreateCampaignRequest): Promise<CampaignResponse>
```

### Application Services (`src/application/`)

-   [ ] Application does NOT inject another Application — extract shared logic to a Domain or Helper
-   [ ] No direct Sequelize model access — all data access goes through Domain methods
-   [ ] `Promise.all()` used for independent async calls; sequential only when dependent
-   [ ] Mutations logged via `LogService` with entity identifier and `extraStructuredMetadata`

### Domain (`src/domain/`)

-   [ ] Domain extends `RepositoryAdapter<T>` — no raw SQL outside `rawQuery()`
-   [ ] No `include` in any Sequelize query — fetch related entities in separate calls
-   [ ] No cross-domain injection unless the relationship is strictly parent-child

---

## 2. PII / Security Checklist

These are the most critical checks. A single leaked field can be a compliance violation.

### Response DTOs

-   [ ] Response DTOs do NOT include: `email`, `phone`, `cpf`, `document`, `birthDate`, `password`, `accessToken`, `apiKey` — unless the endpoint explicitly requires exposing that field (e.g., a login response returning `token`)
-   [ ] Controllers return a typed DTO, not the raw Sequelize `Model` instance
-   [ ] If a Customer or User model is returned, verify only safe fields are included (id, name, role — not contact details)

```typescript
// BLOCKER — raw model exposes all fields including PII
public async getById(@Param('id') id: string): Promise<Customer>

// CORRECT — DTO projects only safe fields
public async getById(@Param('id') id: string): Promise<CustomerResponse>
```

### Error Logs

-   [ ] Exception interceptors and catch blocks do NOT serialize `request.body` or `request.headers` containing customer data
-   [ ] Log entries use structured metadata — do not interpolate user-supplied strings directly into log messages

### Authentication & Authorization

-   [ ] Every new webhook endpoint validates HMAC or JWT (check middleware in `src/cross-cutting/middlewares/`)
-   [ ] Guard order: `RoleGuard` before `BlockFreeTierGuard` before `FeatureGuard` — wrong order causes 403 instead of 401
-   [ ] Public endpoints are explicitly marked `@IsPublic()` — unlabeled endpoints are NOT automatically public

---

## 3. Performance Checklist

### Query Efficiency

-   [ ] No Sequelize `include` — this triggers N+1 and bypasses the `RepositoryAdapter` constraint layer
-   [ ] No O(n²) nested loops — use `Map` or `Set` for lookups when iterating over lists

```typescript
// BLOCKER — O(n²)
for (const order of orders) {
    const customer = customers.find(c => c.id === order.customerId);
}

// CORRECT — O(n)
const customerMap = new Map(customers.map(c => [c.id, c]));
for (const order of orders) {
    const customer = customerMap.get(order.customerId);
}
```

### Async Patterns

-   [ ] Independent queries use `Promise.all()` — sequential `await` for unrelated calls wastes time
-   [ ] No floating promises — every `Promise` is either `await`ed or explicitly `.catch()`ed

```typescript
// WARNING — sequential when parallel is possible
const orders = await orderDomain.findMany();
const customers = await customerDomain.findMany();

// CORRECT
const [orders, customers] = await Promise.all([orderDomain.findMany(), customerDomain.findMany()]);
```

---

## 4. Code Quality Checklist

-   [ ] No hardcoded strings or magic numbers — use enums or constants
-   [ ] TypeScript `any` avoided — use proper types or generics
-   [ ] No commented-out code
-   [ ] No `console.log` — use `LogService`
-   [ ] Error handling uses typed exceptions (`NotFoundException`, `UnprocessableEntityException`, etc.)

---

## Output Format

Structure findings like this:

```
## BLOCKERS
- [file.ts:42] Controller returns raw `Customer` model — exposes `email`, `phone`, `cpf`.
  Fix: create `CustomerResponse` DTO projecting only `id`, `name`, `role`.

- [order.domain.ts:88] Sequelize `include` in `findWithItems()` — causes N+1.
  Fix: fetch `OrderItem` separately via `orderItemDomain.findMany({ orderId })`.

## WARNINGS
- [campaign.application.ts:120] Missing `await` on `logService.info(...)` — floating promise.
  Fix: add `await`.

## SUGGESTIONS
- [customer.controller.ts:55] Method name `getAll` could be `findAll` to match domain naming convention.
```
