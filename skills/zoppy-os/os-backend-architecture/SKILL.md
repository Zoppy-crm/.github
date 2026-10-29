---
name: os-backend-architecture
description: >
    Organiza o backend Bun/TypeScript do Zoppy OS v2 por camadas e assuntos, define direção
    de imports, portas e composição. Use ao criar uma fatia, escolher onde um arquivo mora
    ou revisar fronteiras entre assuntos. Triggers: "arquitetura backend OS", "nova fatia OS",
    "onde colocar no backend", "porta OS", "composition", "imports backend".
compatibility: Zoppy OS v2; Bun 1.4.3, TypeScript 7.0.2, ESM.
metadata:
  author: zoppy
  version: "1.0"
  stack: "Bun 1.4.3 / TypeScript 7.0.2 / Hono / Drizzle / PostgreSQL"
---

# Arquitetura do backend OS

Ferramenta interna da Zoppy, com uma única organização e uma codebase backend, com três entradas: HTTP, worker e scheduler.
Pessoa ativa/pendente, times, capacidades e audiência são autorização da aplicação, testada no
domínio e na integração. RLS é apenas possibilidade futura, dependente de decisão do dono.
O backend é somente Bun/TypeScript. O frontend mantém suas camadas React em `apps/web`.

## 1. Coloque cada arquivo no seu lugar

```text
apps/api/
├── package.json · drizzle.config.ts
├── src/
│   ├── domain/<assunto>/
│   ├── application/<assunto>/
│   ├── adapters/
│   │   ├── postgres/<assunto>/
│   │   ├── auth/ · jobs/ · agents/ · telemetry/
│   ├── entrypoints/
│   │   ├── http/<assunto>/
│   │   ├── worker/
│   │   └── scheduler/
│   ├── composition/
│   ├── platform/
│   └── main.http.ts · main.worker.ts · main.scheduler.ts
├── db/
│   ├── schema/<assunto>.ts · schema/auth.ts
│   └── migrations/
└── tests/unit/ · integration/ · http/ · architecture/
packages/contract/zoppy-os.openapi.yaml
```

| Conteúdo | Destino dentro de `apps/api/` |
| --- | --- |
| Valores, invariantes e erros de negócio puros | `src/domain/<assunto>/` |
| Caso de uso e contratos estruturais de dependência | `src/application/<assunto>/{acao.ts,ports.ts}` |
| Repositório implementando porta | `src/adapters/postgres/<assunto>/` |
| Unidade de trabalho | `src/adapters/postgres/unit-of-work.ts` |
| Better Auth, pg-boss e Deep Agents | `src/adapters/{auth,jobs,agents}/` |
| Rota, DTO Zod e erro HTTP | `src/entrypoints/http/<assunto>/{routes.ts,dto.ts}` |
| Sessão e tradução comum de erros | `src/entrypoints/http/{session-middleware.ts,errors.ts}` |
| Factories, injeção de UoW e lifecycle | `src/composition/{container.ts,http-app.ts}` |
| Env, client SQL, relógio e logger sem política | `src/platform/` |
| Tabelas e migrações SQL | `db/schema/` e `db/migrations/` |

Crie pastas quando houver arquivo real; não replique uma árvore vazia em cada assunto.
O workspace tem `apps/*` e `packages/*`; tipos do contrato são gerados, nunca editados à mão.

## 2. Respeite a direção dos imports

| Camada | Dependências permitidas |
| --- | --- |
| `domain` | Domínio puro; sem framework, SQL, runtime Bun ou I/O |
| `application` | Domínio e portas da aplicação |
| `adapters` | Portas, domínio, `db/schema` e SDK pertinente; nunca entrypoints/composition |
| `entrypoints` | Casos de uso injetados, DTOs, contrato e framework da entrada; nunca adaptadores ou `db` |
| `composition` | Todas as camadas para montar recursos, implementações e entradas |
| `platform` | Runtime e configuração; sem negócio nem import de `db/schema` |

Somente a composição conhece o conjunto de concretos e faz a ligação entre eles.
Uma porta usa tipos do produto, não `Context`, sessão Better Auth, transação Drizzle ou grafo.

```typescript
export interface AgentCatalog {
    listAuthorized(principal: Principal): Promise<readonly AgentSummary[]>;
}
```

`Principal` e `AgentSummary` são tipos internos do produto, importados de seus módulos.
O caso de uso recebe `AgentCatalog`; a composição injeta o adaptador PostgreSQL.

## 3. Escolha o assunto dono da regra

| Assunto | Responsabilidade |
| --- | --- |
| `identity` | Pessoa pendente/ativa, times e capacidades da organização |
| `catalog` | Agentes, skills, audiência e versões explícitas |
| `projects` | Membros, contexto e ACL do projeto; vínculo não abre conversa pessoal |
| `execution` | Execução, aprovação autenticada de uso único, pausa e retomada com admissão atual |
| `scheduling` | Agenda, ocorrência e tentativa; gerir metadados não autoriza resultado ou execução alheia |
| `governance` | Budget, uso, custo e auditoria; agregados autorizados não expõem conteúdo privado |

Um assunto nunca importa repositório ou tabela de outro: solicita a capacidade por porta pública.
O caso de uso decide a fronteira e abre a transação pela porta de UoW; o adaptador da UoW executa
`db.transaction`. Repositórios e enqueue só recebem o executor transacional. A composição apenas
injeta essas dependências; não abre transação por request nem decide a fronteira do caso de uso.

## 4. Monte e prove a fatia

1. Localize a operação em `packages/contract/zoppy-os.openapi.yaml` e o assunto dono.
2. Implemente regra pura, caso de uso/portas, adaptador e entrada nessa direção.
3. Monte pool, sessão, repositórios, UoW e lifecycle na composição. Cada `main.*` inicia sua entrada.
4. Teste regra com portas falsas, comportamento de banco com Postgres real e imports em `tests/architecture`.
5. Não escolha defaults para reserva/overshoot, atraso/DST/sobreposição, versão fixa versus publicação,
   delegação, retenção ou destino de telemetria. São decisões pendentes do dono; avance na parte independente.

## 5. Nada hardcoded

Regra de negócio configurável, texto de instrução de agente, IDs, domínios, listas de pessoas e URLs
vêm de configuração validada ou de dado do catálogo, nunca de constante no código. A composição
valida e injeta configuração por portas; domínio e aplicação não leem env nem catálogos por I/O direto.
Se faltar um valor ou decisão do dono, mantenha a pendência explícita, sem inventar fallback.
Literais de protocolo e fixtures determinísticas de teste não são configuração de produto.

## Anti-padrões

- Hono, Better Auth, Drizzle, pg-boss ou Deep Agents dentro de domínio/aplicação.
- Rota criando pool, worker acessando tabela diretamente ou SDK definindo autorização.
- `shared` genérico acumulando regras dos seis assuntos; importar tabela do vizinho.
- Transformar as três entradas em microserviços por causa do desenho de pastas.
- Editar a cópia sincronizada em `.claude/skills/`; a fonte canônica é o repositório `.github`.

Consulte [fontes e limites](references/fontes.md) ao revisar a origem destas fronteiras.
