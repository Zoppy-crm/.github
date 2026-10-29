# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `src/auth.ts`, `src/schema.ts`, `tests/database.test.ts`: `betterAuth`,
  `drizzleAdapter(db, { provider: "pg", schema })`, `baseURL`, `basePath`, `secret`,
  `telemetry`, `auth.api.getSession({ headers })` e `auth.handler(request)`.
- [Better Auth: Google](https://better-auth.com/docs/authentication/google):
  `socialProviders.google.clientId/clientSecret`, base URL, callback e escopos adicionais separados.
- [Hono: middleware](https://hono.dev/docs/guides/middleware) e
  [Context](https://hono.dev/docs/api/context): `createMiddleware` de `hono/factory`,
  genéricos de variáveis, `set/get`, `app.use` e encadeamento com `next`.
- [HonoRequest](https://hono.dev/docs/api/request): `context.req.raw` é o Request original.

Google e middleware foram confirmados em documentação oficial. O ensaio confirmou somente
inicialização Drizzle, sessão ausente nula e handler de sessão ausente. Não mediu login Google,
cookie autenticado, renovação/revogação, associação interna ou autorização de produção.
