---
name: flow-prd-to-plan
description: Turn a PRD into a multi-phase implementation plan using tracer-bullet vertical slices, saved as a local Markdown file in docs/plans/. Use when user wants to break down a PRD, create an implementation plan, plan phases from a PRD, or mentions "tracer bullets".
---

# PRD to Plan

Break a PRD into a phased implementation plan using vertical slices (tracer bullets). Output is a Markdown file in `docs/plans/`.

## Process

### 1. Locate the PRD

If the user provided a path as argument, use that. Otherwise, look for PRD files in `docs/prds/`. If multiple PRDs exist there, ask the user which one to use. If none exist, ask for the path.

Read the PRD file to load its contents.

After locating the PRD, check if issue files already exist in `docs/<prd-filename-without-extension>/`. If they do, read all issue files — they contain vertical slices, acceptance criteria, and dependency information that should inform the plan. Use them as the primary input for drafting phases instead of slicing from scratch.

### 2. Explore the codebase

If you have not already explored the codebase, do so to understand the current architecture, existing patterns, and integration layers.

### 3. Identify durable architectural decisions

Before slicing, identify high-level decisions that are unlikely to change throughout implementation:

-   Route structures / URL patterns
-   Database schema shape
-   Key data models
-   Authentication / authorization approach
-   Third-party service boundaries

These go in the plan header so every phase can reference them.

### 4. Draft vertical slices

Break the PRD into **tracer bullet** phases. Each phase is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
- Do NOT include specific file names, function names, or implementation details that are likely to change as later phases are built
- DO include durable decisions: route paths, schema shapes, data model names
</vertical-slice-rules>

### 5. Quiz the user

Present the proposed breakdown as a numbered list. For each phase show:

-   **Title**: short descriptive name
-   **User stories covered**: which user stories from the PRD this addresses

Ask the user:

-   Does the granularity feel right? (too coarse / too fine)
-   Should any phases be merged or split further?

Iterate until the user approves the breakdown.

### 6. Write the plan file

Create `docs/plans/` if it doesn't exist. Write the plan as a Markdown file named after the feature (e.g. `docs/plans/user-onboarding.md`). Use the template below.

<plan-template>
# Plano: <Feature Name>

> PRD Fonte: [<prd-filename>](relative-path-to-prd)

## Decisões Arquiteturais

Durable decisions that apply across all phases:

-   **Rotas**: ...
-   **Schema**: ...
-   **Modelos principais**: ...
-   (add/remove sections as appropriate)

---

## Fase 1: <Title>

**Histórias de usuário**: <list from PRD>

### O que construir

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

### Critérios de Aceite

-   [ ] Critério 1
-   [ ] Critério 2
-   [ ] Critério 3

---

## Fase 2: <Title>

**Histórias de usuário**: <list from PRD>

### O que construir

...

### Critérios de Aceite

-   [ ] ...

<!-- Repeat for each phase -->
</plan-template>
