---
name: flow-github-issues
description: Documenta trabalho no GitHub Issues da organização Zoppy-crm — epics, sub-issues por fase ou issues avulsas. Use quando o usuário quiser criar epics, sub-issues ou qualquer issue no GitHub a partir de PRDs, planos de fases ou descrições livres. Também use quando o usuário quiser preencher ou atualizar campos de uma issue no Project Board (horas gastas, start date, target date, priority, size, estimate). Ativado por "cria issue", "documenta no github", "cria epic", "sobe para o github", "cria as issues", "documenta as fases", "lança no github", "abre issue", "cria o epic", "preenche campos da issue", "atualiza horas gastas", "coloca a start date", "preenche o board", "atualiza o projeto".
---

# GitHub Issues — Zoppy-crm

Cria issues no GitHub da organização `Zoppy-crm` com hierarquia adequada (epic → sub-issues), labels padrão e vínculo ao project board.

---

## Fase 1 — Identificar intenção e contexto

### 1.1 Detectar o modo de operação

Analise o que o usuário quer criar:

| Intenção detectada | Modo |
|--------------------|------|
| PRD + plano com fases existem em `docs/` | **Estruturado** — epic pai + sub-issues por fase |
| Quer documentar qualquer outra coisa (feature, tarefa, bug, chore) | **Ad-hoc** — uma ou mais issues avulsas |
| Quer apenas o epic vazio, sem sub-issues ainda | **Epic Simples** |

### 1.2 Coletar informações obrigatórias

**Antes de executar qualquer `gh` command**, confirme as informações abaixo. Detecte pelo contexto sempre que possível — só pergunte o que não ficou claro:

| Informação | Como obter | Default |
|------------|------------|---------|
| **Repositório** | Detectar pela branch atual, nome do plano/PRD, menção explícita. Se ambíguo: perguntar | — |
| **Epic label** | Detectar pelo nome da feature, PRD ou menção no prompt. Se ambíguo: perguntar (ex: `epic:whatsapp-v2`) | — |
| **Tipo de trabalho** | Detectar pela natureza da tarefa | `work: feature` |

**Repositórios disponíveis na organização `Zoppy-crm`:**
- `zoppy-FE` — Frontend Angular
- `zoppy-api` — Backend NestJS principal
- `zoppy-workflow` — Motor de workflows
- `zoppy-model` — Modelos de dados
- `zoppy-admin-FE` — Painel administrativo
- `ui-components` — Design system

Se o usuário mencionar outro repositório, use o nome informado.

> **Importante:** se `gh` não estiver autenticado, instrua o usuário a rodar `gh auth login` antes de continuar.

---

## Fase 2 — Coletar conteúdo

### Modo Estruturado (PRD + Plano → Epic + Sub-issues)

1. Procurar o PRD em `docs/prds/` — leia o arquivo
2. Procurar o plano geral em `docs/plans/` — leia o arquivo e extraia as fases
3. Para cada fase, verificar se existe plano detalhado (ex: `docs/plans/<feature>-fase-N.md` ou seção `## Fase N` no plano geral)

**O que cada issue vai conter:**

- **Epic (issue pai):**
  - Conteúdo completo do PRD embutido diretamente no body (não link — colar o markdown)
  - Visão geral do plano de implementação
  - Checklist das fases
  - Critérios de aceite gerais

- **Sub-issue por fase:**
  - Título: `[Fase N] <título da fase>`
  - Conteúdo completo do plano da fase embutido diretamente no body (não link — colar o markdown)
  - Critérios de aceite da fase

> **Regra:** Nunca inserir links para arquivos `.md` do repositório. Sempre colar o conteúdo do arquivo diretamente no body da issue em markdown.

### Modo Ad-hoc

Use o que o usuário forneceu diretamente. Explore o código quando necessário para preencher o detalhamento técnico. Se o conteúdo estiver incompleto, pergunte apenas:

- O que precisa ser feito? (se não claro)
- Quais os critérios de aceite?

Não faça perguntas desnecessárias — se o usuário deu contexto suficiente, infira e confirme no rascunho.

---

## Fase 3 — Apresentar rascunho para aprovação

**Antes de executar qualquer `gh` command**, mostre o resumo do que será criado:

```
📋 Vou criar as seguintes issues em Zoppy-crm/<repo>:

Epic: "<título>"
Labels: refinement | origin: master | work: feature | epic:<nome>

  Sub-issues:
  ├── [Fase 1] <título>
  ├── [Fase 2] <título>
  └── [Fase N] <título>

Confirma? (ou ajuste o que quiser)
```

Para issues avulsas (Ad-hoc), mostrar apenas o título, repo e labels antes de criar.

**Só avance após confirmação do usuário.**

---

## Fase 4 — Criar as issues

### 4.1 Labels obrigatórias (sempre incluir em toda issue)

```bash
--label "refinement" --label "origin: master" --label "work: feature" --label "epic:<nome>"
```

Ajustar `work: feature` conforme o tipo:
- Bug: `--label "work: fix"`
- Chore/infra: `--label "work: chore"`

### 4.2 Criar o Epic (issue pai)

```bash
EPIC_URL=$(gh issue create \
  --repo Zoppy-crm/<repo> \
  --title "<título do epic>" \
  --assignee @me \
  --label "refinement" \
  --label "origin: master" \
  --label "work: feature" \
  --label "epic:<nome>" \
  --body "$(cat <<'EOF'
<conteúdo do epic>
EOF
)")

echo "Epic criado: $EPIC_URL"
EPIC_NUMBER=$(echo "$EPIC_URL" | grep -o '[0-9]*$')
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
  --label "epic:<nome>" \
  --body "$(cat <<'EOF'
<conteúdo da fase>
EOF
)")

echo "Sub-issue criada: $SUB_URL"
SUB_NUMBER=$(echo "$SUB_URL" | grep -o '[0-9]*$')
```

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

Após criar cada issue (epic e sub-issues):

```bash
gh project item-add 7 --owner Zoppy-crm --url <issue-url>
```

**Imediatamente após adicionar**, setar os campos obrigatórios do board (Priority, Size, Estimate). Sem isso, o item pode ficar **invisível** por filtros ativos no board.

```bash
# Buscar o Item ID recém-adicionado
ITEM_ID=$(gh project item-list 7 --owner Zoppy-crm --format json --limit 1000 \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data.get('items', []):
    c = item.get('content', {})
    if c.get('number') == <ISSUE_NUMBER> and '<repo>' in c.get('repository', ''):
        print(item['id'])
        break
")

# Setar Priority, Size e Estimate (ver IDs na seção 6.5)
gh project item-edit --project-id PVT_kwDOCAubUc4BQdrV --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k1Ns --single-select-option-id <priority_id>
gh project item-edit --project-id PVT_kwDOCAubUc4BQdrV --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k1Nw --single-select-option-id <size_id>
gh project item-edit --project-id PVT_kwDOCAubUc4BQdrV --id $ITEM_ID \
  --field-id PVTF_lADOCAubUc4BQdrVzg-k1N0 --number <estimate_hours>
```

> **Aprendizado:** Issues no board sem Priority/Size/Estimate ficam ocultas quando há filtros ativos. Sempre preencher esses campos ao adicionar.

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

| Campo | Tipo | Opções | Pergunta |
|-------|------|--------|----------|
| **Priority** | Single Select | `P0`, `P1`, `P2` | Qual a prioridade? |
| **Size** | Single Select | `XS`, `S`, `M`, `L`, `XL` | Qual o tamanho? |
| **Estimate** | Number | Horas estimadas | Quantas horas foram estimadas? |
| **Horas Gastas** | Number | Horas reais | Quantas horas foram gastas? |
| **Start date** | Date | `YYYY-MM-DD` | Qual a data de início? |
| **Target date** | Date | `YYYY-MM-DD` | Qual a data de entrega? |

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
# Status Done = 98236657
gh project item-edit \
  --project-id PVT_kwDOCAubUc4BQdrV \
  --id $ITEM_ID \
  --field-id PVTSSF_lADOCAubUc4BQdrVzg-k0-w \
  --single-select-option-id 98236657
```

### 7.5 Referência rápida de IDs

| Campo | Field ID | Tipo | Como atualizar |
|-------|----------|------|----------------|
| Status | `PVTSSF_lADOCAubUc4BQdrVzg-k0-w` | SingleSelect | `gh project item-edit` |
| Priority | `PVTSSF_lADOCAubUc4BQdrVzg-k1Ns` | SingleSelect | `gh project item-edit` |
| Size | `PVTSSF_lADOCAubUc4BQdrVzg-k1Nw` | SingleSelect | `gh project item-edit` |
| Estimate | `PVTF_lADOCAubUc4BQdrVzg-k1N0` | Number | GraphQL `updateProjectV2ItemFieldValue` |
| Horas Gastas | `PVTF_lADOCAubUc4BQdrVzg-opYQ` | Number | GraphQL `updateProjectV2ItemFieldValue` |
| Start date | `PVTF_lADOCAubUc4BQdrVzg-k1N4` | Date | GraphQL `updateProjectV2ItemFieldValue` |
| Target date | `PVTF_lADOCAubUc4BQdrVzg-k1N8` | Date | GraphQL `updateProjectV2ItemFieldValue` |

> **Regra crítica:** Campos do tipo `NUMBER` e `DATE` **não funcionam com `gh project item-edit`**. Sempre usar a mutation GraphQL `updateProjectV2ItemFieldValue` com `value: { number: X }` ou `value: { date: "YYYY-MM-DD" }` respectivamente.

| Status | Option ID |
|--------|-----------|
| Done | `98236657` |
| In progress | `47fc9ee4` |
| To Do | `61e4505c` |
| Backlog | `f75ad846` |

| Priority | Option ID |
|----------|-----------|
| P0 | `79628723` |
| P1 | `0a877460` |
| P2 | `da944a9c` |

| Size | Option ID |
|------|-----------|
| XS | `6c6483d2` |
| S | `f784b110` |
| M | `7515a9f1` |
| L | `817d0097` |
| XL | `db339eb2` |

---

## Regras

- **Nunca criar issues sem confirmação** do rascunho pelo usuário
- **Sempre `--assignee @me`** — nunca deixar sem atribuição
- **Sempre verificar assignee em epics existentes** — ao vincular sub-issues a um epic pré-existente, checar se o epic tem assignee e setar se não tiver
- **Sempre 4 labels** obrigatórias: `refinement`, `origin: master`, `work: feature` (ou fix/chore), `epic:<nome>`
- **Sempre capturar a URL** de cada issue criada para vincular sub-issues e adicionar ao board
- **Sempre setar campos do board ao adicionar** — Priority, Size e Estimate devem ser preenchidos imediatamente ao adicionar issue ao Project Board. Issues sem esses campos ficam invisíveis quando há filtros ativos
- **Sempre verificar campos antes de mover status** — ao mover para In Progress/Done, garantir que Priority, Size, Estimate e assignee estão preenchidos
- **Usar GraphQL para vincular sub-issues** — `addSubIssue` mutation com `node_id`, não REST API
- **Não fazer perguntas desnecessárias** — inferir pelo contexto e confirmar no rascunho
- **Repositório pode mudar por sub-issue** — para milestones cross-repo, pergunte ao dev em qual repo cada sub-issue deve ficar
