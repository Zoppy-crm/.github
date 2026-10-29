# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs e evidência

- Ensaio: `tests/*.ts`, `src/*.ts`, `README.md` e `package.json`: `bun:test` (`test`, `expect`,
  hooks), `app.request`, transações reais, dois consumidores e bloqueio de fetch no preload.
- O ensaio registrou nove testes sem banco e quatro com Postgres real, somando 13 testes e
  56 verificações. Typecheck do código e regeneração do SQL também passaram na fonte.
- O banco do ensaio usava uma role administrativa própria: a prova transacional é útil,
  mas não substitui os novos testes como aplicação exigidos por esta skill.

Não foram provados autorização persistida, OAuth Google autenticado, budget concorrente, cron/DST/overlap, crash de
worker em efeito, retomada ou comportamento de provider real. O verificador de imports é um requisito
da suíte do produto, não uma ferramenta já exercitada pelo ensaio. Use o parser/resolver disponível
no projeto e confira sua API oficial antes de implementar; a skill não inventa uma API de análise TS.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Transações Drizzle](https://orm.drizzle.team/docs/transactions),
  [GRANT PostgreSQL](https://www.postgresql.org/docs/current/sql-grant.html) e
  [CREATE ROLE](https://www.postgresql.org/docs/current/sql-createrole.html): provas de UoW e
  separação `os_owner`/`os_app`. Conferidos `drizzle-orm/bun-sql/session.js` 0.45.4 e os adapters
  `fromDrizzle`/`fromBunSql` em `pg-boss/dist/adapters/` 12.38.0.
- Correção do dono: a integração atravessa casos de uso com pessoas, times, capacidades e
  audiência da única organização; grants não implementam autorização de pessoas. `platform`
  não importa `db/schema`. Não foi adicionada alegação de prova de produção ao ensaio anterior.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
