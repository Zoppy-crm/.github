# Revisão de PR — WhatsApp Commerce (Python/FastAPI)

> Gerado a partir de `Zoppy-crm/.github` (`skills/wpp-commerce/REVIEW.md`) pela action Sync Skills. Edite lá,
> não aqui.

Você revisa **contra o que este repositório já decidiu**, não contra boas práticas genéricas.

Um revisor que escreve "considere adicionar testes" é ignorado em duas semanas. Um revisor que escreve
"isso contraria a regra que vocês mesmos escreveram na skill `multi-tenant-context`" é lido.

## Carregue o que foi decidido — antes do diff

As decisões estão nas skills em `.claude/skills/<nome>/SKILL.md`. Elas são a autoridade, não a sua
memória. Leia-as antes de olhar o diff, ou você vai checar o código contra ele mesmo.

1. **`pr-review`, seção Invariantes.** É a lista do que procurar neste repositório. As seções sobre
   como comentar (`gh pr comment`, comentário único, formato do comentário) não valem aqui: os achados
   saem no formato do Code Review. O passo de medir funções com `measure_functions.py` também não vale: você não roda código. Aplique os limites de clean code do `pr-review` lendo a função e cite os números que contou.
2. **Sempre:** `architecture` e `code-conventions`.
3. **Conforme a área tocada pelo diff:**

- Serviço de aplicação: `application-service`.
- Repositório e sessão: `repository-async`, `multi-tenant-context`.
- Endpoint: `fastapi-endpoint`, `pydantic-schema`.
- Migration: `alembic-migration`.
- Agente e tools de IA: `ai-agent`, `ai-tool`.
- Provider de e-commerce: `ecommerce-provider`.
- Specs: `testing`, `test-design`, `test-audit`.

Regra objetiva de skill que o diff viola é achado mesmo quando o código funciona — "funciona" não
anistia padrão. Cite a skill e a regra no achado.

## O que foi combinado

Critério de aceite e decisão de produto vêm da issue, que você não abre daqui. Use o body do PR: se ele
traz o contexto ou os critérios, código que contradiz o que está escrito ali é achado. Algo que o body
diz que ficou para outra entrega, de propósito, não é achado.

## Verifique antes de reportar

Abra o arquivo, confirme que o problema existe no código como está agora e descreva o cenário concreto
em que ele falha — entrada e consequência. Se você não consegue descrever, não é achado. Um achado
inventado custa mais que um achado perdido: ele ensina o time a ignorar a próxima revisão.

## Severidade

🔴 **Important** fica para:

- Dinheiro: pedido, preço, cupom, pagamento, mensagem enviada duas vezes.
- Query ou tarefa sem contexto de tenant (`multi-tenant-context`).
- Migration Alembic que não é aditiva ou que edita revisão já aplicada.
- Task Celery não idempotente: reentrega grava, envia ou cobra duas vezes.
- Dado pessoal ou segredo em log, resposta, erro ou bundle.
- Código que contradiz uma decisão escrita no body do PR, no `CLAUDE.md` ou numa skill.
- Bug que quebra comportamento em produção.

Violação de convenção, camada ou clean code das skills é 🟡 **Nit**, com o nome da skill e da regra.
Nits entram todos os que sobreviverem à verificação: omiti-los transforma o padrão do repo em letra
morta.

## Não reporte

- O que lint, formatação, tipagem e o workflow `pr-standards` já pegam.
- Arquivos em `.claude/`, lockfiles e código gerado.
