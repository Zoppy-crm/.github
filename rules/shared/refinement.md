# Refinamento Técnico

Cria um card de refinamento técnico no GitHub Issues seguindo o template da organização Zoppy.

## Instruções

O usuário vai descrever a feature ou tarefa. Você deve:

1. **Entender o contexto** — pergunte o que for necessário antes de gerar o card
2. **Explorar o código** — leia os arquivos relevantes para fundamentar o detalhamento técnico
3. **Gerar o card** — preencha TODOS os campos do template abaixo com base no que descobriu
4. **Criar a issue** — use `gh issue create` no repositório correto

## Template

O card deve ser criado com o seguinte formato no body (GitHub-flavored markdown):

```markdown
### Resumo da Solução

<!-- Cenário atual. Qual o problema? Ponto de partida. -->

### Objetivo

<!-- Como o problema será resolvido. Ponto de chegada. -->

### Critérios de Aceite

-   [ ] Critério 1
-   [ ] Critério 2
-   [ ] Critério 3

### Layout

<!-- Links do Figma ou imagens. "N/A" se não aplicável. -->

### Detalhamento Técnico

## **Arquivos/Módulos impactados:**

## **Endpoints novos/alterados:**

## **Banco de dados:**

## **Dependências externas:**

### Serviços Afetados

<!-- Ex: zoppy-api (API/PVT/WORKER), zoppy-FE, shared packages (@Zoppy-crm/models, etc.) -->

### Migrations

<!-- Nome do arquivo, tipo de operação, descrição do impacto. "N/A" se não aplicável. -->

### Infraestrutura

<!-- Buckets S3, Redis, filas BullMQ, env vars, IAM. "N/A" se não aplicável. -->

### Permissões de Endpoints

| Rota | Método | Guards | Níveis de acesso |
| ---- | ------ | ------ | ---------------- |

<!-- Preencher para endpoints novos ou alterados -->

### Jobs de Correção de Dados Retroativos

<!-- Origem, lógica, critério, estratégia de execução. "N/A" se não aplicável. -->

### Monitoramento e Observabilidade

<!-- Métricas, alertas, dashboards, logs estruturados. "N/A" se não aplicável. -->

### Feature Flag

<!-- Nome da feature flag ou "N/A". -->

### Estratégia de Testes

<!-- IMPORTANTE: pense em cada tipo de teste que faz sentido para esta feature -->

**Testes unitários (zoppy-api — Jest):**

## <!-- Domain/Application specs. Quais comportamentos precisam de teste? -->

**Testes de integração (zoppy-api — Jest + supertest):**

## <!-- Controller specs. Quais endpoints precisam de teste de contrato HTTP? -->

**Testes E2E de API (zoppy-e2e-api — Playwright):**

<!-- Para endpoints NÃO consumidos pelo frontend: Partners API, webhooks, APIs internas (PVT), segment.
     Listar os endpoints e cenários que devem ser cobertos. -->

-   **Testes E2E de Frontend (zoppy-FE — Cypress/Playwright):**
    <!-- Para fluxos consumidos pelo frontend: telas, formulários, fluxos de navegação.
         Listar as telas e fluxos que devem ser cobertos. -->

-

### Roteiro de Teste (QA)

## **Telas:**

## **Rotinas:**

## **Locais de impacto:**

## **Resultado Esperado:**

### Collections E2E alteradas/adicionadas

<!-- Nome das collections ou "N/A". -->
```

## Criando a issue

Use o comando `gh issue create` com:

-   `--repo Zoppy-crm/<repo>` — pergunte ao desenvolvedor em qual repositório a issue deve ser criada se não ficar claro pelo contexto
-   `--title` conciso e descritivo
-   `--assignee @me` — sempre atribuir ao usuário autenticado no gh
-   `--label "refinement" --label "origin: master" --label "work: feature"` (sempre incluir essas 3 labels)
-   Adicionar também a **label do epic** relacionado (pergunte ao usuário se não ficar claro, ex: `epic:partners-migration`, `epic:whatsapp-v2`)
-   `--body` com o conteúdo preenchido acima (usar HEREDOC)

Após criar a issue, **adicione ao projeto do time**:

```bash
gh project item-add 7 --owner Zoppy-crm --url https://github.com/Zoppy-crm/<repo>/issues/<number>
```

### Milestones complexas (múltiplos cards)

Quando a tarefa é grande demais pra um único card (milestone complexa), crie uma estrutura hierárquica:

1. **Card base da milestone** — issue principal com o template completo, visão macro do objetivo e critérios de aceite gerais
2. **Sub-issues** — uma issue por tarefa, cada uma seguindo o mesmo template de refinamento técnico, com escopo menor e critérios de aceite específicos

Para criar sub-issues, use `gh issue create` com `--body` contendo o template completo, e depois vincule como sub-issue do card base:

```bash
# Criar o card base da milestone (normalmente no zoppy-api)
gh issue create --repo Zoppy-crm/zoppy-api --title "Milestone: <nome>" \
  --label "refinement" --label "origin: master" --label "work: feature" --label "<epic-label>" --body "..."
gh project item-add 7 --owner Zoppy-crm --url https://github.com/Zoppy-crm/zoppy-api/issues/<card-base-number>

# Criar sub-issues (pergunte ao dev em qual repo cada uma deve ficar)
gh issue create --repo Zoppy-crm/<repo-da-sub-issue> --title "<tarefa específica>" \
  --label "refinement" --label "origin: master" --label "work: feature" --label "<epic-label>" --body "..."
gh project item-add 7 --owner Zoppy-crm --url https://github.com/Zoppy-crm/<repo-da-sub-issue>/issues/<sub-issue-number>

# Vincular sub-issue ao card base
gh issue edit <card-base-number> --add-sub-issue <sub-issue-number> --repo Zoppy-crm/zoppy-api
```

**Critérios pra decidir se é milestone:**

-   Envolve mais de 2 serviços afetados
-   Tem mais de 5 critérios de aceite independentes
-   O prazo de execução é maior que 1 sprint
-   Tem etapas que podem ser feitas em paralelo por devs diferentes

## Diretrizes de preenchimento

-   **Resumo**: descreva o estado atual, não a solução
-   **Objetivo**: descreva o estado desejado, não os passos
-   **Critérios de aceite**: mensuráveis e verificáveis, sem ambiguidade
-   **Detalhamento técnico**: inclua paths reais de arquivos que serão modificados — explore o código antes de preencher
-   **Serviços afetados**: liste todos os repos/packages que precisam de mudança
-   **Migrations**: se houver, especifique o tipo (create table, add column, etc.)
-   **Infraestrutura**: seja específico (nome da fila, nome do bucket, nome da env var)
-   **Permissões**: use os Guards reais do codebase (RoleGuard, FeatureGuard, BlockFreeTierGuard)
-   **Roteiro de teste (QA)**: pense como QA — descreva os passos pra validar cada critério de aceite
-   Se um campo não é aplicável, escreva "N/A" — não deixe em branco

## Estratégia de testes — como decidir

A seção "Estratégia de Testes" é uma das mais importantes do card. Interaja com o desenvolvedor para preencher cada tipo:

**Testes unitários (Jest)**: para lógica de negócio pura no domain/application. Pergunte: "Quais regras de negócio essa feature introduz ou altera?"

**Testes de integração (Jest + supertest)**: para o contrato HTTP do controller. Pergunte: "Quais endpoints são novos ou tiveram comportamento alterado? Quais status codes precisam de cobertura?"

**Testes E2E de API (zoppy-e2e-api)**: para endpoints que **não são consumidos pelo frontend**. Isso inclui:

-   Partners API (ExternalToken auth)
-   Webhooks públicos (WhatsApp, Wake Commerce, PDV, etc.)
-   APIs internas/PVT (serviço a serviço)
-   Endpoints de segment/analytics

Pergunte: "Esse endpoint é chamado pelo frontend ou por um sistema externo/parceiro? Se for externo, precisa de e2e de API."

**Testes E2E de Frontend (zoppy-FE)**: para fluxos que o usuário final interage via browser. Pergunte: "Existe tela nova ou fluxo alterado no frontend por causa dessa feature?"

O objetivo é que, ao final do refinamento, o card tenha uma visão clara de **o que testar, onde testar, e por que testar** em cada camada.
