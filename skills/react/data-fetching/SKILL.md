---
name: data-fetching
description: >
    Como os frontends React da Zoppy falam com o zoppy-api: cliente openapi-fetch com tipos gerados,
    hooks do TanStack Query em api/, factory de query keys, invalidação, contrato de erro (ZoppyException),
    autenticação e modo mock. Use ao buscar ou alterar dados, criar hook em features/*/api, tratar erro da
    API ou gerar os tipos. Triggers: "fetch", "api", "query", "mutation", "useQuery", "useMutation",
    "cache", "invalidate", "erro da api", "errorType", "loading", "openapi", "client", "tipos da api",
    "api:types", "unwrap", "ApiError", "mock".
---

# Dados — frontends React

## O cliente é gerado, nunca escrito à mão

`npm run api:types` baixa o OpenAPI do zoppy-api (`docs-json`) e regenera
`src/shared/lib/api/schema.d.ts` com `openapi-typescript`. O arquivo é versionado e fica fora do lint.
O cliente tipado (`openapi-fetch`) é o `apiClient` de `src/shared/lib/api/client.ts`.

-   Caminho, parâmetros, corpo e resposta vêm do contrato real. Uma quebra de contrato na API quebra o
    typecheck no ponto de uso — é o objetivo. Depois de mudar a API, rode `api:types` e corrija o que o
    typecheck apontar.
-   Nunca redeclare um tipo da API à mão. Derive de `paths` no `types.ts` da feature:

```typescript
import type { paths } from '@/shared/lib/api/schema';

export type Agent = paths['/wpp-commerce/agent']['get']['responses']['200']['content']['application/json'];
```

-   Rota cuja resposta não está documentada no swagger (interface TypeScript sem `@ApiResponse` no
    controller) gera tipo vazio. A correção é documentar a resposta no zoppy-api, não escrever o tipo
    no front.

## Só os hooks de `api/` falam com a rede

Toda chamada mora em `features/<feature>/api/` (ou `entities/<entidade>/api/`) como hook. Componentes
nunca importam o cliente: `no-restricted-imports` no `@/shared/lib/api/client` e `no-restricted-syntax`
contra `fetch(...)` valem fora de `api/` e de `shared/lib/api/`.

Toda resposta passa por `unwrap` (devolve o dado ou lança `ApiError`) ou `unwrapEmpty` (204). O hook
declara o tipo de retorno e sempre repassa o `signal`:

```typescript
export function useAgent(): UseQueryResult<Agent> {
    return useQuery({
        queryKey: agentKeys.detail(),
        queryFn: async ({ signal }: QueryFunctionContext): Promise<Agent> =>
            unwrap(await apiClient.GET('/wpp-commerce/agent', { signal }))
    });
}
```

Nomes em `api/`: `use-<coisa>.query.ts` para uma query, `use-<ação>.mutation.ts` para uma mutation,
`use-<coisa>.mutations.ts` quando o arquivo junta várias relacionadas.

## Query keys

Uma factory por feature em `api/<feature>-keys.ts`. Toda key começa pela raiz da feature, para dar
para invalidar o módulo inteiro:

```typescript
export const agentKeys = {
    all: ['agent'] as const,
    detail: (): readonly ['agent', 'detail'] => [...agentKeys.all, 'detail'] as const,
    documents: (page: number): readonly ['agent', 'documents', number] => [...agentKeys.all, 'documents', page] as const
};
```

-   Nada de array cru no ponto de uso: crie a entrada na factory.
-   Tudo que muda o resultado entra na key (página, filtros, ids).
-   A factory é isenta de `typedef.variableDeclaration` (as tuplas precisam ficar `readonly`) e tem
    spec próprio conferindo o formato e o prefixo.

## Mutations e invalidação

-   Invalide a key mais estreita que pode ter mudado; `<feature>Keys.all` quando várias telas leem o
    mesmo recurso.
-   **Sem update otimista em nada que toque cobrança ou pagamento.** Mostre o estado real ou nada.
-   O componente decide o resultado para o lojista (toast, navegação). O texto do toast é chave de
    tradução (ver ui-and-styling).

## Erros: o contrato do zoppy-api

As exceções tipadas do zoppy-api (`ZoppyException`) respondem:

```json
{ "statusCode": 422, "errorType": "...", "title": "...", "message": "...", "publicDetails": {}, "project": "...", "timestamp": "..." }
```

`unwrap` transforma qualquer falha em `ApiError`, com `status`, `errorType` (quando existe) e o corpo.

-   **`errorType` é a chave estável.** Ramifique por ele quando a tela precisa reagir diferente; nunca
    pelo texto da mensagem.
-   **Cada feature tem um mapa `errorType → chave de tradução`**, com fallback genérico por status
    (4xx: "confira os dados", 5xx: "tente de novo"). Texto técnico nunca vira texto de interface.
-   Resposta sem `errorType` (exceção não tipada do Nest) cai no fallback por status.
-   **401 é do middleware do cliente, nunca do componente**: ele renova a sessão uma vez e repete a
    requisição; se não conseguir, limpa a sessão. Páginas não tratam 401.
-   429 é tratado explicitamente onde a API pode devolver (mensagem de "tente em instantes"), nunca
    pelo fallback genérico.

## Padrões do QueryClient (definidos uma vez no provider)

`staleTime: 30_000`; queries repetem até 2 vezes, **nunca em 4xx**; mutations não repetem. Não
sobrescreva por hook sem motivo. Carregamento é skeleton do layout real, não spinner.

## Modo mock

Com `VITE_USE_MOCKS=true` o app sobe com MSW no navegador, usando os mesmos handlers e fixtures dos
testes (`test/msw/`). Serve para desenvolver tela sem backend; nunca entra no build de produção.
