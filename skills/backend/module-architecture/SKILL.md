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
2. **Controllers inject applications only** — never inject private services directly into a controller
3. **One module per bounded context** — avoid dumping everything into `ApplicationModule`

```typescript
@Module({
    imports: [DomainModule, SessionModule, QueueServiceModule, LogModule],
    providers: [
        FeatureApplication,        // public → exported
        FeatureProcessApplication, // public → exported
        FeatureSyncService,        // private (not exported)
        FeatureValidationService   // private (not exported)
    ],
    exports: [FeatureApplication, FeatureProcessApplication]
})
export class FeatureModule {}
```

### Registering the module

Import in `src/application/application.module.ts` and add to both `imports` and `exports`. The HTTP module already imports `ApplicationModule`, so controllers automatically get access to exported applications.

### When NOT to create a module

Simple features with a single application and no private services can live directly in `ApplicationModule` as providers. Create a dedicated module when:
- You have 2+ private services that shouldn't be exposed
- The feature has internal orchestration logic (sync services, strategies, pipelines)
- You want to prevent other modules from depending on implementation details

---

## Layered Architecture — Injection Rules

### Application Layer

Application services orchestrate Domains and shared Services.

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
- Every endpoint: `@ExceptionInterceptor()`, `@ApiOperation`, `@ApiResponse`, `@ApiBearerAuth`
- Write endpoints (POST, PUT, PATCH, DELETE): `@UsingTransaction()`
- Auth: `@UseGuards(RoleGuard([...]))` plus `BlockFreeTierGuard()` for most endpoints
- Input MUST be a typed Request DTO from `src/access/http/requests/`
- Output MUST be a typed Response DTO from `src/access/http/response/` — never return a raw Sequelize model

### Domain Layer

Domains extend `RepositoryAdapter<T>` and auto-filter by `companyId` via `SessionService`.

- Add entity-specific query methods (`findByCode`, `findByPhone`, etc.)
- Keep them focused on data access, not orchestration
- **Domain-to-Domain injection** is only allowed for strictly parent-child relationships (child has a foreign key to the parent). Injecting unrelated Domains into each other is not allowed.

### Queue Processors

```typescript
@Processor(QueueEnum.SOME_QUEUE, { concurrency: 5, lockDuration: 30 * 60 * 1000 })
export class SomeProcessor extends QueueProcessorBase {
    async process(job: Job<QueueBaseData<JobData>>) {
        await this.setSession(job);  // MUST be first
        // business logic
    }
}
```

- MUST extend `QueueProcessorBase`
- MUST call `await this.setSession(job)` before any business logic — the session provides `companyId` for multi-tenant filtering
