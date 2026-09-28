---
name: jornadas-criticas
description: Tags de jornada crítica (`@jornada:<id>` e `@happy-path`) que fazem um teste E2E contar no KPI de cobertura da Bússola. Use ao escrever, mover ou revisar um teste E2E no zoppy-FE ou no zoppy-e2e-api, e quando perguntarem se uma jornada está coberta ou por que ela não conta.
---

# Jornadas críticas — tags nos testes E2E

O KPI "Cobertura de teste automatizado das jornadas críticas" sai da run, não de planilha. O coletor do
`zoppy-eng-metrics` (`scripts/collect_e2e_journeys.py`) lê o `test-results.json` da última run de cada
suíte e decide o nível de cada jornada pelas tags do próprio teste. Teste sem tag não existe para o KPI,
por melhor que seja.

## Ao escrever ou mover um teste E2E

1. **Decida a jornada.** Compare o fluxo que o teste exercita com a tabela abaixo. Termina quando você
   tem um ou mais ids, ou a conclusão explícita de que o teste não toca jornada crítica.
2. **Marque o `describe`** com cada jornada que ele exercita. Um bloco pode declarar mais de uma.

    ```ts
    test.describe('Segmentos — criação', { tag: ['@jornada:E4'] }, () => { ... });
    ```

3. **Marque o happy path.** O teste que atravessa a jornada inteira, do começo ao resultado que o cliente
   vê, contra a API real da Zoppy, recebe `@happy-path`. Os outros testes do bloco (validação, estados de
   erro, telas isoladas) ficam só com a jornada.

    ```ts
    test('salva o segmento com regras e o encontra na listagem', { tag: ['@happy-path'] }, async ({ page }) => { ... });
    ```

4. **Prove o happy path**, conforme o repo:
    - **zoppy-FE:** importe `test` de `shared/fixtures` (`import { test, expect } from '../../shared/fixtures'`).
      O guard dali vigia todo `@happy-path`, grava a annotation `happy-path-guard` e falha o teste que
      responder a API da Zoppy com corpo inventado. Dentro do happy path, deixe a chamada da Zoppy ir para
      a rede: `route.continue()`, ou `route.fetch()` seguido de `route.fulfill({ response })` quando
      precisar observar a resposta. Mock de terceiro (Meta, gateway, ERP, CDN) continua valendo.
    - **zoppy-e2e-api:** o teste já chama a API direto, então a suíte se declara sem guard no coletor.
      Crie a própria massa pela API e confira o resultado pela API.
5. **Confira a marcação.** `npx playwright test --list --grep @jornada:<id>` lista o teste com as tags. No
   FE, `npm run e2e:typecheck` também precisa passar, porque roda antes da suíte e barra a run.

## Níveis

| Nível | Quando                                                                                                                 |
| ----- | ---------------------------------------------------------------------------------------------------------------------- |
| 0     | nenhum teste da run tem `@jornada:<id>`                                                                                |
| 1     | existe teste com a jornada, mas nenhum `@happy-path` dela passou vigiado pelo guard                                    |
| 2     | um teste com `@jornada:<id>` e `@happy-path` passou (retry verde conta) com a annotation do guard. Só este nível conta |

O nível é revogável: a jornada cai no dia em que o happy path falha, é pulado ou a suíte não roda. O
ambiente de referência do KPI é o mirror. O KPI é nível 2 dividido por 20, com Canary e Infra/Ops fora
do denominador.

## As jornadas

A lista é decisão de produto e mora em `config/critical-journeys.yml` no `zoppy-eng-metrics`. Mudar uma
jornada é PR lá. A coluna "Happy path" diz em qual repo o teste fim a fim deve morar.

| Id      | Jornada                        | Happy path    | O que ele atravessa                                                     |
| ------- | ------------------------------ | ------------- | ----------------------------------------------------------------------- |
| E1      | Criar a integração             | zoppy-FE      | conecta um provedor pelo wizard e vê o card ativo                       |
| E2      | Validar a sincronização        | zoppy-e2e-api | pedido, cliente e produto pela Partners aparecem na API da Zoppy        |
| E3      | Integrar WPP API               | zoppy-e2e-api | cadastro do número concluído e número ativo na conta                    |
| E4      | Segmentação: criação de regras | zoppy-FE      | segmento com regras salvo na API real e encontrado na listagem          |
| E5      | Segmentação: cálculo           | zoppy-e2e-api | mesma contagem em MySQL e OpenSearch                                    |
| E6      | Segmentação: visualização      | zoppy-FE      | segmento criado por API aparece na lista, na busca e no detalhe         |
| E7      | Modelo de mensagem             | zoppy-e2e-api | modelo criado, webhook de aprovação recebido, modelo aprovado           |
| E8      | Checkout                       | zoppy-FE      | cadastro até o pagamento enviado                                        |
| V1      | Criar campanha                 | zoppy-FE      | wizard inteiro, com segmento, mensagem e agendamento, salvo na API real |
| V2      | Enviar uma campanha            | zoppy-e2e-api | campanha para segmento de 1 cliente até o status enviada                |
| V3      | Visualizar resultados          | zoppy-FE      | relatório de campanha já enviada com os números da API                  |
| V4      | Giftback                       | zoppy-e2e-api | pedido pela Partners gera o cupom do cliente                            |
| V5      | Carrinho Abandonado            | zoppy-e2e-api | carrinho pela Partners dispara o fluxo                                  |
| V6      | Aniversário                    | zoppy-e2e-api | cliente que faz aniversário hoje recebe a mensagem do fluxo             |
| V7      | Painel do vendedor             | zoppy-FE      | vendedor vê a tarefa criada pelo passo "Tarefa" do fluxo                |
| PLAT-1  | Financeiro                     | zoppy-FE      | faturas, assinatura e troca de cartão                                   |
| PLAT-2  | Acesso                         | zoppy-FE      | usuário com perfil restrito não alcança a tela bloqueada                |
| PLAT-3  | Partners e sync                | zoppy-e2e-api | CRUD das entidades da Partners API                                      |
| PLAT-4  | Email Gateway                  | zoppy-e2e-api | e-mail transacional até o registro do envio                             |
| INFRA-1 | MCP/OAuth                      | zoppy-e2e-api | OAuth com PKCE, lista as tools do MCP e chama uma                       |
| INFRA-2 | Canary                         | —             | fora do KPI: medida por smoke pós-deploy                                |
| INFRA-3 | Infra/Ops                      | —             | fora do KPI: medida por alarme de RDS e Redis                           |

## Onde ver o resultado

O dashboard [E2E — Jornadas Críticas](https://grafana.zoppy.com.br/d/e2e-jornadas-criticas) mostra o
nível de cada jornada, o teste que deu o nível e a run lida de cada suíte. O painel "Marcação que não
conta no KPI" lista tag de jornada inexistente e `@happy-path` que o guard não vigiou: é onde um teste
marcado que não sobe de nível aparece.
