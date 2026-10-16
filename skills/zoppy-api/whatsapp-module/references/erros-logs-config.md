# Erros, logs, config e contexto

## Erros

Lib `@Zoppy-crm/exceptions`. O núcleo, em `@Zoppy-crm/exceptions/core`, não depende de nada: `ErrorCategory`, `ZoppyBaseError`, `isZoppyError`. A raiz do pacote traz a `ZoppyException`, o `toZoppyException` e o mapa `ERROR_CATEGORY_HTTP_STATUS`, e só o access a importa.

- O domain lança subclasse de `ZoppyBaseError` com `category` e `errorType`.
- Só o `access/` conhece HTTP: traduz `ZoppyError` em `ZoppyException` com `toZoppyException`, pelo mapa de categoria.
- O processor base traduz a categoria em retry ou não (tabela em [filas-e-eventos.md](filas-e-eventos.md)).
- Meta recusou uma mensagem: é estado do agregado (`markFailed`), não exceção.
- Os `errorType` que já existem são preservados, porque o front e os alertas dependem deles.
- Proibido o `catch` que só loga e relança: quem loga o erro é a borda.

| Categoria | HTTP |
|---|---|
| validation | 422 |
| not_found | 404 |
| conflict | 409 |
| unauthorized / forbidden | 401 / 403 |
| rate_limited | 429 |
| unavailable | 503 |
| internal | 500 |

## Logs

- Só pela `LoggerPort` do `platform/logging`. Proibidos `console.*` e o `LogService` do CRM.
- `company_id`, `correlation_id` e `project` entram sozinhos, vindos do contexto.
- Identificador é membro do enum `<sub>.logs.ts`, no formato `WHATSAPP_<SUB>_<FATO>`. Os identificadores que já existem (wpp-flow-logger) são preservados.

| Camada | Loga |
|---|---|
| domain | nunca |
| application | decisões de orquestração (pulou, agendou, desistiu) |
| access | entrada, saída e erro |
| infrastructure | chamada externa: destino, duração, resultado |

Cada fato é logado uma vez, onde ele é conhecido. Telefone continua como hoje nos logs.

## Config

```ts
const schema = z.object({ WPP_SEND_RATE_PER_SECOND: z.coerce.number().int().positive() });

export const messagingConfig = registerAs('whatsapp.messaging', () => {
    const env = schema.parse(process.env);
    return { sendRatePerSecond: env.WPP_SEND_RATE_PER_SECOND };
});
```

- Um `<sub>.config.ts` por submódulo; falha no boot se faltar variável.
- Injeção: `@Inject(messagingConfig.KEY) config: ConfigType<typeof messagingConfig>`.
- `process.env` só existe nesses arquivos.

## Contexto do tenant

- `ContextStore` do `platform/context`, sobre AsyncLocalStorage. Nenhum `Scope.REQUEST` nem `REQUEST` no módulo.
- Quem abre o contexto: interceptor HTTP (da sessão), base de processor (do envelope do job), consumidor de evento (do envelope do evento).
- O repositório filtra por `tenantId` de forma explícita.
- `tenantId` é opaco para o módulo: é o `companyId` do CRM, mas o módulo não depende disso.
