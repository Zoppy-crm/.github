---
name: code-conventions
description: >
  Coding conventions specific to zoppy-api: logging with LogService, which exception to throw,
  method complexity limits, clean code patterns, general imports, ApplicationValidationBase, and
  the queue integration rule. Use this skill whenever writing new code in the project, when asked
  how to handle an error, how to log an operation, what exception to throw, how to structure a
  method, or how to import models/utilities. Triggers on: "how to log", "which exception", "what
  error to throw", "LogService", "NotFoundException", "UnprocessableEntityException",
  "BadRequestException", "ApplicationValidationBase", "@Zoppy-crm/models", "StringUtil",
  "generateUuid", "console.log", "método longo", "complexidade", "early return", "validação",
  "validation class", "queue integration", "api-signatures".
---

# Code Conventions

## Logging

All mutating operations (create, update, delete) must log with structured metadata. Never use `console.log` — always use `LogService`.

```typescript
private readonly LOG_CONTEXT = 'FEATURE_APPLICATION';

// Log at start and end of mutations
await this.logService.info({
    message: 'Creating feature',
    identifier: this.LOG_CONTEXT,
    extraStructuredMetadata: { entityId: id, companyId }
});

// Log before queue dispatches
await this.logService.info({
    message: 'Dispatching feature sync job',
    identifier: this.LOG_CONTEXT,
    extraStructuredMetadata: { queue: QueueEnum.FEATURE_QUEUE, entityId }
});

// Log errors in catch blocks
await this.logService.error({
    message: 'Failed to create feature',
    identifier: this.LOG_CONTEXT,
    extraStructuredMetadata: { error: error.message, entityId }
});
```

**Rules:**
- `logService.info()` at start and end of mutations
- `logService.info()` before queue dispatches (include queue name)
- `logService.error()` in catch blocks
- Do NOT log read operations (find, list) — only log mutations
- Never interpolate user-supplied strings directly into log messages

---

## Error Handling

Map errors to the correct HTTP exception — don't use a generic `Error` or wrap everything in `BadRequestException`.

| Situation | Exception | HTTP Status |
|---|---|---|
| Entity not found by ID, code, phone, etc. | `NotFoundException` | 404 |
| Business rule violation, validation failure | `UnprocessableEntityException` | 422 |
| Malformed request, missing required fields | `BadRequestException` | 400 |

```typescript
const feature = await this.featureDomain.findOne({ where: { id } });
if (!feature) throw new NotFoundException(`Feature ${id} not found`);

if (!request.name) throw new BadRequestException('Name is required');

if (feature.status === FeatureStatusEnum.ARCHIVED) {
    throw new UnprocessableEntityException('Cannot update an archived feature');
}
```

**Do not** wrap domain errors in generic catch blocks that swallow the original status code.

---

## Validation (ApplicationValidationBase)

For create/update operations, use a dedicated validation class in `<feature>/validation/`:

```typescript
// Validation class
export class CreateFeatureValidation extends ApplicationValidationBase {
    public async execute(request: { companyId: string; feature: Feature }): Promise<void> {
        // validate and throw UnprocessableEntityException if invalid
    }
}

// In the application service
const validation = CreateFeatureValidation.create();
await validation.execute({ companyId, feature });
```

This is distinct from `DomainValidation<T>` — `ApplicationValidationBase` is for application-layer validation that may need to coordinate multiple domains. `DomainValidation<T>` lives in the domain layer for entity-specific rules.

---

## Queue Integration

Always use internal queue services (BullMQ) instead of `@Zoppy-crm/api-signatures`. The api-signatures package uses HMAC-based HTTP calls between services — this pattern is deprecated and causes coupling.

```typescript
// CORRECT — use internal queue
await this.queueService.execute({
    session: this.session.getSessionData(),
    job: QueueJobEnum.PROCESS_FEATURE,
    queue: QueueEnum.FEATURE_QUEUE,
    data: { entityId: entity.id }
});
```

If you find existing code using `@Zoppy-crm/api-signatures` for internal calls, migrate it to a queue service.

---

## Method Complexity

Keep methods readable — a method should fit in a single screen.

- **Nesting depth**: more than 2–3 levels of `if` nesting is a red flag — extract into helper methods with descriptive names
- **Method length**: if a method exceeds ~40–50 lines, break into smaller private methods placed at the end of the class
- **Parameter lists**: more than 4–5 parameters suggest the need for an options object

---

## Clean Code

- Use **early returns** to reduce nesting — check for error conditions first and return/throw, then the happy path
- Extract repeated blocks into private methods (at the end of the class)
- Prefer `reduce` over `forEach` with mutable state when transforming collections
- Name variables clearly — `enrichedLineItems` not `lineItemsFiltered` if the operation is enrichment
- Remove dead code (unreachable branches, unused imports) — don't leave commented-out code

---

## General Conventions

- **Models**: import from `@Zoppy-crm/models`; utilities from `@Zoppy-crm/utilities`
- **UUIDs**: use `StringUtil.generateUuid()` — never `uuidv4()` directly or `Math.random()`-based IDs
- **Company context**: use `SessionService` for `companyId` — never pass `companyId` manually as a parameter unless explicitly required (the RepositoryAdapter auto-applies it)
- **TypeScript**: avoid `any` — use proper types or generics
