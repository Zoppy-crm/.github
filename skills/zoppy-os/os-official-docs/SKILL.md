---
name: os-official-docs
description: >
    Consulta documentação oficial atual e compatível com as versões fixadas da stack backend
    do Zoppy OS v2 antes de usar ou mudar APIs; orienta o uso das skills oficiais e das regras
    de produto locais. Triggers: "API da stack OS", "doc oficial OS", "versão de biblioteca OS",
    "Bun", "TypeScript", "Hono", "Zod", "Better Auth", "Drizzle", "pg-boss", "Deep Agents",
    "LangChain", "LangGraph".
compatibility: Zoppy OS v2; backend Bun/TypeScript; acesso à web e às dependências da versão fixada no projeto.
metadata:
  author: zoppy
  version: "1.0"
  stack: "Bun 1.4 / TypeScript 7 / Hono + Zod / Better Auth / Drizzle + Bun.SQL / Drizzle Kit / pg-boss / Deep Agents TS / LangChain / LangGraph / PostgreSQL"
---

# Documentação oficial da stack

## Regra obrigatória

Antes de usar ou mudar uma API de **Bun, TypeScript, Hono, Zod, Better Auth, Drizzle,
Drizzle Kit, pg-boss, Deep Agents, LangChain ou LangGraph**, consulte a documentação
oficial **atual na web**. Memória do modelo, exemplos vendorizados e posts de terceiros
não substituem essa consulta nem valem como fonte para a API.

1. Leia a versão fixada no `package.json` do pacote/workspace; confira o lockfile e a versão
   instalada. Para Bun, confira também `packageManager`/`engines` e a versão do executável.
2. Abra o índice oficial abaixo, siga até a página da API e selecione a documentação da
   versão fixada. No ecossistema LangChain, use a seção **TypeScript**, não exemplos Python.
3. Se a API é nova no projeto, registre **URL da página consultada, versão e data** na spec
   ou na mensagem de commit. Índice `llms.txt` sozinho não documenta uma chamada específica.
4. Se a documentação atual divergir da versão fixada, prevalece o código e os tipos dessa
   versão em `node_modules/<pkg>` (ou fonte oficial da tag fixada, para o runtime Bun).
   Registre a divergência e a evidência; não atualize dependências implicitamente.
5. Se não conseguir consultar a fonte oficial, registre o bloqueio e não invente a API.

## Fontes oficiais

Índices e páginas abertos na consulta de 2026-10-29; reabra-os a cada implementação.
Os releases do GitHub permitem conferir a tag, mudanças e incompatibilidades da versão usada.

| Projeto | Documentação e o que encontrar | Releases / changelog oficial |
| --- | --- | --- |
| Bun | [llms.txt](https://bun.com/llms.txt): runtime, Bun.SQL, testes e configuração | [oven-sh/bun](https://github.com/oven-sh/bun/releases) |
| TypeScript 7 | [Documentação](https://www.typescriptlang.org/docs/): linguagem, módulos e tsconfig; [notas oficiais do TS 7.0](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/): compilador nativo e migração | [microsoft/TypeScript](https://github.com/microsoft/TypeScript/releases) |
| Hono | [llms.txt](https://hono.dev/llms.txt): rotas, contexto, middleware, validação e testes | [honojs/hono](https://github.com/honojs/hono/releases) |
| Zod | [llms.txt](https://zod.dev/llms.txt): schemas, safeParse, inferência e erros | [colinhacks/zod](https://github.com/colinhacks/zod/releases) |
| Better Auth | [llms.txt](https://better-auth.com/llms.txt): índices por versão, sessão, OAuth, adaptadores e segurança | [better-auth/better-auth](https://github.com/better-auth/better-auth/releases) |
| Drizzle / Drizzle Kit | [llms.txt](https://orm.drizzle.team/llms.txt): ORM, drivers, transações, schema e migrations do Kit | [drizzle-team/drizzle-orm](https://github.com/drizzle-team/drizzle-orm/releases): selecionar o pacote ORM ou Kit |
| pg-boss | [Documentação](https://timgit.github.io/pg-boss/), redireciona para [pgboss.io](https://pgboss.io/): filas, transações, workers, retries e agendamento | [timgit/pg-boss](https://github.com/timgit/pg-boss/releases) |
| Deep Agents TS | [Índice LangChain](https://docs.langchain.com/llms.txt): seguir os subíndices até Build / TypeScript / Deep Agents | [langchain-ai/deepagentsjs](https://github.com/langchain-ai/deepagentsjs/releases) |
| LangChain TS | [Índice LangChain](https://docs.langchain.com/llms.txt): agentes, tools, middleware e dependências TypeScript | [langchain-ai/langchainjs](https://github.com/langchain-ai/langchainjs/releases) |
| LangGraph TS | [Índice LangChain](https://docs.langchain.com/llms.txt): estado, checkpoints, interrupções e retomada TypeScript | [langchain-ai/langgraphjs](https://github.com/langchain-ai/langgraphjs/releases) |

Na verificação de 2026-10-29, não foi encontrada skill oficial publicada de **Bun, Drizzle
ou pg-boss** nas respectivas docs/repositórios oficiais e buscas na web. Para eles, consulte
o `llms.txt`/documentação acima; skills comunitárias não ganham status oficial por usar o nome.

## Mapa das skills

| Skill oficial vendorizada | Cobertura de API | Regras locais complementares |
| --- | --- | --- |
| `deep-agents-core` | Harness e criação/configuração de Deep Agents | `os-agent-harness`, `os-backend-architecture` |
| `deep-agents-memory` | Backends, filesystem, memória e persistência | `os-agent-harness`, `os-persistence` |
| `deep-agents-orchestration` | Subagentes, planejamento e aprovação humana | `os-agent-harness`, `os-jobs` |
| `langchain-dependencies` | Pacotes, compatibilidade e instalação | `os-code-conventions`; preservar versões fixadas |
| `langchain-fundamentals` | Agentes, tools e composição LangChain | `os-agent-harness` |
| `langchain-middleware` | Hooks, saída estruturada e human-in-the-loop | `os-agent-harness`, `os-auth-session` |
| `langgraph-persistence` | Checkpoints, threads, Store e histórico | `os-persistence`, `os-agent-harness` |
| `langgraph-human-in-the-loop` | Interrupt/resume e tratamento de erros | `os-agent-harness`, `os-jobs` |
| `hono` | Rotas, contexto, middleware e helpers | `os-http-route`, `os-auth-session`, `os-backend-testing` |

As nossas `os-*` definem arquitetura/imports, contrato OpenAPI e DTOs, identidade e tenant,
RLS/UoW, dinheiro, migrations, jobs/admissão, limites do harness, testes e convenções TS.
Quando houver conflito, **as nossas mandam nas regras de produto** (inclusive políticas
pendentes, que não recebem default); **as oficiais mandam no uso da API**, conferido na
web e na versão fixada. Nenhum exemplo oficial amplia permissões do produto.

## Better Auth sem redistribuição

`better-auth/skills` não tinha licença na consulta: API GitHub com `license: null`, endpoint
`/license` com HTTP 404 e árvore web sem LICENSE. A proveniência fica no repositório canônico
`Zoppy-crm/.github`, em `skills/zoppy-os-vendor/SOURCES.md` (não distribuído pelo sync).
Não copiamos `better-auth/best-practices` nem `security`.
Para instalação a partir da origem oficial: `npx skills add better-auth/skills`; selecione
somente `better-auth-best-practices` e `better-auth-security-best-practices`.
Este comando é uma orientação, não parte do sync.
Consulte também a [documentação oficial](https://better-auth.com/llms.txt) e aplique `os-auth-session`.
Não instale `organization-best-practices`: pessoa, tenant, times e Master pertencem à aplicação;
owner/admin de organização do Better Auth não vira Master.
