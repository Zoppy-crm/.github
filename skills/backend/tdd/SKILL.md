---
name: tdd
description: >
  TDD workflow for the zoppy-api NestJS project. Use this skill whenever writing, modifying, or reviewing
  tests — including unit tests for domains, integration tests for application services, and E2E tests for
  controllers. Triggers on: "write tests for", "add tests", "TDD", "test coverage", "write a spec",
  "test this service", "test this domain", "test this controller", or any task where tests should precede
  implementation. Always apply this skill before writing production code.
---

# TDD — Test-Driven Development

## Role

You are a TDD-focused programmer. Write failing tests **before** implementation. Never write production code without a failing test driving it.

**The cycle:**
1. **Red** — Write a failing test that precisely describes expected behavior
2. **Green** — Write the minimum code to make it pass
3. **Refactor** — Clean up without breaking tests

---

## Layer → Test Type Mapping

Match test type to the layer under test:

| Layer | Test type | Database | Purpose |
|---|---|---|---|
| `src/domain/` | Unit | In-memory SQLite via `TestUtils` | Entity methods, business queries, persistence |
| `src/application/` | Integration | In-memory SQLite via `TestUtils` | Multi-domain orchestration, all branches |
| `src/access/http/` | E2E | In-memory SQLite via `TestUtils` | HTTP codes, guards, request validation, response shape |

---

## File Conventions

- Co-locate with source: `order.domain.ts` → `order.domain.spec.ts`
- One `describe` per class, one `it` per behavior
- Describe blocks: `describe('OrderDomain')` → `it('should filter duplicate spent messages')`

---

## Module Setup Template

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import { Sequelize } from 'sequelize-typescript';
import { TestUtils } from '@Zoppy-crm/test-utils';
import { StringUtil, TestConstants } from '@Zoppy-crm/utilities';
import { SessionService } from 'src/services/session/session.service';
import { TestSession } from 'src/tests/test-session';
import { RedisModuleMock } from 'src/tests/mocks/redis.module.mock';
import { QueueModuleMock } from 'src/tests/mocks/queue-module.mock';

describe('XxxApplication', () => {
    let app: INestApplication;
    let application: XxxApplication;
    let sessionService: SessionService;
    let sequelize: Sequelize;
    let sequelizeId: string;

    beforeAll(async () => {
        sessionService = new SessionService();
        const moduleRef: TestingModule = await Test.createTestingModule({
            imports: [
                RepositoryModule,
                XxxDomainModule,
                XxxApplicationModule,
                SessionModule,
                RedisModuleMock.register(),
                QueueModuleMock.register(),
            ],
            providers: [SessionService],
        })
            .overrideProvider(SessionService)
            .useValue(sessionService)
            .compile();

        app = moduleRef.createNestApplication();
        await app.init();
        application = moduleRef.get(XxxApplication);
    });

    beforeEach(async () => {
        sequelizeId = StringUtil.generateUuid();
        sequelize = await TestUtils.getSequelize(sequelizeId);
        const company = await Company.create({ id: StringUtil.generateUuid() });
        await TestSession.setSession(sessionService, TestConstants.USERS.MASTER.USER_NAME);
        sessionService.setCompany(company);
    });

    afterEach(async () => {
        await TestUtils.clearDatabase(sequelize);
    });

    afterAll(async () => {
        await TestUtils.cleanupSequelize(sequelizeId);
        await app.close();
    });

    it('should <expected behavior>', async () => {
        // Arrange
        // Act
        // Assert
    });
});
```

---

## Mocking Rules

### Never mock Domains
Domains run against the real in-memory SQLite database. Mocking them hides real persistence behavior.

```typescript
// WRONG
jest.spyOn(customerDomain, 'findOne').mockResolvedValue(fakeCustomer);

// RIGHT — seed real data
const customer = await Customer.create({ id: StringUtil.generateUuid(), companyId: company.id });
```

### Only mock external services
Third-party HTTP, AWS SDK, webhook calls — these are the only things that should be mocked.

```typescript
// HTTP via nock
import nock from 'nock';
nock('https://api.provider.com').get('/orders').reply(200, { orders: [] });

// Queues → already handled by QueueModuleMock.register()
// Redis  → already handled by RedisModuleMock.register()
```

### Spy on private methods only as a last resort
```typescript
const spy = jest.spyOn(application as any, 'sendAlert').mockResolvedValue(undefined);
expect(spy).toHaveBeenCalledWith(expectedPayload);
```

---

## Assertion Patterns

### Assert on error type, not message string
```typescript
// WRONG — message strings change
expect(err.message).toBe('Customer not found');

// RIGHT
expect(err).toBeInstanceOf(NotFoundException);
```

### HTTP status codes in controller E2E
```typescript
const res = await request(app.getHttpServer())
    .get('/customers/999')
    .set('Authorization', `Bearer ${token}`);
expect(res.status).toBe(404);
```

### neverthrow result types
```typescript
const result = await application.execute(params);
expect(result.isOk()).toBe(true);
if (result.isOk()) expect(result.value.id).toBeDefined();

const err = await application.execute(badParams);
expect(err.isErr()).toBe(true);
if (err.isErr()) expect(err.error).toBeInstanceOf(ValidationException);
```

---

## What to Test Per Layer

### Domain (unit)
- Public business methods (deduplication, filtering, aggregation)
- `findOne` / `findMany` with multiple filter combinations
- Edge cases: empty results, null fields, boundary values
- Persistence round-trip: create → find → assert fields

### Application (integration)
- Happy path: full input → expected database state
- Every error branch: not found, validation failure, duplicate
- Cross-domain side effects (entity A triggers change in entity B)
- Queue jobs dispatched with correct payload

### Controller (E2E)
- `400` — invalid request body
- `401` — no token
- `403` — wrong role
- `404` — entity not found
- `200`/`201` — happy path including response shape
- Database side effects (record actually created/updated)

---

## Running Tests

```bash
# All tests (CI)
npm run test

# Single file
npm run test -- --testPathPattern="src/application/order-sync/order-sync.application"

# Watch
npm run test:watch

# Coverage
npm run test:cov
```

---

## Avoiding Flaky Tests

- `jest.useFakeTimers()` for any code that calls `new Date()` or uses timers
- Always clean up in `afterEach` via `TestUtils.clearDatabase(sequelize)`
- Generate unique IDs with `StringUtil.generateUuid()` — never hardcode UUIDs
- Each test must be fully self-contained; never rely on execution order
