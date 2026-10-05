---
name: conventions-fe
description: >
    Convenções de código dos frontends React da Zoppy: idioma, TypeScript, regras de lint com os valores
    e o porquê de cada uma, regras locais, isenções, proibição de bypass, nomes de arquivo, commits,
    hooks e fluxo de PR. Use ao escrever qualquer código, ao nomear arquivos, ao receber erro de lint,
    ao commitar ou ao abrir PR. Para estrutura, rotas e estado veja frontend-architecture; para dados,
    data-fetching; para formulários, forms; para UI e i18n, ui-and-styling; para testes, testing.
    Triggers: "eslint", "lint", "regra", "typedef", "tipagem", "max-lines-per-function", "no-else",
    "no-search-in-loop", "no-comments", "no-magic-string-compare", "eslint-disable", "convenção",
    "nome de arquivo", "commit", "PR", "hook".
---

# Convenções — frontends React

## Idioma

A divisão é por **público**, não por tipo de arquivo.

| Inglês                                          | pt-BR                                         |
| ----------------------------------------------- | --------------------------------------------- |
| Identificadores, tipos, nomes de arquivo, rotas | Texto de interface (sempre via i18n)          |
| Chaves de tradução e códigos de erro            | Mensagens traduzidas e de erro para o lojista |
| Skills                                          | Commits, issues, descrição de PR              |
| Mensagens de log                                | Títulos de teste (`it('mostra o motivo…')`)   |

O mesmo conceito tem sempre o mesmo nome em inglês no código. Termo novo de domínio entra no mesmo PR
que o introduz, com o nome em inglês decidido uma vez.

## TypeScript

`strict` com `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noPropertyAccessFromIndexSignature`,
`noImplicitReturns` e `erasableSyntaxOnly` (sem `enum`, sem `namespace`, sem parameter property no
construtor: declare o campo e atribua). O `typecheck` (`tsc -b --noEmit`) cobre app, specs e configs.

## Lint: o que está ligado e por quê

Tudo é `error`. Nenhuma regra fica em `warn`. A CI exige; os hooks só antecipam.

| Área             | Regra e valor                                                                                         | Por quê                                                        |
| ---------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Tamanho          | `max-lines-per-function` **30** (sem linhas em branco), `max-lines` **250**                           | força compor em vez de despejar; JSX conta                     |
| Profundidade     | `max-depth` **2**, `max-nested-callbacks` **3**, `react/jsx-max-depth` **5**, `no-nested-ternary`    | código raso se lê de cima para baixo                           |
| Complexidade     | `complexity` **10**, `sonarjs/cognitive-complexity` **10**, `max-params` **4**                         | uma responsabilidade por função                                |
| Tipagem          | `typedef` em tudo, retorno explícito, `explicit-member-accessibility`, `prefer-readonly`, sem `any`, sem `!` | o tipo é documentação verificada                          |
| Condições        | `switch-exhaustiveness-check`, `strict-boolean-expressions`, `react/jsx-no-leaked-render`              | status novo da API quebra o build; `0` não vaza no JSX         |
| Forma            | sem `enum` (`as const` + union), sem default export, sem barrel file, `eqeqeq`, `curly`, `no-console` | uma forma só; barrel cria ciclo                                |
| Imports          | `import-x/no-cycle`, `simple-import-sort`, `consistent-type-imports`                                  | ciclo vira bug de inicialização                                |
| Fronteiras       | `boundaries` (ver frontend-architecture)                                                              | feature não conhece a outra                                    |
| Strings          | `i18next/no-literal-string` (ver ui-and-styling)                                                      | todo texto passa pela tradução                                 |

`no-inferrable-types` fica desligado de propósito: ele conflita com o `typedef`, e o que vale é anotar
sempre.

### Regras locais (`tools/eslint/rules/`)

| Regra                           | Proíbe                                                                                       | Como resolver                                                       |
| ------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `local/no-else`                 | `else` e `else if`                                                                           | trate a saída primeiro e retorne cedo                               |
| `local/no-search-in-loop`       | `find`/`includes`/`indexOf`/`some`/`every`/`filter` sobre array dentro de iteração; laço dentro de laço | monte um `Map` ou `Set` antes do laço                         |
| `local/no-fixed-color`          | cor arbitrária em classe (`bg-[#…]`) e cor literal em `style`                                 | token do tema                                                       |
| `local/no-comments`             | comentário narrativo                                                                          | o porquê vai no commit, no PR ou na skill                           |
| `local/no-magic-string-compare` | `x === 'pending'`, `case 'pending':` fora de `*.constants.ts` e arquivos de tipo              | compare com a constante do mapa `as const` derivado dos tipos da API |

`no-search-in-loop` é type-aware: busca em `string` passa; código dentro de handler de evento ou de
callback de `setState` passa (não roda durante a iteração); lista dentro de lista sem busca passa.
`no-comments` aceita diretivas de ferramenta (`eslint-*`, `@ts-expect-error <motivo>`,
`@vitest-environment`, `prettier-ignore`, `/// <reference>`) e JSDoc em declaração exportada.

### Isenções de `typedef` — um critério só

`variableDeclaration` fica livre só onde a declaração **é a origem de um tipo derivado** e anotar
destruiria a derivação: `*.schema(s).ts` (`z.infer`), `types.ts`/`*.types.ts` (mapas `as const`),
`shared/config/*.ts`, `**/api/*-keys.ts` (tuplas `readonly`), `routes/**/*.tsx` (árvore de rotas
inferida) e `main.tsx` (registro do router). O resto anota. A chamada de um hook não é isenta:
`const agent: UseQueryResult<Agent> = useAgent();`. `cva(...)` também não: escreva o tipo das
variantes e anote.

O mesmo critério estende a isenção a duas regras vizinhas, e só nesses arquivos:

-   **`*.schema(s).ts` sem tipo de retorno explícito.** O schema é uma factory que recebe `t`
    (`(t) => z.object(...)`), e o tipo do formulário sai do `z.infer` do retorno; anotar o retorno
    destruiria a derivação. Fora de arquivo de schema, anote como `z.ZodType<Saída, Entrada>`.
-   **`routes/**/*.tsx` sem `typedef` nos parâmetros dos callbacks** (`beforeLoad({ context, location })`),
    que o router infere. Ali também `only-throw-error` fica desligado, porque `throw redirect(...)` é o
    padrão do TanStack Router.

### Specs

Tamanho, profundidade, complexidade, `no-else`, `no-search-in-loop`, `no-magic-string-compare` e texto
fixo não valem para specs. `typedef`, `no-comments` e o resto valem.

## Bypass proibido

`eslint-disable` das regras estruturais (tamanho, profundidade, complexidade, fronteiras, strings,
tipagem, as regras locais) é erro. Diretiva sem uso é erro. A saída para um limite é refatorar, nunca
espremer linhas nem desligar a regra.

**Flat config substitui, não mescla.** Um bloco posterior que configura a mesma regra para os mesmos
arquivos troca a configuração inteira. Ao sobrescrever `no-restricted-syntax` num bloco, repita as
restrições de forma (enum, barrel) — senão elas param de valer ali em silêncio. Toda regra nova ganha
caso em `tools/eslint/config.spec.ts`, que roda o lint de verdade sobre fixtures e prova que ela dispara.

## Nomes de arquivo

kebab-case, com sufixo de papel: `agent-card.tsx`, `use-agent.query.ts`, `use-save-agent.mutation.ts`,
`agent-keys.ts`, `agent.schema.ts`, `agent.mapper.ts`, `status.constants.ts`, `agent.types.ts`,
`use-wizard.ts`, `agent-card.spec.tsx`. Um componente por arquivo, export nomeado.

## Git e PR

-   **Conventional commits** (commitlint): `feat:`, `fix:`, `chore:`, `test:`, `refactor:`, `docs:`, `ci:`;
    escopo opcional; assunto em minúsculas.
-   **Hooks** (husky): `pre-commit` roda lint-staged (ESLint `--fix` e Prettier nos staged);
    `commit-msg` roda commitlint; `pre-push` roda `typecheck` e `test`.
-   **Branch de task** a partir da `master` (`task/<milestone>/<n>-<slug>`); o PR vai **contra a
    `master`**, pequeno e com um tema só. Nunca faça push direto na `master`. Confira a branch antes de
    commitar.
-   Descrição do PR em pt-BR: o que entra, **por quê** e como foi testado. "Fecha #n" é para quem lê;
    o GitHub não fecha a issue com texto em português.
-   Mudou uma regra? A skill que a descreve é atualizada no mesmo ciclo, por PR no `Zoppy-crm/.github`.
    Skill editada direto no repo é sobrescrita pela sync.
