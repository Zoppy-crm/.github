# Zoppy Skills — Repositório de Skills para Claude

Este repositório contém as **skills** usadas pela Zoppy no Claude. Skills são instruções especializadas que ensinam o Claude a executar tarefas seguindo os processos e padrões da Zoppy.

---

## O que são Skills?

Cada skill é uma pasta com um arquivo `SKILL.md` que contém:
- **Frontmatter YAML** (`name`, `description`) — usado pelo Claude para identificar quando acionar a skill
- **Conteúdo instrucional** — passo a passo, critérios, exemplos e regras de execução

> As skills se referenciam **pelo `name`** do frontmatter (ex.: "Acione `zoppy-briefing-builder`"), nunca pelo caminho da pasta. Mover uma skill de pasta **não quebra** as referências — só não mude o `name`.

---

## Estrutura do Repositório

O repositório é dividido em duas trilhas no topo: **`pm/`** (Product Management) e **`pd/`** (Product Design).

```
zoppy-skills/
├── README.md                          ← este arquivo
│
├── pm/                                ← esteira de Product Management
│   ├── zoppy-pm-orchestrator/         ← ponto de entrada do PM (acione primeiro)
│   ├── zoppy-pm-capture/              ← Fase 1 — captura de sinais
│   ├── zoppy-pm-qualification/        ← Fase 2 — qualificação
│   ├── zoppy-pm-discovery/            ← Fase 3 — discovery de produto
│   ├── zoppy-pm-prioritization/       ← Fase 4 — priorização (RICE + roadmap/horizontes)
│   ├── zoppy-pm-briefing/             ← Fase 5 — briefing para design
│   ├── zoppy-pm-intake/               ← ponte PM → Design (análise crítica do insumo)
│   └── zoppy-pm-learning/             ← Fase 6 — aprendizado pós-lançamento
│
└── pd/                                ← esteira de Product Design
    ├── orchestrators/                 ← ponto de entrada do design
    │   └── zoppy-product-flow-orchestrator/  ← roteia para a esteira de pipeline
    │
    ├── profiles/                      ← perfil de papel (designer sênior)
    │   └── zoppy-product-designer-v2/        ← orquestra os 6 specialists
    │
    ├── contexto/                      ← base de conhecimento (NÃO é perfil de entrada)
    │   └── product-designer-zoppy/           ← produto, módulos, DS, heurísticas — herdada por toda a esteira
    │
    ├── esteira/                       ← fases sequenciais do design
    │   ├── zoppy-briefing/            ┐
    │   ├── zoppy-discovery/           │  skills-BASE
    │   ├── zoppy-ideacao/             │  (lógica e formato originais)
    │   ├── zoppy-prototipacao/        │
    │   ├── zoppy-documentacao/        ┘
    │   ├── zoppy-briefing-builder/    ┐
    │   ├── zoppy-discovery-planner/   │  versões de PIPELINE
    │   ├── zoppy-ideation-designer/   │  (herdam das base + Status de Etapa
    │   ├── zoppy-prototyping-figma/   │   e rastreamento entre fases)
    │   ├── zoppy-handoff-builder/     ┘
    │   ├── zoppy-design-system-figma/ ← DS Check (entre Ideação e Prototipação)
    │   ├── zoppy-design-review/       ← review de implementação (pós-handoff)
    │   └── zoppy-feature-workflow/    ← organização de arquivos/pastas no Figma
    │
    ├── specialists/                   ← lentes especialistas chamadas dentro da esteira
    │   ├── zoppy-ux-research/
    │   ├── zoppy-ux-writer/
    │   ├── zoppy-accessibility/
    │   ├── zoppy-plg-design/
    │   ├── zoppy-data-design/
    │   └── zoppy-customer-intelligence/
    │
    └── figma/                         ← execução direta no Figma via MCP
        ├── zoppy-figma-mcp/           ← ★ da Zoppy: component keys, gotchas, protocolo do DS
        ├── VENDORED.md                ← aviso: as skills abaixo são cópias do plugin oficial
        ├── figma-use/                 ← PRÉ-REQUISITO de qualquer use_figma  ┐
        ├── figma-generate-design/                                          │
        ├── figma-create-new-file/                                          │ vendorizadas
        ├── figma-create-design-system-rules/                               │ (não editar à mão;
        ├── edit-figma-design/                                              │  ver VENDORED.md)
        ├── apply-design-system/                                            │
        ├── sync-figma-token/                                               │
        └── rad-spacing/                                                    ┘
```

---

## Base vs. Pipeline (esteira de design)

A esteira de design tem **duas gerações** que coexistem:

- **Skills-base** (`zoppy-briefing`, `zoppy-discovery`, `zoppy-ideacao`, `zoppy-prototipacao`, `zoppy-documentacao`) — contêm a lógica e o formato originais de cada fase. Funcionam standalone.
- **Skills de pipeline** (`zoppy-briefing-builder`, `zoppy-discovery-planner`, `zoppy-ideation-designer`, `zoppy-prototyping-figma`, `zoppy-handoff-builder`) — **herdam** das base ("leia e execute `zoppy-X` como base") e acrescentam o bloco de **Status da Etapa** e o rastreamento explícito entre fases.

> **Não apague as base** — as versões de pipeline dependem delas em tempo de execução ("leia e execute `zoppy-X` como base").

O orquestrador atual (`zoppy-product-flow-orchestrator`) aciona as versões de **pipeline**, que por sua vez puxam as **base**. As base ainda têm gatilhos próprios para uso **standalone** (fora da esteira).

> Nota de manutenção: como existe só um orquestrador, o par base+pipeline é candidato a fusão futura (1 skill por fase em vez de 2). Mantido separado por ora porque as base também são acionadas soltas.

---

## Fluxo Geral

### Esteira de PM
```
Captura → Qualificação → Discovery → Priorização → Briefing → (PM Intake) → Aprendizado
```

### Esteira de Design
```
PM Intake → Briefing → Discovery → Ideação → DS Check → Prototipação → Handoff → Review
```

---

## Como usar

### No Claude (claude.ai)
1. Faça upload das pastas de skill desejadas nas suas **instruções de projeto**
2. O Claude detecta automaticamente quando acionar cada skill pelo `description` no frontmatter
3. Para iniciar qualquer fluxo, use os **orchestrators** — eles roteiam para as skills corretas

### Ponto de entrada recomendado
- **Para o PM:** `pm/zoppy-pm-orchestrator`
- **Para Design (fluxo completo):** `pd/orchestrators/zoppy-product-flow-orchestrator`
- **Para Design (designer sênior com specialists):** `pd/profiles/zoppy-product-designer-v2`
- Cole qualquer insumo (PRD, demanda, relato de CS) e o orchestrator decide onde começar

> `pd/contexto/product-designer-zoppy` **não é ponto de entrada** — é a base de conhecimento (produto, módulos, Design System, heurísticas) herdada por toda a esteira e pelo `zoppy-product-designer-v2`. Está sempre ativa como contexto; você não a aciona diretamente.

---

## Filosofia de Execução

> Avançar rápido no entendimento. Avançar devagar nas decisões. Avançar com muito cuidado no Figma.

- **Nunca** pular etapas da esteira
- **Nunca** prototipar antes de entender o problema
- **Nunca** criar componente no Figma sem verificar o Design System primeiro
- **Sempre** apresentar o diagnóstico antes de executar

---

## Convenções

- Cada skill tem **uma responsabilidade clara**
- Skills da esteira são **sequenciais** — respeite a ordem
- Skills de Figma **exigem** que `figma-use` seja carregado antes de qualquer `use_figma`
- Orchestrators são os **pontos de entrada externos** — specialists são chamados internamente

---

## Manutenção

Para criar ou editar uma skill, use a skill `skill-creator` (disponível nas skills públicas do Claude).

Para adicionar uma skill nova:
1. Crie a pasta com o nome da skill (kebab-case) na trilha correta (`pm/` ou `pd/...`)
2. Adicione o `SKILL.md` com frontmatter YAML (`name` e `description`)
3. Atualize este README com a nova skill na categoria correta
