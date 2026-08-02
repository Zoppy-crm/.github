# Português técnico controlado para revisão

Use this contract for reviewer-facing PT-BR. The goal is the Portuguese equivalent of Standard Technical English: short, consistent, unambiguous prose that a Zoppy engineer can read once.

## Rules

1. Use one language per artifact. Do not alternate English and Portuguese headings or connective prose.
2. Prefer active voice and name the actor: “O worker move o job” instead of “é feito o movimento do job”.
3. Put one claim in each sentence. Prefer subject, action, object, consequence.
4. Use the same term for the same concept throughout the stack.
5. Keep code identifiers, product names, and team-established technical terms unchanged. Explain an uncommon term on first use.
6. Rewrite the idea; never translate an English idiom word by word.
7. State the behavior before the abstraction.
8. Separate fact, inference, and open validation need.
9. Avoid promotional or absolute language such as “garante”, “à prova de falhas”, “sem risco”, or “zero regressões” unless the stated evidence proves that exact scope.
10. Read the sentence aloud. If it would sound unnatural in a Zoppy daily, rewrite it from the underlying idea.

## Stable glossary

| Avoid | Prefer |
|---|---|
| freshness / frescor | dado atualizado; atualidade do dado |
| ownership | responsabilidade; camada responsável |
| spine | fluxo central; cadeia de envio |
| caller | consumidor |
| cleanup | liberação; limpeza; etapa final, according to behavior |
| retryable | que permite nova tentativa; use `retryable` only for a code enum/name |
| delayed state | estado `delayed` do BullMQ |
| net LOC | saldo de linhas; +A / -D |
| bundle | guia; pacote local, according to artifact |
| gate | verificação; critério de saída; use `gate` only for an established named gate |
| rollout | implantação gradual; sequência de implantação |
| best effort | tentativa sem interromper o fluxo principal |
| false green | resultado verde incorreto |
| drift | divergência; desatualização |

Accepted team terms include PR, commit, diff, branch, build, worker, job, webhook, payload, hook, deploy, lock, Redis, BullMQ, and Meta. Do not force awkward translations for these.

## Comment pattern

Use compact paragraphs, not translated form labels on every sentence:

> 🤖 [prep] O worker move a falha que permite nova tentativa para o estado `delayed` do BullMQ. Assim, a fila controla o horário e a retomada sem ocupar um worker. O comportamento muda de propósito: a contenção deixa de consumir uma tentativa de falha. Relançar o erro comum marcaria a tentativa como `failed`; esperar com `sleep` prenderia a concorrência.

For a corrective hunk:

> 🤖 [prep] Esta mudança restaura a separação dos contatos bloqueados antes da montagem. A PR #123 removeu essa verificação porque QUERY já filtrava os contatos, mas SHEET e WEBHOOK ainda os devolviam como válidos. O teste desta PR reproduz esse contraste. Colocar a regra no transporte duplicaria uma decisão de campanha; por isso a correção fica no resolver.

The exact `🤖 [prep]` prefix is mandatory. Do not add ordinal text inside it.
