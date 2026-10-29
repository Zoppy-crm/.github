---
name: os-persistence
description: >
    Implementa persistência do Zoppy OS v2 com Drizzle sobre Bun.SQL, repositórios por porta,
    unidade de trabalho e autorização da aplicação, preservando dinheiro decimal. Use ao
    escrever consulta, repositório, transação ou teste de autorização. Triggers: "persistência OS",
    "Bun.SQL", "unidade de trabalho OS", "transação OS", "repositório Drizzle", "dinheiro OS".
compatibility: Zoppy OS v2; Bun 1.4.3, TypeScript 7.0.2, Drizzle 0.45.4 e PostgreSQL.
metadata:
  author: zoppy
  version: "1.0"
  stack: "drizzle-orm 0.45.4 / drizzle-orm/bun-sql / Bun.SQL / PostgreSQL / decimal.js"
---

# Persistência do OS

## 1. Abra recursos na composição

`platform/` cria apenas o client SQL, sem importar `db/schema`.
`adapters/postgres/database.ts` monta Drizzle e importa os schemas; a composição controla lifecycle
e injeta a UoW. O exemplo fica nesse adaptador, por isso o import relativo alcança `apps/api/db/`.
Use o driver validado, não `node-postgres`, outro ORM ou um wrapper SQL inventado.

```typescript
import { SQL } from "bun";
import { drizzle } from "drizzle-orm/bun-sql";
import * as schema from "../../../db/schema/catalog.ts";

export function openDatabase(url: string, max: number, connectionTimeout: number) {
    const client = new SQL(url, { max, connectionTimeout });
    return { client, db: drizzle({ client, schema }) };
}
```

URL, tamanho do pool e timeout vêm de configuração validada; não fixe parâmetros de produção no código.
Componha os exports dos schemas necessários. No shutdown, encerre consumidores antes de
`await client.close()`. Não feche o pool por request nem deixe conexões reservadas sem liberação.

## 2. Implemente a porta do assunto

A interface mora em `application/<assunto>/ports.ts`; o adaptador em
`adapters/postgres/<assunto>/<entidade>-repository.ts` implementa essa porta.
Recebe o executor da transação e converte linhas em valores internos. Não retorna builders,
linhas Drizzle ou tipos SQL à aplicação. Não consulta tabela de outro assunto.

## 3. O caso de uso abre a unidade de trabalho

O caso de uso decide quais operações são atômicas e chama a porta de UoW. A composição só injeta
a implementação. O adaptador da UoW abre `db.transaction`, constrói repositórios e enqueue com o
mesmo `tx` e entrega apenas portas transacionais ao callback do caso de uso. Repositórios e
produtor de jobs recebem esse executor; não abrem outra transação nem usam o pool global.

Trecho interno do adaptador da UoW, acionado pela porta chamada pelo caso de uso:

```typescript
return db.transaction(async (tx) => {
    return work(createTransactionalPorts(tx));
});
```

`work` e `createTransactionalPorts` são funções locais, não APIs da biblioteca. Drizzle/Bun
reservam a conexão e fazem commit/rollback ao terminar o callback; não misture `BEGIN` manual
no pool. Não há configuração de identidade de negócio na conexão. O principal resolvido no
servidor é entrada do caso de uso, que aplica regras de pessoa, times, capacidades e audiência.
Uma recusa retornada como valor **não causa rollback automaticamente**: não escreva antes da
recusa ou faça a UoW traduzir o resultado de rollback para uma falha interna controlada, capturada
fora da transação. Nunca confirme alterações parciais porque nenhum `throw` ocorreu.

## 4. Separe as duas roles por higiene

- **`os_app`:** HTTP e worker, sem DDL, sem ownership, sem superuser, sem criar roles/bancos e
  sem poder assumir `os_owner`; recebe grants mínimos por objeto e operação.
- **`os_owner`:** possui os objetos e roda migrações. Sua credencial fica fora de HTTP/worker.

O OS é interno e tem uma organização só. A autorização é regra da aplicação, testada no domínio
e na integração através dos casos de uso: pessoa ativa/pendente, times, capacidades e audiência.
Grants protegem objetos, não decidem acesso de pessoas. RLS é apenas possibilidade futura que
depende do dono; não implante policies ou contexto de sessão SQL como autorização nesta fatia.
Prefira schema declarado e migrações do Kit; roles externas usam `pgRole(...).existing()` conforme
`os-migration`. SQL escrito à mão fica restrito ao bootstrap de roles/grants. O SQL interno
da fila é gerado pelo próprio SDK e versionado em etapa de migração da dona.

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

- Identidade em variável global, consulta fora do `tx` da UoW ou repositório abrindo transação própria.
- Usar a credencial dona em runtime ou tratar grants de banco como autorização de pessoas.
- Esperar modelo/aprovação com lock/conexão transacional ocupada.
- Converter `numeric` para `number` ou duplicar saldo financeiro no checkpoint do grafo.

Leia [fontes e limites](references/sources.md) antes de mudar driver ou transação de banco.
