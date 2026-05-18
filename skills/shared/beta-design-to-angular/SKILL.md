---
name: beta-design-to-angular
description: Analyzes a screen design from a pasted image (screenshot) and developer notes to produce an Angular implementation plan. Use when the user attaches a screenshot, paste an image, or describes a screen visually — says "implementar esta tela", "montar este componente", "segue o print do design", "tenho o screenshot do Figma", "cola a imagem aqui", or when starting any frontend task with visual reference WITHOUT a Figma URL. Preferred over /figma-to-angular-mcp because it uses Claude's vision instead of MCP calls — far fewer tokens.
---

# Design to Angular (via Screenshot + Notas)

Analisa o design a partir de uma imagem e notas do desenvolvedor para produzir um plano de implementação Angular: hierarquia de componentes, decisões de estado, contrato de inputs/outputs e oportunidades de reuso — sem chamar APIs externas.

## O que você precisa trazer

### Passo 0 — Verificar se já existe design no plano

Antes de pedir qualquer coisa ao usuário, verifique se existe um plano detalhado da fase em `docs/plans/` que já contenha informações de design (imagens, notas de estilo, tokens, espaçamentos). Se existir:

> "Encontrei informações de design no plano `docs/plans/<fase>.md`. Quer que eu use o design que está no plano, ou você tem uma versão atualizada para fornecer?"

Se o usuário confirmar o plano, use as informações de lá sem pedir novamente. Se o usuário fornecer uma versão atualizada, use a nova e atualize o plano.

### Se não houver design no plano

O usuário deve fornecer:

1. **Screenshot da tela** — print do Figma, Figma Dev Mode, ou qualquer captura visual
2. **Notas do design** (quanto mais, melhor):
    - Cores e tipografia (`#1A1A2E`, `font-size: 14px`, tokens como `--color-primary`)
    - Espaçamentos relevantes (`padding: 16px 24px`, `gap: 8px`)
    - Comportamentos interativos (hover, click, estados: empty, loading, error)
    - Componentes do design system já identificados (ex: "esse botão é o `<zoppy-button>` primário")
    - Breakpoints relevantes (mobile/desktop)

Se o usuário não forneceu a imagem, peça:

> "Anexe o screenshot da tela e, se possível, as propriedades copiadas do Figma Dev Mode (cores, espaçamentos, tipografia)."

### Salvar design recebido no plano

Quando o usuário fornecer imagens de design, salvar no plano da fase para uso futuro nas implementações:

-   Tentar incorporar a imagem diretamente no markdown do plano via `![descricao](caminho)`
-   Se não for possível (imagem muito grande, formato incompatível), salvar em `docs/plans/assets/<nome-do-plano>/` e referenciar no markdown
-   Adicionar/atualizar a seção `## Design de Referência` no plano com imagem + notas de estilo extraídas

## Workflow

### 1. Analisar a imagem

Observe a imagem com atenção e identifique:

-   **Estrutura geral**: é uma página completa, um modal, um card, um formulário?
-   **Regiões visuais**: header, sidebar, conteúdo principal, footer, painéis
-   **Componentes presentes**: tabelas, listas, botões, inputs, badges, ícones, avatares
-   **Estados visíveis**: loading skeleton, empty state, erro, selecionado, desabilitado
-   **Interações inferíveis**: cliques, hovers, expansão, paginação, filtros

### 2. Cruzar com as notas do desenvolvedor

Use as notas fornecidas para preencher os detalhes que a imagem não revela:

-   Substitua cores visuais por tokens ou variáveis reais quando fornecidos
-   Use os espaçamentos exatos em vez de estimados
-   Confirme quais componentes do design system já cobrem os elementos identificados

### 3. Explorar o projeto para reuso

Busque no codebase:

-   Componentes existentes em `@Zoppy-crm/ui-*` que cobrem elementos do design
-   Features similares em `src/core/pages/dashboard/` como referência de estrutura
-   State services que já gerenciam dados relacionados

### 4. Produzir o plano de implementação

#### 4.1 — Resumo Visual

2–3 frases descrevendo o que a tela faz e as interações principais. Mencione incertezas da análise visual (ex: "não está claro se o filtro colapsa ou abre um dropdown — confirme com o designer").

#### 4.2 — Hierarquia de Componentes

```
<feature-name-page> (Smart Container)
  ├── Injeta: FeatureNameStateService
  ├── <feature-header> (Dumb)
  │     inputs: title: input<string>(), count: input<number>()
  ├── <feature-filters> (Dumb) [se houver]
  │     inputs: filters: input<FilterState>()
  │     outputs: filterChanged: output<FilterState>()
  ├── <feature-table> (Dumb)
  │     inputs: items: input<Item[]>(), loading: input<boolean>()
  │     outputs: itemSelected: output<Item>()
  └── <feature-modal> (Dumb) [se houver]
        inputs: open: input<boolean>(), item: input<Item | null>()
        outputs: saved: output<Item>(), closed: output<void>()
```

Regras:

-   Smart container = 1 por feature; injeta services, não recebe `input()`
-   Dumb components = só `input()` e `output()`, sem injeção de service
-   Nenhum componente > ~150 linhas; extraia sub-componentes quando crescer
-   Use componentes do `@Zoppy-crm/ui-*` em vez de reimplementar (liste quais)

#### 4.3 — Estrutura de Pastas

```
src/core/pages/dashboard/<feature-name>/
├── <feature-name>.component.ts        ← Smart container
├── <feature-name>.component.html
├── <feature-name>.routes.ts
├── <feature-name>-state.service.ts    ← Se houver estado compartilhado
└── components/
    ├── <sub-component-a>/
    │   ├── <sub-component-a>.component.ts
    │   └── <sub-component-a>.component.html
    └── <sub-component-b>/
        ├── <sub-component-b>.component.ts
        └── <sub-component-b>.component.html
```

#### 4.4 — Plano de Estado

| Dado                  | Onde                             | Por quê                             |
| --------------------- | -------------------------------- | ----------------------------------- |
| Lista de itens da API | `WritableSignal` no StateService | Compartilhado entre tabela e modal  |
| Item selecionado      | `WritableSignal` no StateService | Necessário em múltiplos componentes |
| Modal aberto/fechado  | `signal()` no Smart Container    | Estado local de UI                  |
| Valores de formulário | `signal()` no Dumb Component     | Encapsulado no form                 |

Regra: estado que cruza mais de 1 nível de componente → state service. Estado local de 1 componente → `signal()` dentro dele.

#### 4.5 — Reuso do Design System

Liste o mapeamento entre elementos do design e componentes existentes:

-   ex: "Botão primário → `<zoppy-button variant='primary'>`"
-   ex: "Tabela com paginação → `<zoppy-table>`"
-   ex: "Campo de texto → `<zoppy-input>`"

Liste elementos sem componente existente que precisarão ser criados do zero.

#### 4.6 — Estilização (Tailwind)

Classes-chave inferidas do design ou das notas:

-   Layout: `flex`, `grid`, colunas, gaps
-   Espaçamentos: padding/margin relevantes
-   Cores: classes ou CSS custom properties (`var(--color-primary)`)
-   Tipografia: tamanhos, pesos

#### 4.7 — Incertezas e Perguntas

Liste o que não ficou claro na imagem e precisa de confirmação antes de implementar:

-   ex: "O estado vazio da tabela tem uma ilustração ou apenas texto?"
-   ex: "O modal fecha ao clicar fora ou só pelo botão X?"
-   ex: "Qual endpoint alimenta esta lista?"

#### 4.8 — Sequência de Implementação

1. State service (sinais + stubs dos métodos de API)
2. Smart container (layout + injeção do service)
3. Sub-componente mais simples (sem dependências)
4. Sub-componentes restantes
5. Conectar fluxo de dados (service → smart container → dumb)
6. Interações e outputs
7. Validar visualmente com `/agent-browser`

#### 4.9 — Próximas Skills

```
1. /angular-component    → implementar cada componente
2. /angular-signals      → configurar estado reativo
3. /feature-composition  → montar estrutura smart/dumb
4. /feature-state        → criar state service
5. /agent-browser        → validar UI no browser
```

## Regras

-   **Nunca comece a implementar** — esta skill só planeja
-   Se a imagem for ambígua em algum ponto, registre na seção 4.7 (Incertezas) em vez de assumir
-   Se as notas do desenvolvedor conflitarem com a imagem, pergunte antes de decidir
-   Se a tela for complexa (>5 componentes), sugira dividir em fases
-   Sempre verifique features similares em `src/core/pages/dashboard/` antes de propor novos padrões
