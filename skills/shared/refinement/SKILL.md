---
name: refinement
description: Cria um card de refinamento técnico no GitHub Issues seguindo o template da organização Zoppy, ou posta um retorno de solução em issues de bug já resolvidas. Use esta skill sempre que o usuário quiser criar um refinamento, abrir uma issue de feature, documentar uma tarefa técnica, criar um card no GitHub, descrever o escopo de uma nova funcionalidade, ou comentar a solução de um bug num card existente. Acione também em frases como "abre uma issue", "cria o refinamento de X", "vamos refinar", "monta o card", "cria a issue no GitHub", "coloca o retorno de solução", "comenta a solução no card".
---

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

## Fechamento de bug — dois artefatos

Ao resolver um bug, preencha **sempre os dois** artefatos com públicos e linguagens diferentes:

| Artefato              | Onde vai                                                      | Público                   | Linguagem                                              |
| --------------------- | ------------------------------------------------------------- | ------------------------- | ------------------------------------------------------ |
| Comentário técnico    | Comentário na issue (`gh issue comment`)                      | Devs, reviewers           | Técnica — arquivos, classes, regras, resultado de testes |
| Retorno de Solução    | Field do project `Zoppy Engineering` (preenchido via `gh project item-edit`) | Cliente / CSM / produto   | Alto nível, sem jargão — sintoma → causa → correção    |

Se o usuário pedir "coloca o retorno de solução no card", ele está falando do **field do project** (não do comment). Se pedir "comenta a solução na issue" ou "posta o resumo técnico", é o **comment**. Na dúvida, preencha os dois.

---

### 1) Comentário técnico na issue

Público: devs. Serve pra registro histórico da causa raiz, da correção e da cobertura de testes.

#### Template

```markdown
## Solução

### Causa raiz

<!-- 1-3 frases: o que estava errado e por que o sintoma relatado acontecia. Cite nomes reais (arquivo, classe, variável, tela). -->

### Correção

<!-- O que foi alterado. Cite o arquivo principal e a regra aplicada. Se houver precedência/ordem de fallback, liste numerado. -->

### Testes

<!-- Cenários de teste adicionados + resultado da suíte (ex.: "13/13 passando"). -->
```

#### Exemplo — issue #6270

```markdown
## Solução

### Causa raiz
O payload do segmento chegava com o array de sub-regras em **camelCase** (`segmentSubRules`) na tela de Segmentos e em **PascalCase** (`SegmentSubRules`) na tela de Campanhas. O `SegmentRuleResolver` só olhava a versão camelCase, então segmentos abertos via fluxo de Campanha (ex.: filtro de cupom que depende das sub-regras de data) perdiam essas condições e retornavam lista vazia.

### Correção
Normalização das duas variantes no `segment-rule.resolver.ts` com precedência:
1. Usa `SegmentSubRules` (PascalCase) se for array não-vazio
2. Senão, usa `segmentSubRules` (camelCase) se for array não-vazio
3. Senão, array vazio

Extraído para o método privado `normalizeSegmentSubRules`.

### Testes
5 cenários cobrindo: PascalCase preenchido tem prioridade, camelCase usado quando PascalCase ausente/vazio, fallback `[]` quando ambos ausentes/vazios. Suíte total: 13/13 passando.
```

#### Como postar

```bash
gh issue comment <numero> --repo Zoppy-crm/<repo> --body "$(cat <<'EOF'
<conteúdo do comentário técnico>
EOF
)"
```

#### Diretrizes

-   **Causa raiz** descreve o "porquê", não só o "o quê" — conecte o sintoma reportado à falha técnica
-   Cite arquivos reais (`src/...`), nomes de métodos e classes
-   Mencione quantos testes foram adicionados e se a suíte passa
-   Não copie o diff inteiro — explique, não re-mostre o código

---

### 2) Retorno de Solução (field do GitHub Project)

Público: cliente / CSM / produto. É texto **não-técnico**, em alto nível, que o dev/PM vai repassar ao cliente que abriu o ticket.

#### Como escrever

-   **Linguagem de negócio, não técnica** — fale em "tela de Segmentos", "filtro de cupom", "campanha"; nunca em classes/arquivos/variáveis
-   **3-5 frases corridas** em parágrafo único (não use bullets)
-   **Comece pelo sintoma do cliente** (o que acontecia de errado)
-   **Explique a causa de forma metafórica** ("formato diferente", "rota diferente", "cálculo antigo") em vez de termos técnicos
-   **Termine pelo resultado prático** ("agora funciona em qualquer tela", "a contagem volta a refletir…")
-   Sem código, sem nomes de arquivo, sem contagem de testes

#### Exemplo — issue #6270

> O problema acontecia quando uma campanha era criada a partir de um segmento que usava filtro de cupom. As informações complementares do segmento (como datas) chegavam em formatos diferentes dependendo da tela: na tela de Segmentos vinham de um jeito e na tela de Campanhas de outro. O sistema só reconhecia o formato da tela de Segmentos, então, ao abrir a campanha, essas informações eram ignoradas e o segmento aparecia como vazio. A correção passou a aceitar os dois formatos, garantindo que a contagem e o disparo da campanha funcionem igual em qualquer tela.

#### Como preencher via CLI

1. Pegue o **ID do item no project** a partir do número da issue:

    ```bash
    gh api graphql -f query='query { repository(owner:"Zoppy-crm",name:"<repo>"){ issue(number:<numero>){ projectItems(first:10){ nodes { id project { number title } } } } } }'
    ```

    Use o `id` do node cujo `project.number` é `7` (Zoppy Engineering).

2. IDs fixos do project `Zoppy Engineering`:

    - Project ID: `PVT_kwDOCAubUc4BQdrV`
    - Field ID "Retorno de Solução": `PVTF_lADOCAubUc4BQdrVzg-wo9s`

3. Atualize o field:

    ```bash
    gh project item-edit \
      --id <ITEM_ID> \
      --project-id PVT_kwDOCAubUc4BQdrV \
      --field-id PVTF_lADOCAubUc4BQdrVzg-wo9s \
      --text "<texto do retorno de solução>"
    ```

4. (Opcional) Verificar:

    ```bash
    gh api graphql -f query='query { node(id:"<ITEM_ID>"){ ... on ProjectV2Item { fieldValueByName(name:"Retorno de Solução"){ ... on ProjectV2ItemFieldTextValue { text } } } } }'
    ```

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
