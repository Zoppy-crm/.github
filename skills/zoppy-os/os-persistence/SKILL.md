---
name: os-persistence
description: >
    Implementa persistência do Zoppy OS v2 com Drizzle sobre Bun.SQL, repositórios por porta,
    unidade de trabalho, contexto transacional e RLS, preservando dinheiro decimal. Use ao
    escrever consulta, repositório, transação ou teste de isolamento. Triggers: "persistência OS",
    "Bun.SQL", "unidade de trabalho OS", "RLS OS", "repositório Drizzle", "dinheiro OS".
compatibility: Zoppy OS v2; Bun 1.4.3, TypeScript 7.0.2, Drizzle 0.45.4 e PostgreSQL.
metadata:
  author: zoppy
  version: "1.0"
  stack: "drizzle-orm 0.45.4 / drizzle-orm/bun-sql / Bun.SQL / PostgreSQL / decimal.js"
---

# Persistência do OS

## 1. Abra recursos na composição

`platform/database.ts` cria o recurso técnico; a composição controla lifecycle e injeta a UoW.
Use o driver validado, não `node-postgres`, outro ORM ou um wrapper SQL inventado.

```typescript
import { SQL } from "bun";
import { drizzle } from "drizzle-orm/bun-sql";
import * as schema from "../../db/schema/catalog.ts";

export function openDatabase(url: string) {
    const client = new SQL(url, { max: 4, connectionTimeout: 5 });
    return { client, db: drizzle({ client, schema }) };
}
```

O tamanho do pool acima é o do ensaio, não um parâmetro de produção obrigatório.
Componha os exports dos schemas necessários. No shutdown, encerre consumidores antes de
`await client.close()`. Não feche o pool por request nem deixe conexões reservadas sem liberação.

## 2. Implemente a porta do assunto

A interface mora em `application/<assunto>/ports.ts`; o adaptador em
`adapters/postgres/<assunto>/<entidade>-repository.ts` implementa essa porta.
Recebe o executor da transação e converte linhas em valores internos. Não retorna builders,
linhas Drizzle ou tipos SQL à aplicação. Não consulta tabela de outro assunto.

## 3. Use a mesma conexão durante a unidade de trabalho

1. Entre em `db.transaction(async (tx) => ...)`, que reserva a conexão e faz commit/rollback.
2. Antes de qualquer consulta de negócio, aplique tenant/pessoa autenticados, parametrizados,
   com `set_config(..., true)` usando **esse `tx`**.
3. Construa repositórios e enqueue com o mesmo `tx`. A porta de UoW entrega portas transacionais,
   não um objeto Drizzle ao caso de uso. Nenhuma operação interna usa o `db` global/pool.
4. Ao sair do callback, a transação termina e a conexão retorna ao pool inclusive em falha.
   Não misture `BEGIN` manual no pool nem implemente outra reserva sobre a já gerida pelo Drizzle.

Trecho dentro da UoW; `principal` é resolvido pelo servidor. Os nomes de configuração são um par
de exemplo: devem coincidir com as policies versionadas do projeto.

```typescript
import { sql } from "drizzle-orm";

await db.transaction(async (tx) => {
    await tx.execute(sql`select set_config('app.tenant_id', ${principal.tenantId}, true)`);
    await tx.execute(sql`select set_config('app.person_id', ${principal.personId}, true)`);
    return work(createRepositories(tx));
});
```

`work` e `createRepositories` são funções locais da composição/UoW, não APIs das bibliotecas.
Uma recusa de negócio retornada como valor **não causa rollback automaticamente**: não escreva antes
da recusa ou faça a UoW traduzir o resultado de rollback para uma falha interna controlada,
capturada fora da transação. Nunca confirme alterações parciais porque nenhum `throw` ocorreu.

## 4. Separe as duas roles

- **Aplicação:** sujeita a RLS, sem ser dona das tabelas, sem superuser/BYPASSRLS nem possibilidade
  de assumir a role dona; recebe apenas grants necessários.
- **Dona:** possui schema/tabelas e roda migrações; nesse modelo ignora RLS. Nunca fornece a
  credencial de execução HTTP/worker. Nomes concretos das roles dependem da configuração do projeto.

RLS complementa a autorização da aplicação: tenant/pessoa autenticados restringem linhas, mas
não substituem audiência, projeto, times ou capacidades. Policies usam `USING` e `WITH CHECK`
conforme leitura/escrita e recusam contexto ausente. Veja `os-migration` para SQL.
Teste conectado realmente como aplicação: role dona/admin não prova isolamento, mesmo com dois tenants.

## 5. Termine a transação antes de esperar o mundo externo

Transações são curtas. Persista admissão/intenção, faça commit, chame modelo ou destino externo,
e abra outra transação curta para custo/resultado. Aprovação humana nunca mantém transação aberta.
Atomicidade com fila usa o mesmo `tx`, conforme `os-jobs`. Rollback não desfaz efeito externo.

## 6. Preserve dinheiro sem conversão binária

Use PostgreSQL `numeric`, strings no transporte e `Decimal` de decimal.js para cálculo.
Nunca `number`, `parseFloat`, `Number`, coerção unária ou `.toNumber()` para preço, débito, custo ou budget.

```typescript
import Decimal from "decimal.js";

const total = new Decimal("0.10").plus(new Decimal("0.20"));
const persistedAmount = total.toString();
```

Precisão/escala e arredondamento devem seguir contrato aprovado. Algoritmo de reserva concorrente
e overshoot estão pendentes; decimal exato não resolve admissão concorrente nem escolhe um default.

## Anti-padrões

- `set_config(..., false)`, identidade em variável global ou consulta fora do `tx` da UoW.
- Testar RLS como dona, desligar RLS para corrigir teste ou confundir filtro de app com policy.
- Esperar modelo/aprovação com lock/conexão transacional ocupada.
- Converter `numeric` para `number` ou duplicar saldo financeiro no checkpoint do grafo.

Leia [fontes e limites](references/fontes.md) antes de mudar driver ou contexto de banco.
