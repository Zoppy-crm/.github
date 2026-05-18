---
name: module-architecture
description: >
    How to create a feature module in zoppy-api and which layer can inject which. Use this skill
    whenever creating a new NestJS feature, adding a new module, registering providers in
    ApplicationModule, or when you need to understand layered architecture injection rules. Triggers
    on: "create new feature", "novo módulo", "nova feature", "register in application module",
    "layered architecture", "can application inject another application", "which layer", "module
    structure", "feature module", "bounded context", "camadas", "arquitetura".
---

# Module Architecture

## Feature Module Pattern

Each bounded context should have its own NestJS module. The `UploadDataModule` is the reference implementation.

### Directory structure

```
src/application/<feature>/
├── <feature>.module.ts              # Module definition
├── <feature>.application.ts         # Public application (exported)
├── <feature>-<sub>.application.ts   # Other public applications if needed
├── <feature>-<sub>.service.ts       # Private services (NOT exported)
├── <sub-service>/                   # Grouped private services
│   └── <feature>-<sub>.service.ts
└── validation/
    └── <operation>-<feature>.validation.ts
```

### Key rules

1. **Only export applications** — services, helpers, and internal logic stay private in the module
2. **Access only injects applications** — controllers, queue processors, and WebSocket gateways may **only** inject `*Application` classes. Never a domain, never a service, never a helper. If a processor needs business logic, the logic moves up to the Application.
3. **One module per bounded context** — avoid dumping everything into `ApplicationModule`

```typescript
@Module({
    imports: [DomainModule, SessionModule, QueueServiceModule, LogModule],
    providers: [
        FeatureApplication, // public → exported
        FeatureProcessApplication, // public → exported
        FeatureSyncService, // private (not exported)
        FeatureValidationService // private (not exported)
    ],
    exports: [FeatureApplication, FeatureProcessApplication]
})
export class FeatureModule {}
```

### Registering the module

Import in `src/application/application.module.ts` and add to both `imports` and `exports`. The HTTP module already imports `ApplicationModule`, so controllers automatically get access to exported applications.

### When NOT to create a module

Simple features with a single application and no private services can live directly in `ApplicationModule` as providers. Create a dedicated module when:

-   You have 2+ private services that shouldn't be exposed
-   The feature has internal orchestration logic (sync services, strategies, pipelines)
-   You want to prevent other modules from depending on implementation details

---

## Layered Architecture — Injection Rules

The layers, top to bottom:

```
access (controllers, queue processors, websockets)
  ↓ may only inject
applications
  ↓ may inject
services (public or private) + domains + queue services
  ↓ may inject
domains + queue services
  ↓
repository (Sequelize via RepositoryAdapter)
```

### Application vs Service — when to use which

|             | Application                                                             | Service                                             |
| ----------- | ----------------------------------------------------------------------- | --------------------------------------------------- |
| Suffix      | `*.application.ts`                                                      | `*.service.ts`                                      |
| Consumed by | **access only** (controllers / processors / sockets)                    | applications or other services                      |
| Visibility  | **always exported** by the module                                       | public (exported) **or** private (only `providers`) |
| Purpose     | public API surface of a feature; orchestrates services + queue services | building block consumed by an application           |

If two consumers (e.g., a controller and a processor) need the same business flow, put it in an Application and let both call it. The processor never reaches into the Service directly.

If a Service is consumed **inside the same module only**, leave it out of `exports`. Only export services that are imported by a different feature module.

### Application Layer

Application services orchestrate Domains, queue services, and internal services.

**Critical rule: never inject one Application into another Application.** If two Applications need shared logic, extract it to a Domain, Helper, or Service. This is the most common architecture violation — watch for it.

```typescript
@Injectable()
export class FeatureApplication {
    private readonly LOG_CONTEXT = 'FEATURE_APPLICATION';

    public constructor(
        private readonly featureDomain: FeatureDomain,
        public readonly session: SessionService,      // public readonly (convention)
        public readonly logService: LogService,       // public readonly (convention)
        private readonly queueService: FeatureQueueService
    ) {}

    // Public methods first (the API surface)
    public async create(request: CreateRequest): Promise<Response> { ... }
    public async update(id: string, request: UpdateRequest): Promise<Response> { ... }
    public async delete(id: string): Promise<BooleanResponse> { ... }
    public async find(id: string): Promise<Response> { ... }
    public async list(after, page, pageSize, updatedAt?): Promise<ZoppyFilter<Response[]>> { ... }

    // Private helpers at the end
    private async buildEntity(request: CreateRequest): Promise<Feature> { ... }
}
```

### Controller Layer

Controllers are **thin facades** — zero business logic inside them. A controller method should read like: validate input → call application → return response.

```typescript
@Post('endpoint')
@UseGuards(RoleGuard([RoleEnum.MASTER]))
@UsingTransaction()
@ExceptionInterceptor()
@ApiOperation({ summary: 'Create entity' })
@ApiResponse({ status: 200, description: 'Success.' })
@ApiBearerAuth('access-token')
public async method(@Body() request: RequestDto): Promise<ResponseDto> {
    return await this.application.doSomething(request);
}
```

**Required decorators:**

-   Every endpoint: `@ExceptionInterceptor()`, `@ApiOperation`, `@ApiResponse`, `@ApiBearerAuth`
-   Write endpoints (POST, PUT, PATCH, DELETE): `@UsingTransaction()`
-   Auth: `@UseGuards(RoleGuard([...]))` plus `BlockFreeTierGuard()` for most endpoints
-   Input MUST be a typed Request DTO from `src/access/http/requests/`
-   Output MUST be a typed Response DTO from `src/access/http/response/` — never return a raw Sequelize model

### Domain Layer

Domains extend `RepositoryAdapter<T>` and auto-filter by `companyId` via `SessionService`.

-   Add entity-specific query methods (`findByCode`, `findByPhone`, `findNextAttemptNumberFor`, etc.).
-   **Push business rules down into the Domain, not up into the Application.** Today many domains are anemic CRUD wrappers and applications hold rules they shouldn't — when adding behavior, prefer a Domain method. State transitions (`markAsIssued`, `markAsCancelled`, `markAsFailed`), invariant-checks, and "create with defaults" flows belong here.
-   A rich Domain method:
    -   Encapsulates a transition or a query that may evolve independently of any caller.
    -   Returns the updated entity when it mutates, so callers don't double-fetch.
    -   Is testable in isolation (DB integration spec, no application/service wiring).
-   Keep them focused on data + entity behavior; **orchestration across multiple domains belongs to a Service or Application**.
-   **Domain-to-Domain injection** is only allowed for strictly parent-child relationships (child has a foreign key to the parent). Injecting unrelated Domains into each other is not allowed.

### Queue Processors

```typescript
@Processor(QueueEnum.SOME_QUEUE, { concurrency: 5, lockDuration: 30 * 60 * 1000 })
export class SomeProcessor extends QueueProcessorBase {
    public constructor(
        public sessionService: SessionService,
        public logService: LogService,
        private readonly application: FeatureApplication // ← the ONLY business dep
    ) {
        super(sessionService, logService);
    }

    public async process(job: Job<QueueBaseData<JobData>>) {
        await this.setSession(job); // MUST be first
        await this.application.executeSomething(job.data.data);
    }
}
```

-   MUST extend `QueueProcessorBase`.
-   MUST call `await this.setSession(job)` before any business logic — the session provides `companyId` for multi-tenant filtering (the `@JobMutex` decorator does this for you when present).
-   **MUST only inject Applications.** Never a domain, never a service, never another processor's queue service. The processor is a transport facade: parse the job → delegate to the Application. If a processor needs to enqueue a follow-up job, expose a method on the Application that schedules it and let the Application call the queue service.
-   For Redis-locked processors, use `@JobMutex({ lockKey, getLockIdentifier, ... })` instead of hand-rolling lock acquisition. The decorator requires `this.zoppyRedisService` and `this.sessionService` to be present on the processor instance.
