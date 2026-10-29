# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `drizzle.config.ts`, `scripts/check-migration.ts`, `tests/database.test.ts` e
  `migrations/`: `defineConfig`, `drizzle-kit generate`, geração temporária/comparação de SQL e
  `migrate` de `drizzle-orm/bun-sql/migrator`.
- [Configuração Drizzle Kit](https://orm.drizzle.team/docs/drizzle-config-file): `schema` aceita
  glob e `out` define saída; o glob foi confirmado na documentação, não no schema único do ensaio.
- [Declaração de schema](https://orm.drizzle.team/docs/sql-schema-declaration): exports e vários arquivos.

O ensaio exerceu o Kit com tabelas de prova/auth. Igualdade do SQL gerado não comprova grants
nem autorização da aplicação. Teste os privilégios reais após migração como dona.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Kit generate](https://orm.drizzle.team/docs/drizzle-kit-generate),
  [config](https://orm.drizzle.team/docs/drizzle-config-file) e
  [roles/schema](https://orm.drizzle.team/docs/rls): ORM **0.45.4**, Kit **0.31.11**.
  Conferidos `drizzle-orm/pg-core/roles.{js,d.ts}`, `policies.d.ts`, `table.d.ts`,
  `bun-sql/migrator.js`, `pg-core/dialect.js`, e `drizzle-kit/{api.js,bin.cjs}`.
  `.existing()` marca `_existing`; o serializer do Kit exclui essas roles da geração.
  O CLI suporta `generate --custom --name`; preserve o layout SQL/snapshots/journal da versão
  fixada, pois a documentação atual mostra também outro formato de diretórios.
- RLS só é opção futura dependente do dono; se aprovada, o ORM/Kit suporta declaração de
  policies no schema. Nenhuma policy foi prescrita como autorização atual. Bootstrap completo
  de roles/grants não é representado pelo Kit fixado e fica em SQL custom separado.
- [Utilitários pg-boss](https://pgboss.io/api/utils) e
  [construtor](https://pgboss.io/api/constructor): 12.38.0, `dist/index.d.ts`,
  `dist/contractor.js`, `dist/plans.js`; planos de instalação/upgrade gerados pelo SDK têm
  fronteiras transacionais próprias. Versionar/aplicar separadamente como dona, sem DDL runtime.
- [CREATE ROLE](https://www.postgresql.org/docs/current/sql-createrole.html) e
  [GRANT](https://www.postgresql.org/docs/current/sql-grant.html): bootstrap, uso do schema e
  privilégios mínimos por tabela/operação. Não conceder a dona nem DDL a `os_app`.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
