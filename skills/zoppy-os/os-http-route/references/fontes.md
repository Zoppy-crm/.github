# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `src/http.ts` e `tests/http.test.ts`: `Hono`, `.post`, `req.json`, `context.json`,
  `app.request`, Zod `object`, `string`, `trim`, `min`, `max`, `strict` e `safeParse`.
- [Context Hono](https://hono.dev/docs/api/context) e
  [middleware Hono](https://hono.dev/docs/guides/middleware): contexto tipado, montagem e ordem.

O ensaio verifica `/proof`, não uma operação do produto. Método, status, erro e dados reais devem
vir de `packages/contract/zoppy-os.openapi.yaml`; nenhum endpoint do exemplo passa a fazer parte dele.
