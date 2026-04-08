---
name: queue-processor
description: >
  Guide for creating Queue Processors and Queue Services in the zoppy-api project with BullMQ. Use
  this skill whenever you need to create a new queue processor, create a QueueService to enqueue
  jobs, configure concurrency and lockDuration, use Redis locks via ProviderQueueProcessorBase,
  register processors in QueueModule, or understand how session and context are propagated in jobs.
  Trigger this skill when the user mentions: "create processor", "queue processor", "bullmq",
  "queue processor", "create queue service", "enqueue job", "worker", "setSession",
  "QueueProcessorBase", "ProviderQueueProcessorBase", or when implementing asynchronous background
  processing.
---

# Creating a Queue Processor in zoppy-api

## BullMQ architecture overview

```
src/access/queues/
├── base.queue.ts                    ← BaseQueue: enqueues jobs
├── constants/queue.constants.ts     ← QueueEnum, QueueJobEnum
├── processors/
│   ├── queue.processor.base.ts      ← Base for all processors
│   ├── provider-queue.processor.base.ts  ← Base for sync with Redis lock
│   └── {provider}-{entity}.queue.processor.ts
└── services/
    └── {provider}-{entity}.queue.service.ts
```

Each feature needs **two files**: a Processor (consumes jobs) and a QueueService (produces jobs).

---

## 1. Define queue constants

Add in `src/access/queues/constants/queue.constants.ts`:

```typescript
// QueueEnum — queue name in Redis
export enum QueueEnum {
    // ...existing...
    MY_FEATURE_QUEUE = 'my-feature-queue',
}

// QueueJobEnum — job types within the queue
export enum QueueJobEnum {
    // ...existing...
    MY_FEATURE_PROCESS = 'my-feature-process',
}
```

---

## 2. Create the QueueService

The QueueService is the producer — it enqueues jobs from other places (domains, applications):

```typescript
// src/access/queues/services/my-feature.queue.service.ts
import { Injectable, Scope } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';
import { BaseQueue, QueueEnum, QueueJobEnum } from '../base.queue';
import { SessionService } from 'src/services/session/session.service';
import { LogService } from 'src/services/log/log.service';

@Injectable({ scope: Scope.REQUEST })
export class MyFeatureQueueService extends BaseQueue {
    public jobs = [QueueJobEnum.MY_FEATURE_PROCESS];

    public constructor(
        @InjectQueue(QueueEnum.MY_FEATURE_QUEUE) public queue: Queue,
        public session: SessionService,
        public logService: LogService
    ) {
        super(queue, logService);
    }
}
```

**QueueService rules:**
- Always `scope: Scope.REQUEST` — inherits session context from the request
- `public jobs` lists all `QueueJobEnum` entries this queue accepts
- `@InjectQueue` uses the correct `QueueEnum`

**Available enqueueing methods (inherited from `BaseQueue`):**

| Method | Usage |
|--------|-------|
| `execute(data, skipLogs?, priority?, jobId?)` | Enqueue immediately |
| `executeWithDelay(data, delayMs)` | Enqueue with delay |
| `executeWithDebounce(data, delaySeconds, debounceKey)` | Debounce by Redis key |
| `scheduleExecution(data, date)` | Schedule for a specific date |
| `batchExecute(data[])` | Enqueue multiple at once |

---

## 3. Create the Processor

### Simple case: extend QueueProcessorBase

Use when the job doesn't need an exclusive lock per company/integration:

```typescript
// src/access/queues/processors/my-feature.queue.processor.ts
import { Processor } from '@nestjs/bullmq';
import { Job } from 'bullmq';
import { QueueBaseData, QueueEnum } from '../base.queue';
import { QueueProcessorBase } from './queue.processor.base';
import { SessionService } from 'src/services/session/session.service';
import { LogService } from 'src/services/log/log.service';
import { MyEntityDomain } from 'src/domain/my-entity.domain';

interface JobData {
    entityId: string;
    // job-specific data
}

@Processor(QueueEnum.MY_FEATURE_QUEUE, {
    concurrency: 5,                      // simultaneous jobs
    lockDuration: 30 * 60 * 1000        // 30-minute lock (prevents duplicate reprocessing)
})
export class MyFeatureQueueProcessor extends QueueProcessorBase {
    public constructor(
        public session: SessionService,
        public logService: LogService,
        private readonly myEntityDomain: MyEntityDomain
    ) {
        super(session, logService);
    }

    public async process(job: Job<QueueBaseData<JobData>>): Promise<boolean> {
        // REQUIRED: always the first line
        await this.setSession(job);

        const { entityId } = job.data.data;
        const entity = await this.myEntityDomain.findById(entityId);
        if (!entity) return false;

        // processing logic
        await this.myEntityDomain.updateOne({ ...entity, processed: true });

        return true;
    }
}
```

**`await this.setSession(job)` is required** — propagates company, user, features and token to
the session context. Without it, domains won't have `companyId` and all queries will fail.

### Redis lock case: extend ProviderQueueProcessorBase

Use when processing needs to be exclusive per company/integration (e.g., ERP sync):

```typescript
@Processor(QueueEnum.MY_SYNC_QUEUE, { concurrency: 5 })
export class MySyncQueueProcessor extends ProviderQueueProcessorBase {
    protected readonly REDIS_KEY = 'my-sync-lock';
    protected readonly EXPIRATION_MINUTES = 10;

    public constructor(
        public session: SessionService,
        public logService: LogService,
        protected readonly zoppyRedisService: ZoppyRedisService,
        protected readonly dataSyncManagementDomain: DataSyncManagementDomain,
        private readonly myStrategy: MySyncRequestStrategy
    ) {
        super(session, logService, zoppyRedisService, dataSyncManagementDomain);
    }

    public async process(job: Job<QueueBaseData<JobData>>): Promise<boolean> {
        await this.setSession(job);
        const request = job.data.data.dataSyncManagement;

        return await this.executeWithLock(job, request, async () => {
            // exclusive logic — only one execution per company at a time
            await this.processSyncLogic(request);
            return true;
        });
    }
}
```

---

## 4. Job data structure

Always use `QueueBaseData<T>` when enqueueing:

```typescript
// When enqueueing (in QueueService or Domain)
await this.myFeatureQueueService.execute({
    session: this.session.getSessionData(),  // complete session context
    job: QueueJobEnum.MY_FEATURE_PROCESS,   // job type
    queue: QueueEnum.MY_FEATURE_QUEUE,      // queue name
    data: { entityId: entity.id }           // job data
});

// In the processor, accessing the data:
const { entityId } = job.data.data;         // job.data is QueueBaseData<JobData>
const session = job.data.session;           // session available before setSession
```

---

## 5. Logging in the processor

Use `logService` for structured logs — logs appear in NewRelic/Datadog:

```typescript
public async process(job: Job<QueueBaseData<JobData>>): Promise<boolean> {
    await this.setSession(job);

    await this.logService.info({
        message: `[MyFeatureProcessor] Starting job processing ${job.id}`,
        identifier: 'MY_FEATURE_PROCESS'
    });

    try {
        // logic...
        return true;
    } catch (error) {
        await this.logService.error({
            message: {
                error,
                description: `[MyFeatureProcessor] Error in job ${job.id}`,
                jobData: JSON.stringify(job.data.data)
            },
            confirm: true
        });
        throw error;  // re-throw so BullMQ registers as failure and retries
    }
}
```

---

## 6. QueueJobOptions — retry presets

Use available presets in `QueueJobOptions`:

```typescript
import { QueueJobOptions } from 'src/access/queues/base.queue';

// Enqueue with specific preset
await this.myQueueService.execute(data, false, null, jobId, QueueJobOptions.DEFAULT);
// DEFAULT: 10 attempts, exponential backoff of 2s
```

Available presets: `DEFAULT`, `DEFAULT_FOUR_ATTEMPTS`, `CAMPAIGN`, `WHATSAPP_WEBHOOK`, etc.

---

## 7. Register the Processor in the correct Pipeline Module

The project runs as multiple isolated worker services. Each processor must be registered in **exactly one** pipeline module — adding it to multiple modules causes duplicate job consumption.

### Choose the right module based on domain:

| Module file | `WORKER_CONTEXT` | Purpose |
|---|---|---|
| `src/access/queues/integrations-pipeline.modules.ts` | `INTEGRATION_PIPELINE` | ERP/e-commerce sync, order sync, abandoned cart, provider integrations |
| `src/access/queues/message-pipeline.module.ts` | `MESSAGE_PIPELINE` | Message sending (WhatsApp, SMS, email), campaigns, webhooks |
| `src/access/queues/workflow-pipeline.module.ts` | `WORKFLOW_PIPELINE` | Workflow execution steps, automation triggers |
| `src/access/queues/queue.module.ts` | fallback `WORKER` | General/cross-cutting processors (RFM, segments, company setup, etc.) |

**Rule: register in ONE module only.** Simply adding the processor to a module's `providers[]` is enough — the worker for that context starts consuming immediately on deploy.

```typescript
// Example: src/access/queues/message-pipeline.module.ts
import { MyFeatureQueueProcessor } from './processors/my-feature.queue.processor';

const processors: Type<any>[] = [
    // ...existing processors...
    MyFeatureQueueProcessor,
];
```

**`src/access/queues/queue-service.module.ts`** — registers the QueueService (producer side, used by all contexts):
```typescript
import { MyFeatureQueueService } from './services/my-feature.queue.service';

// providers[] and exports[]
providers: [MyFeatureQueueService, ...others]
exports: [MyFeatureQueueService, ...others]
```

**`src/access/queues/zoppy-bull.module.ts`** — registers the queue in BullMQ:
```typescript
BullModule.registerQueue(
    // ...existing queues...
    { name: QueueEnum.MY_FEATURE_QUEUE }
)
```

---

## Pre-finalization checklist

- [ ] `QueueEnum.MY_FEATURE_QUEUE` and `QueueJobEnum.MY_FEATURE_PROCESS` added in `queue.constants.ts`
- [ ] QueueService with `scope: Scope.REQUEST`, `public jobs = [QueueJobEnum.MY_FEATURE_PROCESS]`
- [ ] Processor with `@Processor(QueueEnum.MY_FEATURE_QUEUE, { concurrency, lockDuration })`
- [ ] `await this.setSession(job)` as the first line of `process()`
- [ ] `super(session, logService)` called in the constructor
- [ ] `throw error` in catch so BullMQ registers and retries
- [ ] Queue registered in `ZoppyBullModule`
- [ ] Processor registered in **exactly one** pipeline module (`integrations-pipeline`, `message-pipeline`, `workflow-pipeline`, or `queue.module.ts`) — never duplicated
- [ ] QueueService in `QueueServiceModule`
- [ ] Tests written (see skill-tdd)
