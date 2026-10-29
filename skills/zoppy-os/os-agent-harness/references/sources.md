# Fontes e limites

## Base incorporada

- Arquitetura do OS: `docs/architecture/estrutura-de-diretorios.md` e `docs/architecture/model.c4`.
  O conteúdo necessário está incorporado na skill; não depende desses arquivos para ser aplicado.
- Ensaio Bun/TS validado em 28/10/2026: `spikes/bun-stack/README.md`, `package.json` e arquivos
  identificados abaixo. Resultado registrado na fonte: 13 testes e 56 verificações, não uma nova
  execução feita ao criar esta skill. Não equivale a backend de produção ou políticas aprovadas.
- [Especificação Agent Skills](https://agentskills.io/specification): formato, frontmatter e recursos.

## APIs

- Ensaio: `src/fake-agent.ts` e `tests/agent.test.ts`: `createDeepAgent`, `agent.invoke`,
  `BaseChatModel`, `BindToolsInput`, `ChatResult`, `AIMessage`, `ToolMessage`, `tool` e Zod.
- O asset reproduz esse arquivo validado, inclusive `bindTools`, `_llmType` e `_generate`.
  O teste e preload derivam de `tests/agent.test.ts` e `tests/offline.ts`.
- Referências oficiais registradas no ensaio:
  [Deep Agents JavaScript](https://docs.langchain.com/oss/javascript/deepagents/quickstart) e
  [BaseChatModel](https://reference.langchain.com/javascript/langchain-core/language_models/chat_models/BaseChatModel).
  As APIs do exemplo são confirmadas pelo código do ensaio, sem depender de evolução dessas páginas.

O ciclo com modelo local é real e determinístico. Não mede qualidade/preço de provider, callbacks
de uso em falha, cancelamento, retomada persistida, privacidade persistida ou isolamento de processos. A skill não
prescreve API não verificada de saver, interrupção ou instrumentação de provider; confirme e teste
a chamada oficial da versão fixada quando essa integração entrar na fatia.

## Conferência da correção — 2026-10-29

Documentação oficial atual consultada na web e comparada com o código/tipos fixados em
`spikes/bun-stack/node_modules/` do worktree `fatia-01-spec` do Zoppy OS.

- [Deep Agents TS: quickstart](https://docs.langchain.com/oss/javascript/deepagents/quickstart):
  criação/invocação. Conferidos exports e implementação em `deepagents/dist/index.d.ts`,
  `dist/agent-*.d.ts` e `dist/langsmith-*.js` da 1.16.0; o asset local exporta `createFakeAgent`,
  não a tool interna. O exemplo agora usa esse export, sem alterar o asset oficial do ensaio.
- Correção do dono: threads/checkpoints são autorizados pela aplicação por pessoa/escopo na
  única organização; instruções de produção vêm de configuração validada ou do catálogo.

A conferência de fonte não substitui prova de login real, grants no banco ou operação de produção.
