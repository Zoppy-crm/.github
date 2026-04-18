---
name: flow-prd-to-issues
description: Break a PRD into independently-grabbable local issue files using tracer-bullet vertical slices. Use when user wants to convert a PRD to issues, create implementation tickets, or break down a PRD into work items. Works with local markdown PRD files.
---

# PRD to Issues

Break a PRD into independently-grabbable issue files (local markdown) using vertical slices (tracer bullets).

## Process

### 1. Locate the PRD

If the user provided a path as argument, use that. Otherwise, look for PRD files in `docs/prds/`. If multiple PRDs exist there, ask the user which one to use. If none exist, ask for the path.

Read the PRD file to load its contents.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.

### 3. Draft vertical slices

Break the PRD into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories from the PRD this addresses

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the issue files

Derive the output directory from the PRD filename: `docs/<prd-filename-without-extension>/`. For example, if the PRD is `docs/prds/auth-redesign.md`, issues go in `docs/auth-redesign/`.

Create one markdown file per approved slice. Use a slugified version of the issue title as the filename (e.g., `setup-database-schema.md`).

Create files in dependency order (blockers first) so you can reference the correct filenames in the "Blocked by" field.

Use the issue template below for each file:

<issue-template>
# <Título da Issue>

## PRD Pai

[<prd-filename>](relative-path-to-prd)

## O que construir

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation. Reference specific sections of the parent PRD rather than duplicating content.

## Critérios de Aceite

- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério 3

## Bloqueado por

- [<título-da-issue-bloqueadora>](./<nome-arquivo-bloqueador>.md) (if any)

Ou "Nenhum - pode iniciar imediatamente" se não houver bloqueios.

## Histórias de Usuário Atendidas

Reference by number from the parent PRD:

- História de usuário 3
- História de usuário 7

</issue-template>

Do NOT modify the parent PRD file.
