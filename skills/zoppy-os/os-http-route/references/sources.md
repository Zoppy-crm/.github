# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `src/http.ts` e `tests/http.test.ts`: `Hono`, `.post`, `req.json`, `context.json`,
  `app.request`, Zod `object`, `string`, `trim`, `min`, `max`, `strict` e `safeParse`.
- [Context Hono](https://hono.dev/docs/api/context) e
  [middleware Hono](https://hono.dev/docs/guides/middleware): contexto tipado, montagem e ordem.

O ensaio verifica `/proof`, não uma operação do produto. Método, status, erro e dados reais devem
vir de `packages/contract/zoppy-os.openapi.yaml`; nenhum endpoint do exemplo passa a fazer parte dele.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [CSRF](https://hono.dev/docs/middleware/builtin/csrf),
  [CORS](https://hono.dev/docs/middleware/builtin/cors),
  [Request](https://hono.dev/docs/api/request) e
  [Context](https://hono.dev/docs/api/context): Hono 4.13.14,
  `dist/middleware/{csrf,cors}/index.js`, `dist/request.js` e `dist/context.js`.
  `csrf()` não cobre JSON; `req.json()` não impõe media type. A guarda de Origin vale para
  todo método inseguro e CORS usa origem exata/configurada com credenciais, sem curinga.
- [Segurança Better Auth](https://www.better-auth.com/docs/reference/security): cobre rotas
  montadas no handler de auth, sem proteger automaticamente as rotas do produto. Conferidos
  `better-auth/dist/api/middlewares/origin-check.mjs` e configuração basePath da 1.7.14.
- Correção do dono: executor e capacidades vêm do principal; autorização é da aplicação.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
