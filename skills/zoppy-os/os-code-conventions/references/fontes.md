# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## Tipos e versões

- Ensaio: `package.json`, `tsconfig.json`, `src/public-types.ts` e `README.md`.
- Checker real: TypeScript 7.0.2, `strict`, `exactOptionalPropertyTypes`,
  `noUncheckedIndexedAccess`, ESM, `skipLibCheck: true`; código consumidor verificado.
- Resultado registrado: `typecheck:declarations` com `skipLibCheck: false` falhou com
  **100 diagnósticos** nas declarações de LangChain, pg-boss e Drizzle, incluindo drivers opcionais
  ausentes e inconsistências de tipos. A restrição não foi convertida em teste verde.
- A árvore validada usa `langsmith` 0.9.0; atualizar Core isoladamente pode romper seus peers.
  Sem patches de declaração, overrides ou relaxamento da tipagem autoral.

Nomes ingleses, ausência de comentários/docstrings e erros de negócio como valores são convenções
do backend OS. `skipLibCheck` apenas omite a checagem interna das declarações; não prova que todas
as APIs dos SDKs são compatíveis. O schema financeiro e a reserva concorrente não foram medidos.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Bun: TypeScript](https://bun.com/docs/typescript) e
  [TS: lib](https://www.typescriptlang.org/tsconfig/lib.html): backend sem `lib DOM`,
  mantendo `types: ["bun"]`. Conferidos TypeScript 7.0.2 (`lib/lib.dom.d.ts` e configuração do
  checker) e `@types/bun`/`bun-types` 1.4.3 (`index.d.ts`, `globals.d.ts` e tipos de runtime).
  A configuração anterior do ensaio incluía DOM; a recomendação foi corrigida, sem alegar
  que a configuração original já fazia essa restrição.
- Correção do dono: nada hardcoded para regra configurável, instruções de agente, IDs, domínios,
  listas de pessoas ou URLs; a composição injeta configuração validada/dados de catálogo.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.

Conferência executada em cópia temporária do ensaio: `tsc --version` → `Version 7.0.2` e
`tsc --noEmit` → exit 0 com `lib: ["ES2023"]`, `types: ["bun"]` e flags estritas preservadas.
Incluiu o middleware corrigido e a configuração/chamada de sessão Better Auth, sem tocar o ensaio.
