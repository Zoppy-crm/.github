---
name: queue-scheduler
description: How to create a recurring job scheduler (cron/interval) in the zoppy-api project using BaseCommand. Use this skill whenever the user wants to schedule a job to run periodically (every hour, daily cron, etc.), create a repeatable BullMQ job, or asks about BaseCommand, CommandKeyEnum, RepeatOptions, job schedulers, or "scheduled job". Trigger on phrases like "agendar job", "job recorrente", "cron", "executar periodicamente", "BaseCommand", or when a queue processor needs to be triggered automatically on a schedule rather than on demand.
---

# Queue Scheduler (BaseCommand)

A `BaseCommand` registers a BullMQ repeatable job via `upsertJobScheduler()` on module initialization. Each command corresponds to one scheduled job that runs on a configured interval or cron schedule.

## Creating a scheduler

```typescript
import { Injectable } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';
import { BaseCommand, CommandKeyEnum } from '../base.command';
import { QueueEnum, QueueJobEnum } from '../base.queue';
import { RepeatOptions } from 'bullmq';

@Injectable()
export class YourSchedulerCommand extends BaseCommand<YourJobData> {
    // Unique identifier for the scheduler — must be in CommandKeyEnum
    public readonly key: CommandKeyEnum = CommandKeyEnum.YOUR_SCHEDULER;

    // How often to run (cron or interval)
    public readonly repeatOptions: RepeatOptions = {
        every: 60 * 60 * 1000 // every 1 hour in ms
        // OR use cron:
        // pattern: '0 9 * * 1-5'  // 9am Mon–Fri
    };

    // The job template enqueued on each tick
    public readonly templateOptions = {
        name: QueueJobEnum.YOUR_JOB,
        data: {
            session: null, // session is null for scheduled jobs (no user context)
            job: QueueJobEnum.YOUR_JOB,
            queue: QueueEnum.YOUR_QUEUE,
            data: {}
        }
    };

    public constructor(
        @InjectQueue(QueueEnum.YOUR_QUEUE)
        protected readonly queue: Queue
    ) {
        super(queue);
    }
}
```

### What happens on startup

`BaseCommand` implements `OnModuleInit`. When the module initializes:

1. If `IS_LOCAL=1` env var is set, the scheduler is **skipped** — local dev doesn't run background jobs
2. Otherwise, `execute()` calls `queue.upsertJobScheduler(key, repeatOptions, templateOptions)`
3. BullMQ deduplicates by `key` — running again won't create duplicates

## Adding to CommandKeyEnum

```typescript
// src/access/queues/base.command.ts
export enum CommandKeyEnum {
    CAMPAIGN_METRICS = 'campaign-metrics',
    OPENSEARCH = 'opensearch',
    TINY_DAILY_ORDER_SYNC = 'tiny-daily-order-sync',
    YOUR_SCHEDULER = 'your-scheduler' // add here
}
```

## RepeatOptions examples

```typescript
// Every 30 minutes
repeatOptions = { every: 30 * 60 * 1000 };

// Daily at midnight UTC
repeatOptions = { pattern: '0 0 * * *' };

// Every weekday at 9am Brazil time (BRT = UTC-3)
repeatOptions = { pattern: '0 12 * * 1-5' }; // 12 UTC = 9 BRT

// Every 5 minutes
repeatOptions = { every: 5 * 60 * 1000 };
```

## Registering in CommandModule

```typescript
// src/access/queues/command.module.ts
const commands: any[] = [
    CampaignMetricsCommand,
    OpensearchCommand,
    YourSchedulerCommand  // add here
];

@Module({
    imports: [ZoppyBullModule, ...],
    providers: [...commands],
})
export class CommandModule {}
```

## Handling session in the processor

Scheduled jobs have no user session — they're initiated by the scheduler, not by a request. In the processor, use `loginMaster()` instead of `setSession()` (which requires a session in the job data):

```typescript
@Processor(QueueEnum.YOUR_QUEUE, { concurrency: 1 })
export class YourScheduledProcessor extends QueueProcessorBase {
    public async process(job: Job<QueueBaseData<YourJobData>>): Promise<void> {
        // For scheduled jobs with no user session, login as master
        await this.loginMaster(job); // NOT await this.setSession(job)

        // Your processing logic here
    }
}
```

Check existing processors like `CampaignMetricsQueueProcessor` to confirm the pattern for your use case.

## Complete checklist

-   [ ] Add `YOUR_SCHEDULER` to `CommandKeyEnum`
-   [ ] Create `your-scheduler.command.ts` extending `BaseCommand<T>`
-   [ ] Set `key`, `repeatOptions`, and `templateOptions`
-   [ ] Inject `@InjectQueue(QueueEnum.YOUR_QUEUE)` in constructor
-   [ ] Register in `CommandModule` providers array
-   [ ] Create/update the processor to handle `null` session (use `loginMaster`)
-   [ ] Verify `IS_LOCAL=1` is set in local `.env` to avoid running schedulers locally
