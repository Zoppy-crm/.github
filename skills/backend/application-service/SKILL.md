---
name: application-service
description: >
  Guide for creating and modifying Application Services in the zoppy-api project. Use this skill
  whenever you need to create a new application service, add a use case to an existing service,
  orchestrate business flows (validate → persist → enqueue), or register a service in the
  ApplicationModule. Trigger this skill when the user mentions: "create application", "new
  application service", "application module", "use case", "orchestrate domains", "call
  queue from a service", or when implementing business logic that coordinates multiple domains.
---

# Creating an Application Service in zoppy-api

## Application Layer Responsibility

Application Services (`src/application/`) orchestrate complete use cases. They:
1. Receive a Request DTO from the controller
2. Execute business validations
3. Call domains for persistence
4. Enqueue jobs via QueueServices when necessary
5. Return a Response DTO

They do not directly access the database (that is the Domain's responsibility). They do not expose infrastructure details to the controller.

---

## Minimal structure

```typescript
// src/application/my-feature/my-feature.application.ts
import { Injectable } from '@nestjs/common';
import { MyEntity } from '@Zoppy-crm/models';
import { MyEntityDomain } from 'src/domain/my-entity.domain';
import { SessionService } from 'src/services/session/session.service';
import { LogService } from 'src/services/log/log.service';
import { MyFeatureRequest } from 'src/access/http/requests/my-feature/my-feature.request';
import { MyFeatureResponse } from 'src/access/http/response/my-feature/my-feature.response';

@Injectable()
export class MyFeatureApplication {
    public constructor(
        private readonly myEntityDomain: MyEntityDomain,
        public readonly session: SessionService,
        public readonly logService: LogService
    ) {}

    public async create(request: MyFeatureRequest): Promise<MyFeatureResponse> {
        const entity: MyEntity = await this.myEntityDomain.saveOne({
            name: request.name,
            companyId: this.session.getCompany().id
        });
        return { id: entity.id, name: entity.name };
    }
}
```

**Conventions:**
- Always `@Injectable()` without explicit scope (uses `Scope.DEFAULT` — singleton per module)
- `session` and `logService` are almost always injected
- `companyId` comes from `this.session.getCompany().id` — never from the HTTP request

---

## Orchestration pattern: validate → persist → enqueue

Typical flow for a write use case:

```typescript
@Injectable()
export class CampaignApplication {
    public constructor(
        private readonly campaignDomain: CampaignDomain,
        private readonly campaignQueueService: CampaignQueueService,
        private readonly featureDomain: FeatureDomain,
        public readonly session: SessionService,
        public readonly logService: LogService
    ) {}

    public async create(request: CampaignRequest): Promise<CampaignResponse> {
        // 1. Validate business rules
        const hasFeature: boolean = await this.featureDomain.hasFeature(Features.Campaigns);
        if (!hasFeature) throw new ForbiddenException('Feature not enabled');

        // 2. Persist via Domain
        const campaign: Campaign = await this.campaignDomain.saveOne({
            name: request.name,
            type: request.type,
            companyId: this.session.getCompany().id
        });

        // 3. Enqueue async job
        await this.campaignQueueService.execute({
            session: this.session.getSessionData(),
            job: QueueJobEnum.CAMPAIGN_PROCESS,
            queue: QueueEnum.CAMPAIGN_QUEUE,
            data: { campaignId: campaign.id }
        });

        // 4. Return Response DTO
        return { id: campaign.id, name: campaign.name };
    }
}
```

---

## Dependency injection

Inject in the constructor all resources the service needs:

```typescript
@Injectable()
export class MyApplication {
    public constructor(
        // Domains — for data access
        private readonly myEntityDomain: MyEntityDomain,
        private readonly otherEntityDomain: OtherEntityDomain,

        // Queue services — for enqueueing jobs
        private readonly myQueueService: MyQueueService,

        // Cross-cutting services
        public readonly session: SessionService,   // always public
        public readonly logService: LogService,    // always public

        // Direct repository — only when needed for raw queries
        @Inject(ProviderNames.MyEntityRepository) private readonly repository: Repository<MyEntity>
    ) {}
}
```

**When to use `@Inject(ProviderNames.XRepository)` directly:**
- Only for very specific SQL queries that the Domain doesn't support
- Always prefer adding the method to the Domain instead of accessing the repository directly in the Application

---

## Request and Response DTOs

Create DTOs in the correct folders:

```
src/access/http/
├── requests/
│   └── my-feature/
│       └── my-feature.request.ts      ← controller input
└── response/
    └── my-feature/
        └── my-feature.response.ts     ← controller output
```

**Request DTO** (with validation and Swagger):
```typescript
// src/access/http/requests/my-feature/my-feature.request.ts
import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsOptional, IsUUID } from 'class-validator';

export class MyFeatureRequest {
    @ApiProperty()
    @IsString()
    public name: string;

    @ApiProperty({ required: false })
    @IsOptional()
    @IsUUID()
    public parentId?: string;
}
```

**Response DTO** (simple, no decorators):
```typescript
// src/access/http/response/my-feature/my-feature.response.ts
export class MyFeatureResponse {
    public declare id: string;
    public declare name: string;
    public declare createdAt: Date;
}
```

---

## Error handling

Use standard NestJS exceptions. The Application is the right place to throw business errors:

```typescript
import {
    BadRequestException,
    NotFoundException,
    ForbiddenException,
    UnprocessableEntityException
} from '@nestjs/common';
import { ZoppyBadRequestException } from 'src/cross-cutting/exceptions/zoppy-general.exceptions';

// Examples
if (!entity) throw new NotFoundException('Entity not found');
if (alreadyExists) throw new BadRequestException('A record with this name already exists');
if (!authorized) throw new ForbiddenException('No permission for this operation');
```

---

## Register in ApplicationModule

Add in `src/application/application.module.ts` in 3 places:

**1. Import at the top:**
```typescript
import { MyFeatureApplication } from './my-feature/my-feature.application';
```

**2. In the `providers` array:**
```typescript
providers: [
    // ...alphabetical order...
    MyFeatureApplication,
    // ...
]
```

**3. In the `exports` array:**
```typescript
exports: [
    // ...alphabetical order...
    MyFeatureApplication,
    // ...
]
```

---

## Batch / chunk operations

For processing large volumes, use the chunks pattern:

```typescript
import { ArrayUtil } from '@Zoppy-crm/utilities';

const CHUNK_SIZE = 1000;
const chunks = ArrayUtil.splitArrayIntoChunks(items, CHUNK_SIZE);

for (const chunk of chunks) {
    await this.myEntityDomain.saveMany(chunk);
}
```

---

## Pre-finalization checklist

- [ ] `@Injectable()` on the class
- [ ] `session` and `logService` injected as `public`
- [ ] `companyId` obtained from `this.session.getCompany().id`, not from the request
- [ ] Business validations before persistence
- [ ] Standard NestJS exceptions for business errors
- [ ] Response DTO returned (not the Sequelize entity directly)
- [ ] Registered in `providers` and `exports` of `ApplicationModule`
- [ ] Tests written (see skill-tdd for application test patterns)
