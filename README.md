# .github — Zoppy Organization Defaults

Repositório de configurações compartilhadas da organização Zoppy no GitHub. Templates e workflows definidos aqui são herdados por **todos os repositórios** da org que não possuem seus próprios.

## Issue Templates

| Template | Quando usar | Labels automáticas |
|---|---|---|
| **Refinamento Técnico** | Nova feature ou tarefa que precisa de detalhamento técnico antes do desenvolvimento | `refinement` |
| **Bug Report** | Bug encontrado em produção ou staging | `bug`, `work: bug` |
| **Epic de Roadmap** | Épico de produto rastreado no roadmap | `roadmap` |
| **Preparação Individual — Tech Lead** | Preparação do Tech Lead antes da reunião de refinamento | `refinement`, `preparation` |
| **General Card** | Demandas genéricas que não se encaixam nos outros templates | — |

## Workflows

| Workflow | Trigger | O que faz |
|---|---|---|
| **Auto Label Bug Reports** | Issue aberta com label `bug` | Aplica labels de ambiente (`origin: master/staging/mirror`) e `client:report` baseado no formulário |
| **Auto Label Refinement** | Issue aberta/editada com label `refinement` | Aplica label `ai-assisted` quando o card foi criado com auxílio de IA |
| **PR Standards Check** | PR aberto/editado/atualizado | Valida naming de branch, tamanho do PR e descrição. Comenta warnings e dicas no PR |
| **Sync Rules** | Push em `development` alterando `rules/` ou manual | Sincroniza `rules/` para todos os repos ativos da org (push direto em master, development, staging, mirror) |

## Refinamento Técnico com IA

O template de refinamento técnico pode ser preenchido manualmente ou com auxílio de IA (Claude/Cursor). Para usar com IA:

1. Abra o Claude Code ou Cursor no repositório do projeto (ex: `zoppy-api`)
2. O arquivo `rules/refinement.md` contém as instruções completas para o Claude gerar o card
3. Descreva a feature ou tarefa — o Claude vai explorar o código e preencher o template
4. O Claude cria a issue via `gh issue create` com todos os campos preenchidos
5. Marque **"Sim"** no campo "Criado com auxílio de IA?" — a label `ai-assisted` é aplicada automaticamente

### Medindo o impacto

A label `ai-assisted` permite filtrar e comparar issues criadas com e sem IA:

```
# Issues de refinamento criadas com IA
is:issue label:refinement label:ai-assisted

# Issues de refinamento criadas sem IA
is:issue label:refinement -label:ai-assisted
```

Isso possibilita medir ao longo do tempo: velocidade de criação, completude dos campos, qualidade do refinamento, e tempo até o card estar "pronto para desenvolvimento".

## PR Standards

Todo PR aberto na org passa por um check automático (non-blocking) que valida:

### Branch naming
Prefixos válidos: `milestone/`, `task/`, `bugfix/`, `hotfix/`, `chore/`, `refactor/`, `feat/`, `feature/`, `release/`, `dependabot/`

- **Features**: `milestone/<nome-da-feature>` (branch protegido, PRs obrigatórios)
- **Tasks**: `task/<nome-da-feature>/<nome-da-task>` (PR para o milestone)
- **Bugs**: `bugfix/<descrição>` (vai para staging/mirror)
- **Hotfixes**: `hotfix/<descrição>` (correções urgentes direto em produção)

### Tamanho do PR
- **Recomendado**: até 400 linhas alteradas (excluindo testes, migrations e lockfiles)
- **Warning forte**: acima de 800 linhas
- Se ficou grande demais: fatiar em tasks menores

### Descrição do PR
- Não pode ser vazia
- Deve incluir: o que muda, por que, e como testar

O check comenta no PR com warnings e dicas, mas **não bloqueia o merge**.

## Rules — Source of Truth Centralizado

A pasta `rules/` deste repositório é a **fonte única de verdade** para rules e skills de desenvolvimento da Zoppy. Cada repo recebe apenas as rules relevantes para o seu contexto.

### Como funciona

1. Abra um PR no `.github` alterando arquivos em `rules/`
2. O PR precisa de **aprovação humana** (gate de qualidade)
3. Após merge em `development`, a action **Sync Rules** faz push direto em `master`, `development`, `staging` e `mirror` dos repos configurados
4. Nenhuma aprovação adicional necessária nos repos destino — o gate já aconteceu aqui

### Estrutura

```
rules/
├── sync-config.json              # Mapeamento repo → pastas
├── shared/                       # Todos os repos recebem
│   ├── refinement.md             # Processo de refinamento técnico
│   └── review-pr.md              # Checklist de review de PR
├── backend/                      # Repos NestJS
│   ├── api-development.md        # Arquitetura, padrões, logging, queues
│   └── testing.md                # Testes unitários e integração (Jest)
├── frontend/                     # Repos Angular
│   └── frontend-angular.md       # Componentes, signals, Tailwind, design system
└── e2e/                          # Repos de teste E2E
    └── e2e-testing.md            # Playwright, fixtures, padrões E2E
```

### Mapeamento por grupo

| Grupo | Recebe | Exemplos de repos |
|---|---|---|
| **backend** | `shared` + `backend` | zoppy-api, zoppy-event-bridge, zoppy-workflow |
| **frontend** | `shared` + `frontend` | zoppy-FE, zoppy-partners-fe, zoppy-workflow-FE |
| **e2e** | `shared` + `e2e` | zoppy-e2e-api, playwright-e2e |
| **integrations** | `shared` + `backend` | zoppy-shopify, zoppy-vtex, zoppy-wake-commerce |
| **workers** | `shared` + `backend` | data-sync-worker, totvs-moda-data-sync-worker |
| **shared-packages** | `shared` | zoppy-model, ui-components, zoppy-utilities |

Para adicionar ou mover repos, edite `rules/sync-config.json`.

### Execução manual

A action pode ser disparada manualmente via `workflow_dispatch` com opção de dry run (apenas lista repos sem fazer push).

### O que acontece no repo destino

Os arquivos são copiados para `rules/` na raiz do repo. Exemplo para `zoppy-FE`:

```
rules/
├── refinement.md          # de shared/
├── review-pr.md           # de shared/
└── frontend-angular.md    # de frontend/
```
