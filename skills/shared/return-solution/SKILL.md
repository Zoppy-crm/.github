---
name: retorno-solucao
description: Registra o retorno de solução de um card (issue) do Zoppy em dois lugares — field "Retorno de Solução" do Project v2 "Zoppy Engineering" (#7) e um comentário no issue. Use sempre que o usuário pedir "dá o retorno no card", "retorno de solução", "retorno técnico do card", "/retorno-solucao <issue>", "dá esse retorno", ou qualquer variação para fechar/comunicar a resolução de um bug/card. Separa conteúdo alto-nível (campo do project) de explicação técnica (comentário).
---

# Retorno de Solução

Registra o retorno de solução de um card do Zoppy Engineering. Toda vez que o time fecha (ou contorna) um bug/card, o retorno precisa ficar em **dois lugares**:

1. **Field `Retorno de Solução`** do Project v2 "Zoppy Engineering" (#7) — alimenta views/relatórios do time.
2. **Comentário** no próprio issue — garante visibilidade no feed do card para quem acompanha.

## O que NÃO fazer

Não editar a seção `### Retorno de Solução` que aparece no **body do issue** (o template de bug tem essa seção com `_No response_`). O time ignora esse campo do body — o retorno formal é o field do Project v2. Mexer no body não registra no fluxo do time.

## Divisão de conteúdo

Os dois destinos recebem **conteúdos diferentes**, não a mesma coisa copiada:

| Destino | Conteúdo | Público |
| --- | --- | --- |
| **Field "Retorno de Solução"** (project) | Resumo **alto-nível** em 2–4 linhas: o que aconteceu, como foi contornado, qual a resolução definitiva. Sem jargão técnico pesado, sem nomes de arquivo/função. | Produto, CSM, management — lendo em view/planilha |
| **Comentário no issue** | Explicação **técnica detalhada**: sequência do incidente, causa raiz (componentes/fluxo), por que é intermitente, plano de correção, eventuais IDs/links. | Dev/QA acompanhando o card |

Se a solução for trivial (ex: typo, config), o comentário pode ser curto — mas mesmo assim os dois lugares devem ser preenchidos.

## Linguagem

Sempre **português (pt-BR)**, tom direto. Evite marketing/desculpas — o retorno é técnico/operacional.

## IDs fixos (org `Zoppy-crm`, Project "Zoppy Engineering" #7)

- Project ID: `PVT_kwDOCAubUc4BQdrV`
- Field "Retorno de Solução" ID: `PVTF_lADOCAubUc4BQdrVzg-wo9s` (tipo TEXT)

Outros fields TEXT do mesmo project (caso o usuário peça para preencher junto):
- `Evidencias`: `PVTF_lADOCAubUc4BQdrVzg-z4-Y`
- `Tickets IDs`: `PVTF_lADOCAubUc4BQdrVzg-0GPU`

## Como executar

Dado um issue `<N>` no repo `<ORG>/<REPO>` (default `Zoppy-crm/<repo-atual>`):

### 1) Descobrir o item ID do issue dentro do Project #7

```bash
gh api graphql -f query='
query {
  repository(owner: "<ORG>", name: "<REPO>") {
    issue(number: <N>) {
      projectItems(first: 10) {
        nodes { id project { number } }
      }
    }
  }
}'
```

Pegue o `id` onde `project.number == 7`. Se o issue não estiver no project #7, avise o usuário antes de seguir (provavelmente o card está em outro project ou ainda não foi adicionado).

### 2) Setar o field "Retorno de Solução" (alto-nível)

```bash
gh api graphql -f query='
mutation($project:ID!, $item:ID!, $field:ID!, $value:String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project, itemId: $item, fieldId: $field, value: {text: $value}
  }) { projectV2Item { id } }
}' \
-f project="PVT_kwDOCAubUc4BQdrV" \
-f item="<ITEM_ID_DO_PASSO_1>" \
-f field="PVTF_lADOCAubUc4BQdrVzg-wo9s" \
-f value="<TEXTO_ALTO_NIVEL>"
```

### 3) Postar comentário técnico no issue

```bash
gh issue comment <N> --repo <ORG>/<REPO> --body "$(cat <<'EOF'
## Retorno técnico

### O que aconteceu
<sequência do incidente>

### Causa raiz
<componentes, fluxo, por que aconteceu>

### Tratativa
- **Casos pontuais:** <como estão sendo tratados>
- **Solução definitiva:** <plano estrutural / refactor / PR>
EOF
)"
```

Não é obrigatório seguir exatamente esse template — ajuste conforme o caso. O importante é que o comentário seja **técnico** e o campo seja **alto-nível**.

## Checklist antes de postar

Como são ações visíveis (impactam shared state), **sempre confirme o texto com o usuário antes de executar** — principalmente o alto-nível do campo, que aparece em views de management.

- [ ] Alto-nível (campo): 2–4 linhas, sem jargão, cobre: o que aconteceu + contorno + resolução definitiva
- [ ] Comentário: técnico, cobre causa raiz e plano
- [ ] Issue `<N>` e repo conferidos
- [ ] Issue está no Project #7 (passo 1 retornou item com `project.number == 7`)
- [ ] Body do issue **não** foi editado

## Exemplo preenchido

Issue `Zoppy-crm/zoppy-api#6176` — cupom 100% aplicado mas cliente foi cobrada mesmo assim.

**Campo "Retorno de Solução" (alto-nível):**

> Problema intermitente causado por execuções do billing interrompidas no meio do processamento, deixando estado inconsistente (cupom aplicado + fatura zerada + nova fatura cobrada). Casos esporádicos contornados manualmente (estorno/ajuste). A causa raiz será eliminada pela remodelagem do módulo de billing, já em andamento como iniciativa maior — não será entregue como fix pontual neste card.

**Comentário (técnico):**

> ## Retorno técnico
>
> ### O que aconteceu
> O fluxo de billing desta cliente executou de forma inconsistente no dia 10/03:
> 1. Cupom de 100% foi aplicado com sucesso → gerou uma `invoice` zerada para o ciclo.
> 2. Uma execução subsequente do job de billing, no mesmo dia, não reconheceu a invoice zerada como fechamento válido do ciclo e gerou uma segunda `invoice` com valor cheio.
> 3. A segunda invoice seguiu o fluxo normal de cobrança e foi debitada do cartão da cliente.
>
> ### Causa raiz
> O pipeline atual do billing é composto por múltiplas etapas encadeadas e tem dois problemas estruturais:
> - **Falta de idempotência / chave de ciclo**: a geração de invoice não valida de forma atômica se já existe fechamento para `companyId + ciclo`.
> - **Sem lock distribuído por ciclo**: quando uma execução é interrompida no meio (deploy, timeout, retry do BullMQ) e outra entra em seguida, as duas avançam sobre o mesmo ciclo sem se enxergar.
>
> O cenário é intermitente porque depende de cupom aplicado perto do momento de geração da invoice + execução interrompida e reentrante.
>
> ### Tratativa
> - **Casos pontuais:** tratados manualmente via estorno/ajuste.
> - **Solução definitiva:** remodelagem do módulo de billing já em andamento (state machine explícita, chave de idempotência por `companyId + período`, lock distribuído). Não entra como fix pontual deste card.

## Diretrizes

- **Sempre confirme os textos com o usuário antes de postar** — o campo é visível em views de management e o comentário fica no histórico do card.
- Se o usuário pedir só "atualiza o campo" ou só "comenta", respeite o pedido — mas lembre que a convenção completa inclui os dois.
- Se o usuário não especificar a divisão, pergunte se quer alto-nível no campo + técnico no comentário (default) ou outra distribuição.
- Após postar, ecoe ao usuário: link do issue com o comentário + confirmação de que o field foi atualizado.
- Se o issue não estiver no Project #7, avise antes de prosseguir — não adicione o item ao project sem confirmar.
