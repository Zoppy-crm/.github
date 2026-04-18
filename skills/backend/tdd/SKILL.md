---
name: tdd
description: >
  Test-driven development for the zoppy-api NestJS project — red-green-refactor loop applied to
  NestJS layers (domain unit tests, application integration tests, controller E2E tests). Use when
  writing, modifying, or reviewing tests. Triggers on: "write tests for", "add tests", "TDD",
  "red-green-refactor", "test coverage", "write a spec", "test this service", "test this domain",
  "test this controller", "integration tests", or any task where tests should precede implementation.
  Always apply this skill before writing production code.
---

# Test-Driven Development — zoppy-api

## Role

You are a TDD-focused programmer. Write failing tests **before** implementation. Never write production code without a failing test driving it.

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means (querying the DB directly instead of using the interface). Warning sign: your test breaks when you refactor, but behavior hasn't changed.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" — treating RED as "write all tests" and GREEN as "write all code."

This produces **crap tests**:
- Tests written in bulk test _imagined_ behavior, not _actual_ behavior
- You end up testing the _shape_ of things rather than user-facing behavior
- Tests pass when behavior breaks, fail when behavior is fine
- You outrun your headlights, committing to test structure before understanding the implementation

**Correct approach**: vertical slices via tracer bullets. One test → one implementation → repeat.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

## Workflow

### 1. Planning

Before writing any code:

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm which behaviors to test (prioritize)
- [ ] Identify opportunities for [deep modules](deep-modules.md) (small interface, deep implementation)
- [ ] Design interfaces for [testability](interface-design.md)
- [ ] List the behaviors to test (not implementation steps)
- [ ] Get user approval on the plan

Ask: "What should the public interface look like? Which behaviors are most important to test?"

**You can't test everything.** Focus testing effort on critical paths and complex logic, not every edge case.

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

Proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:
- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor

After all tests pass, look for [refactor candidates](refactoring.md):

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where natural
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```

---

# Project Patterns — zoppy-api (NestJS)

The generic TDD discipline above is the rule. The sections below show **how it lands in this codebase**: which test type per layer, which helpers to use, what to mock and what not to.

## Layer → Test Type Mapping

Match test type to the layer under test:

| Layer | Test type | Database | Purpose |
|---|---|---|---|
| `src/domain/` | Unit | In-memory SQLite via `TestUtils` | Entity methods, business queries, persistence |
| `src/application/` | Integration | In-memory SQLite via `TestUtils` | Multi-domain orchestration, all branches |
| `src/access/http/` | E2E | In-memory SQLite via `TestUtils` | HTTP codes, guards, request validation, response shape |

> **Integration over mocks.** In zoppy-api the DB is fast enough (in-memory SQLite) that integration tests are the default, not a special case. Tracer-bullet cycles exercise real persistence.

## File Conventions

- Co-locate with source: `order.domain.ts` → `order.domain.spec.ts`
- One `describe` per class, one `it` per behavior
- Describe blocks: `describe('OrderDomain')` → `it('should filter duplicate spent messages')`

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

## Mocking Rules

General rule (see [mocking.md](mocking.md)): mock at **system boundaries** only. In zoppy-api this means external HTTP, third-party SDKs, time, and randomness — not your own code.

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

## Avoiding Flaky Tests

- `jest.useFakeTimers()` for any code that calls `new Date()` or uses timers
- Always clean up in `afterEach` via `TestUtils.clearDatabase(sequelize)`
- Generate unique IDs with `StringUtil.generateUuid()` — never hardcode UUIDs
- Each test must be fully self-contained; never rely on execution order

---

## Reference

- [tests.md](tests.md) — good vs bad tests (generic examples)
- [mocking.md](mocking.md) — when and how to mock at boundaries
- [refactoring.md](refactoring.md) — refactor candidates after GREEN
- [deep-modules.md](deep-modules.md) — small interface, deep implementation
- [interface-design.md](interface-design.md) — designing for testability
