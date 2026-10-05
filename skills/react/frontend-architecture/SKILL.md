---
name: frontend-architecture
description: >
    Estrutura de pastas, camadas e fronteiras, rotas, dono de cada estado e tamanho de componente nos
    frontends React da Zoppy. Use ao criar tela, feature, entidade, rota, provider, ao quebrar um
    componente grande ou ao decidir onde um arquivo mora. Triggers: "nova tela", "feature", "entidade",
    "rota", "router", "estrutura", "onde colocar", "provider", "estado", "state", "arquitetura",
    "componente novo", "boundaries", "fronteira", "max-lines-per-function", "layout", "guard".
---

# Arquitetura — frontends React

React 19 + TypeScript estrito, Vite, TanStack Router (por arquivo, tipado), TanStack Query, Tailwind v4,
Radix, react-hook-form + zod, i18next. Alias `@/` = `src/`.

## Pastas

```
src/
├── main.tsx              # cria o router e a pilha de providers
├── routeTree.gen.ts      # gerado pelo plugin do router (versionado, nunca editado)
├── index.css             # Tailwind v4: tokens no @theme
├── routes/               # árvore de rotas — fina: liga URL, guarda, search e página
│   └── -specs/           # specs de rota; o "-" deixa a pasta fora da árvore
├── app/                  # casca da aplicação
│   ├── providers/        # Query, sessão, i18n, toasts
│   └── layouts/          # onboarding (limpo), painel (menu), pagamento obrigatório
├── entities/<entidade>/  # domínio usado por várias features (agente, conhecimento, company)
│   ├── api/  components/  types.ts
├── features/<feature>/   # um contexto de negócio
│   ├── api/              # hooks de query/mutation e factory de keys — único lugar que fala com a API
│   ├── components/       # componentes que conhecem o domínio da feature
│   ├── pages/            # o que a rota renderiza
│   ├── schemas/          # schemas zod e mappers dos formulários
│   ├── lib/              # funções puras da feature
│   ├── content/          # conteúdo longo (artigos, textos de ajuda)
│   └── types.ts          # tipos derivados dos tipos gerados da API
└── shared/
    ├── ui/               # primitivos de design system, sem domínio
    ├── lib/              # cliente da API, formatadores, cn(), hooks genéricos
    └── config/           # env validado por zod
test/                     # infraestrutura de teste (ver testing)
tools/eslint/             # regras locais de lint e seus specs
```

Crie a pasta só quando o primeiro arquivo precisar dela.

## Camadas e fronteiras (`eslint-plugin-boundaries`, `default: disallow`)

| De         | Pode importar                                   |
| ---------- | ----------------------------------------------- |
| `shared`   | `shared`                                        |
| `entities` | `shared` e **a própria entidade**               |
| `features` | `shared`, `entities` e **a própria feature**    |
| `app`      | `shared`, `entities`, `features`, `app`         |
| `routes`   | tudo                                            |

Consequências, cada uma um erro de lint:

1. **Feature não importa outra feature.** O que duas features usam desce para `entities` (domínio) ou
   `shared` (genérico), ou sobe para `app` (composição de casca).
2. **Feature não importa `app`.** Toast, sessão e afins chegam por hook de `shared` ou por prop.
3. **`shared` não conhece domínio.** Se o componente sabe o que é um agente, ele mora numa entidade
   ou feature.
4. **Só `api/` fala com a rede.** `fetch` e o import de `@/shared/lib/api/client` fora de
   `features/*/api`, `entities/*/api` e `shared/lib/api` são erro (ver data-fetching).

## Rotas (TanStack Router por arquivo)

-   Arquivos em `src/routes/`; o plugin regenera `routeTree.gen.ts`. Pontos separam segmentos e `$param`
    é parâmetro (`app.agente.$id.tsx`). Rota de layout sem caminho começa com `_`.
-   **A rota é fina:** `createFileRoute(path)({ validateSearch?, beforeLoad?, component })` e nada mais.
-   **Guardas ficam no `beforeLoad`**, nunca dentro da página (sessão, company inadimplente → tela de
    pagamento).
-   **Search params são validados por schema zod na rota**, com fallback em vez de erro. Leia com
    `Route.useSearch()`, nunca do `window.location`.
-   O `main.tsx` registra o tipo do router (`interface Register { router: typeof router }`); é isso que
    faz `Link to` e `navigate` checarem o caminho no typecheck.
-   Error boundary na rota raiz e nos layouts mostra a tela de erro genérica sem derrubar a casca.

## Dono de cada estado

| Estado                                        | Onde mora                                             |
| --------------------------------------------- | ----------------------------------------------------- |
| Dado do servidor                              | TanStack Query — nunca copiado para `useState`        |
| O que define qual tela é (ids, filtros, aba)  | params e search params validados da rota              |
| Formulário                                    | react-hook-form                                       |
| Sessão                                        | provider de sessão (`useSession()`)                   |
| UI efêmera (modal aberto, hover)              | `useState` no componente                              |

Não há store global (sem Zustand). Copiar dado do servidor para estado local é bug: duplica a fonte e
envelhece. `useEffect` é último recurso: estado derivado se calcula, dado do servidor é do Query,
evento é handler.

## Componente abaixo de 30 linhas

Componente é função, e o JSX conta. Para caber:

-   **A página compõe.** Extraia subcomponentes para `components/` da feature (um por arquivo, export
    nomeado, `kebab-case.tsx`).
-   **Lógica vira hook** ao lado do componente (`use-wizard.ts`): estado, handlers e derivados de uma
    preocupação.
-   **Decisão vira função pura** em `lib/`; tabela de lookup vira mapa `as const` no módulo.
-   Carregando, vazio e erro saem antes do JSX principal com retorno cedo; cada estado pode ser um
    componente pequeno.
-   Props têm `interface` própria, com campos `readonly`, acima do componente.
-   Nunca "resolva" o limite juntando instruções numa linha ou com `eslint-disable` — quebre a função.

## Mobile

Toda tela nasce com versão de celular. Layout mobile-first; o menu do painel vira menu recolhível no
celular. Os specs de tela renderizam nas duas larguras (ver testing).
