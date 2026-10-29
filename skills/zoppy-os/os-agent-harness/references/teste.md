# Teste determinístico do harness

Copie/adapte `assets/deterministic-agent.ts` para a infraestrutura de teste da fatia. O caminho
do import abaixo pressupõe que o arquivo foi colocado em `tests/support/deterministic-agent.ts`.
O modelo e a ferramenta são locais; não requerem chave nem provider pago.

```typescript
import { expect, test } from "bun:test";
import { AIMessage, ToolMessage } from "@langchain/core/messages";
import { createFakeAgent } from "../support/deterministic-agent.ts";

test("executes_model_tool_model_loop_without_provider", async () => {
    const { agent, model, toolInputs } = createFakeAgent();
    const result = await agent.invoke({
        messages: [{ role: "user", content: "Double 21" }],
    }, { callbacks: [], recursionLimit: 8 });
    expect(model.calls).toBe(2);
    expect(model.boundToolNames).toContain("double_integer");
    expect(toolInputs).toEqual([21]);
    const toolResult = result.messages.find((message) => message instanceof ToolMessage);
    expect(toolResult?.content).toBe("42");
    expect(result.messages.at(-1)).toBeInstanceOf(AIMessage);
    expect(result.messages.at(-1)?.content).toBe("result:42");
});
```

Preload baseado no ensaio, a adaptar ao setup do pacote:

```typescript
process.env.LANGSMITH_TRACING = "false";
process.env.LANGCHAIN_TRACING_V2 = "false";
process.env.BETTER_AUTH_TELEMETRY = "0";

Object.defineProperty(globalThis, "fetch", {
    value: () => { throw new Error("network_fetch_forbidden_in_tests"); },
    configurable: false,
    writable: false,
});
```

Execute com `bun --no-env-file test --preload ./tests/offline.ts` após criar esse preload no projeto.
Bloquear fetch não bloqueia todos os sockets; mantenha adaptadores externos falsos e sem credenciais.
Não reutilize esse bloqueio na aplicação de produção. O teste não comprova ACL, privacidade persistida, custo real,
cancelamento, checkpoint ou aprovação: esses comportamentos precisam de provas específicas.
