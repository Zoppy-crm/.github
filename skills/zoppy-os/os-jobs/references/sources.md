# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `src/jobs.ts`, `tests/database.test.ts`: `PgBoss`, `fromBunSql(client)`,
  `fromDrizzle(tx, sql)`, `boss.send(queue, data, { db })`, `createQueue`, `start`, `work`,
  `on("error", ...)` e `stop({ graceful: true, timeout })`.
- As assinaturas partem do ensaio; a correção adiciona flags sem DDL no runtime e exige
  schema/timeout configurados. Essas flags são verificadas no código fixado, sem atribuir
  ao ensaio histórico a prova dos grants mínimos ou do novo provisionamento.

Foram medidos rollback/commit conjunto e oito jobs persistidos consumidos por dois clientes após
fechar graciosamente o produtor. Não foram medidos crash abrupto de worker ativo, fencing,
LISTEN/NOTIFY ou duplicação de efeito externo. Não extrapole essas provas para exactly-once.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Construtor](https://pgboss.io/api/constructor), [operações](https://pgboss.io/api/ops),
  [utilitários](https://pgboss.io/api/utils), [filas](https://pgboss.io/api/queues) e
  [adaptadores](https://pgboss.io/api/adapters): pg-boss **12.38.0** conferido em
  `dist/index.{js,d.ts}`, `dist/types.d.ts`, `dist/contractor.js`, `dist/plans.js`,
  `dist/manager.js` e `dist/adapters/`.
- `migrate: false` e `createSchema: false` impedem instalação/migração no runtime;
  `start()` usa `contractor.check`. `getConstructionPlans(schema)` retorna SQL de instalação;
  `getMigrationPlans(schema, version)` parte da versão instalada do schema. Planos gerados
  contêm transações próprias. A role dona instala/provisiona; `create_queue` pode criar partição.
- `createQueue` sem opções usa defaults de `plans.js`/`types.d.ts`. As opções de retry,
  expiração e retenção devem ser explícitas. Retenção segue pendente do dono, sem número escolhido.
  `createQueue` não atualiza opções existentes; `updateQueue` é a API específica para isso.
- [Transações Drizzle](https://orm.drizzle.team/docs/transactions): implementação em
  `drizzle-orm/bun-sql/session.js` 0.45.4. UoW liga enqueue ao mesmo executor.
- Correção do dono: payload só com IDs, sem dados sensíveis; admissão por pessoa/times/capacidades/
  audiência na aplicação. Nenhuma identidade exige role dona em runtime.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
