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

Não foram provados RLS, OAuth Google autenticado, budget concorrente, cron/DST/overlap, crash de
worker em efeito, retomada ou comportamento de provider real. O verificador de imports é um requisito
da suíte do produto, não uma ferramenta já exercitada pelo ensaio. Use o parser/resolver disponível
no projeto e confira sua API oficial antes de implementar; a skill não inventa uma API de análise TS.
