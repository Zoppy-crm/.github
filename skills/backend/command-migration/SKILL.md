---
name: command-migration
description: 'Migrate any cron-based routine from zoppy-command into zoppy-api — provider sync (Bling/Tiny/Shopify/etc. orders/abandoned-carts/products) OR internal cron (billing invoice generation, notifications, maintenance). End goal: eliminate zoppy-command entirely. Two variants share the same pair-PR flow but differ in the internal pattern. Use when migrating cron commands, moving schedulers to zoppy-api, evicting routines from zoppy-command, or creating an aggregator-based scheduler.'
version: '2.0'
---

# Command Migration

Phased runbook for migrating cron-based routines from `zoppy-command` into `zoppy-api`. The long-term goal is to eliminate `zoppy-command` entirely — the cron-on-api pattern is superior in reliability, observability, queue integration, and zero-HTTP-hop dispatch.

**Trigger phrases:** "migrate command", "migrate cron", "move cron to zoppy-api", "migrate sync", "evict from zoppy-command", "kill zoppy-command", "command-migration", "migrate provider", "internal cron migration".

## Variant selector — choose the right path first

Before anything else, identify which variant applies. They share the same **pair-PR flow** (one adds to api, one removes from command) but differ in internal pattern.

### Variant A — Provider sync (DataSyncManagement-driven)

**Use when:**

-   The routine belongs to a **provider integration** (ERP: Bling, Tiny, Omie, …; ecommerce: Shopify, Nuvemshop, VTEX, …).
-   The entity is provider-owned data: Orders, AbandonedCarts, Products, Customers, etc.
-   The routine operates on `DataSyncManagement` records (DSM queries, status transitions, attempts, sequence, erpKeys).
-   Routine taxonomy: Daily / DoesNotRepeat / Hook / Weekly / etc.

Go to [Variant A section](#variant-a--provider-sync-datasyncmanagement-driven-full-runbook) below.

### Variant B — Internal cron (aggregator + processor)

**Use when:**

-   The routine is **internal** to Zoppy, not a provider integration (billing, notifications, maintenance, reports, data hygiene, etc.).
-   It does **not** use `DataSyncManagement` — it iterates Zoppy-owned entities (Companies, Invoices, Users, etc.) directly.
-   The target is usually a single-entity processor that already exists in the api (e.g., `CHARGE_COMPANY`, `NOTIFICATION_SEND`), and the cron enqueues 1 job per eligible entity through an **aggregator job** on the same queue.
-   Reference PRs: [zoppy-api#6487](https://github.com/Zoppy-crm/zoppy-api/pull/6487) + [zoppy-command#1208](https://github.com/Zoppy-crm/zoppy-command/pull/1208) (charge-company aggregator); same pattern in #6311 and #6338.

Go to [Variant B section](#variant-b--internal-cron-aggregator--processor) below.

### Common flow (both variants)

Regardless of variant, every migration follows this high-level arc:

1. **Source exploration** in `zoppy-command` — identify the command, its cron schedule, its business rule (who is eligible, what it does per entity).
2. **Design the equivalent** in `zoppy-api` — scheduler (extends `BaseCommand`) + dispatch path.
3. **Implement + test** in zoppy-api.
4. **Open paired PRs** — one in `zoppy-api` (adds the scheduler), one in `zoppy-command` (removes the command + any exposed endpoint).
5. **Staging validation** with both PRs present but command's cron already disabled.
6. **Merge both together.** Never merge command's deletion before api's addition is deployed and running.

## Prerequisites (applies to both variants)

Before starting, confirm with the user:

1. **Exact command class** in zoppy-command (e.g., `src/application/integrations/{provider}/daily.command.ts` or `src/application/invoices/process-generate-invoices.command.ts`)
2. **Cron schedule** — read the `CommandKeyEnum` / schedule expression from the source
3. **Target variant** (A or B)
4. **For A:** provider + entity + routine taxonomy
5. **For B:** target queue in api (must already exist) + the single-entity processor name
6. **Whether the command exposes a manual HTTP trigger** (to delete the endpoint as part of the command-side PR)

---

## Variant A — Provider sync (DataSyncManagement-driven, full runbook)

Everything below through "Pitfalls (Lessons from Bling Migration)" applies ONLY to Variant A. Skip to [Variant B](#variant-b--internal-cron-aggregator--processor) if your case is an internal cron.

### When to Use (Variant A)

-   Migrating ANY provider's cron-based routines from zoppy-command (or external) into zoppy-api
-   Applies to: ERP providers (Bling, Tiny, Omie, etc.), ecommerce providers (Shopify, Nuvemshop, etc.)
-   Applies to: Any entity (Orders, AbandonedCarts, Products, Customers, Invoices, etc.)
-   Applies to: Any routine type (Daily, DoesNotRepeat, Hook, Weekly, etc.)

### Variant A Prerequisites

Confirm with the user (in addition to the common Prerequisites above):

1. **Provider name** (e.g., Bling, Tiny, Shopify)
2. **Entity type** (e.g., Orders, AbandonedCarts)
3. **Routines to migrate** (e.g., Daily, DoesNotRepeat, Hook)
4. **Source location** (e.g., zoppy-command/src/application/integrations/{provider}/)

---

## Phase 1 — Source Exploration

**Goal:** Extract the exact behavior of every routine being migrated.

### Steps

1. Read ALL source files for the provider's routines (application classes, helpers, base classes)
2. For EACH routine, document in a table:

| Aspect                    | Value                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| **Routine name**          | Daily / DoesNotRepeat / Hook / etc.                                                        |
| **Cron schedule**         | e.g., EVERY_12_HOURS, EVERY_5_MINUTES                                                      |
| **Company query**         | How companies are found (method, filters, joins)                                           |
| **Blocked check**         | Does it check company.blocked? YES/NO                                                      |
| **Hook check**            | Does it check hookEnabled? YES/NO                                                          |
| **DSM query method**      | findAllCurrentBy / findDailyViaHookByProvider / etc.                                       |
| **DSM WHERE clause**      | Exact fields: provider, entity, routine, status, finishedAt, attempts, sequence, companyId |
| **Status filter**         | IN [list] or NOT IN [list] — be exact                                                      |
| **finishedAt filter**     | IS NULL / not filtered                                                                     |
| **Attempts filter**       | <= N / <= MAX_SAFE_INTEGER / not filtered                                                  |
| **Sequence filter**       | = 0 / not filtered                                                                         |
| **skipAttempts**          | true / false / N/A                                                                         |
| **Force flag**            | exposed? what does it change?                                                              |
| **ErpKey/Key resolution** | By erpKeyId? Fallback to companyId? hookEnabled required?                                  |

3. Check what already exists in zoppy-api for this provider (processor, strategy, helpers, queue service, rate limiter)

**Gate:** Do NOT proceed until every routine is fully documented. Ask the user to validate.

---

## Phase 2 — Behavioral Audit

**Goal:** Design the new aggregator's query logic and prove equivalence.

### Steps

1. Design the new query approach for each routine (batched, optimized)
2. Produce a **formal delta table** comparing source vs target:

```
| # | Delta | Source (old) | Target (new) | Impact | Decision |
|---|-------|-------------|-------------|--------|----------|
```

**Impact levels:**

-   **CRITICAL** — Will MISS or DUPLICATE sync records. Must fix.
-   **MEDIUM** — Behavioral difference that changes which records are processed. Discuss with user.
-   **LOW** — Minor difference, unlikely to cause issues in practice.

**Decision options:**

-   **FIX** — Align target with source behavior
-   **KEEP** — Target behavior is intentionally better (document why)
-   **INTENTIONAL** — Known difference accepted by user

### Common Deltas to Check

These are the most frequent sources of regression. Check ALL of them:

-   [ ] **Status filter direction** — IN vs NOT IN (Hook routines often use NOT IN)
-   [ ] **Status values included** — Does the source include NOT_STARTED? Confirm with user before including it (may enqueue hundreds of jobs at once)
-   [ ] **finishedAt filter** — present or absent (Hook often has no finishedAt check)
-   [ ] **Sequence filter** — Hook routines often require sequence=0
-   [ ] **Attempts filter** — some routines have no limit, some cap at MAX_SYNC_ATTEMPTS
-   [ ] **Blocked company check** — some old routines skip this (usually a bug — confirm with user)
-   [ ] **hookEnabled check** — required for Hook routines only
-   [ ] **ErpKey null fallback** — old code often falls back to companyId lookup
-   [ ] **Entity hardcoding** — some domain methods accept entity as parameter
-   [ ] **Force flag** — does the source expose it? what statuses does it add?

**Gate:** User MUST approve the delta table before proceeding. CRITICAL deltas must have FIX decisions.

---

## Phase 3 — Design & Implement

**Goal:** Create the aggregator and all supporting files following the optimized pattern.

### File Checklist

**Files to CREATE:**

| File                                                                                                | Description                                                        |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `src/access/queues/command/{entity-sync}/{provider}-{entity}-sync.command.ts`                       | N command classes (one per routine), extending `BaseCommand<void>` |
| `src/application/{entity-sync}/aggregators/{provider}-{entity}-sync-aggregator.application.ts`      | Core aggregator with batched queries                               |
| `src/application/{entity-sync}/aggregators/{provider}-{entity}-sync-aggregator.application.spec.ts` | Test suite                                                         |

**Files to MODIFY:**

| File                                                                               | Change                                                                 |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `src/access/queues/base.command.ts`                                                | Add N CommandKeyEnum entries                                           |
| `src/access/queues/constants/queue.constants.ts`                                   | Add N QueueJobEnum entries                                             |
| `src/access/queues/command.module.ts`                                              | Register N commands in providers array                                 |
| `src/application/order-sync/aggregators/order-sync-aggregator.module.ts`           | Register + export aggregator                                           |
| `src/access/queues/processors/order-request-builder.processor.ts`                  | Inject aggregator, add N switch cases + dispatch methods               |
| `src/access/queues/services/order-request-builder.queue.service.ts`                | Add N job names to jobs array                                          |
| `src/access/http/controllers/provider-sync/provider-sync-aggregator.controller.ts` | Add manual trigger endpoints (all-companies + per-company per routine) |
| `src/domain/data-sync-management.domain.ts`                                        | Add routine-specific domain methods if query differs from standard     |

**Existing files to CHECK (already in zoppy-api):**

| File                                                                                        | Verify                                           |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `src/cross-cutting/helpers/data-sync-management/{provider}-data-sync-management.factory.ts` | Exists? Uses proper enums (not string literals)? |
| `src/access/queues/processors/{provider}-order-sync.queue.processor.ts`                     | Exists? What job data does it expect?            |
| `src/access/queues/services/{provider}-order-sync.queue.service.ts`                         | Exists?                                          |

### Optimization Rules (NON-NEGOTIABLE)

1. **Max 2-3 DB queries** per aggregator execution — NO N+1

    - 1 query: companies with keys (`findWithErpKeysByProvider`)
    - 1 query: all managements across companies (batched, cross-tenant)
    - 0 queries for key resolution (pre-built Maps from company query)

2. **Bulk enqueue** — `batchExecute()`, never individual `execute()` in loops

3. **Pre-built Maps** — Build in-memory before the management loop:

    - `Map<erpKeyId, ErpKey>` — for management validation
    - `Map<companyId, ErpKey>` — for null erpKeyId fallback
    - `Map<companyId, Company>` — for session context

4. **Guard clauses** — No nested ifs. Early returns and continues.

5. **Single Responsibility** — Extract: `buildErpKeyMap()`, `buildCompanyIdToErpKeyMap()`, `buildCompanyMap()`, `collectValidCompanyIds()`, `mapManagementsToJobsWithSession()`, `hasValidErpKey()`, `isCompanyBlocked()`, `hasHookEnabledKey()`, `fetchManagements()`

6. **Routine-specific queries** — If a routine (e.g., Hook) uses a fundamentally different WHERE clause, create a separate domain method. Do NOT force it through the standard method with extra parameters.

7. **Proper enums** — Use `CompanyErpProviderEnum.{PROVIDER}` or `CompanyEcommerceProviderEnum.{PROVIDER}`, never `AppConstants.PROVIDERS.{PROVIDER}` or string literals.

8. **ErpKey null fallback** — When `management.erpKeyId` is null, fall back to `companyIdToErpKeyMap.get(management.companyId)`. Do NOT skip the management.

### Aggregator Public API Template

```typescript
// Cross-tenant (cron-triggered, all companies)
execute{Routine}Routine(force?: boolean): Promise<number>

// Per-company (endpoint-triggered, session-scoped)
execute{Routine}RoutineForCurrentCompany(force?: boolean): Promise<RoutineResult>
```

### Controller Endpoint Pattern

```
POST /provider-sync/all/{provider}/{routine}  — MASTER only, all companies
POST /provider-sync/{provider}/{routine}       — MASTER+ADMIN, current company
```

All endpoints accept `?force=true` query parameter.

---

## Phase 4 — Test & Verify

**Goal:** Prove correctness with tests and fresh build.

### Test Coverage Requirements

For each routine, test:

-   [ ] Happy path — enqueues correct count
-   [ ] Blocked companies — skipped
-   [ ] No companies — returns 0
-   [ ] No managements — returns 0
-   [ ] hookEnabled filter (Hook only) — only hookEnabled companies
-   [ ] Mixed companies (blocked + valid, hookEnabled + not) — correct filtering
-   [ ] ErpKey null fallback — resolves via companyId
-   [ ] Orphan erpKeyId — skipped
-   [ ] Force flag — includes Processing status
-   [ ] skipAttempts behavior — correct per routine
-   [ ] Multiple companies + managements — single batchExecute call
-   [ ] Session set per company — verified
-   [ ] Error handling — logged and rethrown

For per-company variants:

-   [ ] Happy path with session
-   [ ] No company in session — throws
-   [ ] Blocked company — throws
-   [ ] Empty managements — returns count 0

### Verification Commands

```bash
npm run build                    # Must exit 0, no errors
npm run test -- --testPathPattern="{provider}-order-sync-aggregator"  # Must: all pass
npm run test -- --testPathPattern="data-sync-management.domain"       # Must: no regressions
```

**Gate:** All tests must pass with fresh evidence before proceeding.

---

## Phase 5 — Staging Validation Strategy

**Goal:** Prove behavioral equivalence against real data before cutover.

Recommend to the user one or more of these approaches:

### Option A: Dry-Run Endpoint

Add `GET /provider-sync/{provider}/dry-run/{routine}` (MASTER only) that returns `{ managementIds: string[], count: number }` WITHOUT enqueuing. Compare output with what the source system produces.

### Option B: Shadow Mode

1. Deploy with new crons active but enqueue to a shadow/log queue
2. Keep source crons active
3. Compare: every management ID from source must appear in shadow logs
4. After N days with 0 delta, disable source crons

### Option C: Side-by-Side Query

Run both old and new queries against staging DB manually. DIFF the resulting management ID sets per routine.

### Kill Switch

Always recommend: use `IS_LOCAL=1` or a feature flag to disable new crons instantly if issues arise post-deploy.

---

## Pitfalls (Lessons from Bling Migration)

These caused real bugs. Check for ALL of them:

1. **Sequelize association property casing** — `findWithErpKeysByProvider` returns companies with included keys under `company.ErpKeys` (PascalCase, matching the model name), NOT `company.erpKeys` (camelCase). Always verify the actual property name via `Object.keys(company.dataValues)` before writing map builders. This will silently produce empty maps and 0 jobs with no errors.

2. **NOT_STARTED status** — DoesNotRepeat routines may have hundreds of DSMs in NOT_STARTED status waiting for their sequence. The standard filter `[Idle, Failed, Unfinished]` excludes them. Confirm with the user whether to include NOT_STARTED — it may enqueue a large batch. The old zoppy-command code also excluded NOT_STARTED.

3. **Hook routine uses fundamentally different query** — Do NOT reuse the same domain method with extra parameters. Hook queries use `NOT IN [Processing, Queued]` (inverted), no `finishedAt` filter, `sequence: 0`, and no attempts filter. Create a separate domain method.

4. **IS_LOCAL=1 blocks all BaseCommand registration** — `onModuleInit` skips when `IS_LOCAL=1`. Use the HTTP manual trigger endpoints (`POST /provider-sync/all/{provider}/{routine}`) to test locally instead.

5. **Blocked company check on Hook** — Old zoppy-command Hook routine did NOT check `company.blocked`. This is a bug in the old code. Always check blocked for all routines — blocked companies must not have jobs enqueued.

---

## Reference (Variant A)

### Completed Migrations (use as patterns)

| Provider | Entity | Routines                   | Reference PR/Files                                                                  |
| -------- | ------ | -------------------------- | ----------------------------------------------------------------------------------- |
| Tiny     | Orders | Daily, DoesNotRepeat       | `src/application/order-sync/aggregators/tiny-order-sync-aggregator.application.ts`  |
| Bling    | Orders | Daily, DoesNotRepeat, Hook | `src/application/order-sync/aggregators/bling-order-sync-aggregator.application.ts` |

### Key Shared Infrastructure

| Component                               | File                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------- |
| BaseCommand                             | `src/access/queues/base.command.ts`                                                |
| CommandKeyEnum                          | `src/access/queues/base.command.ts`                                                |
| QueueJobEnum                            | `src/access/queues/constants/queue.constants.ts`                                   |
| BaseQueue (batchExecute)                | `src/access/queues/base.queue.ts`                                                  |
| OrderRequestBuilderProcessor            | `src/access/queues/processors/order-request-builder.processor.ts`                  |
| OrderRequestBuilderQueueService         | `src/access/queues/services/order-request-builder.queue.service.ts`                |
| DataSyncManagementDomain                | `src/domain/data-sync-management.domain.ts`                                        |
| CompanyDomain.findWithErpKeysByProvider | `src/domain/company.domain.ts`                                                     |
| CommandModule                           | `src/access/queues/command.module.ts`                                              |
| OrderSyncAggregatorModule               | `src/application/order-sync/aggregators/order-sync-aggregator.module.ts`           |
| ProviderSyncAggregatorController        | `src/access/http/controllers/provider-sync/provider-sync-aggregator.controller.ts` |
| ForceSyncResponse                       | `src/access/http/response/provider-sync/force-sync.response.ts`                    |

---

## Variant B — Internal cron (aggregator + processor)

Use this variant for internal Zoppy crons that don't depend on `DataSyncManagement` (billing, notifications, maintenance, reports). Simpler pattern, fewer files, same PR pairing discipline.

### The Pattern

Three building blocks, all in `zoppy-api`:

1. **Scheduler command** — a `BaseCommand<void>` with the original cron expression. Its job is to enqueue a single **aggregator job** on an existing queue.
2. **Aggregator job case** — a new case in the target processor's `switch(job.name)` that, when fired, queries eligible entities and enqueues a per-entity job on the **same queue**.
3. **Per-entity processor case** (already exists) — the existing case that processes one entity. Untouched.

Data flow:

```
cron fires
  └─> Scheduler.execute()            ← command (new)
       └─> queue.execute({name: *_AGGREGATOR})
            └─> Processor.process(AGGREGATOR)     ← new case
                 └─> for each eligible entity:
                      queue.execute({name: *_PER_ENTITY}) ← existing case runs it
```

### Phase 1 — Source exploration

1. Read the source command in `zoppy-command` (usually `src/application/<feature>/<name>.command.ts`).
2. Extract and document:

| Aspect                    | Value                                                   |
| ------------------------- | ------------------------------------------------------- |
| **Command class**         | Full path + class name                                  |
| **Cron schedule**         | Key / cron expression / timezone                        |
| **Eligibility rule**      | Exact WHERE clause / filter used to select entities     |
| **Per-entity action**     | What method is called per eligible entity (HTTP? call?) |
| **HTTP trigger endpoint** | Does the command expose a manual POST? (if yes — URL)   |
| **ProcessDataManagement** | Does it create DSMs? If yes, where (command vs api)?    |
| **Guard clauses**         | Boundary guards (e.g. `chargeDay > 28`, `plan != null`) |
| **Target queue in api**   | Existing queue the per-entity processor lives on        |
| **Per-entity job name**   | Existing `QueueJobEnum` entry to reuse                  |
| **Per-entity processor**  | Existing processor class + file                         |

**Gate:** Confirm target queue and per-entity processor exist. If they don't, this isn't a Variant B migration — it's a full rebuild.

### Phase 2 — Design parity table

Formal delta check against source:

| #   | Aspect             | Source (command) | Target (api) | Impact | Decision |
| --- | ------------------ | ---------------- | ------------ | ------ | -------- |
| 1   | Cron schedule      |                  |              |        |          |
| 2   | Eligibility filter |                  |              |        |          |
| 3   | Guard clauses      |                  |              |        |          |
| 4   | DSM creation       |                  |              |        |          |
| 5   | Timezone           |                  |              |        |          |

**Impact levels:** CRITICAL (drops or duplicates eligibility), MEDIUM (behavior difference), LOW.

**Do NOT invent rules.** Target mirrors source 1:1 — change of behavior is a separate PR.

### Phase 3 — Implement

**Files to CREATE:**

| File                                                      | Description                                                 |
| --------------------------------------------------------- | ----------------------------------------------------------- |
| `src/access/queues/command/<feature>/<name>.command.ts`   | Scheduler, extends `BaseCommand<void>`, enqueues aggregator |
| `src/application/<feature>/<feature>.application.spec.ts` | Unit tests for the new aggregator method                    |

**Files to MODIFY:**

| File                                                         | Change                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| `src/access/queues/base.command.ts`                          | Add 1 `CommandKeyEnum` entry + schedule mapping               |
| `src/access/queues/constants/queue.constants.ts`             | Add 1 `QueueJobEnum` entry (`*_AGGREGATOR`)                   |
| `src/access/queues/command.module.ts`                        | Register the new command in providers                         |
| `src/access/queues/processors/<existing>.queue.processor.ts` | New switch case for `*_AGGREGATOR` → calls application method |
| `src/access/queues/services/<existing>.queue.service.ts`     | Add new job name to `jobs` array                              |
| `src/application/<feature>/<feature>.application.ts`         | New method `queue<Entity>ForEligible<X>(today?: Date)`        |

**Design rules:**

-   **Scheduler is thin.** Its job is: enqueue the aggregator job. Nothing else. Never query entities inside the scheduler.
-   **Aggregator method lives in the application layer** (not the processor) — processors stay thin facades.
-   **Same queue as per-entity processor.** Do NOT create a new queue unless there's a specific reason (rate limits, concurrency); reuse existing infrastructure.
-   **Guard clauses up front.** Replicate the source's early returns (e.g., `if (today.getDate() > 28) return 0;`).
-   **Use existing queue service** to enqueue per-entity jobs — pass `session` from the aggregator job's session data.
-   **DSM creation stays where source has it.** If source creates DSMs inside the per-entity flow (common), do nothing in the aggregator. If source creates in the command, move it into the aggregator — but flag to the user, as it may be refactorable into the processor itself.
-   **Tests live with the application method**, not the processor or scheduler.

### Phase 4 — Test & Verify

For the aggregator method, cover:

-   [ ] Happy path — returns correct count, enqueues 1 job per eligible entity
-   [ ] Empty eligibility — returns 0, no jobs enqueued
-   [ ] Guard clause trips — early return without DB query (if guard is day/time-based)
-   [ ] Filter correctness — ineligible entities excluded (mirror source filters exactly)
-   [ ] Session propagation — each enqueued job carries valid session data
-   [ ] Batch size — if eligibility may return hundreds/thousands, confirm `batchExecute` is used

**Verification:**

```bash
npm run build                                                           # must exit 0
npm run test -- --testPathPattern="<feature>.application.spec"          # all pass
npm run lint
```

### Phase 5 — Pair PRs and cutover

1. Open `zoppy-api` PR — adds scheduler + aggregator case. Title: `add: <feature> aggregator scheduler para <what> (#<issue>)`.
2. Open `zoppy-command` PR — removes the command, the application method, the HTTP controller/endpoint (if exposed), and module registrations. Title: `remove: cron de <feature> (migrado pro zoppy-api) (#<issue>)`.
3. Both PRs link to each other + to the issue.
4. Staging: deploy `zoppy-api` PR first, confirm BullMQ Board shows the repeatable scheduler job, trigger manually, verify 1 per-entity job per eligible entity.
5. Only after api is stable on staging, merge the `zoppy-command` removal PR.

### Variant B pitfalls

1. **Duplicate DSM creation.** If the per-entity processor already does find-or-create on `ProcessDataManagement`, don't create it again in the aggregator. Check the existing processor's flow first.
2. **Guard drift.** The source command may have a subtle guard (e.g., holiday calendar, feature flag). Easy to miss when translating. Grep the source for any `if (... return)` early in `run()`.
3. **Timezone.** `zoppy-command` often uses `America/Sao_Paulo` in cron expressions. Confirm zoppy-api's scheduler uses the same — `BaseCommand` respects the TZ in the schedule mapping.
4. **HTTP trigger deletion.** If the command also exposed a `POST /<feature>/execute` endpoint, delete it in the command PR — it's not called from the FE (verify via search in `zoppy-FE` for the URL).
5. **Double cron during rollout.** Never let both the source command and the api scheduler run in parallel in production. Merge sequence: api-first (disabled via feature flag or deploy) → enable api → merge command removal.

### Variant B reference

| Case                            | PRs                                                                                                                                     |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `ChargeCompanyAggregateCommand` | api: [#6487](https://github.com/Zoppy-crm/zoppy-api/pull/6487) / command: [#1208](https://github.com/Zoppy-crm/zoppy-command/pull/1208) |
| Earlier aggregator migrations   | #6311, #6338 (same pattern, different features)                                                                                         |
