import { BaseChatModel, type BindToolsInput } from "@langchain/core/language_models/chat_models";
import { AIMessage, ToolMessage, type BaseMessage } from "@langchain/core/messages";
import type { ChatResult } from "@langchain/core/outputs";
import { tool } from "@langchain/core/tools";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

export class DeterministicChatModel extends BaseChatModel {
  public calls = 0;
  public boundToolNames: string[] = [];

  public bindTools(tools: BindToolsInput[]) {
    this.boundToolNames = tools.flatMap((entry) => {
      if ("name" in entry && typeof entry.name === "string") return [entry.name];
      return [];
    });
    return this;
  }

  public _llmType() {
    return "deterministic-stack-spike";
  }

  public async _generate(messages: BaseMessage[]): Promise<ChatResult> {
    this.calls += 1;
    const last = messages.at(-1);
    const message = last instanceof ToolMessage
      ? new AIMessage({ content: `result:${last.content}` })
      : new AIMessage({
        content: "",
        tool_calls: [{ id: "proof-call", name: "double_integer", args: { value: 21 }, type: "tool_call" }],
      });
    return { generations: [{ text: typeof message.content === "string" ? message.content : "", message }] };
  }
}

export function createFakeAgent() {
  const model = new DeterministicChatModel({ callbacks: [], maxRetries: 0 });
  const toolInputs: number[] = [];
  const doubleInteger = tool(({ value }) => {
    toolInputs.push(value);
    return String(value * 2);
  }, {
    name: "double_integer",
    description: "Double an integer deterministically without I/O",
    schema: z.object({ value: z.number().int() }),
  });
  const agent = createDeepAgent({
    model,
    tools: [doubleInteger],
    systemPrompt: "Run the deterministic proof tool and return its result.",
  });
  return { agent, model, toolInputs };
}
