---
name: flow-start-card
description: Marca o começo do trabalho num card do Project v2 "Zoppy Engineering" (#7) — move o Status para `In progress`, garante assignee e Start date, e avisa de cara o que vai faltar pro Done. Use quando o usuário disser "vou pegar esse card", "peguei a issue", "comecei o card X", "to começando isso", "start no card", "move pra in progress", "/flow-start-card <issue>", ou logo antes de criar a branch de uma issue. Use também, sem o usuário pedir, quando perceber que já há trabalho acontecendo numa issue que continua em `To Do`/`Backlog`.
---

# Começar um card

O ciclo de vida de um card já é coberto nas duas pontas: a criação (campos obrigatórios) e o
Done (o portão do `validate_done`). O meio — "peguei isso, estou mexendo" — não era coberto por
nada, e o efeito é card parado em `To Do` enquanto a branch já existe e o PR já está aberto.
Essa skill fecha essa lacuna.

A mecânica de board (IDs, mutations, tabela do Done) vive em `flow-github-issues`. Esta skill é
o ritual; quando precisar de detalhe de campo que não está aqui, vá lá.

---

## Quando rodar

-   O usuário disse que vai pegar / pegou o card.
-   Você vai criar a branch de uma issue (rode **antes** do `git checkout -b`).
-   Você percebeu trabalho em andamento num card que ainda está em `To Do`/`Backlog` — nesse caso
    avise em uma linha e rode, não espere pedirem.

Não rode para card de outra pessoa sem avisar: mover o status de quem não é você confunde o board.

---

## Passo 1 — Descobrir o número da issue

Na ordem:

1. O argumento (`/flow-start-card 12927`).
2. O nome da branch atual: `task/<feature>/<N>-...`, `bugfix/<N>-...`, `hotfix/<N>-...`.
3. Perguntar. Não adivinhe pelo título.

Confirme que a issue existe e **em qual repo** ela está — o board é da org, e o mesmo número
existe em repos diferentes:

```bash
gh issue view <N> --repo Zoppy-crm/<repo> --json number,title,state,labels,assignees,createdAt
```

## Passo 2 — Achar o item no board

Use GraphQL a partir da issue, não `gh project item-list`: a listagem pagina em centenas de
itens e é lenta. Uma issue pode estar em **mais de um project** (#7 Engineering e #9 Quality
Assurance) — filtre pelo número 7:

```bash
ITEM=$(gh api graphql -f query='
{ repository(owner:"Zoppy-crm",name:"<repo>"){ issue(number:<N>){
  projectItems(first:10){ nodes{ id project{ number } } } } } }' \
  -q '.data.repository.issue.projectItems.nodes[] | select(.project.number==7) | .id')
```

Item vazio = a issue não está no board. Adicione antes de seguir (`flow-github-issues`, Fase 2).

## Passo 3 — Assignee

Se não tiver assignee, assuma o trabalho:

```bash
gh issue edit <N> --repo Zoppy-crm/<repo> --add-assignee @me
```

Se já tiver **outra pessoa**, pare e pergunte. Card com dono é dele.

## Passo 4 — Start date

Se estiver vazia, hoje. Se já tiver data, **não sobrescreva** — a primeira vez que o trabalho
começou é o dado que interessa.

```bash
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {
  projectId: "PVT_kwDOCAubUc4BQdrV", itemId: "'$ITEM'",
  fieldId: "PVTF_lADOCAubUc4BQdrVzg-k1N4", value: { date: "'$(date +%F)'" }
}) { projectV2Item { id } } }'
```

## Passo 5 — Não preencha Estimate nem Horas Gastas

Os dois ficam para o fim, junto com o Done. **Não pergunte agora.**

O motivo é que número estimado antes do trabalho infla. Quem preenche no começo coloca folga
por segurança, e depois as horas reais se acomodam na folga em vez de medirem o que aconteceu —
os dois campos acabam contando a mesma história inventada. Medido no fim, `Estimate` e
`Horas Gastas` são dois dados de verdade e dá para comparar um com o outro.

Eles entram pelo `flow-github-issues` ou pelo `retorno-solucao` quando o card fecha.

Efeito colateral conhecido: item sem `Priority`/`Size`/`Estimate` some do board quando há filtro
ativo. `Priority` e `Size` costumam vir do refinamento, então na prática o card segue visível;
se os três estiverem vazios, avise o usuário em uma linha — não preencha por conta própria.

## Passo 6 — Mover o Status

```bash
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {
  projectId: "PVT_kwDOCAubUc4BQdrV", itemId: "'$ITEM'",
  fieldId: "PVTSSF_lADOCAubUc4BQdrVzg-k0-w", value: { singleSelectOptionId: "46203a32" }
}) { projectV2Item { id } } }'
```

`In progress` = `46203a32`. Os outros status estão na tabela do `flow-github-issues`.

Faça o read-back: releia o Status e confirme que mudou. A mutation responde 200 com item id
mesmo quando o valor não foi aplicado.

## Passo 7 — Dizer o que vai faltar no Done

Antes de encerrar, liste em **duas ou três linhas** o que o `validate_done` vai exigir e ainda
não está lá. Isso é o valor real da skill: o dev descobre a dívida no começo, quando ainda dá
para resolver barato, e não no dia em que o card volta de `Done` sozinho.

Checagem rápida pelas labels do card (a tabela completa está em `flow-github-issues`, 7.0.0):

| Card                                  | Vai exigir                                                       |
| ------------------------------------- | ---------------------------------------------------------------- |
| Qualquer um sem `roadmap`             | `Priority` + `Size` + `Estimate` + ≥1 label `work: *`            |
| `work: bug`                           | **+** `Retorno de Solução` preenchido                            |
| `work: *` (menos `reuniao`)           | **+** `Horas Gastas` (pode ser `0`, não pode ser nulo)           |
| `work: bug`/`work: feature` novo      | **+** ≥1 label `epic: *` (e `origin: *` para bug)                |

"Novo" = criado em ou depois de `2026-04-25` — confira o `createdAt`.

---

## Diretrizes

-   **Uma mensagem no fim**, curta: o que foi movido, o que foi preenchido, o que ficou faltando.
    Não narre passo a passo.
-   **Não invente número** de Estimate nem de Horas Gastas, e não pergunte por eles aqui.
-   **Não mexa em Priority, Size ou Team** se já estiverem preenchidos — esses são decisão de
    quem refinou o card, não de quem pegou.
-   **Não feche nem comente a issue.** Começar um card não gera comentário.
-   Se o card já estiver em `In progress` ou adiante (`Dev Testing`, `PR review`...), não volte o
    status. Diga que já estava e siga.
