---
name: root-cause
description: >
    Structured root cause analysis for bugs in the zoppy-api NestJS project. Use this skill whenever
    investigating an error, unexpected behavior, failing test, or production incident. Triggers on:
    "debug this", "why is this failing", "investigate this bug", "trace this error", "root cause",
    "why is X returning empty", "why is this returning 403", "why is the queue not processing",
    "why is the job failing", or any investigation task in this codebase. Immediately apply the
    systematic trace path — do not guess before reading the code.
---

# Root Cause Analysis

## Role

You are a debugger. Do not guess. Follow the trace path below from the entry point inward until you find where the behavior diverges from expectations. Document each layer you inspect.

---

## Trace Path

Work through these layers in order. Stop at the layer where the problem is found.

### Step 1 — HTTP Layer

**Files:** `src/access/http/controllers/`

-   Which controller and method handles this request?
-   What guards are applied and in what order? (Wrong guard order → 403 instead of 401)
-   Is `@ExceptionInterceptor()` present? (Absent → errors not logged)
-   Is the endpoint marked `@IsPublic()`? (Unexpected public access)
-   Does the request DTO have the correct validation decorators?

### Step 2 — Application Layer

**Files:** `src/application/`

-   Which Application method is called?
-   Trace the method body: what domains are queried, in what order?
-   Are `await` keywords present on every Promise? (Floating promise → silent failure)
-   Are independent calls using `Promise.all()`? (Sequential awaits on unrelated calls → slow)
-   Does the method log mutations? (Missing log → hard to trace in production)

### Step 3 — Domain Layer

**Files:** `src/domain/`, `src/repository/adapters/repository-adapter.ts`

-   Which Domain methods are called?
-   Does the query include a `companyId` filter? `RepositoryAdapter` auto-applies this from `SessionService` — if session is wrong, results are empty or wrong-company data leaks.
-   Is `withTrashed` needed? Soft-deleted records are excluded by default.
-   Is there a `Sequelize include`? This bypasses the adapter's constraint layer and causes N+1.
-   Check the raw query built by the adapter — log it if needed.

### Step 4 — SessionService Context

**Files:** `src/services/session/session.service.ts`

-   Is `setSession(job)` or `TestSession.setSession()` called before the operation?
-   Does the session have the correct `companyId`?
-   In queue processors: is `await this.setSession(job)` the **first line** of `process()`?

```typescript
// Queue processor — missing setSession causes all domain queries to have no companyId
async process(job: Job<QueueBaseData<JobData>>) {
    await this.setSession(job); // MUST be first
    // ...
}
```

### Step 5 — Queue Path (async flows only)

**Files:** `src/access/queues/processors/`

-   Find the processor handling this queue: search by `@Processor(QueueEnum.X)`
-   Is `concurrency` and `lockDuration` appropriate for the job type?
-   Check the job data shape in `job.data` — does it match what the producer sent?
-   Is there a dead-letter queue or retry logic? Check if the job is silently retrying.
-   Are there mutex decorators (`@JobMutex`) preventing concurrent execution?

### Step 6 — External Integration

**Files:** `src/application/*/strategies/`, `src/cross-cutting/middlewares/`

-   Which provider strategy is selected? (Routing via `CompanyEcommerceProviderEnum`)
-   Does the HMAC middleware validate the webhook signature correctly? (5-minute timestamp window)
-   Is the external API returning an unexpected response shape?
-   Use `nock` or log interception to inspect the actual HTTP exchange.

---

## Toolbox

```bash
# Find all usages of a method or class
grep -r "methodName" src/ --include="*.ts" -n

# Find the controller for a route
grep -r "@Get\|@Post\|@Put\|@Delete" src/access/http/ --include="*.ts" -n | grep "route-segment"

# Find the queue processor for a queue name
grep -r "QueueEnum.QUEUE_NAME" src/access/queues/ --include="*.ts" -n

# Find where setSession is or is not called
grep -r "setSession" src/access/queues/ --include="*.ts" -n
```

Look for structured logs from `LogService` — they include `companyId`, entity identifiers, and `extraStructuredMetadata` that reveal runtime state.

For production issues, check OpenTelemetry traces or NewRelic/Datadog spans to see the execution path and timing.

---

## Common Root Causes in This Codebase

| Symptom                                       | Likely cause                                                          | Where to look                           |
| --------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------- |
| Query returns empty results                   | `setSession()` not called → wrong `companyId`                         | Queue processor `process()` first line  |
| Related entity is `undefined`                 | `Sequelize include` removed or never added; fetch separately          | Domain method, RepositoryAdapter call   |
| Job silently succeeds but nothing changes     | Floating `Promise` — missing `await`                                  | Application method or Domain call       |
| Partial write on failure                      | Missing `@UsingTransaction()` on controller                           | Controller method decorators            |
| `403 Forbidden` instead of `401 Unauthorized` | Guard order wrong — `RoleGuard` must come before `BlockFreeTierGuard` | Controller `@UseGuards(...)` order      |
| `401` on a public endpoint                    | Missing `@IsPublic()` decorator                                       | Controller method decorators            |
| Queue job stuck / not processing              | `lockDuration` too short, or job mutex blocking                       | Processor config, `@JobMutex` decorator |
| Wrong provider called                         | `CompanyEcommerceProviderEnum` routing logic                          | Strategy selector in application layer  |

---

## Output Format

After completing the trace, report:

```
## Root Cause
[One clear sentence describing what is wrong and where.]

## Evidence
- [Step N] [file.ts:line] — [what you found]
- [Step N] [file.ts:line] — [what you found]

## Fix
[Concrete code change or configuration fix.]

## Prevention
[What test or lint rule would have caught this earlier.]
```
