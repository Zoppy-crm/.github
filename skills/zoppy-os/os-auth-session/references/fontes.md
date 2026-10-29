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

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Opções](https://www.better-auth.com/docs/reference/options),
  [sessão](https://www.better-auth.com/docs/concepts/session-management),
  [segurança](https://www.better-auth.com/docs/reference/security) e
  [API server](https://www.better-auth.com/docs/concepts/api): `trustedOrigins`, cookies,
  cache desligado, janela de revogação com cache, `encryptOAuthTokens` e `returnHeaders`.
- Better Auth 1.7.14: `@better-auth/core/dist/types/init-options.d.mts`,
  `better-auth/dist/cookies/index.mjs`, `dist/api/routes/session.mjs`, `dist/api/dispatch.mjs`,
  `dist/oauth2/utils.mjs`, `dist/oauth2/link-account.mjs` e `dist/db/internal-adapter.mjs`.
  **Limite da versão:** link-account aplica `setTokenUtil` a access/refresh e grava `idToken`
  diretamente. A descrição genérica de cifragem da doc não garante cifragem de idToken nessa versão.
- [Adaptador Drizzle](https://www.better-auth.com/docs/adapters/drizzle) e
  [schema de auth](https://www.better-auth.com/docs/concepts/database): quatro tabelas e acesso
  pelo adaptador. A doc atual mostra `@better-auth/drizzle-adapter`; a 1.7.14 também exporta
  `better-auth/adapters/drizzle` (package.json e `dist/adapters/drizzle-adapter/index.mjs`).
- [CSRF Hono](https://hono.dev/docs/middleware/builtin/csrf),
  [CORS](https://hono.dev/docs/middleware/builtin/cors) e
  [Context](https://hono.dev/docs/api/context): Hono 4.13.14,
  `dist/middleware/{csrf,cors}/index.js`, `dist/context.js` e `dist/types/context.d.ts`.
  CSRF só avalia tipos de formulário; JSON exige guarda de Origin independente. `header` aceita
  `{ append: true }`. `getSetCookie()` é documentado na API server do Better Auth e consta nas
  declarações de fetch de `undici-types` usadas pelos tipos Bun/Node instalados.
- [GRANT PostgreSQL](https://www.postgresql.org/docs/current/sql-grant.html): uso do schema e
  privilégios específicos por tabela/coluna. Verbos de auth foram confrontados com o adaptador
  interno fixado; endpoints adicionais exigem prova dos grants que realmente usam.
- Correção do dono: membership, pessoa pendente/ativa, times, capacidades e audiência pertencem
  à aplicação; sem plugin de organização. Domínio de e-mail é configuração, nunca valor fixo.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
