---
name: os-jobs
description: >
    Implementa entrega durável do Zoppy OS v2 com pg-boss sobre Bun.SQL e enqueue atômico
    com Drizzle, separando admissão, retry técnico e efeito externo idempotente. Use ao criar
    produtor, worker ou recuperação de job. Triggers: "pg-boss OS", "job OS", "enqueue atômico",
    "worker OS", "retry técnico", "desfecho desconhecido".
compatibility: Zoppy OS v2; Bun 1.4.3, pg-boss 12.38.0, Drizzle 0.45.4 e PostgreSQL.
metadata:
  author: zoppy
  version: "1.0"
  stack: "pg-boss 12.38.0 / fromBunSql / fromDrizzle / Drizzle ORM 0.45.4"
---

# Jobs do OS

## 1. Monte a fila atrás de uma porta

`application/<assunto>/ports.ts` define a entrega; `adapters/jobs/` implementa pg-boss.
A composição recebe o client Bun.SQL e monta `new PgBoss({ db: fromBunSql(client), ... })`.
Fila usa tabelas no mesmo PostgreSQL; não é broker separado nem extensão Rust.
Não importe pg-boss na aplicação ou em regras de agenda.

```typescript
import { PgBoss, fromBunSql } from "pg-boss";
import type { SQL } from "bun";

export function createBoss(client: SQL) {
    return new PgBoss({
        db: fromBunSql(client),
        schema: "os_jobs",
        supervise: false,
        schedule: false,
        useListenNotify: false,
    });
}
```

`os_jobs` é nome ilustrativo. As três flags reproduzem o modo do ensaio; não são defaults
de operação aprovados. Avalie supervisão e recuperação antes de produção; LISTEN/NOTIFY não foi
testado. A tabela persiste trabalho mesmo quando notificação é usada.

## 2. Confirme escrita e enqueue juntos

Na UoW já configurada com tenant/pessoa, grave a ocorrência/intenção e envie usando o mesmo `tx`:

```typescript
import { sql } from "drizzle-orm";
import { fromDrizzle } from "pg-boss";

await db.transaction(async (tx) => {
    await writeOccurrence(tx, occurrence);
    const jobId = await boss.send(queue, { occurrenceId: occurrence.id }, {
        db: fromDrizzle(tx, sql),
        retryLimit: 0,
    });
    if (jobId === null) throw new Error("enqueue_returned_no_job");
});
```

`writeOccurrence` é função local do adaptador, não API do SDK; o trecho assume a configuração
transacional descrita em `os-persistence`. `retryLimit: 0` vem da prova de atomicidade: não decide
a política de retry de produção. A porta de entrega transacional deve ser ligada pela UoW para
que o caso de uso não receba `tx`. Enqueue com conexão independente permite linha sem job/job sem linha.

## 3. Revalide no consumo

1. A composição registra erros com `boss.on("error", handler)`, inicia com `await boss.start()`
   e prepara a fila com `await boss.createQueue(queue)` no lifecycle autorizado.
2. `entrypoints/worker/` valida `job.data` com Zod e chama o caso de uso injetado. O callback
   de `boss.work(queue, options, async (jobs) => ...)` recebe um **array** de jobs.
3. Resolva o vínculo persistido da execução e refaça a admissão atual: pessoa ativa, tenant,
   times, audiência, projeto, contas e budget. A autorização do enqueue pode ter sido revogada.
4. Registre ocorrência, revisão e tentativa separadas do estado técnico da entrega. Posse de job
   não autoriza efeito; lease/fencing e recovery exigem prova própria antes de produção.
5. Desligue com `await boss.stop({ graceful: true, timeout: 5000 })` antes de fechar o pool.

## 4. Separe retry técnico e política de negócio

Falha de transporte pode admitir nova tentativa técnica. Recusa de acesso, limite excedido ou
aprovação ausente não são falhas transitórias a repetir cegamente. O caso de uso persiste a recusa
e decide o desfecho de negócio; pg-boss não decide atraso, DST, sobreposição, delegação ou versão
fixa versus seguir publicação. Essas políticas permanecem pendentes, sem default.

## 5. Proteja o efeito externo

Persista intenção e chave estável de idempotência antes de chamar o destino. A chave identifica o
mesmo efeito lógico entre tentativas, não um UUID novo por retry. Confira recurso, conta, destino,
argumentos e aprovação autenticada de uso único antes da escrita. Use a chave no provedor quando
ele oferecer suporte. Nenhuma transação fica aberta durante chamada externa/aprovação.

Se houve possível envio e timeout, registre **desfecho desconhecido** e reconcilie com o destino
antes de repetir. Falta de resposta não prova falta de efeito. Sem idempotência do destino não há
promessa de exactly-once; deduplicar jobs não deduplica efeitos.

## 6. Prove com Postgres real

Verifique rollback da linha e do job, commit conjunto e entrega após reiniciar produtor, com role
de aplicação e grants reais. Teste revogação antes do consumo e retorno externo ambíguo.
O ensaio observou dois consumidores e oito jobs sem dupla posse; não provou crash de worker ativo,
RLS, recuperação de lease ou ausência de duplicação externa.

## Anti-padrões

- Enqueue após commit sem coordenação durável, fila em memória ou worker confiando no payload como identidade.
- Retentar todo erro, reutilizar aprovação sem controle ou gerar nova chave por tentativa.
- Deixar pg-boss escolher regra temporal, orçamentária ou de autoridade do produto.
- Tratar cancelamento local/rollback como cancelamento do efeito remoto.

Leia [fontes e limites](references/fontes.md) para a integração validada.
