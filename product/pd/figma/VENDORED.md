# Skills de Figma — vendorizadas (NÃO editar à mão)

As skills abaixo **não são da Zoppy** — são cópias das skills oficiais do plugin/MCP do Figma, mantidas aqui só para o caso de o plugin oficial não estar instalado no setup de Claude usado pelo time:

- `figma-use/` — **pré-requisito obrigatório** de qualquer `use_figma`
- `figma-generate-design/`
- `figma-create-new-file/`
- `figma-create-design-system-rules/`
- `edit-figma-design/`
- `apply-design-system/`
- `sync-figma-token/`
- `rad-spacing/`

## Regras

- **Não edite** esses arquivos manualmente. Eles devem ser sincronizados a partir do upstream (plugin oficial do Figma). Edição à mão gera divergência silenciosa com a versão oficial.
- Se o plugin oficial do Figma **estiver instalado** no ambiente de Claude do time, estas cópias podem ser **removidas** — o Claude usa as oficiais automaticamente.
- A única skill de Figma **própria da Zoppy** nesta pasta é `zoppy-figma-mcp/` (component keys, variable IDs, gotchas e protocolo de execução do DS da Zoppy). Essa **é** mantida e evoluída aqui.

## Por que não foram deletadas

Em 2026-06-09 não foi possível confirmar se o plugin oficial do Figma está instalado no setup do time. Enquanto isso, as cópias ficam como fallback. Quando confirmado que o plugin está disponível, apague as 8 pastas acima e mantenha apenas `zoppy-figma-mcp/`.
