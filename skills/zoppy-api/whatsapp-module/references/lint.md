# Regras do lint

Cada mensagem do lint cita a regra e aponta para cá. L1 e L6 rodam no repositório inteiro; as
demais, só em `src/modules/whatsapp/**` e `src/platform/**`.

| # | Regra | Decisão | Como corrigir | Regra do ESLint |
|---|---|---|---|---|
| L1 | De fora do módulo, só `whatsapp/public` | D1 | Injete o token de `public/`. Se a operação não existe na fachada, ela entra na fachada | `npm run lint` (repo) |
| L2 | Entre submódulos, só o `api/` do irmão, a partir da `application`. O `<sub>.module.ts` pode importar o módulo irmão | D22 | Importe `<irmão>/api` na application. Se falta a operação, ela entra no `api/` dele | `whatsapp/layer-imports` |
| L3 | O módulo não importa o CRM | D1 | O que o módulo precisa do CRM vira porta com adaptador, ou chega no Command | `whatsapp/layer-imports` |
| L4 | `platform/` não importa `modules/` nem o CRM | D1 | Torne a peça genérica ou deixe-a no módulo | `whatsapp/layer-imports` |
| L5 | De fora do platform, só `*.port.ts` | D1 | Dependa da porta; o binding é do módulo do platform | `whatsapp/layer-imports` |
| L6 | Models `Wpp*` só no `repository/` do submódulo dono | D16 | Leia pelo `api/` ou pela fachada. Dentro do módulo, mova a consulta para o repositório | `npm run lint` (repo) e `whatsapp/layer-imports` |
| L7 | `api/` só importa os próprios tipos; `public/` não importa nada interno | D22 | Declare o tipo de leitura no próprio `api/` ou o Command em `public/`; a implementação fica no access | `whatsapp/layer-imports` |
| L8 | access → application → domain; application não importa repository nem infrastructure | D1, D21 | Dependa da porta em `domain/ports` | `whatsapp/layer-imports` |
| L9 | domain não importa nada de fora dele | D11 | Tire framework do domain; I/O vira porta | `whatsapp/layer-imports` |
| L10 | Application não injeta application | D22 | Use o `api/` do irmão; composição entre casos de uso fica no access | `whatsapp/layer-imports` |
| L11 | Sem `Scope.REQUEST` nem `REQUEST` | D8 | Use o `ContextStore` | `whatsapp/no-request-scope` |
| L12 | `@Module` do submódulo só exporta tokens de `api/` ou `public/` | D21 | Tire do `exports` | `whatsapp/module-exports` |
| L13 | `api/` sem CRUD genérico: `create`, `update`, `save`, `delete`, `remove`, `upsert`, `insert`, `find`, `findAll`, `findOne`, `get`, nem prefixos `save*` e `upsert*` | D22 | Dê nome de negócio à operação (`block`, `findForSending`) | `whatsapp/api-no-crud` |
| L14 | `public/` sem lógica | D21 | Mova a lógica para o access do submódulo | `whatsapp/public-no-logic` |
| L15 | Erro estende `ZoppyBaseError`; `HttpException`, `ZoppyException` e `statusCode` só no access | D24 | Lance com categoria; o access traduz | `whatsapp/error-boundary` |
| L16 | Sem `catch` que só loga e relança | convenção | Deixe subir; a borda loga | `whatsapp/no-log-rethrow` |
| L17 | `process.env` só em `*.config.ts` | D25 | Leia do config injetado | `whatsapp/env-in-config` |
| L18 | Sem `console.*` e sem `LogService` do CRM | D25 | Use a `LoggerPort` | `no-console + whatsapp/layer-imports` |
| L19 | domain não importa a porta de log | D26 | Logue na application | `whatsapp/layer-imports` |
| L20 | Fila `whatsapp.<sub>.<ação>`, com `@InjectRingQueue`; constante de fila não sai do módulo | D17 | Use o enum `<Sub>Queue` do `<sub>.queues.ts` e o adaptador da porta | `whatsapp/queue-conventions` |
| L21 | Lista de exceções de L1 e L6 só diminui | D29, D30 | Ao resolver uma violação, tire o arquivo da lista no mesmo PR | spec da lista de isentos (repo) |
| L22 | Identificador de log é membro de enum | D27 | Acrescente o fato ao `<sub>.logs.ts` | `whatsapp/log-identifier-enum` |
| L23 | access só enxerga `domain/values`; infrastructure só `domain/ports` e `values` | D21 | Passe pela application; implemente a porta, não o agregado | `whatsapp/layer-imports` |

## Estrutura e TypeScript

| Regra | Valor |
|---|---|
| max-lines-per-function | 30 |
| max-depth | 2 |
| max-params | 4 em métodos; construtor até 6 dependências (regra local) |
| complexity / cognitive-complexity | 10 |
| import-x/no-cycle | erro |
| no-comments | erro |
| no-magic-string-compare | erro: compare com enum ou constante |
| eslint-disable em regra estrutural | proibido |
| strictTypeChecked | switch exaustivo, boolean estrito, retorno explícito, readonly, type imports, sem promise solta, sem any |

Exceção só por arquivo, na config, com motivo.

## Rodar

- `npm run lint:whatsapp`: lint do módulo e do platform (ESLint 9, pacote em `tools/eslint`)
- `npm run lint:whatsapp:test`: testes das regras, quando mudar o próprio lint
- `npm run lint`: lint do repositório (ESLint 8), onde vivem L1, L6 e L21
