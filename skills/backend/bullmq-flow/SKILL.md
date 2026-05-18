---
name: bullmq-flow
description: How to create a BullMQ Flow (FlowProducer) in the zoppy-api project. Use this skill whenever the user wants to create a flow with parent/child job dependencies, chain multiple queue jobs that must execute in sequence or conditionally, or asks about FlowProducer, FlowJob, BaseFlow, QueueFlowModule, or job orchestration with dependencies. Trigger on phrases like "criar flow", "flow de filas", "jobs dependentes", "parent job", "child job", or when a processor needs to wait for another processor's output.
---

# BullMQ Flow (FlowProducer)

Flows are for **job dependency chains** — when job B must only run after job A succeeds, or when you have a "parent" that fans out into "children" and then aggregates their results. If you just want to queue a single independent job, use a regular `QueueService` instead.

## When to use a Flow vs a Queue

| Use Flow                                     | Use Queue                    |
| -------------------------------------------- | ---------------------------- |
| Job B depends on Job A's output              | Jobs are independent         |
| Fan-out + fan-in (parent waits for children) | Fire-and-forget processing   |
| Need `getChildrenValues()` to aggregate      | No result aggregation needed |

## Adding a new FlowNameEnum entry

```typescript
// src/access/queues/flows/base.flow.ts
export enum FlowNameEnum {
    CUSTOMER_SELLER_CHAMPION = 'customer-seller-champion',
    UPLOAD_DATA = 'upload-data',
    OPENSEARCH_MIGRATION = 'opensearch-migration',
    YOUR_NEW_FLOW = 'your-new-flow' // add here
}
```

## Creating the Flow Service

The flow service is a `Scope.REQUEST` service that builds and executes the `FlowJob` tree.

```typescript
import { Injectable, Scope } from '@nestjs/common';
import { InjectFlowProducer } from '@nestjs/bullmq';
import { FlowJob, FlowProducer } from 'bullmq';
import { BaseFlow } from '../base.flow';
import { FlowNameEnum, QueueBaseData } from 'src/access/queues/base.queue';
import { LogService } from 'src/services/log/log.service';
import { SessionService } from 'src/services/session/session.service';
import { QueueEnum, QueueJobEnum } from 'src/access/queues/base.queue';

@Injectable({ scope: Scope.REQUEST })
export class YourFlowService extends BaseFlow {
    public constructor(
        @InjectFlowProducer(FlowNameEnum.YOUR_NEW_FLOW)
        protected readonly flowProducer: FlowProducer,
        public readonly session: SessionService,
        public readonly logService: LogService
    ) {
        super(flowProducer, logService);
    }

    public async execute(data: YourFlowInput): Promise<void> {
        const sessionData = this.session.getSessionData();

        const flow: FlowJob = {
            name: QueueJobEnum.PARENT_JOB,
            queueName: QueueEnum.PARENT_QUEUE,
            data: {
                session: sessionData,
                job: QueueJobEnum.PARENT_JOB,
                queue: QueueEnum.PARENT_QUEUE,
                data: { ...data }
            } as QueueBaseData<YourFlowInput>,
            opts: { failParentOnFailure: true },
            children: [
                {
                    name: QueueJobEnum.CHILD_JOB_A,
                    queueName: QueueEnum.CHILD_QUEUE_A,
                    data: {
                        session: sessionData,
                        job: QueueJobEnum.CHILD_JOB_A,
                        queue: QueueEnum.CHILD_QUEUE_A,
                        data: { ...data }
                    } as QueueBaseData<YourFlowInput>,
                    opts: { failParentOnFailure: true }
                }
            ]
        };

        await this.executeFlow(flow);
    }
}
```

### Key points:

-   Always `scope: Scope.REQUEST` — each request gets its own session context
-   `@InjectFlowProducer(FlowNameEnum.X)` — must match the enum entry
-   Pass `session: this.session.getSessionData()` in every job's `data` — children need session too
-   `failParentOnFailure: true` — parent waits; if a child fails, parent also fails (typical behavior)
-   Set `failParentOnFailure: false` when the parent should proceed even if some children fail

## Accessing child results in the parent processor

In the parent processor's `process()` method, after `await this.setSession(job)`:

```typescript
// Get all children's return values as a flat object keyed by queue name
const childrenValues = await job.getChildrenValues();

// Or use the helper from BaseFlow to navigate a nested tree
const childValue = BaseFlow.getChildValueFromTree(job, QueueEnum.CHILD_QUEUE_A);
```

Children only become available to the parent once all children have completed — BullMQ handles the dependency resolution automatically.

## Registering in QueueFlowModule

```typescript
// src/access/queues/queue-flow.module.ts
const flows: any[] = [
    CustomerSellerChampionFlowService,
    UploadDataFlowService,
    OpenSearchMigrationFlowService,
    YourFlowService // add here
];

@Module({
    imports: [LogModule, ZoppyBullModule, DomainModule],
    providers: [...flows],
    exports: [...flows]
})
export class QueueFlowModule {}
```

## ZoppyBullModule — registering the FlowProducer

The flow producer itself is registered in `ZoppyBullModule`. Check `src/access/queues/zoppy-bull.module.ts` and add:

```typescript
BullMQFlowProducerModule.registerFlowProducer({
    name: FlowNameEnum.YOUR_NEW_FLOW,
    connection: redisConnection
});
```

## Complete flow setup checklist

-   [ ] Add `YOUR_NEW_FLOW` to `FlowNameEnum`
-   [ ] Create `your-flow.service.ts` extending `BaseFlow` with `scope: Scope.REQUEST`
-   [ ] Create parent and child processors (see `skill-queue-processor`)
-   [ ] Register flow producer in `ZoppyBullModule`
-   [ ] Add flow service to `QueueFlowModule`
-   [ ] Add flow service to `exports[]` in `QueueFlowModule`
-   [ ] Inject `QueueFlowModule` wherever the flow service is used
