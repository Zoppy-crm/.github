# Fontes e limites

Esta referência registra a correção das skills locais; a cópia vendorizada não foi alterada.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Opções Better Auth](https://www.better-auth.com/docs/reference/options),
  [sessão](https://www.better-auth.com/docs/concepts/session-management) e
  [API](https://www.better-auth.com/docs/concepts/api): cotejadas com Better Auth **1.7.14**,
  `dist/api/{dispatch.mjs,routes/session.mjs}`, `dist/oauth2/{utils,link-account}.mjs` e
  `@better-auth/core/dist/types/init-options.d.mts`. A doc genérica não garante cifragem de
  `idToken` nessa versão. Detalhes e fontes de segurança em `os-auth-session/references/sources.md`.
- [Utilitários pg-boss](https://pgboss.io/api/utils): planos SQL conferidos na **12.38.0**,
  `dist/index.d.ts`, `dist/contractor.js` e `dist/plans.js`; instalação como dona, flags runtime
  e limites em `os-jobs/references/sources.md`.
- [Roles Drizzle](https://orm.drizzle.team/docs/rls) e
  [Kit generate](https://orm.drizzle.team/docs/drizzle-kit-generate): ORM **0.45.4**,
  `pg-core/roles.js`, e Kit **0.31.11**, `api.js`/`bin.cjs` (serializer e comando generate).
- Correção do dono: OS é interno com uma organização só. Membership de times, capacidades,
  audiência e Master têm fonte única na aplicação, sem plugin de organização Better Auth.
  Essa é decisão de produto; exemplos oficiais não a ampliam. Nenhuma nova API foi adicionada
  a esta skill de roteamento; a conferência registra as APIs corrigidas nas skills locais.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
