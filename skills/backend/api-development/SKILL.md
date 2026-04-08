# API Development Guidelines

Rules and patterns for developing features in the zoppy-api codebase.

## Module Architecture

### Feature Modules (preferred pattern)

Each feature should have its own NestJS module with clear boundaries. The `UploadDataModule` is the reference implementation.

**Structure:**

```
src/application/<feature>/
├── <feature>.module.ts              # Module definition
├── <feature>.application.ts         # Public application (exported)
├── <feature>-<sub>.application.ts   # Other public applications if needed
├── <feature>-<sub>.service.ts       # Private services (NOT exported)
├── <sub-service>/                   # Grouped private services
│   ├── <feature>-<sub>.service.ts
│   └── <feature>-<sub>.service.ts
└── validation/                      # Validation classes
    └── <operation>-<feature>.validation.ts
```

**Key rules:**

1. **Only export applications** — services, helpers, and internal logic stay private in the module
2. **Controllers inject applications only** — never inject private services directly
3. **One module per bounded context** — avoid dumping everything into `ApplicationModule`

**Example:**

```typescript
@Module({
    imports: [DomainModule, SessionModule, QueueServiceModule, LogModule],
    providers: [
        FeatureApplication, // public
        FeatureProcessApplication, // public
        FeatureSyncService, // private (not exported)
        FeatureValidationService // private (not exported)
    ],
    exports: [FeatureApplication, FeatureProcessApplication]
})
export class FeatureModule {}
```

**Registering the module:**

-   Import in `src/application/application.module.ts` and add to both `imports` and `exports`
-   The HTTP module already imports `ApplicationModule`, so controllers get access to exported applications

### When NOT to create a module

Simple features with a single application and no private services can live directly in `ApplicationModule` as providers. Create a module when:

-   You have 2+ private services that don't need to be exposed
-   The feature has internal orchestration logic (sync services, strategies, pipelines)
-   You want to prevent other modules from depending on implementation details

## Layered Architecture — Critical Rules

### Application Layer

Application services orchestrate multiple Domains and Services.

-   **NEVER inject one Application into another Application.** If two Applications need shared logic, extract it to a Domain, Helper, or Service.
-   Application services coordinate Domains — they do not access the database directly.

**Class Structure:**

```typescript
@Injectable()
export class FeatureApplication {
    private readonly LOG_CONTEXT: string = 'FEATURE_APPLICATION';

    public constructor(
        private readonly domain: FeatureDomain,
        private readonly sessionService: SessionService,
        private readonly logService: LogService,
        private readonly queueService: FeatureQueueService
    ) {}

    // Public methods first (the API surface)
    public async create(request: CreateRequest): Promise<Response> { ... }
    public async update(id: string, request: UpdateRequest): Promise<Response> { ... }
    public async delete(id: string): Promise<BooleanResponse> { ... }
    public async find(id: string): Promise<Response> { ... }
    public async list(after, page, pageSize, updatedAt?): Promise<ZoppyFilter<Response[]>> { ... }

    // Private methods at the end
    private async helperMethod(): Promise<void> { ... }
}
```

### Controller Layer

Controllers are **thin facades**. They must NOT contain business logic.

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

-   Every endpoint: `@ExceptionInterceptor()`, Swagger decorators (`@ApiOperation`, `@ApiResponse`, `@ApiBearerAuth`)
-   Write endpoints (POST, PUT, PATCH, DELETE): `@UsingTransaction()`
-   Auth: `@UseGuards(RoleGuard([...]))` for main API, `@IsPublic()` for partners webhooks

**Input/Output typing:**

-   Input MUST use a Request DTO from `src/access/http/requests/`
-   Output MUST use a Response DTO from `src/access/http/response/` — never return Sequelize models directly

### Domain Layer

Domains extend `RepositoryAdapter<T>` and auto-filter by `companyId` via `SessionService`.

-   Add business-specific query methods (e.g., `findByCode`, `findByPhone`)
-   Keep them focused on data access, not orchestration
-   Complex multi-domain operations belong in the application layer
-   **Domain-to-Domain injection** is only allowed for parent-child relationships (where the child has a foreign key to the parent). Injecting unrelated Domains is not allowed.

### Queue Processors

```typescript
@Processor(QueueEnum.SOME_QUEUE, { concurrency: 5, lockDuration: 30 * 60 * 1000 })
export class SomeProcessor extends QueueProcessorBase {
    async process(job: Job<QueueBaseData<JobData>>) {
        await this.setSession(job);
        // business logic
    }
}
```

-   MUST extend `QueueProcessorBase`
-   MUST call `await this.setSession(job)` before any business logic
-   Use `QueueJobOptions` constants for job configuration

## Forbidden Patterns

### No Direct Sequelize Access

**NEVER** call Sequelize model methods directly (`Model.findOne()`, `Model.create()`, `Model.destroy()`, etc.). All database operations MUST go through the Domain class. The `RepositoryAdapter` auto-applies company-scoped filtering — bypassing it means bypassing multi-tenant isolation.

### No Sequelize `include`

**NEVER** use eager loading with `include`. This has caused severe production performance issues. Fetch related entities separately, and use `Promise.all` when the queries are independent:

```typescript
// FORBIDDEN:
this.repository.findAll({ include: [{ model: OtherModel }] });

// FORBIDDEN: sequential when queries are independent
const parent = await this.parentDomain.findById(id);
const children = await this.childDomain.findByParentId(parent.id);
const settings = await this.settingDomain.findByParentId(parent.id);

// CORRECT: concurrent fetching for independent queries
const parent = await this.parentDomain.findById(id);
const [children, settings] = await Promise.all([this.childDomain.findByParentId(parent.id), this.settingDomain.findByParentId(parent.id)]);
```

### Concurrent Fetching with Promise.all / Promise.allSettled

When multiple async calls are **independent** (one does not depend on the result of another), always execute them concurrently:

```typescript
// FORBIDDEN: sequential independent calls
const customers = await this.customerDomain.find({ where: { id: customerIds } });
const addresses = await this.addressDomain.find({ where: { id: addressIds } });
const coupons = await this.couponDomain.find({ where: { phone: phones } });

// CORRECT: concurrent with Promise.all
const [customers, addresses, coupons] = await Promise.all([
    this.customerDomain.find({ where: { id: customerIds } }),
    this.addressDomain.find({ where: { id: addressIds } }),
    this.couponDomain.find({ where: { phone: phones } })
]);
```

Use `Promise.allSettled` when some calls can fail without blocking the others:

```typescript
const results = await Promise.allSettled([this.externalService.syncCustomer(customer), this.externalService.syncOrder(order)]);
```

### No O(n²) Complexity

Do not use `.find()`, `.filter()`, `.some()`, `.includes()` inside loops. Use `Map` or `Set` for lookups:

```typescript
// FORBIDDEN:
for (const item of items) {
    const match = otherItems.find(o => o.id === item.relatedId); // O(n²)
}

// CORRECT:
const otherMap = new Map(otherItems.map(o => [o.id, o]));
for (const item of items) {
    const match = otherMap.get(item.relatedId); // O(1)
}
```

### No Hardcoded Values

Use constants, enums, or configuration values:

```typescript
// FORBIDDEN:
if (status === 3) { ... }

// CORRECT:
if (status === OrderStatusEnum.COMPLETED) { ... }
```

## Logging

All mutating operations (create, update, delete) must log with structured metadata:

```typescript
await this.logService.info({
    message: 'Creating feature',
    identifier: this.LOG_CONTEXT,
    extraStructuredMetadata: { entityId: id, relevantField: value }
});
```

-   Use `logService.info()` at start and end of mutations
-   Use `logService.info()` before queue dispatches (include queue name)
-   Use `logService.error()` in catch blocks
-   Do NOT log read operations (find, list)
-   **NEVER** use `console.log` — always use `LogService`

## Queue Integration

Always use internal queue services (BullMQ) instead of `@Zoppy-crm/api-signatures`:

```typescript
await this.queueService.execute({
    session: this.sessionService.getSessionData(),
    job: QueueJobEnum.PROCESS_FEATURE,
    queue: QueueEnum.FEATURE_QUEUE,
    data: { entityId: entity.id }
});
```

Never use HMAC-based HTTP calls between internal services. If you find existing code using `@Zoppy-crm/api-signatures`, migrate it to a queue service.

## Validation

Use dedicated validation classes for create/update operations:

```typescript
const validation: CreateFeatureValidation = CreateFeatureValidation.create();
await validation.execute({ companyId, request });
```

Validation classes live in `<feature>/validation/` and extend `ApplicationValidationBase`.

## Error Handling

-   `NotFoundException` (404) — entity not found by ID, code, phone, etc.
-   `UnprocessableEntityException` (422) — validation failures, business rule violations
-   `BadRequestException` (400) — malformed request, missing required fields

Do NOT wrap domain errors in generic catch blocks that swallow the original status code.

## Method Complexity

-   **Deeply nested conditionals**: more than 2-3 levels of `if` nesting is a red flag — extract into helper methods
-   **Overly long methods**: if a method exceeds ~40-50 lines, break into smaller private methods
-   **Long parameter lists**: more than 4-5 parameters suggest the need for an options object

## Clean Code

-   Extract repeated blocks into private methods (placed at the end of the class)
-   Use early returns to reduce nesting
-   Prefer `reduce` over `forEach` with mutable state
-   Name variables clearly — `enrichedLineItems` not `lineItemsFiltered` if the operation is enrichment
-   Fix typos in variable names when you find them
-   Remove dead code (unreachable branches, unused imports)

## Migrations

-   Naming pattern: `YYYYMMDDHHMMSS-description.ts`
-   Generate with: `npx sequelize-cli migration:generate --name migration-name`

### Índices sem lock

Ao criar índices em tabelas grandes, **sempre** use `ALGORITHM: 'INPLACE'` e `LOCK: 'NONE'` para evitar bloquear a tabela em produção:

```typescript
// FORBIDDEN: lock implícito na tabela inteira
await queryInterface.addIndex('orders', ['customerId'], { name: 'idx_orders_customer_id' });

// CORRECT: sem lock (online DDL do MySQL 8)
await queryInterface.addIndex('orders', ['customerId'], {
    name: 'idx_orders_customer_id',
    // @ts-ignore — Sequelize typing não expõe essas opções mas o MySQL 8 suporta
    algorithm: 'INPLACE',
    lock: 'NONE'
});
```

Para índices `UNIQUE`, o mesmo se aplica. Se o `INPLACE` não for possível (ex: índice `FULLTEXT`), documente o motivo e alinhe com o time antes de rodar em produção.

### Boas práticas

-   Uma migration faz **uma coisa** — não misture criação de tabela com adição de coluna em outra
-   Sempre implemente o `down()` para rollback
-   Teste localmente com `npm run migrate` antes de subir

## Branching & Pull Requests

### Nomenclatura de Branches

| Tipo              | Padrão                                                 | Exemplo                                  |
| ----------------- | ------------------------------------------------------ | ---------------------------------------- |
| Feature/Milestone | `milestone/<nome-da-feature>`                          | `milestone/coupon-engine`                |
| Task (sub-branch) | `task/<nome-da-feature>/<issue-number>-<nome-da-task>` | `task/coupon-engine/456-create-endpoint` |
| Hotfix            | `hotfix/<issue-number>-<descrição>`                    | `hotfix/789-fix-order-sync-null`         |

-   **Sempre incluir o número da issue** no nome da branch para vinculação automática com GitHub Projects
-   Branches `milestone/*` são protegidos — sem push direto, todas as mudanças entram via PR
-   Branches `task/*` são criados a partir do `milestone/*` correspondente
-   Nomes devem ser curtos, descritivos e em kebab-case

### Vinculação com GitHub Projects

O número da issue na branch faz o link automático no GitHub. Para fechar o card ao mergear, use keywords na descrição do PR:

```markdown
Closes #456
```

Keywords válidas: `Closes`, `Fixes`, `Resolves` — ao mergear o PR, a issue é fechada e o card move automaticamente no GitHub Projects.

### Fluxo de Branches

```
milestone/<feature>  ← task/<feature>/<task-1>  (PR)
                     ← task/<feature>/<task-2>  (PR)
                     ← task/<feature>/<task-3>  (PR)

staging ← milestone/<feature>  (PR final)
master  ← staging
```

1. Criar `milestone/<feature>` a partir de `development`
2. Para cada unidade de trabalho, criar `task/<feature>/<task>` a partir do milestone
3. Abrir PR de `task/...` → `milestone/...`, revisar e mergear
4. Ao concluir a feature, abrir PR de `milestone/...` → `staging` → `master`

### Política de Tamanho de PR

-   **Meta**: ~200–400 linhas alteradas por PR (excluindo testes unitários)
-   **Sinais de PR grande demais**:
    -   Muitos arquivos não relacionados
    -   Mistura de refactor + feature + bugfix no mesmo PR
    -   Dificuldade de explicar a mudança em 2–3 frases
-   Se o PR ficou grande demais: **fatiar** em PRs menores

### Boas Práticas de PR

**Ao abrir um PR:**

-   Escrever descrição clara e curta: o que muda, por quê, como testar
-   Um PR = uma mudança bem definida (bugfix, sub-feature, ou refactor pontual)
-   Não misturar assuntos diferentes no mesmo PR
-   Garantir CI verde antes de pedir review

**Ao revisar um PR:**

-   Review profundo e objetivo — não apenas "LGTM"
-   Pedir fatiamento quando o PR está grande ou misturando assuntos
-   Verificar se há testes suficientes para as mudanças
-   Mínimo de 2 approvals antes do merge

### O que NÃO fazer em PRs

-   PR "big bang" com toda a feature de uma vez
-   Push direto em branches protegidos (`milestone/*`, `staging`, `master`)
-   Mergear sem CI verde ou sem reviews suficientes
-   Deixar PR aberto por dias sem ação — revisar e integrar o quanto antes

## General Conventions

-   Models are imported from `@Zoppy-crm/models`, utilities from `@Zoppy-crm/utilities`
-   Use `SessionService` for company/user context — never pass `companyId` manually unless explicitly needed
-   Use `StringUtil.generateUuid()` for generating IDs

## Partners API Specifics

The Partners API runs as `API_SERVICE_ENVIRONMENT=PARTNERS` on port 8082:

-   No `/api` prefix — endpoints are at root (`/customers`, `/coupons`)
-   Authentication via `PartnersExternalAuthMiddleware` (ExternalToken lookup, not JWT)
-   Validation pipe is more permissive (no whitelist/forbidNonWhitelisted)
-   Separate Swagger at `/docs` via `initializePartnersSwagger()`
-   SysMiddle endpoints were intentionally removed (partnership cancelled)
