---
name: os-migration
description: >
    Cria e revisa migrações PostgreSQL do Zoppy OS v2 com Drizzle Kit, schema TypeScript,
    SQL versionado, policies RLS e grants, verificando regeneração sem deriva. Use ao alterar
    tabela, índice, constraint ou policy. Triggers: "migração OS", "drizzle-kit generate",
    "schema OS", "policy RLS", "grants OS", "deriva de migração".
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
Fila e checkpoints têm migrações/privilégios próprios, coordenados na implantação; não trate
as tabelas internas de SDK como tabelas de domínio.

Em `apps/api/drizzle.config.ts`:

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
    dialect: "postgresql",
    schema: "./db/schema/*.ts",
    out: "./db/migrations",
});
```

## 2. Gere, revise e versione

1. A partir de `apps/api`, use o Kit instalado e fixado no lock:

   ```bash
   bun run --bun drizzle-kit generate
   ```

2. Revise SQL, índices, unicidade, chaves, nulabilidade, defaults e risco sobre dados existentes.
   Dinheiro é `numeric`, nunca float/double. Não fixe precisão/escala sem regra aprovada.
3. Versione SQL e metadados/snapshots/journal gerados. Não edite migração já aplicada para fazer
   um ambiente parecer atualizado; crie migração sucessora.
4. Policies RLS e grants ficam em SQL de migração revisado, não em bootstrap de request ou dashboard.
   Leia [exemplo de RLS](references/rls.md) antes de adicionar uma policy.

## 3. Regere sem deriva

Após gerar, nova geração sobre os mesmos schemas e histórico não deve criar mudança inesperada.
Para conferir SQL inicial, o ensaio gera em diretório temporário e compara o SQL byte a byte com
o versionado. Para histórico incremental, reproduza a sequência a partir do estado anterior;
não compare todo histórico com um dump inicial novo.

Mantenha SQL manual de RLS/grants identificável e verifique sua aplicação no banco: igualdade do
SQL gerado das tabelas não prova que o Kit reproduz policies escritas à mão. Não apague essas
policies ou snapshots para zerar o diff. Revise qualquer diferença antes de atualizar a referência.

## 4. Aplique com a role dona e teste como aplicação

Use credencial de migração da role dona, separada da execução da aplicação. O migrator validado
recebe o `db` já conectado com essa credencial; trecho executado a partir de `apps/api`:

```typescript
import { migrate } from "drizzle-orm/bun-sql/migrator";

await migrate(db, { migrationsFolder: "./db/migrations" });
```

Prove aplicação em Postgres descartável e atualização do estado anterior relevante. Depois abra
conexão **como role de aplicação** para ler/escrever dados de dois tenants/pessoas, negar contexto
ausente e conferir grants. A dona ignora RLS nesse modelo; seu teste de leitura não é prova de isolamento.
Não execute migração privilegiada no startup de cada request/worker nem use a senha dona na aplicação.

## Anti-padrões

- `push` para substituir histórico SQL revisado ou mudança manual só no banco.
- Comitar SQL sem snapshots/journal ou gerar com CLI não fixado na árvore instalada.
- RLS/grants apenas no teste, no init de um pool ou fora do controle de versão.
- Chamar regeneração de prova de RLS, ou declarar migração segura porque compilou.

Consulte [fontes e limites](references/fontes.md) para os comandos e APIs confirmados.
