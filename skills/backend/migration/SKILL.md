---
name: migration
description: How to create Sequelize migrations and seeders in the zoppy-api project. Use this skill whenever the user wants to add a new database table, add/remove/modify columns, create foreign key constraints, or seed initial data. Trigger on phrases like "criar migration", "nova tabela", "adicionar coluna", "foreign key", "seeder", "rollback", or when a new domain entity needs a database table. Make sure to use this skill for any database schema changes, even if the user just says "criar tabela X" without mentioning migrations explicitly.
---

# Sequelize Migrations and Seeders

## Generating a migration file

```bash
npx sequelize-cli migration:generate --name create-your-entity
```

This creates `src/db/migrations/<timestamp>-create-your-entity.ts`.

## Migration structure

Migrations are plain CommonJS modules with `up` and `down` functions. Always implement `down` — it's needed for `npm run rollback`.

```typescript
'use strict';

module.exports = {
    async up(queryInterface, Sequelize) {
        await queryInterface.createTable('YourEntities', {
            id: {
                allowNull: false,
                primaryKey: true,
                defaultValue: Sequelize.UUIDV4,
                type: Sequelize.UUID
            },
            name: {
                allowNull: false,
                type: Sequelize.STRING
            },
            description: {
                allowNull: true,
                type: Sequelize.TEXT
            },
            // Always include soft delete + timestamps
            createdAt: {
                allowNull: false,
                type: Sequelize.DATE
            },
            updatedAt: {
                allowNull: false,
                type: Sequelize.DATE
            },
            deletedAt: {
                allowNull: true,
                type: Sequelize.DATE
            }
        });
    },

    async down(queryInterface) {
        await queryInterface.dropTable('YourEntities');
    }
};
```

### Conventions

- **PK**: UUID with `Sequelize.UUIDV4` as default — never integer auto-increment
- **Soft delete**: `deletedAt DATE NULL` — all tables use paranoid soft delete
- **Timestamps**: `createdAt` and `updatedAt` — always `allowNull: false`
- **Table names**: PascalCase plural (e.g., `Companies`, `MessageTemplates`)
- **Column names**: camelCase (e.g., `companyId`, `createdAt`)

### Foreign keys

```typescript
companyId: {
    allowNull: false,
    type: Sequelize.UUID,
    references: { model: 'Companies', key: 'id' }
    // Note: companyId usually doesn't have CASCADE — companies are soft-deleted
},
parentId: {
    allowNull: false,
    type: Sequelize.UUID,
    references: { model: 'ParentEntities', key: 'id' },
    onUpdate: 'CASCADE',
    onDelete: 'CASCADE'
}
```

Use `onDelete: 'CASCADE'` for "owned" relationships (e.g., message items belong to a message group — delete items when group is deleted). Skip cascade for `companyId` — companies are soft-deleted, not hard-deleted.

### Enum columns

```typescript
status: {
    allowNull: false,
    type: Sequelize.ENUM('active', 'inactive', 'pending')
}
```

### Adding/removing columns (ALTER TABLE)

```typescript
module.exports = {
    async up(queryInterface, Sequelize) {
        await queryInterface.addColumn('YourEntities', 'newColumn', {
            allowNull: true,
            type: Sequelize.STRING
        });
    },
    async down(queryInterface) {
        await queryInterface.removeColumn('YourEntities', 'newColumn');
    }
};
```

### Adding an index

```typescript
async up(queryInterface, Sequelize) {
    await queryInterface.addIndex('YourEntities', ['companyId', 'status'], {
        name: 'idx_yourentities_companyid_status'
    });
}
```

## Running migrations

```bash
# Inside the Docker container or with proper env vars
npm run migrate       # apply pending migrations
npm run rollback      # undo the last migration
```

## Seeders

Seeders insert initial/reference data. They live in `src/db/seeders/`.

```typescript
'use strict';

module.exports = {
    async up(queryInterface) {
        const uuid = require('uuid');
        return queryInterface.bulkInsert('YourEntities', [
            {
                id: uuid.v4(),
                name: 'Default Record',
                createdAt: new Date(),
                updatedAt: new Date()
            }
        ]);
    },

    async down(queryInterface) {
        // Usually leave empty — seeders are typically not reversible
    }
};
```

Run all seeders: `npm run seeder`

## Companion entity in `zoppy-model` (THREE files, not two)

Any table created here usually has a matching entity class in the sibling
`zoppy-model` package. **Touch all three files — the third one is the one
that's easy to forget and silently breaks runtime:**

1. `zoppy-model/src/api/<entity-kebab-name>.ts` — the entity class
   (`@Table`, `@PrimaryKey`, `@Column`, relations).
2. `zoppy-model/src/index.ts` — add `export * from './api/<entity-kebab-name>';`
   so consumers can import the symbol.
3. **`zoppy-model/src/api/database.provider.ts`** — add the import AND add
   the class to the `databaseModels: Repository<Model>[]` array. This is
   the array passed to `connection.addModels(...)` when bootstrapping the
   Sequelize connection. **If you skip this step the imports compile fine
   but every query against the new table fails at runtime** (sequelize
   reports the model is not initialized).

After editing, verify with:

```bash
grep "<EntityName>" zoppy-model/src/api/database.provider.ts
# Expect TWO matches: the import line and the array entry.
```

Then in `zoppy-api`:

4. `src/cross-cutting/providers/repository.providers.ts` — add the import
   from `@Zoppy-crm/models` and the
   `{ provide: ProviderNames.<EntityName>Repository, useValue: <Entity> }`
   line.
5. `zoppy-utilities/src/constants/provider-names.constants.ts` — add
   `<EntityName>Repository = '<SCREAMING_SNAKE>_REPOSITORY'` to the
   `ProviderNames` enum. Publish a `patch`.

## Cross-repo PR sequencing

The user prefers a **migration-first split** when both repos change:

1. PR #1 in `zoppy-api` — migration only. Merge and run in prod first.
2. PR in `zoppy-model` — entity + index export + `database.provider.ts`.
   Publish as **prerelease** (`npm run publish:pre`, `:next` tag).
3. After PR #1 has merged and migrated, promote `zoppy-model` to a stable
   patch (`npm run publish:patch`) and merge the model PR.
4. PR #2 in `zoppy-api` — bump `@Zoppy-crm/models` to the stable version
   and land the code that uses the new entity (domain, application, etc.).

## Complete checklist for a new table

- [ ] `npx sequelize-cli migration:generate --name create-your-entity`
- [ ] Add `id` (UUID PK), all columns, `createdAt`, `updatedAt`, `deletedAt`
- [ ] Add foreign key columns with `references` if needed
- [ ] Add indexes via `queryInterface.addIndex(...)` when querying by
      non-PK columns
- [ ] Implement `down` (dropTable)
- [ ] Run `npm run migrate` inside the container to verify
- [ ] `zoppy-model`: create entity class in `src/api/`
- [ ] `zoppy-model`: export from `src/index.ts`
- [ ] **`zoppy-model`: register in `src/api/database.provider.ts` (import + `databaseModels` array)**
- [ ] `zoppy-utilities`: add `<Entity>Repository` to `ProviderNames` enum
- [ ] `zoppy-api`: register in `src/cross-cutting/providers/repository.providers.ts`
- [ ] `zoppy-api`: create a Domain extending `RepositoryAdapter<T>` (see `skill-domain`)
- [ ] Register the Domain in `src/domain/domain.module.ts` (providers AND exports arrays)
- [ ] Create a seeder if initial data is needed
