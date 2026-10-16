# Filas e eventos

## Filas do módulo

- **Nome:** `whatsapp.<submódulo>.<ação>` (ex.: `whatsapp.messaging.dispatch`), no enum `<Sub>Queue` do `<sub>.queues.ts` (ex.: `MessagingQueue.DISPATCH`).
- **Frota:** registradas só na `WHATSAPP_PIPELINE`. O Redis continua compartilhado.
- **Produtor:** porta no `domain/ports`, adaptador em `infrastructure/` com `@InjectRingQueue`. Nunca `@InjectQueue` (canary blue/green).
- **jobId:** o id de negócio (`messageId`), para o mesmo trabalho não entrar duas vezes.
- **Envelope:** `{ data, context, eventId? }`. O processor base restaura o contexto do tenant a partir dele.
- **Processor:** estende `WhatsappProcessorBase`, que loga entrada, saída e erro e traduz a categoria do erro:

| Categoria | Fila |
|---|---|
| validation, not_found, conflict, unauthorized, forbidden | sem retry (UnrecoverableError) |
| rate_limited, unavailable | retry |
| internal | retry padrão |

- **Constantes de fila** não saem do módulo: ninguém de fora enfileira direto numa fila `whatsapp.*`.

## Filas que trocam de nome por milestone

| Milestone | Fila legada |
|---|---|
| F1a | WHATSAPP_ACCOUNT, SYNC_WHATSAPP_TECH_PROVIDER, FULFILL_WHATSAPP_ACCOUNT, CREATE_WPP_MANAGER |
| F1b | WPP_HEALTH_SIGNAL, WPP_ACCOUNT_RESTRICTION_EXPIRATION (cron) |
| F2 | UPDATE_WHATSAPP_MESSAGE_TEMPLATE, SYNC_WHATSAPP_TEMPLATES, BACKFILL_TEMPLATE_REASON_INFO, RECREATE_PENDING_DELETION_TEMPLATE(S_ORCHESTRATOR) |
| F4a.1 | WHATSAPP_MESSAGE_SENDER |
| F4b.2 | WHATSAPP_WEBHOOK |

Não mudam, porque são multicanal e ficam no CRM: `FETCH_ENTITIES`, `MESSAGE_RESULT_HANDLER`,
`WEBHOOK_MESSAGE_STATUS`. A drenagem de cada troca está em [migrar.md](migrar.md), passo 4.

## Eventos de integração

O módulo publica fatos para quem está fora. Transporte: **EventBridge Custom Event Bus** (o
barramento novo, não o Classic), barramento `whatsapp`, com retenção configurada.

- **Publicar:** a application chama a porta `EventPublisher` do `platform/events`. Nunca o SDK da AWS direto.
- **Nome:** `whatsapp.<agregado>.<fato>` com versão no tipo (`MessageReceivedV1`). O tipo mora em `public/events/`.
- **Envelope:** `{ eventId, name, version, occurredAt, tenantId, correlationId, payload }`.
- **Quando publicar:** depois que o dado está salvo.
- **Payload:** ids e o que o assinante precisa para decidir; nada de agregado serializado.

| Evento | Desde |
|---|---|
| whatsapp.phone-number.changed | F1a |
| whatsapp.account.health-changed | F1b |
| whatsapp.template.status-changed | F2 |
| whatsapp.contact.opted-out | F3 |
| whatsapp.message.dispatched / dispatch-failed | F4a |
| whatsapp.message.status-changed | F4b.1 |
| whatsapp.message.received | F4b.2 |

Evento de domínio (dentro de um submódulo) não entra nessa lista e não passa pelo EventBridge.

## Assinar um evento (lado do CRM)

1. Na infraestrutura: um **subscriber** no barramento com filtro pelo `name`, entregando numa **fila SQS própria** com DLQ. Um assinante, uma fila.
2. No código: o handler com `@HandlesEvent(<evento>)`, consumido pelo runtime de `src/access/messaging` (ACK, RETRY, DISCARD, DEAD_LETTER).
3. **Idempotência:** dedupe pelo `eventId`, mas um evento reenviado por replay traz a marca de replay e deve ser processado de novo.
4. **Ordem:** não há garantia. O handler tolera fora de ordem (o status já usa `MessageStatusTransitionHelper`).

## Replay

O barramento guarda os eventos pelo período configurado. Para reprocessar depois de um bug num
assinante: corrija o handler e reposicione **só o subscriber dele** para antes do bug. Os outros
assinantes não recebem nada de novo. O mesmo serve para um assinante novo que precisa de histórico.
