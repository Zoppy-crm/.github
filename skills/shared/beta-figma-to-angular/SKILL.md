---
name: beta-figma-to-angular
description: Uses the Figma MCP server to read a design directly from a Figma URL and produce an Angular implementation plan. Use ONLY when the user provides a figma.com URL AND the Figma MCP server is available in the session. High token cost (~20-50k tokens) — prefer /design-to-angular when the user already has a screenshot or copied properties. Triggers: user shares figma.com URL, "usar MCP do Figma", "ler direto do Figma".
allowed-tools: mcp__claude_ai_Figma__get_design_context, mcp__claude_ai_Figma__get_screenshot, mcp__claude_ai_Figma__get_metadata, Read, Glob, Grep
---

# Figma to Angular (via MCP)

> **Atenção:** Esta skill usa o Figma MCP, que consome entre 20k e 50k tokens por chamada dependendo do tamanho do arquivo. Use apenas quando necessário. Para uma alternativa eficiente, use `/design-to-angular`.

Lê o design diretamente do Figma via MCP e produz um plano estruturado de componentes Angular.

## Workflow

### 1. Extract Figma identifiers

Parse the URL provided by the user:

-   `figma.com/design/:fileKey/:name?node-id=:nodeId` → extract `fileKey` and `nodeId` (replace `-` with `:` in nodeId)
-   `figma.com/design/:fileKey/branch/:branchKey/...` → use `branchKey` as fileKey
-   If no URL provided, ask: "Qual é a URL do Figma para esta tela?"

### 2. Fetch the design

Run in parallel:

```
get_design_context(fileKey, nodeId)   → code reference + layout hints
get_screenshot(fileKey, nodeId)       → visual reference image
```

Study both outputs carefully before proceeding.

### 3. Explore project for reuse

Search the codebase for:

-   Existing components in `@Zoppy-crm/ui-*` that match design elements (buttons, inputs, cards, modals, tables)
-   Similar feature pages in `src/core/pages/dashboard/` for structural patterns
-   Existing state services that might already manage related data

### 4. Produce the implementation plan

Output a structured plan with these sections:

#### 4.1 — Visual Summary

Brief description of what the screen does (2–3 sentences) and the main user interactions.

#### 4.2 — Component Hierarchy

```
<feature-name-page> (Smart Container)
  ├── Injects: FeatureNameStateService
  ├── <feature-header> (Dumb)
  │     inputs: title: string, subtitle: string
  ├── <feature-table> (Dumb)
  │     inputs: items: Signal<Item[]>, loading: Signal<boolean>
  │     outputs: itemSelected: OutputEmitterRef<Item>
  └── <feature-modal> (Dumb) [if applicable]
        inputs: open: Signal<boolean>, item: Signal<Item | null>
        outputs: saved: OutputEmitterRef<Item>, closed: OutputEmitterRef<void>
```

Rules:

-   Smart container = 1 per feature; owns data fetching and state service
-   Dumb components = receive `input()`, emit via `output()`, no service injection
-   No component > ~150 lines; extract sub-components when growing
-   Use `@Zoppy-crm/ui-*` components instead of reimplementing (list which ones)

#### 4.3 — Folder Structure

```
src/core/pages/dashboard/<feature-name>/
├── <feature-name>.component.ts        ← Smart container
├── <feature-name>.component.html
├── <feature-name>.routes.ts
├── <feature-name>-state.service.ts    ← State service (if needed)
└── components/
    ├── <sub-component>/
    │   ├── <sub-component>.component.ts
    │   └── <sub-component>.component.html
```

#### 4.4 — State Plan

Decide what goes where:

| Data                   | Where                            | Why                      |
| ---------------------- | -------------------------------- | ------------------------ |
| List of items from API | `WritableSignal` in StateService | Shared across components |
| Selected item          | `WritableSignal` in StateService | Needed in modal + table  |
| Modal open/close       | `signal()` in Smart Container    | Local UI state           |
| Form field values      | `signal()` in Dumb Component     | Encapsulated in form     |

Rule: If state crosses more than 1 component level → state service. If local to 1 component → `signal()` inside it.

#### 4.5 — Design System Reuse

List components from `@Zoppy-crm/ui-*` that map to design elements:

-   e.g., "Header card → `<zoppy-page-header>`"
-   e.g., "Table → `<zoppy-table>`"
-   e.g., "Primary button → `<zoppy-button variant='primary'>`"

List any design elements that have NO existing component and need to be created.

#### 4.6 — Tailwind Notes

Key layout classes derived from the design (spacing, colors, flex/grid patterns).

#### 4.7 — Implementation Sequence

Ordered list of what to build:

1. State service skeleton (signals + API method stubs)
2. Smart container (layout + service injection)
3. [Sub-component 1] — start with simplest, no dependencies
4. [Sub-component 2]
5. Wire up data flow (connect service → smart container → dumb components)
6. Add interactions and outputs
7. Validate visually with `/agent-browser`

#### 4.8 — Skills to Invoke

```
Next steps:
1. /angular-component    → implement each component
2. /angular-signals      → set up signal-based state
3. /feature-composition  → wire smart/dumb structure
4. /feature-state        → create state service
5. /agent-browser        → validate UI in browser
```

## Rules

-   **Never start implementing** — this skill only plans; execution is done by the Angular skills
-   If `get_design_context` returns Code Connect snippets (codebase component mappings), use those components directly instead of creating new ones
-   If the design has annotations or designer notes, include them in the Visual Summary
-   If the screen is complex (>5 components), suggest splitting into phases
-   Always check for existing similar features in `src/core/pages/dashboard/` before proposing new patterns
