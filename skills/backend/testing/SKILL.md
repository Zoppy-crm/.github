---
name: testing
description: >
    Test conventions for the zoppy-api NestJS project: in-memory DB via TestUtils, minimize mocks,
    layer-specific particularities (controller / application / domain). Use this skill whenever writing
    or reviewing .spec.ts files, deciding what to mock vs what to run against a real DB, structuring
    describe/it blocks, setting up integration tests, or answering "how do I test X in this project".
    Triggers on: "write a test", "add tests", "test this service", "test this controller", "test this
    domain", "how to test", "spec file", ".spec.ts", "TestUtils", "test conventions", "integration
    test", "in-memory database", "minimize mocks", "TestingModule", "jest setup for zoppy-api".
---

# TESTING.MD

This is a document outlining rules and best practices to write and mantain test code (.spec.ts files) within the zoppy-api codebase.

## Overview

Zoppy-api is a project structured in layers. The main layers are the Controller, Application and Domain layers. We extend this logic by creating helpers and services to organize and reuse code as needed. Each layer has its own test particularities, but we still have general rules that should be followed in any case.

Remember that a code file is to be used also as documentation of a code. A test file should tell a story to its readers about what the code can, and can not do.

### General rules

**Minimize mocks.**
We emulate real execution as closely as possible using an in-memory database via `TestUtils`. Only mock external integrations outside zoppy-api scope (API calls to third-party services, AWS etc.)

**When mocking external services**, test all scenarios:

-   Successful response with expected data
-   Successful response with unexpected/malformed data
-   Network/connection failures
-   Timeout scenarios
-   Error responses (4xx, 5xx)

**Avoid flaky tests:**

-   DON'T assert on specific error message strings → DO assert on error class/type
-   DON'T test time-sensitive scenarios directly → DO use `jest.useFakeTimers()`
-   DON'T rely on execution order → DO make tests independent

**Find similar references first.**
Before writing a test, search for similar entity patterns:

-   `UserAction` → `CustomerAction`
-   `UserActionGroup` → `MessageTemplateGroup`
-   Use grep: `grep -r "describe.*YourEntity" src/`

**One behavior per `it()` block.**

-   Keep setup close to assertions. Only put truly shared setup in `beforeEach` `beforeAll`.

We have boilerplate code that every test uses that consist in the setup and teardown of our tests via jest hooks. An example for a application test is the following:

```typescript
...

describe(`CustomerActionApplication`, () => {
let app: INestApplication;
let application: CustomerActionApplication;
let sessionService: SessionService;
let sequelize: Sequelize;
let sequelizeId: string;

    beforeAll(async () => {
        sessionService = new SessionService()
        const moduleRef: TestingModule = await Test.createTestingModule({
            controllers: [],
            imports: [
                RepositoryModule,
                DomainModule,
                ApplicationModule,
                SessionModule,
                RedisModuleMock.register(),
                QueueModuleMock.register(),
                JwtModule.register({
                    secret: process.env.JWT_SECRET,
                    signOptions: { expiresIn: process.env.JWT_EXPIRATION_TIME }
                })
            ],
            providers: [LocalStrategy, JwtService, SessionService, WcCouponAlertDomain, ...repositoryProviders]
        })
            .overrideProvider(SessionService)
            .useValue(sessionService)
            .compile();
        app = moduleRef.createNestApplication();
        await app.init();

        const contextId: ContextId = ContextIdFactory.create();

        application = await moduleRef.resolve(CustomerActionApplication, contextId);
    });

    beforeEach(async () => {
        sequelizeId = StringUtil.generateUuid();
        sequelize = await TestUtils.getSequelize(sequelizeId);
        const company: Company = await Company.create({ id: StringUtil.generateUuid() });
        sessionService.setCompany(company);
        const user: User = await User.create({
            id: StringUtil.generateUuid(),
            companyId: company.id,
            role: RoleEnum.MASTER,
            userName: TestConstants.USERS.MASTER.USER_NAME
        });
        sessionService.setUser(user);
    });

    afterAll(async () => {
        await TestUtils.cleanupSequelize(sequelizeId);
    });


    it('Should create customer action for type abandonedCart', async () => {
      ...
    })

    ...

});

```

Remember to setup your tests in a similar way, but you can adapt it to the context of the test as needed.

### Domain layer

When testing the domain layer, make sure to test the core behaviour of an entity. Test each public method and its edge cases making sure that you focus on the business rules of an entity, not the functionality of code we trust to be working (like the RepositoryAdapter). If there is no code in this layer other then extending the RepositoryAdapter, ask the user if this is a valid test to be making.

If there is another domain injected in the domain to be tested (case to ONLY happen when taling about hierarchical domains, like userAction and userActionGroups, where an userActionGroup can interact with the userAction domain of its children ), test their interactions and their relationships.

Make persistence tests also. When testing if an entity is created correctly, you can fetch it from the db after the act and use this as the font of truth.

This layer could be seen as an "Unit test" within zoppy-api, meaning that it is to be tested as a separate unit, only regarding the domain of one entity/feature.

### Application layer

Here, we start to coordinate multiple domains and other services/helpers. This means the test should focus on seeing how one entity interferes with another, all edge cases this relationships could have, and more.

This is the layer with the most logic in zoppy-api so you have plenty of references to run on. This should be the layer that is more thourghly tested of them all.

This layer could be seen as an "Integration test" within zoppy-api, meaning that it coordinates multiple entities/domains/services and should focus on testing the relationship between them all.

### Controller layer (integration tests)

This layer tests the HTTP contract end-to-end within the application: parameter validation, error response codes (not error messages — that is flaky), role-based access, and the side effects of a route. You call an endpoint via supertest, then query the database to verify the expected state — without concerning yourself with internal implementation details.

This layer could be seen as an "integration test" within zoppy-api, meaning that it closely mimics the use of an actual client to our API.

**Setup boilerplate for controller tests:**

```typescript
import { INestApplication } from '@nestjs/common';
import { JwtModule, JwtService } from '@nestjs/jwt';
import { Test, TestingModule } from '@nestjs/testing';
import { ExternalToken } from '@Zoppy-crm/models';
import { TestConstants } from '@Zoppy-crm/utilities';
import { PartnersApplicationModule } from 'src/application/partners/partners-application.module';
import { repositoryProviders } from 'src/cross-cutting/providers/repository.providers';
import { DomainModule } from 'src/domain/domain.module';
import { QueueServiceModuleMock } from 'src/tests/mocks/queue-service-module.mock';
import { RedisModuleMock } from 'src/tests/mocks/redis.module.mock';
import { QueueModuleMock } from 'src/tests/mocks/queue-module.mock';
import { RepositoryModule } from 'src/repository/repository.module';
import { SessionModule } from 'src/services/session/session.module';
import { SessionService } from 'src/services/session/session.service';
import { TestSession } from 'src/tests/test-session';
import { TestUtils } from '@Zoppy-crm/test-utils';
const request: any = require('supertest');

describe('FeatureController', () => {
    let app: INestApplication;
    let jwtService: JwtService;
    let sessionService: SessionService;
    let externalToken: ExternalToken;

    const BASE_URL: string = '/feature';

    beforeAll(async () => {
        await TestUtils.setSequelize();
        const moduleRef: TestingModule = await Test.createTestingModule({
            controllers: [FeatureController],
            imports: [
                RepositoryModule,
                DomainModule,
                QueueServiceModuleMock.register(),
                RedisModuleMock.register(),
                QueueModuleMock.register(),
                PartnersApplicationModule, // or ApplicationModule for main API
                SessionModule,
                JwtModule.register({
                    secret: process.env.JWT_SECRET,
                    signOptions: { expiresIn: process.env.JWT_EXPIRATION_TIME }
                })
            ],
            providers: [JwtService, SessionService, ...repositoryProviders]
        })
            .overrideProvider(SessionService)
            .useValue(new SessionService())
            .compile();

        app = moduleRef.createNestApplication();
        await app.init();

        jwtService = await moduleRef.get(JwtService);
        sessionService = await moduleRef.resolve(SessionService);
        await TestSession.setSession(sessionService, TestConstants.USERS.ADMIN.USER_NAME);
        externalToken = await TestSession.getExternalToken(sessionService, jwtService);
    });

    it('Should create entity', async () => {
        const response: any = await request(app.getHttpServer())
            .post(BASE_URL)
            .set('Authorization', externalToken.hash)
            .send({ name: 'test' /* ... */ });

        expect(response.status).toEqual(200);
        expect(response.body).toHaveProperty('id');
    });

    it('Should return 404 for non-existent entity', async () => {
        const response: any = await request(app.getHttpServer())
            .get(`${BASE_URL}/00000000-0000-0000-0000-000000000000`)
            .set('Authorization', externalToken.hash);

        expect(response.status).toEqual(404);
    });
});
```

**Key points:**

-   Use `QueueServiceModuleMock`, `RedisModuleMock`, `QueueModuleMock` to avoid real queue/Redis connections
-   Use `TestSession.setSession()` to establish company/user context
-   Use `TestSession.getExternalToken()` for Partners API auth (ExternalToken), or `TestSession.getToken()` for main API auth (JWT)
-   Use `TestSession.setSessionWithCompanyAndUser()` when you need a specific company configuration (e.g., `provider: WAKE_COMMERCE`)
-   Assert on status codes, not error messages
-   For write operations, verify the side effect by querying the database after the request

### No Mocking Domains

**NEVER** mock Domain classes in tests. Tests that mock Domains are considered low-quality.

```typescript
// FORBIDDEN:
jest.spyOn(someDomain, 'findById').mockResolvedValue(fakeEntity);

// CORRECT: use the real Domain with in-memory DB
const entity = await someDomain.saveOne({ ...validData });
const result = await application.process(entity.id);
```

Only mock **external integrations** (third-party API calls, AWS services, etc.).
