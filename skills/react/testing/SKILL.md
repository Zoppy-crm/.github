---
name: testing
description: >
    Estratégia de testes dos frontends React da Zoppy: Vitest + Testing Library + MSW, onde ficam os
    specs, os helpers de test/ (setup, render, router, msw, fixtures, viewport, a11y), como mockar a API,
    o que testar em cada nível e a cobertura mínima de 85%. Use ao escrever ou mudar teste. Triggers:
    "teste", "test", "spec", "vitest", "testing library", "msw", "mock", "cobertura", "coverage",
    "renderWithProviders", "renderRouterAt", "fixture", "viewport", "axe", "acessibilidade".
---

# Testes — frontends React

**Vitest + Testing Library (React, user-event, jest-dom) + MSW**, em jsdom.

## Comandos e portões

| Comando              | O que faz                                                      |
| -------------------- | -------------------------------------------------------------- |
| `npm test`           | todos os specs uma vez                                         |
| `npm run test:watch` | modo watch                                                     |
| `npm run test:cov`   | com cobertura v8; **falha abaixo de 85%**                      |
| `npm run typecheck`  | `tsc -b --noEmit`, cobrindo `src`, `test` e `tools`            |

**Cobertura mínima de 85% em lines, branches, functions e statements**, sobre `src/**/*.{ts,tsx}` (sem
specs, `*.d.ts`, `main.tsx` e `routeTree.gen.ts`). É piso, não meta: leia o número do seu diff.

O Vitest roda dois projetos: `app` (jsdom, specs de `src/` e `test/`) e `tooling` (node, specs das
regras de lint em `tools/`).

## Onde fica cada coisa

-   **Spec ao lado do código:** `agent-card.tsx` → `agent-card.spec.tsx`. Só `*.spec.ts(x)` é coletado.
-   **Specs de rota** em `src/routes/-specs/` (o `-` deixa a pasta fora da árvore de rotas).
-   `test/`, na raiz, é infraestrutura compartilhada:
    -   `setup.ts`: jest-dom, `asyncUtilTimeout: 10_000` (abaixo do `testTimeout` de 30 s do projeto `app`),
        MSW com `onUnhandledRequest: 'error'`, `cleanup` e `resetHandlers` depois de cada teste, viewport de
        volta para desktop e os shims do jsdom (pointer capture, `scrollIntoView`, `scrollTo`,
        `IntersectionObserver`, `ResizeObserver`, `matchMedia`);
    -   `render.tsx`: `renderWithProviders(ui, { viewport? })`, com um `QueryClient` novo sem retry;
    -   `router.tsx`: `renderRouterAt(path, { session?, viewport? })`, que monta a árvore de rotas real
        em memória com os providers e devolve o router para conferir `router.state.location`. Como ele
        devolve o router e não um resultado de render, a regra `render-result-naming-convention` do
        `testing-library` fica desligada: chame o retorno de `router`;
    -   `msw/server.ts`: o servidor com as respostas padrão de `src/app/mocks/handlers`, só do que quase
        toda tela chama;
    -   `msw/gate.ts`: `createGate()` devolve `{ opened, open }`; o handler faz `await gate.opened` e segura
        a resposta até o teste chamar `gate.open()`;
    -   `fixtures/`: dados de exemplo tipados com os tipos da feature; `build(base, overrides)`;
    -   `viewport.ts`: `setViewport('mobile' | 'desktop')` (390 e 1280 px);
    -   `a11y.ts`: `expectNoA11yViolations(container)`, que roda o axe no DOM renderizado.
-   **`globals` desligado:** todo spec importa `describe`, `it`, `expect` e `vi` de `vitest`. Por isso o
    `cleanup` é manual no `setup.ts`.
-   Specs importam os helpers de `test/` por caminho relativo; o alias `@/` só aponta para `src`.
-   Títulos de teste em frases pt-BR descrevendo o comportamento ("mostra o motivo da recusa").

## O que testar, em que nível

| Nível        | Escopo                                                              | Ferramenta                              |
| ------------ | ------------------------------------------------------------------- | --------------------------------------- |
| Unitário     | lógica pura: formatadores, máscaras, schemas, mappers, factories de keys, mapa de erro | Vitest (`*.spec.ts`)   |
| Hook         | um hook com o contexto do Query ou do formulário                    | `renderHook` ou `renderWithProviders`   |
| Tela         | a tela se comportando do ponto de vista do lojista                  | RTL + MSW (`*.spec.tsx`)                |
| Rota         | guardas, redirects e search params na árvore real                   | `renderRouterAt`                        |
| Regra de lint| caso válido e inválido de cada regra local                          | `RuleTester` em `tools/eslint/rules/`   |

## Regras

1. **Busque por papel e rótulo**, nunca por classe (`getByRole('button', { name: … })`,
   `getByLabelText(…)`). Difícil de buscar costuma ser difícil de usar: corrija a acessibilidade.
   `data-testid` só em wrapper não semântico, nunca em elemento interativo.
2. **A API é mockada na rede com MSW, nunca com stub de hook de dados.** Resposta por teste com
   `server.use(http.get('*/rota', …))`. Falha devolve o formato real de erro do zoppy-api (`statusCode`,
   `errorType`, `title`, `message`) com o status HTTP certo, para exercitar o `ApiError` e a mensagem
   traduzida de verdade. Requisição sem handler falha o teste: crie o handler em vez de silenciar.
3. **Providers reais.** `vi.mock` de módulo do app (`@/…` ou `./…`) é erro de lint; só biblioteca que a
   rede não alcança (o router, SDKs de navegador, analytics) pode ser mockada. Guarda e navegação real
   se testam com `renderRouterAt`.
4. **Comportamento, não implementação:** "mostra o total depois de carregar", não "chama o useQuery uma
   vez". Refatorar por dentro não pode quebrar teste.
5. **Mínimo por tela:** caminho feliz, estado vazio, erro da API (mensagem traduzida visível) e, se tem
   formulário, uma falha de validação e uma de submit. Mais: a tela renderiza em **celular e desktop**
   e passa no `expectNoA11yViolations`.
6. **Assíncrono com `await screen.findBy…`**; interação com `userEvent.setup()`, sempre com `await`. Sem
   timeout arbitrário; timer falso só de propósito, restaurado no fim. **Estado intermediário** (bolha
   pendente, botão `aria-busy`, esqueleto) se testa com o portão: o handler espera `gate.opened`, o teste
   confere o estado e só então chama `gate.open()`. Nunca com `delay(ms)` do MSW: em máquina lenta a
   resposta chega antes da asserção. Requisição que nunca responde usa `delay('infinite')`.
7. Tipagem estrita nos specs (`typedef` vale para eles).
8. Os limites de tamanho e complexidade não valem para specs, mas `describe` gigante é sinal de spec
   testando coisa demais: empurre setup para helpers nomeados e fixtures.

## O que não testar

Tipos gerados (`schema.d.ts`), `routeTree.gen.ts`, classes do Tailwind, internals do Radix, ou que uma
biblioteca faz o que a documentação dela diz.
