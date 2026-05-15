---
name: controller
description: >
  Guide for creating and modifying HTTP Controllers in the zoppy-api project. Use this skill
  whenever you need to create a new controller, add endpoints to an existing controller, configure
  authentication and authorization guards, use standard decorators (@UsingTransaction,
  @ExceptionInterceptor, @RateLimit), create Request/Response DTOs, or register the controller in
  HttpModule. Trigger this skill when the user mentions: "create controller", "new endpoint",
  "HTTP route", "guards", "RoleGuard", "BlockFreeTierGuard", "FeatureGuard", "NestJS controller",
  "register in http module", or when exposing a use case via REST API.
---

# Creating an HTTP Controller in zoppy-api

## Controller Role

Controllers in `src/access/http/controllers/` are thin facades — thin layers that only:
1. Receive the HTTP request
2. Apply guards and decorators
3. Delegate to the Application Service
4. Return the response

They contain no business logic. All business rules live in the Application.

---

## Minimal structure

```typescript
// src/access/http/controllers/my-feature/my-feature.controller.ts
import { AppConstants } from '@Zoppy-crm/utilities';
import { Body, Controller, Delete, Get, HttpCode, HttpStatus, Param, Post, Put, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { MyFeatureApplication } from 'src/application/my-feature/my-feature.application';
import { ExceptionInterceptor } from 'src/cross-cutting/decorators/exception-interceptor.decorator';
import { UsingTransaction } from 'src/cross-cutting/decorators/using-transaction.decorator';
import { BlockFreeTierGuard } from 'src/cross-cutting/guards/block-free-tier-auth.guard';
import { RoleGuard } from 'src/cross-cutting/guards/role-auth.guard';
import { MyFeatureRequest } from '../requests/my-feature/my-feature.request';
import { MyFeatureResponse } from '../response/my-feature/my-feature.response';

@ApiTags('My Feature')
@Controller('my-feature')
export class MyFeatureController {
    public constructor(private readonly application: MyFeatureApplication) {}

    @Post()
    @ApiOperation({ summary: 'Create my feature' })
    @HttpCode(HttpStatus.OK)
    @ApiBearerAuth('access-token')
    @UseGuards(BlockFreeTierGuard())
    @UseGuards(RoleGuard([AppConstants.ROLES.MASTER, AppConstants.ROLES.ADMIN]))
    @UsingTransaction()
    @ExceptionInterceptor()
    public async create(@Body() request: MyFeatureRequest): Promise<MyFeatureResponse> {
        return await this.application.create(request);
    }

    @Get(':id')
    @ApiOperation({ summary: 'Find my feature by id' })
    @HttpCode(HttpStatus.OK)
    @ApiBearerAuth('access-token')
    @UseGuards(BlockFreeTierGuard())
    @UseGuards(RoleGuard([AppConstants.ROLES.MASTER, AppConstants.ROLES.ADMIN]))
    @ExceptionInterceptor()
    public async findById(@Param('id') id: string): Promise<MyFeatureResponse> {
        return await this.application.findById(id);
    }
}
```

---

## Guards — when and how to use

Guards are **factory functions** that return Mixin classes. The order of `@UseGuards` matters:
guards are evaluated bottom-up (the last `@UseGuards` is evaluated first).

**Guards required on most endpoints:**

```typescript
@UseGuards(BlockFreeTierGuard())   // Blocks free-tier companies
@UseGuards(RoleGuard([AppConstants.ROLES.MASTER, AppConstants.ROLES.ADMIN]))  // Checks user role
```

**Available roles in `AppConstants.ROLES`:**
- `MASTER` — full access
- `ADMIN` — company administrator
- `USER` — regular user

**FeatureGuard** — for endpoints that require a feature flag:
```typescript
import { FeatureGuard } from 'src/cross-cutting/guards/feature.guard';
import { Features } from '@Zoppy-crm/utilities';

@UseGuards(FeatureGuard(Features.MyFeature))
@UseGuards(BlockFreeTierGuard())
@UseGuards(RoleGuard([AppConstants.ROLES.MASTER]))
```

**Public endpoints** (no JWT authentication):
```typescript
import { IsPublic } from 'src/cross-cutting/decorators/is-public.decorator';

@IsPublic()
@Post('webhook')
public async receiveWebhook(@Body() request: WebhookRequest): Promise<void> { ... }
```

---

## Standard decorators

**`@UsingTransaction()`** — use on any endpoint that writes (POST, PUT, DELETE).
Enables automatic rollback if the request fails:
```typescript
@Post()
@UsingTransaction()
@ExceptionInterceptor()
public async create(@Body() request: CreateRequest): Promise<Response> { ... }
```

**`@ExceptionInterceptor()`** — enables HTTP exception logging. Use on all endpoints:
```typescript
@ExceptionInterceptor()
public async myMethod(): Promise<void> { ... }
```

**`@RateLimit()`** — for endpoints sensitive to abuse:
```typescript
import { RateLimit } from 'src/cross-cutting/decorators/rate-limit.decorator';

@RateLimit({ limit: 10, window: 60 })  // 10 req per 60 seconds
@Post('send-message')
public async sendMessage(): Promise<void> { ... }
```

---

## Route and query parameters

```typescript
import { Body, Param, Query } from '@nestjs/common';

// Path parameter
@Get(':id')
public async findById(@Param('id') id: string): Promise<Response> { ... }

// Query string (using the project's filter pattern)
@Get()
public async list(@Query() filter: ZoppyFilter<Entity[]>): Promise<ZoppyFilter<Entity[]>> { ... }

// Request body
@Post()
public async create(@Body() request: CreateRequest): Promise<Response> { ... }
```

---

## Request DTOs

```typescript
// src/access/http/requests/my-feature/my-feature.request.ts
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsString, IsOptional, IsUUID, IsEnum, IsArray, IsBoolean } from 'class-validator';
import { Type } from 'class-transformer';

export class MyFeatureRequest {
    @ApiProperty({ description: 'Feature name' })
    @IsString()
    public name: string;

    @ApiPropertyOptional()
    @IsOptional()
    @IsUUID()
    public parentId?: string;

    @ApiProperty({ enum: MyEnum })
    @IsEnum(MyEnum)
    public type: MyEnum;

    @ApiPropertyOptional({ type: [String] })
    @IsOptional()
    @IsArray()
    public tags?: string[];
}
```

**Response DTOs** — simple, only with `declare`:
```typescript
// src/access/http/response/my-feature/my-feature.response.ts
export class MyFeatureResponse {
    public declare id: string;
    public declare name: string;
    public declare type: string;
    public declare createdAt: Date;
}
```

---

## File upload (multipart)

```typescript
import { FileInterceptor } from '@nestjs/platform-express';
import { UploadedFile, UseInterceptors } from '@nestjs/common';

@Post('upload')
@UseInterceptors(FileInterceptor('file'))
@UseGuards(BlockFreeTierGuard())
@UseGuards(RoleGuard([AppConstants.ROLES.MASTER]))
@ExceptionInterceptor()
public async upload(@UploadedFile() file: Express.Multer.File): Promise<void> {
    await this.application.upload(file);
}
```

---

## Register in HttpModule

Two registrations in `src/access/http/http.module.ts`. Both required.

### 1. The `controllers` array

```typescript
import { MyFeatureController } from './controllers/my-feature/my-feature.controller';

@Module({
    imports: [...],
    controllers: [
        // ...alphabetical order...
        MyFeatureController,
        // ...
    ]
})
export class HttpModule {}
```

### 2. AuthMiddleware in `configure(consumer)`

**Apply `AuthMiddleware` for standard authenticated controllers. Always.**

```typescript
export class HttpModule implements NestModule {
    public configure(consumer: MiddlewareConsumer): void {
        // ...existing lines...
        consumer.apply(HmacAuthMiddleware({ strict: false }), AuthMiddleware).forRoutes(MyFeatureController);
    }
}
```

---

## URL patterns

Follow the project's REST conventions:

| Operation | Method | URL |
|----------|--------|-----|
| Create | POST | `/my-feature` |
| List | GET | `/my-feature` |
| Find by ID | GET | `/my-feature/:id` |
| Update | PUT | `/my-feature/:id` |
| Delete | DELETE | `/my-feature/:id` |
| Specific action | POST | `/my-feature/:id/action-name` |

---

## Pre-finalization checklist

- [ ] `@ApiTags()` and `@Controller()` on the class
- [ ] `@ApiBearerAuth('access-token')` on authenticated endpoints
- [ ] `@UseGuards(BlockFreeTierGuard())` on customer endpoints
- [ ] `@UseGuards(RoleGuard([...]))` with correct roles
- [ ] `@UsingTransaction()` on write endpoints (POST/PUT/DELETE)
- [ ] `@ExceptionInterceptor()` on all endpoints
- [ ] `@HttpCode(HttpStatus.OK)` when not using status 201
- [ ] Business logic only in the Application, not in the controller
- [ ] Controller added to the `controllers: [...]` array in `HttpModule`
- [ ] **Standard authenticated controller wired with `AuthMiddleware` in `HttpModule.configure(consumer)`** — always
- [ ] Integration tests written (see skill-tdd)
