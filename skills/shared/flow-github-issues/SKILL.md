---
name: flow-github-issues
description: Documenta trabalho no GitHub Issues da organização Zoppy-crm — epics, sub-issues por fase ou issues avulsas. Use quando o usuário quiser criar epics, sub-issues ou qualquer issue no GitHub a partir de PRDs, planos de fases ou descrições livres. Também use quando o usuário quiser preencher ou atualizar campos de uma issue no Project Board (horas gastas, start date, target date, priority, size, estimate). Ativado por "cria issue", "documenta no github", "cria epic", "sobe para o github", "cria as issues", "documenta as fases", "lança no github", "abre issue", "cria o epic", "preenche campos da issue", "atualiza horas gastas", "coloca a start date", "preenche o board", "atualiza o projeto".
---

# GitHub Issues — Zoppy-crm

Cria issues no GitHub da organização `Zoppy-crm` com hierarquia adequada (epic → sub-issues), labels padrão e vínculo ao project board.

## Templates oficiais — fonte da verdade

Os templates da org vivem em `Zoppy-crm/.github/.github/ISSUE_TEMPLATE/`. Sempre alinhar o body da issue com o template correspondente:

| Tipo de issue         | Template oficial            | Labels auto-aplicadas pelo form |
| --------------------- | --------------------------- | ------------------------------- |
| Epic de roadmap       | `epic-roadmap.yml`          | `roadmap`                       |
| Refinamento técnico   | `technical-refinement.yml`  | `refinement`, `work: feature`   |
| Bug report            | `bug-report.yml`            | (variam)                        |
| Demanda técnica       | `technical-demand.yml`      | (variam)                        |
| POC                   | `poc.yml`                   | (variam)                        |
| Card geral            | `general-card.yml`          | (variam)                        |
| Tech lead preparation | `tech-lead-preparation.yml` | (variam)                        |

**Importante:** quando criar issue via `gh issue create` (bypass do form), as labels auto-aplicadas pelo template **NÃO são adicionadas automaticamente** — passar manualmente via `--label`.

Pra ler um template antes de gerar o body, baixar via:

```bash
curl -s "https://raw.githubusercontent.com/Zoppy-crm/.github/development/.github/ISSUE_TEMPLATE/<template>.yml"
```

Ou ler do repo `Zoppy-crm/.github` clonado localmente quando disponível.

## Workflows automáticos — atenção crítica

O workflow `auto-label-refinement.yml` (em `Zoppy-crm/.github/.github/workflows/`) parseia o body procurando o heading `### Criado com auxílio de IA?` seguido por `Sim` e aplica a label `ai-assisted`. **MAS o workflow só roda em issues do próprio repo `.github`** — não propaga pra `zoppy-api`, `zoppy-FE`, etc. Pra issues criadas em outros repos:

1. **Sempre incluir a seção `### Criado com auxílio de IA?` + valor (Sim/Não) no body** — alinha com o template oficial e serve de doc.
2. **Aplicar label `ai-assisted` manualmente** via `gh issue edit <num> --add-label "ai-assisted"` quando a issue foi criada com auxílio de IA.

---

## Fase 1 — Identificar intenção e contexto

### 1.1 Detectar o modo de operação

Analise o que o usuário quer criar:

| Intenção detectada                                                 | Modo                                             |
| ------------------------------------------------------------------ | ------------------------------------------------ |
| PRD + plano com fases existem em `docs/`                           | **Estruturado** — epic pai + sub-issues por fase |
| Quer documentar qualquer outra coisa (feature, tarefa, bug, chore) | **Ad-hoc** — uma ou mais issues avulsas          |
| Quer apenas o epic vazio, sem sub-issues ainda                     | **Epic Simples**                                 |

### 1.2 Coletar informações obrigatórias

**Antes de executar qualquer `gh` command**, confirme as informações abaixo. Detecte pelo contexto sempre que possível — só pergunte o que não ficou claro:

| Informação           | Como obter                                                                                                                                                                                                                                                                      | Default         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| **Repositório**      | Detectar pela branch atual, nome do plano/PRD, menção explícita. Se ambíguo: perguntar                                                                                                                                                                                          | —               |
| **Epic label**       | Detectar pelo nome da feature, PRD ou menção no prompt. **Format real é `epic: <nome>` com espaço após `:`** (ex: `epic: envio-email`, `epic: chat-whatsapp`). Validar via `gh label list --repo <repo> \| grep "epic:"` antes de usar; se não existir, perguntar se pode criar | —               |
| **Tipo de trabalho** | Detectar pela natureza da tarefa                                                                                                                                                                                                                                                | `work: feature` |

**Repositórios disponíveis na organização `Zoppy-crm`:**

-   `zoppy-FE` — Frontend Angular
-   `zoppy-api` — Backend NestJS principal
-   `zoppy-workflow` — Motor de workflows
-   `zoppy-model` — Modelos de dados
-   `zoppy-admin-FE` — Painel administrativo
-   `ui-components` — Design system

Se o usuário mencionar outro repositório, use o nome informado.

> **Importante:** se `gh` não estiver autenticado, instrua o usuário a rodar `gh auth login` antes de continuar.

---

## Fase 2 — Coletar conteúdo

### Modo Estruturado (PRD + Plano → Epic + Sub-issues)

1. Procurar o PRD em `docs/prds/` — leia o arquivo
2. Procurar o plano geral em `docs/plans/` — leia o arquivo e extraia as fases
3. Para cada fase, verificar se existe plano detalhado (ex: `docs/plans/<feature>-fase-N.md` ou seção `## Fase N` no plano geral)

**O que cada issue vai conter:**

-   **Epic (issue pai):**

    -   Conteúdo completo do PRD embutido diretamente no body (não link — colar o markdown)
    -   Visão geral do plano de implementação
    -   Checklist das fases
    -   Critérios de aceite gerais

-   **Sub-issue por fase:**
    -   Título: `[Fase N] <título da fase>`
    -   Conteúdo completo do plano da fase embutido diretamente no body (não link — colar o markdown)
    -   Critérios de aceite da fase

> **Regra:** Nunca inserir links para arquivos `.md` do repositório. Sempre colar o conteúdo do arquivo diretamente no body da issue em markdown.

### Modo Ad-hoc

Use o que o usuário forneceu diretamente. Explore o código quando necessário para preencher o detalhamento técnico. Se o conteúdo estiver incompleto, pergunte apenas:

-   O que precisa ser feito? (se não claro)
-   Quais os critérios de aceite?

Não faça perguntas desnecessárias — se o usuário deu contexto suficiente, infira e confirme no rascunho.

---

## Fase 3 — Apresentar rascunho para aprovação

**Antes de executar qualquer `gh` command**, mostre o resumo do que será criado:

```
📋 Vou criar as seguintes issues em Zoppy-crm/<repo>:

Epic: "<título>"
Labels: roadmap | refinement | origin: master | work: feature | epic: <nome>

  Sub-issues:
  ├── [Fase 1] <título>     → Size <X>, P<N>, ~<estimate>
  ├── [Fase 2] <título>     → Size <X>, P<N>, ~<estimate>
  └── [Fase N] <título>     → Size <X>, P<N>, ~<estimate>

Cada sub-issue:
  - Labels: refinement | origin: master | work: feature | epic: <nome>
  - Body: conteúdo do .md correspondente (incluindo seção "### Criado com auxílio de IA?")
  - Vinculada ao epic via GraphQL addSubIssue
  - Adicionada ao Project Board #7 com Priority/Size/Estimate setados
  - Label `ai-assisted` aplicada manualmente após criação

Confirma? (ou ajuste o que quiser)
```

Para issues avulsas (Ad-hoc), mostrar apenas o título, repo e labels antes de criar.

**Só avance após confirmação do usuário.**

---

## Fase 4 — Criar as issues

### 4.1 Labels obrigatórias

**Sub-issues (refinements):** sempre 4 labels.

```bash
--label "refinement" --label "origin: master" --label "work: feature" --label "epic: <nome>"
```

Ajustar `work: feature` conforme o tipo:

-   Bug: `--label "work: fix"`
-   Chore/infra: `--label "work: chore"`

**Epic (parent):** as 4 acima + a label `roadmap` (que o template oficial `epic-roadmap.yml` aplicaria automaticamente, mas precisa ser passada manual quando criando via API).

```bash
--label "refinement" --label "origin: master" --label "work: feature" --label "epic: <nome>" --label "roadmap"
```

> **Format de label de epic:** sempre `epic: <nome>` com espaço após `:`. Validar via `gh label list --repo <repo> | grep "epic:"`.

### 4.2 Criar o Epic (issue pai)

Preferir `--body-file` quando o body é longo (PRDs costumam ter 200+ linhas — escapar em HEREDOC fica frágil):

```bash
EPIC_URL=$(gh issue create \
  --repo Zoppy-crm/<repo> \
  --title "<título do epic>" \
  --assignee @me \
  --label "refinement" \
  --label "origin: master" \
  --label "work: feature" \
  --label "epic: <nome>" \
  --label "roadmap" \
  --body-file <path/prd.md>)

echo "Epic criado: $EPIC_URL"
EPIC_NUMBER=$(echo "$EPIC_URL" | grep -o '[0-9]*$')
EPIC_NODE_ID=$(gh api "/repos/Zoppy-crm/<repo>/issues/$EPIC_NUMBER" --jq '.node_id')
```

### 4.3 Criar cada sub-issue (fase)

Para cada fase, execute:

```bash
SUB_URL=$(gh issue create \
  --repo Zoppy-crm/<repo> \
  --title "[Fase N] <título da fase>" \
  --assignee @me \
  --label "refinement" \
  --label "origin: master" \
  --label "work: feature" \
  --label "epic: <nome>" \
  --body-file <path/fase-N.md>)

echo "Sub-issue criada: $SUB_URL"
SUB_NUMBER=$(echo "$SUB_URL" | grep -o '[0-9]*$')
SUB_NODE_ID=$(gh api "/repos/Zoppy-crm/<repo>/issues/$SUB_NUMBER" --jq '.node_id')
```

> **O body do .md deve incluir a seção `### Criado com auxílio de IA?` seguida por `Sim` ou `Não`** — alinha com o template oficial `technical-refinement.yml`.

### 4.4 Vincular sub-issues ao epic

Usar a **GraphQL API** com `node_id` (não o número da issue):

```bash
# Buscar o node_id de cada issue
EPIC_NODE_ID=$(gh api "/repos/Zoppy-crm/<repo>/issues/$EPIC_NUMBER" --jq '.node_id')
SUB_NODE_ID=$(gh api "/repos/Zoppy-crm/<repo>/issues/$SUB_NUMBER" --jq '.node_id')

# Vincular sub-issue ao epic via GraphQL
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$EPIC_NODE_ID\", subIssueId: \"$SUB_NODE_ID\"}) {
    issue { number title }
    subIssue { number title }
  }
}"
```

> **Nota:** Usar `node_id` (não `id` numérico). A mutation `addSubIssue` exige os IDs no formato `I_...`.

### 4.5 Adicionar ao Project Board + setar campos obrigatórios

Após criar cada issue (epic e sub-issues), adicionar ao board e capturar o Item ID direto da resposta (mais rápido que `item-list` em projects grandes):

```bash
ITEM_ID=$(gh project item-add 7 --owner Zoppy-crm --url <issue-url> --format json | jq -r '.id')
```

**Imediatamente após adicionar**, setar os campos obrigatórios do board (Priority, Size, Estimate). Sem isso, o item pode ficar **invisível** por filtros ativos no board.

```bash
PROJECT_ID="PVT_kwDOCAubUc4BQdrV"

# Priority (single select) — usa gh project item-edit
gh project item-edit --project-id $PROJECT_ID --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k1Ns --single-select-option-id <priority_id>

# Size (single select) — usa gh project item-edit
gh project item-edit --project-id $PROJECT_ID --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k1Nw --single-select-option-id <size_id>

# Estimate (Number) — REQUER GraphQL (gh project item-edit não funciona pra Number)
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "'$PROJECT_ID'"
    itemId: "'$ITEM_ID'"
    fieldId: "PVTF_lADOCAubUc4BQdrVzg-k1N0"
    value: { number: <estimate> }
  }) { projectV2Item { id } }
}'
```

> **Aprendizado:** Issues no board sem Priority/Size/Estimate ficam ocultas quando há filtros ativos. Sempre preencher esses campos ao adicionar.

### 4.6 Aplicar label `ai-assisted` quando criado com auxílio de IA

O workflow `auto-label-refinement.yml` no `.github` repo só roda em issues do próprio `.github` repo — **não propaga**. Pra issues criadas em outros repos com auxílio de IA, aplicar a label manualmente:

```bash
gh issue edit <number> --repo Zoppy-crm/<repo> --add-label "ai-assisted"
```

---

## Fase 5 — Confirmar resultado

Ao final, exibir todas as URLs criadas:

```
✅ Issues criadas com sucesso em Zoppy-crm/<repo>!

Epic: <url-do-epic>

Sub-issues:
├── Fase 1: <url>
├── Fase 2: <url>
└── Fase N: <url>

Todas adicionadas ao Project Board #7.
```

---

## Fase 6 — Gerenciar issues existentes

### 6.0 Vincular sub-issue a epic existente

Quando o usuário quer criar sub-issues para um epic que **já existe** (não foi criado nesta sessão):

1. **Verificar assignee do epic** — se estiver vazio, setar com `gh issue edit <number> --repo Zoppy-crm/<repo> --add-assignee @me`
2. **Verificar se o epic está no board** — buscar no project item-list. Se não estiver, adicionar com `gh project item-add`
3. **Setar campos obrigatórios do epic no board** (Priority, Size, Estimate) — sem isso o epic fica invisível por filtros

> **Aprendizado:** Issues sem assignee ou sem campos obrigatórios (Priority/Size/Estimate) ficam ocultas no board quando há filtros ativos. Sempre verificar e preencher ao interagir com issues existentes.

### 6.1 Mover issue de status (In Progress, To Do, etc)

Quando o usuário pedir para mover uma issue de status:

1. **Buscar o Item ID** no project (seção 7.2)
2. **Garantir que campos obrigatórios estão preenchidos** — verificar se Priority, Size e Estimate já têm valor. Se não, setar antes de mover status
3. **Garantir que a issue tem assignee** — se não tiver, setar com `gh issue edit`
4. **Mover o status** usando o field ID e option ID da tabela de referência (seção 7.5)

---

## Fase 7 — Mover issue para Done

Quando o usuário pedir para marcar uma issue como "Done" (ex: "marca como done", "fecha essa issue", "coloca como done", "finaliza a issue"), os seguintes campos obrigatórios do Project Board #7 devem ser preenchidos **antes** de mover o status para Done. Caso contrário, um bot automático reverterá para "In progress".

### 7.0 Identificar a issue e o repositório a partir do handoff

**Antes de perguntar qualquer coisa ao usuário**, buscar o contexto no handoff:

1. Localizar o `handoff.md` do projeto (geralmente `docs/plans/handoff.md` ou `docs/<feature>/plans/handoff.md`)
2. Ler a seção **"Registro de branches por fase"** — ela contém a branch de cada fase concluída
3. Ler a seção **"Branch e referências"** — contém o repositório, branch atual e último commit
4. Com o repositório identificado, buscar a issue da fase no GitHub:

```bash
# Buscar a issue pelo título da fase
gh issue list --repo Zoppy-crm/<repo> --search "[Fase N]" --state open --json number,title
```

Se o handoff não tiver as informações necessárias, perguntar ao usuário: "Qual o número da issue e o repositório?"

### 7.1 Perguntar ao usuário os valores

Antes de preencher, pergunte ao usuário:

| Campo            | Tipo          | Opções                    | Pergunta                       |
| ---------------- | ------------- | ------------------------- | ------------------------------ |
| **Priority**     | Single Select | `P0`, `P1`, `P2`          | Qual a prioridade?             |
| **Size**         | Single Select | `XS`, `S`, `M`, `L`, `XL` | Qual o tamanho?                |
| **Estimate**     | Number        | Horas estimadas           | Quantas horas foram estimadas? |
| **Horas Gastas** | Number        | Horas reais               | Quantas horas foram gastas?    |
| **Start date**   | Date          | `YYYY-MM-DD`              | Qual a data de início?         |
| **Target date**  | Date          | `YYYY-MM-DD`              | Qual a data de entrega?        |

Inferir pelo contexto quando possível (ex: se a issue é uma fase pequena, sugira `S` e `P1`; se foi concluída hoje, start date e target date = hoje). Confirme antes de aplicar.

### 7.2 Obter o Item ID no project

```bash
ITEM_ID=$(gh project item-list 7 --owner Zoppy-crm --format json --limit 500 \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data.get('items', []):
    if item.get('content', {}).get('number') == <ISSUE_NUMBER> and item.get('content', {}).get('repository') == 'Zoppy-crm/<repo>':
        print(item['id'])
        break
")
```

### 7.3 Preencher os campos obrigatórios

**Priority** (Single Select):

```bash
# Opções: P0=79628723, P1=0a877460, P2=da944a9c
gh project item-edit \
  --project-id PVT_kwDOCAubUc4BQdrV \
  --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k1Ns \
  --single-select-option-id <option_id>
```

**Size** (Single Select):

```bash
# Opções: XS=6c6483d2, S=f784b110, M=7515a9f1, L=817d0097, XL=db339eb2
gh project item-edit \
  --project-id PVT_kwDOCAubUc4BQdrV \
  --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k1Nw \
  --single-select-option-id <option_id>
```

**Estimate** (Number):

```bash
gh project item-edit \
  --project-id PVT_kwDOCAubUc4BQdrV \
  --id $ITEM_ID \
  --field-id PVTF_lADOCAubUc4BQdrVzg-k1N0 \
  --number <valor>
```

**Horas Gastas** (Number — usar GraphQL):

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCAubUc4BQdrV"
    itemId: "'$ITEM_ID'"
    fieldId: "PVTF_lADOCAubUc4BQdrVzg-opYQ"
    value: { number: <valor> }
  }) { projectV2Item { id } }
}'
```

**Start date** (Date — usar GraphQL):

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCAubUc4BQdrV"
    itemId: "'$ITEM_ID'"
    fieldId: "PVTF_lADOCAubUc4BQdrVzg-k1N4"
    value: { date: "YYYY-MM-DD" }
  }) { projectV2Item { id } }
}'
```

**Target date** (Date — usar GraphQL):

```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOCAubUc4BQdrV"
    itemId: "'$ITEM_ID'"
    fieldId: "PVTF_lADOCAubUc4BQdrVzg-k1N8"
    value: { date: "YYYY-MM-DD" }
  }) { projectV2Item { id } }
}'
```

> **Importante:** Campos do tipo `DATE` e `NUMBER` **não funcionam** com `gh project item-edit`. Sempre usar a mutation GraphQL `updateProjectV2ItemFieldValue` para esses tipos.

### 7.4 Mover para Done

Após preencher todos os campos obrigatórios:

```bash
# Status Done = 2c2f548e
gh project item-edit \
  --project-id PVT_kwDOCAubUc4BQdrV \
  --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k0-w \
  --single-select-option-id 2c2f548e
```

### 7.5 Referência rápida de IDs

| Campo        | Field ID                         | Tipo         | Como atualizar                          |
| ------------ | -------------------------------- | ------------ | --------------------------------------- |
| Status       | `PVTSSF_lADOCAubUc4BQdrVzg-k0-w` | SingleSelect | `gh project item-edit`                  |
| Priority     | `PVTSSF_lADOCAubUc4BQdrVzg-k1Ns` | SingleSelect | `gh project item-edit`                  |
| Size         | `PVTSSF_lADOCAubUc4BQdrVzg-k1Nw` | SingleSelect | `gh project item-edit`                  |
| Estimate     | `PVTF_lADOCAubUc4BQdrVzg-k1N0`   | Number       | GraphQL `updateProjectV2ItemFieldValue` |
| Horas Gastas | `PVTF_lADOCAubUc4BQdrVzg-opYQ`   | Number       | GraphQL `updateProjectV2ItemFieldValue` |
| Start date   | `PVTF_lADOCAubUc4BQdrVzg-k1N4`   | Date         | GraphQL `updateProjectV2ItemFieldValue` |
| Target date  | `PVTF_lADOCAubUc4BQdrVzg-k1N8`   | Date         | GraphQL `updateProjectV2ItemFieldValue` |

> **Regra crítica:** Campos do tipo `NUMBER` e `DATE` **não funcionam com `gh project item-edit`**. Sempre usar a mutation GraphQL `updateProjectV2ItemFieldValue` com `value: { number: X }` ou `value: { date: "YYYY-MM-DD" }` respectivamente.

| Status                  | Option ID  |
| ----------------------- | ---------- |
| Backlog                 | `7de56815` |
| Discovery               | `bc261486` |
| Em prototipacao         | `23f51f2a` |
| Pronto pra Tech         | `d2c63592` |
| Handoff Realizado       | `40fd64d4` |
| Refinamento Concluido   | `1d8def79` |
| Blocked                 | `8ae79bc2` |
| To Do                   | `8042c61b` |
| Bugs                    | `36b7ad33` |
| In progress             | `46203a32` |
| Dev Testing             | `cfe4dca6` |
| PR review               | `5a0dbc82` |
| In Product Review       | `bb7c9294` |
| Product Reviewed        | `aa507816` |
| Waiting Staging         | `487d8b23` |
| In Staging              | `b9c9d2bb` |
| In Mirror               | `a62e17eb` |
| Deploying               | `e678890f` |
| Done                    | `2c2f548e` |
| Rollout - Fase 1        | `3fc64093` |
| Rollout - Fase 2        | `d92fb0c3` |
| Rollout Finalizado      | `1fbd5f01` |
| Amplamente Disponivel   | `41df697e` |

| Priority | Option ID  |
| -------- | ---------- |
| P0       | `79628723` |
| P1       | `0a877460` |
| P2       | `da944a9c` |

| Size | Option ID  |
| ---- | ---------- |
| XS   | `6c6483d2` |
| S    | `f784b110` |
| M    | `7515a9f1` |
| L    | `817d0097` |
| XL   | `db339eb2` |

---

## Regras

-   **Nunca criar issues sem confirmação** do rascunho pelo usuário
-   **Sempre `--assignee @me`** — nunca deixar sem atribuição (a não ser que o usuário peça explicitamente sem assignee)
-   **Sempre verificar assignee em epics existentes** — ao vincular sub-issues a um epic pré-existente, checar se o epic tem assignee e setar se não tiver
-   **Sempre 4 labels** obrigatórias em refinements: `refinement`, `origin: master`, `work: feature` (ou fix/chore), `epic: <nome>` (com espaço após `:`)
-   **Para epics, adicionar `roadmap`** como 5ª label (auto-aplicada pelo template oficial mas não quando criado via API)
-   **Para issues criadas com auxílio de IA, aplicar `ai-assisted` manualmente** — o workflow `auto-label-refinement.yml` não propaga pra outros repos
-   **Sempre incluir seção `### Criado com auxílio de IA?` no body** — alinha com o template oficial `technical-refinement.yml`
-   **Sempre capturar a URL** de cada issue criada para vincular sub-issues e adicionar ao board
-   **Sempre setar campos do board ao adicionar** — Priority, Size e Estimate devem ser preenchidos imediatamente ao adicionar issue ao Project Board. Issues sem esses campos ficam invisíveis quando há filtros ativos
-   **Sempre verificar campos antes de mover status** — ao mover para In Progress/Done, garantir que Priority, Size, Estimate e assignee estão preenchidos
-   **Usar GraphQL para vincular sub-issues** — `addSubIssue` mutation com `node_id`, não REST API
-   **Usar GraphQL para campos Number e Date no board** — `gh project item-edit` não funciona pra esses tipos; só single-select.
-   **Preferir `--body-file` sobre `--body` HEREDOC** — quando o body é longo (> 50 linhas), evita escape hell.
-   **Capturar Item ID via `--format json | jq -r '.id'` no `item-add`** — mais rápido que listar todos os items do board.
-   **Não fazer perguntas desnecessárias** — inferir pelo contexto e confirmar no rascunho
-   **Repositório pode mudar por sub-issue** — para milestones cross-repo, pergunte ao dev em qual repo cada sub-issue deve ficar
