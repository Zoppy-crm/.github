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
  `on("error", ...)` e `stop({ graceful: true, timeout: 5000 })`.
- Os exemplos mantêm as assinaturas e flags exercitadas; o schema de fila do ensaio é `spike_jobs`,
  enquanto `os_jobs` é somente nome ilustrativo, sujeito à configuração do projeto.

Foram medidos rollback/commit conjunto e oito jobs persistidos consumidos por dois clientes após
fechar graciosamente o produtor. Não foram medidos RLS, crash abrupto de worker ativo, fencing,
LISTEN/NOTIFY ou duplicação de efeito externo. Não extrapole essas provas para exactly-once.
