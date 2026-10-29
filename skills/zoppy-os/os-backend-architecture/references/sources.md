# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## Fronteiras

A árvore, os seis assuntos e a matriz de imports vêm dos dois documentos de arquitetura.
Os rascunhos `docs/proposals/skills/*/SKILL.md` contribuíram com separação de autoridade,
privacidade, erro de borda e efeitos. A transição de runtime dos rascunhos foi descartada:
o backend é somente Bun/TypeScript.

A skill define organização de código, não implantação, algoritmo financeiro, política de agenda,
delegação, retenção ou destino de telemetria. As roles são `os_app` e `os_owner`, conforme correção do dono.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Transações Drizzle](https://orm.drizzle.team/docs/transactions): na 0.45.4,
  `drizzle-orm/bun-sql/session.js` abre a transação com `client.begin` e fornece `tx` ao callback.
  O caso de uso chama a porta de UoW; seu adaptador abre a transação; repositórios e enqueue
  recebem o executor. A composição injeta. `platform` não importa schema; a factory Drizzle
  com schema fica em `adapters/postgres/database.ts`.
- Correção do dono: ferramenta interna com uma organização; autorização da aplicação por
  pessoa, times, capacidades e audiência, testada no domínio/integração. Nada hardcoded:
  regras configuráveis, instruções, IDs, domínios, pessoas e URLs vêm de configuração/catálogo.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
