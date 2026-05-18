---
name: design-to-plan
description: Analisa um design do Figma (via screenshot + estilos colados) e produz um plano de implementação Angular completo para o projeto Zoppy FE, mapeando cada elemento visual para os componentes reais do design system (@Zoppy-crm/*). Use sempre que o usuário enviar uma imagem do Figma, screenshot de tela, print de design, ou mencionar "planejar a tela", "planejar o componente", "analisar o design", "criar plano da feature com o Figma". Também use quando o usuário colar estilos do Figma Dev Mode junto com uma imagem.
---

# Design to Plan — Zoppy FE

Analisa um design do Figma e produz um plano de implementação Angular usando os componentes reais do design system Zoppy (`@Zoppy-crm/*`).

## O que o usuário deve fornecer

1. **Screenshot da tela** — print do Figma, Figma Dev Mode, ou qualquer captura visual
2. **Estilos/notas do Figma** (opcional mas recomendado):
    - Cores, tokens (`--color-primary`, `text-text-primary`)
    - Espaçamentos (`padding: 16px 24px`, `gap: 8px`)
    - Comportamentos interativos (hover, estados: empty, loading, error)
    - Breakpoints relevantes

Se o usuário não forneceu a imagem, peça:

> "Anexe o screenshot da tela e, se possível, as propriedades copiadas do Figma Dev Mode."

---

## Catálogo do Design System Zoppy

Antes de planejar, mapeie cada elemento visual para os componentes abaixo. Prefira sempre um componente existente a criar um novo.

### Componentes UI (versão atual — prefira estes)

| Elemento visual    | Componente                                                                    | Import                       |
| ------------------ | ----------------------------------------------------------------------------- | ---------------------------- |
| Botão              | `<ui-button type="primary" size="medium" text="..." (onClick)="...">`         | `@Zoppy-crm/ui-button`       |
| Campo de texto     | `<ui-input>`                                                                  | `@Zoppy-crm/ui-input`        |
| Dropdown / Select  | `<ui-dropdown>`                                                               | `@Zoppy-crm/ui-dropdown`     |
| Seleção única      | `<ui-selector>`                                                               | `@Zoppy-crm/ui-selector`     |
| Multi-seleção      | `<ui-multi-select>`                                                           | `@Zoppy-crm/ui-multi-select` |
| Data picker        | `<ui-datepicker>`                                                             | `@Zoppy-crm/ui-datepicker`   |
| Time picker        | `<ui-timepicker>`                                                             | `@Zoppy-crm/ui-timepicker`   |
| Texto / Tipografia | `<ui-text htmlTag="span" type="body-highlight" className="text-primary">`     | `@Zoppy-crm/ui-text`         |
| Tag / Badge / Pill | `<ui-tag-pill>`                                                               | `@Zoppy-crm/ui-tag-pill`     |
| Label de campo     | `<ui-label>`                                                                  | `@Zoppy-crm/ui-label`        |
| Abas / Tabs        | `<ui-tab>`                                                                    | `@Zoppy-crm/ui-tab`          |
| Barra de progresso | `<ui-progress>`                                                               | `@Zoppy-crm/ui-progress`     |
| Alerta informativo | `<ui-info-alert type="warning" icon="warning" title="..." description="...">` | `@Zoppy-crm/ui-info-alert`   |
| Tag de filtro      | `<ui-filter-tag>`                                                             | `@Zoppy-crm/ui-filter-tag`   |
| Radio button       | `<ui-radio-button>`                                                           | `@Zoppy-crm/ui-radio-button` |
| Ícone              | `<ps-icon [icon]="'nome'" class="text-20 neutral-500">`                       | `@Zoppy-crm/icon`            |
| Toast (serviço)    | `UiToastService`                                                              | `@Zoppy-crm/ui-toast`        |

**Alertas e warnings:** Sempre usar `<ui-info-alert>` para blocos de aviso/alerta. Tipos disponíveis: `info`, `warning`, `error`, `success`, `primary`. O componente já renderiza ícone, border, background e tipografia automaticamente — **nunca criar div custom para alertas**.

### Serviços compartilhados

| Funcionalidade | Serviço          | Import                                      | Uso                                                                                                                                                                                       |
| -------------- | ---------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Modal / Dialog | `ModalService`   | `src/shared/components/modal/modal.service` | `modal.open({ component, data, callback })` — renderiza componente dinâmico. Dentro do modal: `inject(ModalService)`, lê `modal.data`, fecha via `modal.close(executeCallback, response)` |
| Toast          | `UiToastService` | `@Zoppy-crm/ui-toast`                       | `toast.success('msg')`, `toast.error('msg')`                                                                                                                                              |

### Componentes legados (ainda em uso — use se já existir no contexto)

`<checkbox>`, `<switch>`, `<skeleton>`, `<pagination>`, `<stepper>`, `<confirm-action>`, `<tooltip>`, `<infinite-scroll>`, `<search-bar>`, `<mini-menu>`, `<contact>`

### Utilitários

-   `cn()` de `@Zoppy-crm/visual-identity` — composição segura de classes Tailwind
-   `FormatUtils`, `ArrayUtil` de `@Zoppy-crm/utilities`
-   `<floating-input>` de `@Zoppy-crm/floating-input` — input com label flutuante
-   `<graph>` de `@Zoppy-crm/graph` — gráficos

### Tokens de design (Tailwind)

Cores via classes Tailwind do preset `@Zoppy-crm/tailwind`:

-   Superfícies: `bg-surface-primary`, `bg-surface-secondary`, `bg-surface-default`, `bg-surface-disabled`
-   Texto: `text-primary`, `text-secondary`, `text-disabled`
-   Bordas: `border-default`, `border-border-default`, `border-primary`
-   Status: `text-critical`, `text-success`, `text-warning`
-   Backgrounds neutros: `bg-white`, `bg-neutral-100`, `bg-neutral-200`, `bg-neutral-300`
-   Ações: `bg-primary`, `text-primary` (para ações/links)
-   Hover: `bg-hover`, `hover:bg-hover`

**IMPORTANTE — Conversão Figma → Tailwind:**

Os nomes do Figma (Dev Mode) usam PascalCase e NÃO são classes Tailwind válidas. Sempre converter:

| Nome Figma (NÃO usar)   | Classe Tailwind (usar)                    |
| ----------------------- | ----------------------------------------- |
| `bg-Surface-Primary`    | `bg-surface-primary`                      |
| `bg-Surface-Disable`    | `bg-surface-disabled` ou `bg-neutral-200` |
| `bg-Action-Primary`     | `bg-primary`                              |
| `bg-Hover-Default`      | `bg-hover` ou `bg-neutral-100`            |
| `text-Action-Primary`   | `text-primary`                            |
| `border-Border-Default` | `border-border-default`                   |
| `bg-Surface-Selected`   | `bg-surface-selected` ou `bg-primary-100` |

**Regra:** Nunca copiar nomes PascalCase do Figma direto nos templates. Se não souber a classe Tailwind equivalente, usar `grep` no codebase para encontrar a classe correta antes de escrever no plano.

### Formatação de dados nos templates

Ao planejar templates que exibem dados dinâmicos, sempre especificar os pipes de formatação:

-   Datas: `{{ date | date:'dd/MM/yyyy' }}`
-   Porcentagens: `{{ value | number:'1.0-0' }}%`
-   Moedas: `{{ value | zoppyCurrency }}`
-   Números grandes: `{{ value | number:'1.0-0' }}`

---

## Workflow

### 1. Analisar a imagem

Observe com atenção e identifique:

-   **Estrutura geral**: página, modal, card, formulário, drawer?
-   **Regiões visuais**: header, sidebar, conteúdo principal, footer, painéis
-   **Elementos presentes**: tabelas, listas, botões, inputs, badges, ícones, abas, filtros
-   **Estados visíveis**: loading skeleton, empty state, erro, selecionado, desabilitado
-   **Interações inferíveis**: cliques, hover, expansão, paginação, filtros, modais

### 2. Mapear para o design system

Para cada elemento visual identificado:

1. Verifique se existe um componente `@Zoppy-crm/*` no catálogo acima
2. Se existir → liste na seção "Reuso do Design System"
3. Se não existir → marque como "criar localmente"

### 3. Produzir o plano

---

## Formato de saída

### Resumo Visual

2–3 frases descrevendo o que a tela faz e as interações principais. Mencione incertezas da análise visual.

### Hierarquia de Componentes

```
<feature-name-page> (Smart Container)
  ├── providers: [FeatureNameStateService]
  ├── <feature-header>
  │     title: InputSignal<string>
  │     count: InputSignal<number>
  ├── <feature-filters> [se houver]
  │     injeta: FeatureNameStateService (lê e escreve filtros diretamente)
  ├── <feature-list> ou <feature-table>
  │     injeta: FeatureNameStateService (lê items, loading; chama selectItem)
  └── <feature-modal> [se houver]
        injeta: FeatureNameStateService (lê item selecionado, chama save/close)
```

Regras:

-   Smart container = 1 por feature; injeta services, coordena navegação
-   Sub-components injetam o state service diretamente — sem `output()` para comunicação entre componentes da mesma feature; use `output()` apenas para dados que vêm de **fora** da feature
-   Nenhum componente > ~150 linhas; extraia sub-componentes quando crescer
-   Use `ChangeDetectionStrategy.OnPush` em todos

### Estrutura de Pastas

```
src/core/pages/dashboard/<feature-name>/
├── <feature-name>.component.ts
├── <feature-name>.component.html
├── <feature-name>.routes.ts
├── <feature-name>-state.service.ts    ← se houver estado compartilhado
└── components/
    ├── <sub-a>/
    │   ├── <sub-a>.component.ts
    │   ├── <sub-a>.component.html
    │   └── <sub-a>.service.ts         ← se o sub-componente tiver lógica própria
    └── <sub-b>/
```

### Plano de Estado

| Dado             | Onde            | Tipo                           | Por quê          |
| ---------------- | --------------- | ------------------------------ | ---------------- |
| Lista da API     | StateService    | `WritableSignal<Item[]>`       | Compartilhado    |
| Item selecionado | StateService    | `WritableSignal<Item \| null>` | Multi-componente |
| Modal aberto     | Smart Container | `WritableSignal<boolean>`      | UI local         |
| Filtros ativos   | StateService    | `WritableSignal<FilterState>`  | Compartilhado    |

Regra: estado que cruza mais de 1 nível de componente → state service. Estado local → `signal()` dentro do próprio componente.

### Reuso do Design System

Mapeamento explícito elemento → componente:

```
Botão "Salvar"         → <ui-button type="primary" size="medium" text="Salvar" (onClick)="save()">
Campo "Nome"           → <ui-input>
Dropdown "Status"      → <ui-dropdown>
Ícone de fechar        → <ps-icon [icon]="'close'" class="text-20 neutral-500">
Badge de status        → <ui-tag-pill variant="success">
Abas da tela           → <ui-tab>
[elemento sem par]     → criar localmente
```

### Template de Referência

Esboço do template HTML do smart container e dos sub-components principais, usando os componentes reais do design system. Não é código final — é guia visual para o desenvolvedor:

```html
<!-- feature-name.component.html -->
<div class="flex flex-col gap-4 p-6">
    <app-feature-header [title]="state.title()" [count]="state.items().length" />

    <app-feature-filters [filters]="state.filters()" (filterChanged)="state.setFilters($event)" />

    @if (state.loading()) {
    <skeleton />
    } @else {
    <app-feature-list [items]="state.items()" [loading]="state.loading()" (itemSelected)="state.selectItem($event)" />
    }
</div>

<!-- app-feature-filters — exemplo de uso do design system -->
<!-- sub-components injetam o state service e escrevem diretamente nele -->
<div class="flex gap-2 flex-wrap">
    <ui-dropdown [options]="statusOptions" (selected)="state.setStatus($event)"> Status </ui-dropdown>
    <ui-datepicker (dateChange)="state.setPeriod($event)">Período</ui-datepicker>
    @for (tag of state.activeTags(); track tag.id) {
    <ui-filter-tag (removed)="state.removeTag(tag)">{{ tag.label }}</ui-filter-tag>
    }
</div>
```

### Estilização (Tailwind)

Classes-chave inferidas do design:

-   Layout geral: ex `flex flex-col gap-6 p-6`
-   Cards/painéis: ex `rounded-lg border border-default bg-surface-primary`
-   Tipografia: ex `text-primary`, `text-secondary text-sm`
-   Cores de status: ex `text-success`, `text-critical`

### Incertezas e Perguntas

Liste o que não ficou claro e precisa de confirmação antes de implementar:

-   ex: "O estado vazio da lista tem ilustração ou só texto?"
-   ex: "O modal fecha ao clicar fora ou apenas pelo botão X?"
-   ex: "Qual endpoint alimenta esta lista?"
-   ex: "Existe paginação ou scroll infinito?"

### Sequência de Implementação

1. State service (signals + stubs dos métodos de API)
2. Smart container (layout + route config)
3. Sub-componente mais simples (sem dependências de estado)
4. Sub-componentes restantes (com injeção do state service)
5. Conectar fluxo de dados completo
6. Interações, outputs e feedbacks (toast, loading, error)
7. Validar visualmente no browser

---

## Regras

-   **Nunca comece a implementar** — esta skill só planeja
-   **Nunca usar nomes de tokens Figma (PascalCase) nos templates** — sempre converter para classes Tailwind reais (kebab-case). Consultar a tabela de conversão acima. Se não souber, fazer `grep` no codebase.
-   **Sempre incluir pipes de formatação** em templates que exibem datas, porcentagens e números
-   **Services HTTP devem estender `ApiService`** — nunca usar `HttpClient` direto. Usar `this.get()`, `this.post()`, `this.put()`, `this.delete()` e `this.url`
-   Sempre prefira componentes `@Zoppy-crm/*` a criar locais
-   Se um componente do catálogo cobrir parcialmente, liste o gap — não reimplemente do zero
-   Se a tela for complexa (>5 componentes ou >2 fluxos distintos), sugira dividir em fases
-   Tipagem explícita em todos os signals: `const x: WritableSignal<T> = signal(value)`
-   Registre incertezas em vez de assumir — é melhor perguntar ao designer do que replanejar depois
