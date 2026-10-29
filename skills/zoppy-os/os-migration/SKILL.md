---
name: os-migration
description: >
    Cria e revisa migrações PostgreSQL do Zoppy OS v2 com Drizzle Kit, schema TypeScript,
    SQL versionado, roles externas e grants, verificando regeneração sem deriva. Use ao alterar
    tabela, índice, constraint ou permissão. Triggers: "migração OS", "drizzle-kit generate",
    "schema OS", "roles OS", "grants OS", "deriva de migração".
compatibility: Zoppy OS v2; Bun 1.4.3, drizzle-orm 0.45.4, drizzle-kit 0.31.11 e PostgreSQL.
metadata:
  author: zoppy
  version: "1.0"
  stack: "Drizzle Kit 0.31.11 / Drizzle ORM 0.45.4 / Bun.SQL / PostgreSQL"
---

# Migrações do OS

## 1. Declare o schema no lugar canônico

Tabelas do produto em `apps/api/db/schema/<assunto>.ts`; auth em `db/schema/auth.ts` com
propriedade explícita da integração Better Auth. Exporte os modelos para o Kit descobri-los.
Prefira o que drizzle-orm 0.45.4 e drizzle-kit 0.31.11 declaram, geram e acompanham em snapshots;
não duplique DDL de tabela, índice ou constraint em SQL manual.

Em `apps/api/drizzle.config.ts`:

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
    dialect: "postgresql",
    schema: "./db/schema/*.ts",
    out: "./db/migrations",
});
```

Roles provisionadas externamente podem ser referenciadas em `db/schema/roles.ts`:

```typescript
import { pgRole } from "drizzle-orm/pg-core";

export const appRole = pgRole("os_app").existing();
export const ownerRole = pgRole("os_owner").existing();
```

`.existing()` impede que o Kit tente criá-las. Não cria roles nem grants. Bootstrap de roles e
grants usa SQL revisado porque a versão fixada não representa todos os atributos/privilégios
necessários; credenciais são provisionadas fora do código. Veja [roles e grants](references/grants.md).
O OS é interno, com uma organização só; pessoa, times, capacidades e audiência são autorização da
aplicação. RLS é apenas possibilidade futura dependente do dono. Se aprovada futuramente, prefira
`pgPolicy`/`enableRLS` no schema e SQL gerado pelo Kit, sem anexar policies manuais ao SQL gerado.

## 2. Gere, revise e versione

1. A partir de `apps/api`, use o Kit instalado e fixado no lock:

   ```bash
   bun run --bun drizzle-kit generate
   ```

2. Revise SQL, índices, unicidade, chaves, nulabilidade, defaults e risco sobre dados existentes.
   Dinheiro é `numeric`, nunca float/double. Não fixe precisão/escala sem regra aprovada.
3. Versione SQL e os snapshots/journal efetivamente gerados pela **0.31.11**. A documentação atual
   pode mostrar outro layout; não renomeie o histórico para imitá-la. Nunca edite migração aplicada.
4. Para bootstrap de roles/grants não coberto pelo schema, use migração separada:

   ```bash
   bun run --bun drizzle-kit generate --custom --name=roles-grants
   ```

   Edite só o arquivo custom novo. O snapshot não modela esses privilégios; comprove-os no banco.
   Bootstrap de roles exige credencial de provisionamento capaz de criá-las; não dê CREATEROLE
   a `os_app` nem promova a credencial do runtime. `os_owner` aplica as migrações dos objetos.
5. Fila e checkpoints pertencem aos respectivos SDKs, não ao domínio nem ao schema Drizzle.
   Para pg-boss 12.38.0, versione SQL gerado por `getConstructionPlans(schema)` na instalação e
   por `getMigrationPlans(schema, installedSchemaVersion)` no upgrade. É SQL **gerado pelo SDK**,
   não DDL escrito à mão. Aplique em etapa de migração como `os_owner`, coordenada com o histórico
   do Kit e com grants mínimos. Os planos têm suas próprias fronteiras de transação: revise antes
   de executar, sem envolver cegamente no migrator transacional do Drizzle. Runtime usa
   `migrate: false, createSchema: false`; provisionamento de filas também fica com a dona.

## 3. Regere sem deriva

Após gerar, nova geração sobre os mesmos schemas e histórico não deve criar mudança inesperada.
Para SQL inicial, o ensaio gera em diretório temporário e compara byte a byte com o versionado.
Para histórico incremental, reproduza a sequência a partir do estado anterior; não compare todo
histórico com um dump inicial novo. Não anexe SQL manual a arquivos gerados para forçar a igualdade.

Separe na verificação o SQL reproduzível do Kit, o SQL reproduzível do SDK e os arquivos custom de
roles/grants, cada qual com seu gerador ou prova de aplicação. Migração custom não é regenerada
pelo schema: valide seu conteúdo e permissões reais. Não apague snapshots/journal para zerar diff.

## 4. Aplique com a role dona e teste como aplicação

Use credencial de `os_owner`, separada de HTTP/worker. O migrator recebe `db` conectado como dona;
trecho executado a partir de `apps/api`, para as migrações geridas pelo Kit:

```typescript
import { migrate } from "drizzle-orm/bun-sql/migrator";

await migrate(db, { migrationsFolder: "./db/migrations" });
```

Prove instalação limpa e atualização do estado anterior relevante em Postgres descartável.
Reconecte como `os_app`: confira grants mínimos de domínio, das quatro tabelas de auth e da fila;
prove startup/envio/consumo sem DDL e negação de CREATE/ALTER e de assumir a dona. Teste autorização
de pessoa pendente/ativa, times, capacidades e audiência pelos casos de uso no domínio e integração.
Não use teste como dona como prova de runtime. Credencial dona nunca entra no processo HTTP/worker.

## Anti-padrões

- `push` no lugar de histórico revisado, mudanças só no banco ou SQL duplicando schema gerável.
- Comitar SQL gerado sem metadados ou usar CLI diferente da versão instalada.
- Grants globais, bootstrap em request/worker ou senha dona para contornar permissão negada.
- Chamar regeneração de prova de autorização ou declarar migração segura porque compilou.

Consulte [fontes e limites](references/fontes.md) para os comandos e APIs confirmados.
