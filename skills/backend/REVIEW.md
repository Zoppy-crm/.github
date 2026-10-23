# Revisão de PR — Zoppy backend (NestJS)

> Gerado a partir de `Zoppy-crm/.github` (`skills/backend/REVIEW.md`) pela action Sync Skills. Edite lá,
> não aqui.

Você revisa **contra o que este repositório já decidiu**, não contra boas práticas genéricas.

Um revisor que escreve "considere adicionar testes" é ignorado em duas semanas. Um revisor que escreve
"isso contraria a regra que vocês mesmos escreveram na skill `domain`" é lido.

## Carregue o que foi decidido — antes do diff

As decisões estão nas skills em `.claude/skills/<nome>/SKILL.md`. Elas são a autoridade, não a sua
memória. Leia-as antes de olhar o diff, ou você vai checar o código contra ele mesmo.

1. **`pr-review`, seção Invariantes.** É a lista do que procurar neste repositório. As seções sobre
   como comentar (`gh pr comment`, comentário único, formato do comentário) não valem aqui: os achados
   saem no formato do Code Review.
2. **Sempre:** `code-review` (checklist com severidades), `code-conventions` e `clean-code-backend`.
3. **Conforme a área tocada pelo diff:**

- Controller, guard, DTO: `controller`.
- Serviço de aplicação, orquestração entre contextos: `application-service`, `module-architecture`.
- Domain, query, repositório: `domain`, `domain-validation`.
- Migration: `migration`.
- Filas e jobs: `queue-processor`, `queue-scheduler`, `bullmq-flow`.
- Provider, strategy, integração externa: `provider-strategy`.
- Partners API: `partners-api`.
- Specs: `test-design`, `test-audit`.

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

- Dinheiro: cobrança, preço, cupom, limite, retry que cobra ou envia duas vezes.
- Query sem filtro de `companyId` ou endpoint sem o guard que os vizinhos têm.
- Migration que não é aditiva ou que edita migration já aplicada.
- Consulta nova sem a evidência de performance que a skill `domain` exige.
- Dado pessoal ou segredo em log, resposta, erro ou bundle.
- Código que contradiz uma decisão escrita no body do PR, no `CLAUDE.md` ou numa skill.
- Bug que quebra comportamento em produção.

Violação de convenção, camada ou clean code das skills é 🟡 **Nit**, com o nome da skill e da regra.
Nits entram todos os que sobreviverem à verificação: omiti-los transforma o padrão do repo em letra
morta.

## Não reporte

- O que lint, formatação, tipagem e o workflow `pr-standards` já pegam.
- Arquivos em `.claude/`, lockfiles e código gerado.
