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
A composição recebe o client Bun.SQL e monta o adaptador com configuração validada.
Fila usa tabelas no mesmo PostgreSQL; não é broker separado nem extensão Rust.
Não importe pg-boss na aplicação ou em regras de agenda.

```typescript
import { PgBoss, fromBunSql } from "pg-boss";
import type { SQL } from "bun";

export function createBoss(client: SQL, schema: string) {
    return new PgBoss({
        db: fromBunSql(client),
        schema,
        migrate: false,
        createSchema: false,
        supervise: false,
        schedule: false,
        useListenNotify: false,
    });
}
```

`schema` vem da configuração validada. `migrate: false` e `createSchema: false` são obrigatórios
no runtime com `os_app`: schema ausente/incompatível deve falhar, sem elevar privilégios.
As outras três flags reproduzem o modo do ensaio; não são defaults
de operação aprovados. Avalie supervisão e recuperação antes de produção; LISTEN/NOTIFY não foi
testado. A tabela persiste trabalho mesmo quando notificação é usada.

A role `os_owner` instala o schema em migração versionada com SQL **gerado** por
`getConstructionPlans(schema)` de pg-boss 12.38.0. Para atualizar, gere com
`getMigrationPlans(schema, installedSchemaVersion)`, informando a versão real instalada, não
a versão do pacote. Revise o plano e suas fronteiras de transação antes de aplicá-lo; não aninhe
seus `BEGIN`/`COMMIT` cegamente no migrator Drizzle. Veja `os-migration`.
Provisione filas no lifecycle de implantação com a dona, fora de HTTP/worker: `createQueue` pode
executar DDL para partições. Conceda a `os_app` apenas uso do schema, DML e execução das funções
necessárias ao modo exercitado, sem privilégios para criar/alterar objetos nem funções administrativas.
Teste `start`, envio e consumo conectado como `os_app`; ela nunca recebe a credencial dona.

## 2. Confirme escrita e enqueue juntos

O caso de uso abre a transação pela porta de UoW; no adaptador, grave ocorrência/intenção
e envie usando o mesmo `tx`. Repositório e enqueue recebem o executor, sem abrir outra transação:

```typescript
import { sql } from "drizzle-orm";
import { fromDrizzle } from "pg-boss";

await db.transaction(async (tx) => {
    await writeOccurrence(tx, occurrence);
    const jobId = await boss.send(queue, { occurrenceId: occurrence.id }, {
        db: fromDrizzle(tx, sql),
    });
    if (jobId === null) throw new Error("enqueue_returned_no_job");
});
```

O trecho é interno à UoW; `writeOccurrence` é função local do adaptador, não API do SDK.
A UoW usa `db.transaction`, conforme `os-persistence`, e liga a porta
de entrega ao `tx` para que o caso de uso não receba ORM. O envio herda somente opções da fila
explicitamente aprovadas e provisionadas; não use override de retry como política implícita.
Enqueue independente permite linha sem job/job sem linha. Payload leva **somente IDs**, nunca
prompts, mensagens, e-mail, tokens, credenciais ou qualquer dado sensível. O worker busca os dados
pela aplicação após autorizar; um ID no payload não concede autoridade.

## 3. Revalide no consumo

1. A composição registra erros com `boss.on("error", handler)` e inicia com `await boss.start()`.
   A fila deve estar previamente provisionada pela dona, com opções explícitas; runtime não a cria.
2. `entrypoints/worker/` valida `job.data` com Zod e chama o caso de uso injetado. O callback
   de `boss.work(queue, options, async (jobs) => ...)` recebe um **array** de jobs.
3. Resolva o vínculo persistido da execução e refaça a admissão atual: pessoa ativa,
   times, audiência, projeto, contas e budget. A autorização do enqueue pode ter sido revogada.
4. Registre ocorrência, revisão e tentativa separadas do estado técnico da entrega. Posse de job
   não autoriza efeito; lease/fencing e recovery exigem prova própria antes de produção.
5. Desligue com `await boss.stop({ graceful: true, timeout: shutdownTimeoutMs })` antes de fechar o pool;
   `shutdownTimeoutMs` vem de configuração validada.

## 4. Declare opções e mantenha retenção pendente

Nunca use `createQueue(queue)` ou `{}`: a biblioteca preenche retry, expiração e retenção.
Use `createQueue(queue, { retryLimit, retryDelay, retryBackoff, retryDelayMax, expireInSeconds,
retentionSeconds, deleteAfterSeconds })` no provisionamento, com campos aplicáveis explicitados
e validados a partir de decisão aprovada. Tipos opcionais no SDK não tornam a política opcional.
**`retentionSeconds` e `deleteAfterSeconds`: PENDENTES do dono, sem valor escolhido nesta skill.**
Retry e expiração também precisam de decisão explícita, sem herdar defaults. Enquanto faltarem
valores aprovados, a criação/configuração da fila de produção fica bloqueada. Criar fila existente
não altera suas opções: confira a configuração persistida e revise mudanças com `updateQueue`.

## 5. Separe retry técnico e política de negócio

Falha de transporte pode admitir nova tentativa técnica. Recusa de acesso, limite excedido ou
aprovação ausente não são falhas transitórias a repetir cegamente. O caso de uso persiste a recusa
e decide o desfecho de negócio; pg-boss não decide atraso, DST, sobreposição, delegação ou versão
fixa versus seguir publicação. Essas políticas permanecem pendentes, sem default.

## 6. Proteja o efeito externo

Persista intenção e chave estável de idempotência antes de chamar o destino. A chave identifica o
mesmo efeito lógico entre tentativas, não um UUID novo por retry. Confira recurso, conta, destino,
argumentos e aprovação autenticada de uso único antes da escrita. Use a chave no provedor quando
ele oferecer suporte. Nenhuma transação fica aberta durante chamada externa/aprovação.

Se houve possível envio e timeout, registre **desfecho desconhecido** e reconcilie com o destino
antes de repetir. Falta de resposta não prova falta de efeito. Sem idempotência do destino não há
promessa de exactly-once; deduplicar jobs não deduplica efeitos.

## 7. Prove com Postgres real

Verifique rollback da linha e do job, commit conjunto e entrega após reiniciar produtor, com role
de aplicação e grants reais. Teste revogação antes do consumo e retorno externo ambíguo.
O ensaio observou dois consumidores e oito jobs sem dupla posse; não provou crash de worker ativo,
recuperação de lease ou ausência de duplicação externa.

## Anti-padrões

- Enqueue após commit sem coordenação durável, fila em memória ou worker confiando no payload como identidade.
- Retentar todo erro, reutilizar aprovação sem controle ou gerar nova chave por tentativa.
- Deixar pg-boss escolher regra temporal, orçamentária ou de autoridade do produto.
- Tratar cancelamento local/rollback como cancelamento do efeito remoto.

Leia [fontes e limites](references/sources.md) para a integração validada.
