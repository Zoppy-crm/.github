# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `src/database.ts`, `src/jobs.ts`, `tests/database.test.ts`: `SQL`, `drizzle`,
  `db.transaction`, `tx.execute`, insert/select, `sql`, `client.close` e enqueue na transação.
- [decimal.js: projeto oficial](https://github.com/MikeMcl/decimal.js) e
  [referência](https://mikemcl.github.io/decimal.js/): import ESM, construtor, `plus` e `toString`.
- [Drizzle: tipos PostgreSQL](https://orm.drizzle.team/docs/column-types/pg): `numeric`.
  Não configure `mode: 'number'` para dinheiro.

O ensaio confirmou commit/rollback/conexão transacional com privilégios administrativos; não
provou autorização de pessoas ou grants mínimos de produção. A correção abaixo é orientação
verificada nas fontes, não uma alegação de execução dessas provas no banco.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Bun SQL](https://bun.com/docs/runtime/sql),
  [Drizzle Bun.SQL](https://orm.drizzle.team/docs/connect-bun-sql) e
  [transações](https://orm.drizzle.team/docs/transactions): Bun/types **1.4.3** e ORM **0.45.4**,
  `bun-types/sql.d.ts`, `drizzle-orm/bun-sql/{driver,session,migrator}.js`.
  `session.transaction` usa `client.begin` e constrói `tx`; retorno normal confirma a transação.
  O caso de uso chama UoW, o adaptador abre e repositórios/enqueue só recebem executor.
- [Roles Drizzle](https://orm.drizzle.team/docs/rls): `pgRole(...).existing()` existe na 0.45.4;
  Kit 0.31.11 reconhece `_existing` no serializer. Bootstrap de roles/grants segue separado.
- [GRANT PostgreSQL](https://www.postgresql.org/docs/current/sql-grant.html): `os_app` sem DDL,
  ownership ou acesso à dona; `os_owner` migra. Autorização de pessoas é da aplicação, em uma
  organização, testada no domínio e integração. RLS só é possibilidade futura dependente do dono.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
