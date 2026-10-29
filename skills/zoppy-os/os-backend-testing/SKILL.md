---
name: os-backend-testing
description: >
    Escreve testes do backend Bun/TypeScript do Zoppy OS v2 com bun test, portas falsas,
    Postgres real como role de aplicação, contrato HTTP e fronteiras de imports. Use ao testar
    uma fatia ou escolher o nível de prova. Triggers: "teste backend OS", "bun test",
    "integração Postgres OS", "teste RLS", "teste de arquitetura OS", "porta falsa".
compatibility: Zoppy OS v2; Bun 1.4.3, TypeScript 7.0.2; PostgreSQL real para integração.
metadata:
  author: zoppy
  version: "1.0"
  stack: "bun:test / Bun 1.4.3 / TypeScript 7.0.2 / PostgreSQL / Hono"
---

# Testes do backend OS

## 1. Escolha a prova pelo risco

| Suíte em `apps/api/tests/` | Prova | Não prova |
| --- | --- | --- |
| `unit/` | Invariantes puras e decisões do caso de uso com portas falsas | SQL, RLS, transação ou provider real |
| `integration/` | Banco real: constraints, RLS, UoW, concorrência, enqueue/rollback | Efeito externo único ou política ainda não definida |
| `http/` | Middleware, parsing, caso de uso, mapper, status/corpo do contrato com `app.request` | OAuth Google real ou isolamento se banco foi falso |
| `architecture/` | Imports resolvidos respeitam camadas e assuntos | Correção funcional, autorização em runtime ou ciclo transacional |

Use `bun test` para backend; as regras Vitest/Testing Library/MSW das skills React são do frontend.
Não transporte a meta de cobertura ou o comando npm de outro produto para o backend.

## 2. Teste regra sem banco

Injete portas falsas tipadas e relógio controlado; verifique resultado e efeito observável.
Nomes de teste **em inglês snake_case**, descrevendo comportamento. Evite nomes de método isolados.
Exemplo completo de uma regra pura de identidade:

```typescript
import { expect, test } from "bun:test";

type Person = { readonly status: "pending" | "active" };

function canExecute(person: Person): boolean {
    return person.status === "active";
}

test("pending_person_cannot_execute", () => {
    expect(canExecute({ status: "pending" })).toBe(false);
});
```

Nos casos de uso, use o domínio real e portas falsas; não copie a implementação para o teste.
Cubra recusa sem gravar/enfileirar quando acesso/budget não foi admitido.

## 3. Integre com PostgreSQL real e duas credenciais

1. Use banco descartável próprio, credenciais de teste e limpeza apenas dos recursos criados pela suíte.
   Não rode testes destrutivos em URL genérica ou ambiente compartilhado.
2. A role dona aplica migrações; reconecte **como role de aplicação** para os testes funcionais.
   Confira `current_user`, ownership, superuser/BYPASSRLS e grants reais. `SET` de tenant não
   retira privilégios da dona: teste conectado como dona não prova RLS.
3. Prepare dois tenants e pessoas distintas; prove leitura e escrita autorizadas, negação cruzada,
   negação sem contexto e ausência de vazamento após commit/rollback e reuso do pool.
4. Prove a UoW na mesma conexão: escrita invisível fora antes do commit, persistência após commit
   e rollback de linha/job na mesma transação. Enqueue deve receber `fromDrizzle(tx, sql)`.
5. Para concorrência, use clientes independentes e coordenação determinística. Um fake que devolve
   conflito previamente configurado não prova constraint, locks ou admissão concorrente real.

Não invente algoritmo de reserva/overshoot, DST, atraso, sobreposição, versão, delegação ou retenção
para escrever teste verde. Registre a política pendente e teste o que tem contrato aprovado.

## 4. Teste a rota contra o contrato

Use `app.request(path, { method, headers, body })`, como no ensaio. Atravesse o middleware real
com resolução de sessão injetada. Confira formato/status do YAML canônico, entrada inválida,
sessão ausente, pessoa pendente e privacidade. MSW prova estados da UI, não backend implementado.
O ensaio `/proof` é uma prova de Hono/Zod; não demonstra aderência de uma operação OS.

## 5. Trave a arquitetura pelos imports

Percorra arquivos TS com a infraestrutura de análise disponível no projeto. Resolva imports
relativos, aliases, reexports e imports dinâmicos literais até o destino; inclua `import type`.
Não use só busca textual de um alias. Faça casos de teste do verificador com import permitido
e proibido, incluindo reexport que poderia esconder uma dependência.

Aplique a matriz de `os-backend-architecture`: domínio sem runtime/SDK/I/O; aplicação sem adapters,
entrypoints ou SDK; entrypoints sem adapter concreto/`db`; adapters sem entrypoints/composition;
platform sem negócio. Entre assuntos, negue acesso a tabela/repositório privado do vizinho.
A composição monta os concretos. Ao falhar, informe arquivo, import e regra violada.

## 6. Isole modelo e rede

Teste harness com `BaseChatModel` determinístico (asset de `os-agent-harness`), não com provider pago.
Bloqueie `fetch` e tracing externo no preload. Isso não bloqueia todo transporte de rede: mantenha
também credenciais ausentes e adaptadores externos substituídos. Integração de banco usa somente o
Postgres da suíte. Rode o typecheck separadamente: `bun test` não substitui TS7.

## Anti-padrões

- Mock de SQL chamado de teste de isolamento, role dona como aplicação ou falso que já embute a resposta esperada.
- Teste de arquitetura ignorando aliases, reexports e imports de tipo.
- Snapshot de implementação sem comportamento, sleeps fixos para sincronizar corrida ou modelo pago.
- Afirmar crash recovery, custo real ou exactly-once a partir dos 13 testes do ensaio.

Leia [evidências e limites do ensaio](references/fontes.md) para não ampliar o que já foi demonstrado.
