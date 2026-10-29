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
- [PostgreSQL: configuração local](https://www.postgresql.org/docs/current/functions-admin.html):
  `set_config(setting_name, new_value, is_local)` e `current_setting`; `true` limita à transação.
- [PostgreSQL: RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html): policies,
  dono, superuser/BYPASSRLS, `USING` e `WITH CHECK`.
- [decimal.js: projeto oficial](https://github.com/MikeMcl/decimal.js) e
  [referência](https://mikemcl.github.io/decimal.js/): import ESM, construtor, `plus` e `toString`.
- [Drizzle: tipos PostgreSQL](https://orm.drizzle.team/docs/column-types/pg): `numeric`.
  Não configure `mode: 'number'` para dinheiro.

O ensaio confirmou commit/rollback/conexão transacional. Não testou RLS; a role de inicialização
usada nele tinha privilégios administrativos. Configuração local/RLS/decimal foram conferidos na
documentação oficial, sem alegar uma execução de teste de isolamento ou cálculo de produção.
