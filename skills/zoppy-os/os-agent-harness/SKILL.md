---
name: os-agent-harness
description: >
    Integra Deep Agents TypeScript ao backend Zoppy OS v2 por porta de execução, preservando
    identidade, ACL, budget, efeitos e medição por chamada, com modelo determinístico nos testes.
    Use ao implementar harness, ferramenta ou retomada. Triggers: "createDeepAgent OS",
    "harness OS", "thread interna", "custo por chamada", "modelo determinístico", "agente backend OS".
compatibility: Zoppy OS v2; Bun 1.4.3, deepagents 1.16.0, @langchain/core 1.2.14, LangGraph 1.4.10.
metadata:
  author: zoppy
  version: "1.0"
  stack: "deepagents 1.16.0 / @langchain/core 1.2.14 / @langchain/langgraph 1.4.10 / Bun"
---

# Harness de agentes do OS

## 1. Encapsule o SDK

A porta de execução mora em `application/execution/ports.ts`; a implementação em `adapters/agents/`.
A composição injeta modelo, ferramentas autorizadas e persistência pertinentes. Tipos de mensagem,
grafo, callbacks e saver não atravessam a porta; converta para entrada/resultado internos.

```typescript
import { createFakeAgent } from "../support/deterministic-agent.ts";

const { agent, model, toolInputs } = createFakeAgent();
const result = await agent.invoke({
    messages: [{ role: "user", content: "Double 21" }],
}, { callbacks: [], recursionLimit: 8 });
```

Copie/adapte o [modelo de teste](assets/deterministic-agent.ts) para
`tests/support/deterministic-agent.ts`; o import acima parte de `tests/integration/`.
`createFakeAgent()` é o export real que entrega `agent`, `model` e `toolInputs`; a tool é interna
à factory. O ciclo modelo → ferramenta → modelo é teste determinístico, com fixtures fixas.
Em produção, instruções do agente vêm de configuração validada ou do catálogo, nunca prompt inline.
Esse exemplo não configura execução governada de produção.

## 2. Preserve a autoridade fora do SDK

1. A aplicação decide identidade, ACL, orçamento e política de escrita. Prompt, tool arguments e
   SDK não concedem capacidade. Use somente principal autenticado ou vínculo persistido de execução.
2. Gere a thread interna no servidor e vincule a pessoa e execução autorizada. ID recebido
   do cliente nunca concede acesso. Autorize cada get/list/resume/delete na fachada de estado.
3. Namespace de Store/checkpoint respeita pessoa/escopo. A aplicação autoriza o acesso;
   separe schema e privilégios de persistência. Não use checkpoint como ledger, ACL, fila ou deduplicador.
4. Início e retomada passam pela mesma admissão atual. Aprovação é decisão autenticada, específica
   e consumida uma vez; gerir agenda/projeto não empresta credenciais nem abre conversa privada.
5. Ferramenta de escrita passa por intenção, conta/recurso/destino autorizados, aprovação pertinente
   e chave de idempotência. Timeout após envio possível produz desfecho desconhecido, não retry cego.
6. VFS do agente não é sandbox de processo/rede. Não ofereça ferramenta de execução irrestrita
   supondo isolamento porque arquivos são virtuais.

## 3. Meça toda chamada e preserve uso parcial

O adaptador mede uso/custo por chamada, incluindo roteamento, resumo e subagentes, também quando
a execução falha ou é cancelada. Identifique execução/chamada para não contabilizar duas vezes
na reconciliação. Dinheiro usa decimal.js/`numeric`; nunca `number`.

Não derive custo só da última mensagem nem descarte consumo parcial ao abortar. Se uma falha não
trouxer uso completo, persista o que foi observado e a lacuna para reconciliação; não invente custo
zero. O ensaio não validou callbacks de uso/cancelamento de provider real: confirme a API oficial
e teste a versão usada antes de adicionar instrumentação. Não prescreva um callback inexistente.

Persista admissão/intenção, encerre a transação, invoque o modelo e persista uso/resultado em outra
transação curta. Aprovação humana não mantém conexão transacional reservada.

## 4. Teste sem provider pago

Use subclasse de `BaseChatModel` de `@langchain/core/language_models/chat_models`, implementando
`bindTools`, `_llmType` e `_generate`, como no asset. A ferramenta é local e determinística.
Com `bun test`, confira duas chamadas, tool recebendo 21, `ToolMessage` com `42` e resposta `result:42`.
Veja [teste do ciclo](references/testing.md). Bloqueie rede e tracing externo no setup da suíte.

Esse teste prova integração do harness, não qualidade de modelo, custo real, privacidade da persistência,
aprovação, cancelamento ou recovery. Acrescente provas específicas das fronteiras implementadas.

## 5. Mantenha decisões pendentes explícitas

Algoritmo de reserva/overshoot, delegação, retenção e destino de telemetria não têm default nesta
skill. Não ative LangSmith ou exportação de prompts por instalar o SDK. Auditoria de negócio é
durável no banco e não depende do trace. Não introduza APIs de checkpoint/interrupt/abort copiadas
de exemplos de outra linguagem ou versão sem confirmação oficial.

## Anti-padrões

- SDK definindo executor, acesso, saldo ou escrita; thread como token de autorização.
- Provider pago nos testes ou importar um fake cuja existência não foi confirmada.
- Cancelamento apagando custo, tracing como única auditoria ou transação aberta durante modelo.
- Prometer sandbox, autorização ou exactly-once por recurso do grafo.

Consulte [fontes e limites](references/sources.md) antes de ampliar a superfície do SDK.
