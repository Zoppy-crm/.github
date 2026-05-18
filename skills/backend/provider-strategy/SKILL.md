---
name: provider-strategy
description: How to create a new e-commerce or ERP provider strategy in the zoppy-api project. Use this skill whenever the user wants to add support for a new provider (Shopify, VTEX, Yampi, Bling, Tiny, Tray, etc.), create a strategy class for order sync, abandoned cart sync, or similar data sync operations, or asks about Strategy pattern, CompanyEcommerceProviderEnum, CompanyErpProviderEnum, or how to implement the `build()` method. Trigger on phrases like "novo provider", "nova integração", "strategy para X", "sincronização de pedidos", or when implementing a new e-commerce/ERP connector.
---

# Provider Strategy Pattern

Each e-commerce/ERP provider (Shopify, VTEX, Yampi, Bling, etc.) implements its own strategy class. The strategy encapsulates provider-specific API calls while the orchestration (calling the strategy, saving results, managing failures) stays in the Application Service.

## Strategy base classes by domain

| Sync type      | Base class                                              | Location                                     |
| -------------- | ------------------------------------------------------- | -------------------------------------------- |
| Order sync     | `OrderSyncRequestStrategyBase`                          | `src/application/order-sync/strategies/`     |
| Abandoned cart | `AbandonedCartSyncRequestStrategyBase`                  | `src/application/abandoned-cart/strategies/` |
| Customer sync  | (similar pattern — look for `*SyncRequestStrategyBase`) | `src/application/*/strategies/`              |

## Creating a new strategy

A strategy is a plain TypeScript class (no `@Injectable()`) that extends the appropriate base.

```typescript
import { DataSyncManagement, Store, Key } from '@Zoppy-crm/models';
import { StoreTypeEnum } from '@Zoppy-crm/utilities';
import { DataNotSyncedRequest } from 'src/access/http/requests/order-sync/data-not-synced.request';
import { OrderSyncRequestStrategyBase } from './order-sync-request.strategy.base';
import { DataSyncManagementOrderSyncRequest } from 'src/access/http/requests/hub-sync/data-sync-management-order-sync.request';
import { YampiOrderService, YampiOrderMapper, YampiAuthService } from '@Zoppy-crm/yampi';

export class YampiOrderSyncRequestStrategy extends OrderSyncRequestStrategyBase {
    public async build(management: DataSyncManagement, ids: string[] = null): Promise<DataSyncManagementOrderSyncRequest> {
        // 1. Find or resolve the API key for this company
        const key: Key = await this.findKey();

        // 2. Find or create the store record
        const store: Store = await this.findOrCreateStore({
            keyId: key.id,
            type: StoreTypeEnum.E_COMMERCE
        });

        // 3. Determine which IDs to sync
        const orderIds: string[] = ids ?? (await this.getOrderIdsForSync(management, key));

        const orderRequests: OrderSyncRequestBase[] = [];
        const dataNotSyncedRequests: DataNotSyncedRequest[] = [];

        // 4. Iterate and call the provider API for each ID
        for (const orderId of orderIds) {
            try {
                const order = await YampiOrderService.getById({ key }, orderId);
                if (!order) continue;
                orderRequests.push(YampiOrderMapper.toSyncRequest(order, store));
            } catch (error: any) {
                // unprocessable: true = permanent failure (skip on retry)
                // unprocessable: false = transient failure (retry later)
                const unprocessable = error instanceof RequiredFieldsException;
                dataNotSyncedRequests.push(
                    this.buildDataNotSyncedRequest(orderId, management.id, error, unprocessable, null, error.message)
                );
            }
        }

        return {
            dataSyncManagementId: management.id,
            data: orderRequests,
            dataNotSynced: dataNotSyncedRequests
        };
    }
}
```

### What the base class provides

The base class injects all shared domains so you don't need to declare them in the strategy:

```typescript
// Available via `this.` in your strategy:
this.findKey(); // finds the API key for the current company
this.findOrCreateStore(request); // finds or creates the Store record
this.findCompany(key); // fetches the Company record
this.updateCompany(company); // saves company changes
this.buildDataNotSyncedRequest(); // standardized error object for failed IDs
this.sessionService; // session access if needed
```

### The `unprocessable` flag in `buildDataNotSyncedRequest`

-   `unprocessable: true` — the record can never be synced (missing required fields, invalid data). Don't retry.
-   `unprocessable: false` — transient error (API timeout, rate limit). Can be retried.

## Wiring the provider end-to-end

The strategy itself is only half the work. The flow is:

```
OrderSyncBuilderApplication (dispatch) → QueueService (enqueue) → QueueProcessor (execute strategy)
```

### Step 1: Add the provider to the enum

The enum lives in the shared package `@Zoppy-crm/utilities`. Update it there:

```typescript
export enum CompanyEcommerceProviderEnum {
    YAMPI = 'yampi',
    YOUR_PROVIDER = 'your-provider' // add here
}
```

### Step 2: Create the QueueService

Create `src/access/queues/services/your-provider-order-sync.queue.service.ts` — follow `YampiOrderSyncQueueService` as reference (see `skill-queue-processor`):

```typescript
@Injectable({ scope: Scope.REQUEST })
export class YourProviderOrderSyncQueueService extends BaseQueue {
    public jobs = [QueueJobEnum.YOUR_PROVIDER_ORDER_SYNC];

    public constructor(
        @InjectQueue(QueueEnum.YOUR_PROVIDER_ORDER_SYNC_QUEUE) public queue: Queue,
        public session: SessionService,
        public logService: LogService
    ) {
        super(queue, logService);
    }
}
```

Register in `src/access/queues/queue-service.module.ts` (providers + exports).

### Step 3: Add a case in `OrderSyncBuilderApplication`

The real "dispatch factory" in this project is `OrderSyncBuilderApplication` (`src/application/order-sync/order-sync-builder.application.ts`). It has a `buildOrderForHub()` method with a switch that routes each provider to its QueueService.

Add three things:

```typescript
// 1. Inject in the constructor
constructor(
    // ... existing deps
    public readonly yourProviderOrderSyncQueueService: YourProviderOrderSyncQueueService,
) {}

// 2. Add the case in buildOrderForHub()
case CompanyEcommerceProviderEnum.YOUR_PROVIDER:
    await this.executeYourProviderOrderSync(dataSyncManagement);
    break;

// 3. Add the private method (follow existing provider methods for priority/deduplication)
private async executeYourProviderOrderSync(request: DataSyncManagement): Promise<void> {
    const priority = getProviderSyncPriority(CompanyEcommerceProviderEnum.YOUR_PROVIDER, request.routine);
    await this.yourProviderOrderSyncQueueService.execute(
        {
            session: this.session.getSessionData(),
            job: QueueJobEnum.YOUR_PROVIDER_ORDER_SYNC,
            data: { dataSyncManagement: request },
            queue: QueueEnum.YOUR_PROVIDER_ORDER_SYNC_QUEUE
        },
        false,
        priority,
        undefined,
        { deduplication: { id: `${ORDER_SYNC_BUILDER_DEDUP_PREFIX}${request.id}`, ttl: 3600000 } }
    );
}
```

### Step 4: Create the Queue Processor

The processor is where the strategy actually gets called. It's instantiated with `new` because its constructor receives the same shared domains that the strategy base class expects:

```typescript
@Processor(QueueEnum.YOUR_PROVIDER_ORDER_SYNC_QUEUE, { concurrency: 5 })
export class YourProviderOrderSyncQueueProcessor extends QueueProcessorBase {
    public constructor(
        public readonly session: SessionService,
        public readonly logService: LogService,
        // inject all shared domains that OrderSyncRequestStrategyBase needs:
        private readonly wcStoreDomain: WcStoreDomain,
        private readonly keyDomain: KeyDomain // ... other shared domains
    ) {
        super(session, logService);
    }

    public async process(job: Job<QueueBaseData<{ dataSyncManagement: DataSyncManagement }>>): Promise<void> {
        await this.setSession(job);

        const strategy = new YourProviderOrderSyncRequestStrategy(
            this.wcStoreDomain,
            this.keyDomain
            // ... pass all shared deps in the same order as the base constructor
        );

        const result = await strategy.build(job.data.data.dataSyncManagement);
        // ... save result, handle dataNotSynced, etc.
    }
}
```

Register in `src/access/queues/queue.module.ts` (or the appropriate pipeline module).

## Adding QueueEnum and QueueJobEnum entries

```typescript
// src/access/queues/constants/queue.constants.ts
// In QueueEnum:
YOUR_PROVIDER_ORDER_SYNC_QUEUE: `${prefix}YOUR_PROVIDER_ORDER_SYNC_QUEUE`,

// In QueueJobEnum:
YOUR_PROVIDER_ORDER_SYNC = 'YOUR_PROVIDER_ORDER_SYNC_JOB',
```

## Complete checklist for a new provider strategy

-   [ ] Create `your-provider-order-sync-request.strategy.ts` extending the correct base
-   [ ] Implement `build(management, ids?)` with try/catch and `unprocessable` flag
-   [ ] Add the provider to `CompanyEcommerceProviderEnum` (in `@Zoppy-crm/utilities`)
-   [ ] Add `QueueEnum` and `QueueJobEnum` entries in `queue.constants.ts`
-   [ ] Create `YourProviderOrderSyncQueueService` and register in `QueueServiceModule`
-   [ ] Add `case` in `OrderSyncBuilderApplication.buildOrderForHub()` + private method
-   [ ] Create the `QueueProcessor` that instantiates the strategy with `new`
-   [ ] Register the processor in the appropriate queue module
-   [ ] Write tests — the base class spec shows the mock pattern to follow
