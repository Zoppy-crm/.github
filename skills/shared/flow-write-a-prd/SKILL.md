---
name: flow-write-a-prd
description: Create a PRD through user interview, codebase exploration, and module design, then submit as a GitHub issue. Use when user wants to write a PRD, create a product requirements document, or plan a new feature.
---

This skill will be invoked when the user wants to create a PRD. You may skip steps if you don't consider them necessary.

1. Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

2. Explore the repo to verify their assertions and understand the current state of the codebase.

3. Interview the user relentlessly about every aspect of this plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

4. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

5. Once you have a complete understanding of the problem and solution, use the template below to write the PRD. Save it as a markdown file in `docs/prds/` (create the directory if it doesn't exist). Name the file descriptively based on the feature, e.g. `docs/prds/jwt-authentication.md`.

   **Quando o PRD vira um epic no GitHub:** o arquivo gerado por essa skill é o "working draft" pra review. O conteúdo final vira body do epic na organização Zoppy via skill `flow-github-issues` (modo Estruturado). O template oficial `Zoppy-crm/.github/.github/ISSUE_TEMPLATE/epic-roadmap.yml` aplica a label `roadmap` automaticamente quando criado via form — quando criar via `gh issue create --body-file`, passar `--label "roadmap"` manualmente. As 3 seções required do template oficial (`Por que estamos fazendo isso?`, `O que estamos resolvendo?`, `O que está fora do escopo?`) são cobertas pelas seções `Declaração do Problema`, `Solução` + `Decisões de Implementação`, e `Fora do Escopo` deste template — portanto compatíveis.

<prd-template>

## Declaração do Problema

The problem that the user is facing, from the user's perspective.

## Solução

The solution to the problem, from the user's perspective.

## Histórias de Usuário

A LONG, numbered list of user stories. Each user story should be in the format of:

1. Como um <ator>, eu quero <funcionalidade>, para que <benefício>

<user-story-example>
1. Como cliente de banco mobile, eu quero ver o saldo das minhas contas, para que eu possa tomar decisões mais informadas sobre meus gastos
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Decisões de Implementação

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

## Decisões de Teste

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Fora do Escopo

A description of the things that are out of scope for this PRD.

## Observações Adicionais

Any further notes about the feature.

</prd-template>