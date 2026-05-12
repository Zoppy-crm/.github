---
name: domain
description: >
  Guide for creating and modifying Domain classes in the zoppy-api project. Use this skill
  whenever you need to create a new Domain, add custom queries to an existing Domain, register
  lifecycle hooks (post-create/update/delete), integrate a Domain with BullMQ queues, or decide
  between RepositoryAdapter and OpenSearchAdapter. Also covers how to register the Domain in
  DomainModule. Trigger this skill when the user mentions: "create domain", "new domain",
  "add query to domain", "domain hook", "registerHook", "RepositoryAdapter",
  "domain module", or when implementing a new entity in the domain layer.
---

# Creating a Domain in zoppy-api

## What is a Domain

In the zoppy-api architecture, the `src/domain/` layer is responsible for data access with
coupled business rules. A Domain is not a simple repository: it exposes rich queries and can
automatically react to persistence events (hooks).

Every Domain extends `RepositoryAdapter<T>` — a base class that already handles:
- Automatic filtering by `companyId` from the current session
- Soft deletes (`deletedAt`)
- Transaction control
- Hook emission after persistence

## Rich domain, not anemic

Push business rules down into the Domain instead of letting them pile up in the Application. Today many of our Domains are anemic CRUD wrappers — when you're adding behavior to a feature, prefer a Domain method.

Concretely, these belong to the Domain (not the Application):

- **State transitions** — `markAsIssued`, `markAsCancelled`, `markAsFailed`, `markAsArchived`. The Domain validates the previous state if needed, mutates, and `updateOne`s.
- **"Create with defaults" / "next of"** — `createForInvoice(invoice, provider)`, `findNextAttemptNumberFor(invoiceId)`. The rule for choosing the attempt number / centavos conversion / default provider stays in the Domain.
- **Entity-scoped queries** — `findActiveByInvoiceId`, `findPendingForRetry`, `findByExternalReference`. Anything answerable from a single entity (and its parents/children).
- **Field-update bundles** — `updateS3Keys(id, pdfKey, xmlKey)`. The Domain knows which fields go together.

These stay in an Application or Service (not the Domain):

- Orchestration across **multiple unrelated** domains (e.g., loading an Invoice + Company + creating a TaxInvoice + recording an event).
- Calls to **queue services** (enqueue follow-up jobs).
- Calls to **ports / external SDKs** (the Application talks to the gateway lib, not the Domain).

Good Domain methods return the updated entity when they mutate, so callers don't double-fetch.

---

## Minimal structure

```typescript
// src/domain/my-entity.domain.ts
import { Inject } from '@nestjs/common';
import { MyEntity } from '@Zoppy-crm/models';
import { ProviderNames } from '@Zoppy-crm/utilities';
import { Repository } from 'sequelize-typescript';
import { RepositoryAdapter } from 'src/repository/adapters/repository-adapter';
import { SessionService } from 'src/services/session/session.service';
import { LogService } from 'src/services/log/log.service';

export class MyEntityDomain extends RepositoryAdapter<MyEntity> {
    public constructor(
        public readonly session: SessionService,
        @Inject(ProviderNames.MyEntityRepository) repository: Repository<MyEntity>,
        protected readonly logService: LogService
    ) {
        super(repository, session, logService);
    }
}
```

**Constructor rules:**
- `session` and `repository` are always required
- `logService` is optional, but required if you register hooks (enables logging hook errors)
- Always pass `logService` as the third argument to `super()` if the Domain has hooks
- The `ProviderNames` name follows the convention `XRepository` where X is the entity name

---

## Custom queries

Use the methods inherited from `RepositoryAdapter` as a base. The `companyId` filter is **automatic**
— do not add `where: { companyId: ... }` manually.

```typescript
import { Op } from 'sequelize';
import { ZoppyFilter } from 'src/access/http/requests/filter';

export class WcCouponDomain extends RepositoryAdapter<Coupon> {
    // Simple query with conditions
    public async findUnusedCouponByPhone(phone: string, withTrashed = false): Promise<Coupon> {
        return await this.findOne(
            {
                where: {
                    phone,
                    expiryDate: { [Op.gte]: new Date() },
                    used: { [Op.not]: true }
                },
                order: [['createdAt', 'DESC']]
            },
            withTrashed
        );
    }

    // Paginated list
    public async findAllPaginated(request: ZoppyFilter<Coupon[]>): Promise<ZoppyFilter<Coupon[]>> {
        return await this.findPaginated({ where: {} }, false, request);
    }

    // Raw SQL when necessary — use this.session.getCompany().id explicitly
    public async findBetweenDates(start: Date, end: Date): Promise<Coupon[]> {
        return await this.rawQuery(
            `SELECT * FROM WcCoupons WHERE expiryDate BETWEEN ? AND ? AND companyId = ?`,
            { replacements: [start, end, this.session.getCompany().id], type: QueryTypes.SELECT }
        );
    }
}
```

**Available methods in RepositoryAdapter:**

| Method | Description |
|--------|-------------|
| `findById(id, withTrashed?)` | Find by PK |
| `findByIdOrFail(id)` | Find by PK or throw error |
| `findOne(options, withTrashed?)` | Single find with conditions |
| `find(options, withTrashed?)` | List with conditions |
| `findMany(ids[])` | Find by multiple IDs |
| `findPaginated(options, withTrashed, filter)` | Full pagination |
| `findAndCountAll(options)` | Total + data |
| `saveOne(record)` | Create one record |
| `saveMany(records[])` | Create many records |
| `updateOne(record)` | Update one |
| `updateAll(fields, options)` | Update by condition |
| `deleteOne(record)` | Soft delete one |
| `deleteMany(records[])` | Soft delete many |
| `hardDeleteOne(record)` | Hard delete |
| `rawQuery(sql, opts)` | Raw SQL |
| `upsertOne(record)` | Upsert |
| `findOrSave(record, findOptions)` | Find or create |

The `withTrashed: boolean` parameter controls whether records with `deletedAt != null` are included.

---

## Lifecycle hooks

Use hooks to trigger side effects **after** persistence, such as enqueueing jobs. Hooks are
registered in the constructor and fire automatically after any persistence operation
(including `saveMany`, `updateMany`, etc.).

```typescript
import { RepositoryAdapter, RepositoryHookType } from 'src/repository/adapters/repository-adapter';
import { MySyncQueueService } from 'src/access/queues/services/my-sync.queue.service';
import { QueueJobEnum } from 'src/access/queues/constants/queue.constants';
import { QueueEnum } from 'src/access/queues/base.queue';

export class MyEntityDomain extends RepositoryAdapter<MyEntity> {
    public constructor(
        public readonly session: SessionService,
        @Inject(ProviderNames.MyEntityRepository) repository: Repository<MyEntity>,
        private readonly mySyncQueueService: MySyncQueueService,
        protected readonly logService: LogService
    ) {
        super(repository, session, logService);

        // Register hooks in the constructor, after super()
        this.registerHook(RepositoryHookType.CREATION, (record: MyEntity) =>
            this.enqueueSync(record)
        );
        this.registerHook(RepositoryHookType.UPDATE, (record: MyEntity) =>
            this.enqueueSync(record)
        );
    }

    private async enqueueSync(record: MyEntity): Promise<void> {
        await this.mySyncQueueService.execute(
            {
                session: this.session.getSessionData(),
                job: QueueJobEnum.MY_SYNC_JOB,
                queue: QueueEnum.MY_SYNC_QUEUE
            },
            false,           // skipLogs
            null,            // priority
            `my-sync-${record.id}`  // jobId for deduplication
        );
    }
}
```

**Available hook types:**

| Type | When it fires |
|------|---------------|
| `RepositoryHookType.CREATION` | After `saveOne`, `saveMany`, `findOrSave` |
| `RepositoryHookType.UPDATE` | After `updateOne`, `updateMany`, `updateAll` |
| `RepositoryHookType.DELETION` | After `deleteOne`, `deleteMany` |
| `RepositoryHookType.UPSERT` | After `upsertOne` |

**Note on transactions:** When a hook is registered and the operation occurs within a transaction,
the hook **only fires after commit** (not in the middle of the transaction). This prevents
enqueueing jobs for data that could be rolled back.

**Hook error handling:** Errors in hooks are captured silently and logged via `logService` —
they never propagate to the original operation.

---

## Overriding base methods

When you need to execute extra logic beyond hooks (e.g., registering an audit via queue service
directly on the operation result), override the method:

```typescript
public async saveOne(record: CreationAttributes<MyEntity>): Promise<MyEntity> {
    const entity: MyEntity = await super.saveOne(record);
    await this.userActionQueueService.creatingUserAction(!!entity, {
        type: UserActionTypeEnum.CREATE_MY_ENTITY,
        actionId: entity?.id
    });
    return entity;
}
```

Use sparingly — prefer hooks when the side effect is dispatching an async job. Override the
method when you need the return value of the operation to make a decision.

---

## When to use OpenSearchAdapter

Use `OpenSearchAdapter<T>` instead of `RepositoryAdapter<T>` when the Domain requires:
- Full-text search (e.g., search by name, description)
- Complex aggregations (e.g., count by field)
- Dynamic filters with relevance scoring

Examples in the project: `ClientDomain`, `WcOrderDomain`, `WcProductDomain`.

```typescript
import { OpenSearchAdapter } from 'src/services/opensearch/opensearch.adapter';

export class ClientDomain extends OpenSearchAdapter<Client> {
    // Search field configuration
    public readonly textSearchFields: string[] = ['name', 'email', 'phone'];
    public readonly keywordFields: string[] = ['status', 'companyId'];
    public readonly aggregationFields: string[] = ['status'];

    public constructor(
        public readonly session: SessionService,
        @Inject(ProviderNames.ClientRepository) repository: Repository<Client>,
        protected readonly logService: LogService
    ) {
        super(repository, session, logService);
    }
}
```

Use `RepositoryAdapter` when in doubt — `OpenSearchAdapter` only pays off when full-text search
is an explicit requirement.

---

## Register in DomainModule

Add the Domain to `src/domain/domain.module.ts` in two places:

**1. Import at the top of the file:**
```typescript
import { MyEntityDomain } from './my-entity.domain';
```

**2. In the `providers` and `exports` arrays of `@Module`:**
```typescript
@Module({
    imports: [RepositoryModule, ServiceModule, QueueServiceModule, ...],
    providers: [
        // ... other domains in alphabetical order
        MyEntityDomain,
        // ...
    ],
    exports: [
        // ... other domains in alphabetical order
        MyEntityDomain,
        // ...
    ]
})
export class DomainModule {}
```

Keep alphabetical order in the `providers` and `exports` arrays.

---

## Pre-finalization checklist

- [ ] Class extends `RepositoryAdapter<T>` (or `OpenSearchAdapter<T>` if needed)
- [ ] `@Inject(ProviderNames.XRepository)` in the constructor
- [ ] `super(repository, session, logService)` called
- [ ] If hooks exist: `logService` passed to `super()` and injected
- [ ] Hooks registered in the constructor after `super()`
- [ ] Custom queries do not include manual `companyId` in `where` (it's automatic)
- [ ] Domain added to `providers` and `exports` in `DomainModule`
- [ ] Tests written (see skill-tdd for domain test patterns)
