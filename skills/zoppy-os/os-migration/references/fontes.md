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
- [PostgreSQL: RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) e
  [configuração local](https://www.postgresql.org/docs/current/functions-admin.html): policies e contexto.

O Kit foi exercitado no ensaio com tabelas de prova/auth. Comparação idêntica desse SQL não
comprova geração automática de grants/policies nem isolamento. Esses SQLs e permissões exigem
revisão e teste real conectado como aplicação após migração pela dona.
