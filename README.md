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
| **Sync Skills** | Push em `development` alterando `skills/` ou manual | Sincroniza `.claude/skills/` para repos configurados (push direto em master, development, staging, mirror) |
| **Auto Label AI PRs** | PR aberto/atualizado | Detecta `Co-Authored-By` de IA nos commits e aplica label `ai-assisted` automaticamente |

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

## Skills — Source of Truth Centralizado

A pasta `skills/` deste repositório é a **fonte única de verdade** para skills do Claude Code. Cada repo recebe apenas as skills relevantes para o seu contexto, no formato nativo `.claude/skills/<nome>/SKILL.md`.

### Como funciona

1. Abra um PR no `.github` alterando arquivos em `skills/`
2. O PR precisa de **aprovação humana** (gate de qualidade)
3. Após merge em `development`, a action **Sync Skills** faz push direto em `master`, `development`, `staging` e `mirror` dos repos configurados
4. Nenhuma aprovação adicional necessária nos repos destino — o gate já aconteceu aqui
5. O Claude Code descobre automaticamente as skills em `.claude/skills/`

### Estrutura no `.github` (source of truth)

```
skills/
├── sync-config.json                      # Mapeamento repo → grupos
├── shared/                               # Todos os repos recebem
│   ├── refinement/SKILL.md               # Processo de refinamento técnico
│   └── review-pr/SKILL.md                # Checklist de review de PR
├── backend/                              # Repos NestJS
│   ├── api-development/SKILL.md          # Arquitetura, padrões, logging, queues
│   └── testing/SKILL.md                  # Testes unitários e integração (Jest)
├── frontend/                             # Repos Angular
│   └── frontend-angular/SKILL.md         # Componentes, signals, Tailwind, design system
└── e2e/                                  # Repos de teste E2E
    └── e2e-testing/SKILL.md              # Playwright, fixtures, padrões E2E
```

### Mapeamento por grupo

| Grupo | Skills recebidas | Repos |
|---|---|---|
| **backend** | `shared` + `backend` | zoppy-api, zoppy-workflow, zoppy-pixel-lambda, zoppy-whatsapp-commerce, zoppy-event-bridge |
| **frontend** | `shared` + `frontend` | zoppy-FE, ui-components, zoppy-partners-fe |
| **e2e** | `shared` + `e2e` | zoppy-e2e-api |

Para adicionar repos ou grupos, edite `skills/sync-config.json`.

### O que acontece no repo destino

Skills são copiadas para `.claude/skills/` no formato nativo do Claude Code. Exemplo para `zoppy-FE`:

```
.claude/
└── skills/
    ├── refinement/
    │   └── SKILL.md           # de shared/
    ├── review-pr/
    │   └── SKILL.md           # de shared/
    ├── frontend-angular/
    │   └── SKILL.md           # de frontend/
    └── .synced-from-org       # marker de rastreamento
```

O dev também pode criar skills locais no repo (ex: `.claude/skills/checkout/SKILL.md`) — a sync não sobrescreve skills que não vieram da org.

### Execução manual

A action pode ser disparada manualmente via `workflow_dispatch` com opção de dry run.
