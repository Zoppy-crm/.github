---
name: domain-validation
description: How to create domain validations in the zoppy-api project using DomainValidation<T>. Use this skill whenever the user wants to add business rule validation before saving an entity, check for required fields, validate formats, enforce uniqueness constraints, or integrate custom validation into an Application Service. Trigger on phrases like "validação de domínio", "validar antes de salvar", "DomainValidation", "UnprocessableEntityException", or when validation logic needs access to the database (async validation).
---

# Domain Validation

Domain validations encapsulate business rules that should be checked before persisting an entity. They're especially useful when validation requires async database lookups (e.g., checking uniqueness).

## Base class

```typescript
// src/domain/validation/interfaces/domain-validation.ts
export abstract class DomainValidation<T extends Model> {
    protected validationErrors: string[] = [];
    protected domain: RepositoryAdapter<T>; // injected by the framework

    public async execute(request: T): Promise<void> {
        this.validationErrors = [];
        await this.onValidation(request);
        if (this.validationErrors.length > 0) {
            throw new UnprocessableEntityException(this.validationErrors);
        }
    }

    public abstract onValidation(request: T): Promise<void>;
}
```

## Creating a validation class

```typescript
import { Injectable, Scope } from '@nestjs/common';
import { DomainValidation } from '../domain-validation';
import { YourEntity } from '@Zoppy-crm/models';

@Injectable({ scope: Scope.REQUEST })
export class YourEntityCreateValidation extends DomainValidation<YourEntity> {
    public async onValidation(request: YourEntity): Promise<void> {
        // Synchronous checks — add to validationErrors[] instead of throwing
        this.validateRequiredFields(request);
        this.validateFormats(request);

        // Async checks — can also throw directly for uniqueness violations
        await this.validateUniqueness(request);
    }

    private validateRequiredFields(request: YourEntity): void {
        if (!request.name || !request.email) {
            this.validationErrors.push('Nome e email são obrigatórios');
        }
    }

    private validateFormats(request: YourEntity): void {
        if (request.email && !request.email.includes('@')) {
            this.validationErrors.push('Formato de email inválido');
        }
    }

    private async validateUniqueness(request: YourEntity): Promise<void> {
        const existing = await this.domain.findOne({
            where: { email: request.email }
        });
        if (existing && existing.id !== request.id) {
            throw new NotFoundException('Já existe um registro com este email');
        }
    }
}
```

### Key points

-   Always `@Injectable({ scope: Scope.REQUEST })` — needed for database access via session
-   `this.domain` gives access to the associated `RepositoryAdapter<T>` — use it for async checks
-   Accumulate multiple errors in `this.validationErrors[]` when possible (better UX than throwing on first failure)
-   For hard stops (uniqueness violation), throwing directly is acceptable
-   `execute()` throws `UnprocessableEntityException` with all collected errors at the end

## File naming convention

```
src/domain/validation/
├── your-entity/
│   ├── your-entity-create.validation.ts
│   └── your-entity-update.validation.ts  (if different rules for update)
```

## Integrating validation in Application Service

```typescript
// In your Application Service
@Injectable()
export class YourEntityApplication {
    constructor(
        public readonly session: SessionService,
        public readonly logService: LogService,
        private readonly yourEntityDomain: YourEntityDomain,
        private readonly yourEntityCreateValidation: YourEntityCreateValidation
    ) {}

    public async create(request: YourEntityCreateRequest): Promise<YourEntityResponse> {
        // Run validation before persisting
        await this.yourEntityCreateValidation.execute(request as YourEntity);

        const entity = await this.yourEntityDomain.saveOne(request);

        return { id: entity.id, name: entity.name };
    }
}
```

## Registering the validation

Validations are `Scope.REQUEST` providers — register in the appropriate module (usually the domain module or the application module where they're used):

```typescript
// In ApplicationModule or a feature module
providers: [
    YourEntityApplication,
    YourEntityCreateValidation
    // ...
];
```

## When to use DomainValidation vs inline checks

| Use `DomainValidation`                            | Use inline check in Application Service       |
| ------------------------------------------------- | --------------------------------------------- |
| Multiple rules that should be collected           | Single guard condition                        |
| Async uniqueness checks                           | Simple `if (!entity) throw NotFoundException` |
| Rules reused across multiple application services | One-off validation for a specific use case    |
| Complex format/business rule validation           | Existence check after `findById()`            |
