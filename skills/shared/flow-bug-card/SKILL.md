---
name: flow-bug-card
description: Cria um card de bug no GitHub Issues seguindo o template form-based oficial da organização Zoppy (`bug-report.yml`). Use sempre que o usuário quiser abrir um card de bug, registrar um defeito reportado por cliente, criar uma issue de bug, documentar um problema encontrado em produção. Acione também em frases como "abre um bug", "cria card de bug", "registra esse bug", "abre uma issue de bug", "documenta esse defeito", "cria o card desse bug".
---

# Bug Card

Cria um card de bug no GitHub Issues seguindo o template **form-based** oficial da organização Zoppy (`Zoppy-crm/.github/.github/ISSUE_TEMPLATE/bug-report.yml`). Diferente de `flow-refinement` (feature/refinement), este fluxo usa um template enxuto focado em sintoma, comportamento atual e esperado — o detalhamento técnico fica pro **retorno de solução** quando o bug for resolvido (ver `flow-bug-solution-reply` / `return-solution`).

## Template oficial — fonte da verdade

O template real vive em `Zoppy-crm/.github/.github/ISSUE_TEMPLATE/bug-report.yml` e é um **GitHub Issue Form**. Quando submetido via UI, o GitHub renderiza cada field como `### <Label>` no body do issue, com `_No response_` em campos vazios e `- [ ] / - [x]` em checkboxes. Pra criar via API (`gh issue create`) preservando consistência, **o body precisa imitar esse render exatamente** — usando os mesmos headers e os mesmos placeholders de vazio.

Pra ler o template antes de gerar o body:

```bash
curl -s "https://raw.githubusercontent.com/Zoppy-crm/.github/development/.github/ISSUE_TEMPLATE/bug-report.yml"
```

**Importante:** o template auto-aplica a label `work: bug`, mas quando criado via API ela não é aplicada automaticamente — passar manual via `--label`.

## Instruções

O usuário vai descrever o bug. Antes de criar a issue, colete o mínimo necessário (pergunte só o que não estiver claro pelo contexto):

1. **Repo** — `zoppy-api`, `zoppy-FE`, `zoppy-app`, `zoppy-command`, etc.
2. **ID do Ticket** (opcional) — ID de ticket de suporte, se houver
3. **Atendente** (opcional) — quem repassou o chamado, ou vazio se interno
4. **Empresa** (opcional) — cliente afetado, ou vazio se interno/QA
5. **Descrição** (obrigatório) — descrição clara do bug
6. **Comportamento Atual** (obrigatório) — o que está acontecendo
7. **Comportamento Esperado** (obrigatório) — o que deveria acontecer
8. **Relatado por cliente?** — sim/não (vira a label `client:report` se sim)
9. **Ambiente** (obrigatório) — `Produção`, `Staging` ou `Mirror`
10. **Evidências** (opcional) — links de screenshot/log/vídeo/ID de registro
11. **Blocked** (opcional) — o que está bloqueado por causa do bug
12. **Epic label** (opcional) — se houver epic relacionado (ex: `epic: whatsapp`). Confirme que existe via `gh label list --repo Zoppy-crm/<repo> --search "<termo>"` antes de aplicar

## Título

Formato consistente com os bugs existentes do repo:

```
[<EMPRESA>] [<ÁREA / TELA>] [<descrição curta do problema>]
```

Exemplos:

-   `[AIAMI] [MODELOS DE MENSAGENS / WHATSAPP] [Ordem dos cards alterada ao duplicar modelo]`
-   `[VINOTECA VINHO PROSA] [MODELOS DE MENSAGENS / WHATSAPP] [Não é possível criar template com Carousel associado]`

Se a empresa não foi reportante (bug interno/QA), use `[INTERNO]`.

## Template do body (form-based render)

```markdown
### ID do Ticket

<id ou `_No response_`>

### Atendente

<nome ou `_No response_`>

### Empresa

<empresa ou `_No response_`>

### Descrição

<descrição clara do bug>

### Comportamento Atual

<o que está acontecendo>

### Comportamento Esperado

<o que deveria acontecer>

### Relatado por cliente?

-   [<x ou espaço>] Sim, foi reportado por um cliente

### Ambiente

<Produção | Staging | Mirror>

### Evidências

<links/IDs ou `_No response_`>

### Blocked

<o que está bloqueado ou `_No response_`>
```

**Regras de preenchimento:**

-   Campos vazios → literalmente `_No response_` — isso bate com o render do GitHub.
-   Checkbox marcada → `- [x] Sim, foi reportado por um cliente`. Não marcada → `- [ ] Sim, foi reportado por um cliente`.
-   Dropdown "Ambiente" → escreva apenas o valor (sem `_No response_` mesmo se o usuário não falar — assuma `Produção` se não informado, já que é o default mais comum).
-   **Não invente** descrição/comportamento. Se o usuário deu pouca info, pergunte antes de criar.
-   **Não adicione seções fora do template** (ex: "Relato do cliente", "Interpretação do CSM"). O template oficial não tem esses campos.

## Labels

Sempre incluir:

-   `work: bug`
-   `origin: master`
-   `client:report` — só se "Relatado por cliente?" estiver marcado. Bug interno/QA → omitir.
-   `epic: <nome>` — só se houver epic relacionado e a label existir no repo (formato `epic: <nome>` com espaço após `:`).

## Criação

```bash
gh issue create --repo Zoppy-crm/<repo> \
  --title "<título no formato acima>" \
  --assignee @me \
  --label "work: bug" --label "origin: master" --label "client:report" --label "epic: <nome>" \
  --body "$(cat <<'EOF'
### ID do Ticket

_No response_

### Atendente

<nome ou _No response_>

### Empresa

<empresa ou _No response_>

### Descrição

<descrição>

### Comportamento Atual

<atual>

### Comportamento Esperado

<esperado>

### Relatado por cliente?

- [ ] Sim, foi reportado por um cliente

### Ambiente

Produção

### Evidências

_No response_

### Blocked

_No response_
EOF
)"
```

Após criar, **adicionar ao project board** Zoppy Engineering (#7):

```bash
gh project item-add 7 --owner Zoppy-crm --url <URL retornada pelo gh issue create>
```

E preencher os campos obrigatórios do board (Priority, Size, Estimate, Status, Team, Start date) — ver `flow-github-issues` seção 7. Sem isso o card fica invisível por filtros do board.

## Diretrizes

-   **Body precisa bater com o render do form**. Headers `### <Label>`, `_No response_` nos vazios, checkboxes com `- [ ] / - [x]`. Nada de bullets `•` ou cabeçalhos `**bold:**`.
-   **Mantenha o card enxuto**. Detalhamento técnico, causa raiz e arquivos afetados **não vão aqui** — vão no `return-solution` / `flow-bug-solution-reply` quando o bug for resolvido.
-   **Não invente sintoma**. Se o usuário deu pouca informação, peça mais. Não preencha "Descrição" / "Comportamento Atual" / "Comportamento Esperado" com `_No response_` — eles são obrigatórios pelo template.
-   **Confirme labels antes de aplicar** — `gh label list --repo Zoppy-crm/<repo> --search "<termo>"` para validar epic labels.
-   **Antes de criar, cheque duplicata** — `gh issue list --repo Zoppy-crm/<repo> --search "<keywords>" --state all`. Bugs internos óbvios costumam já estar abertos.
-   Sempre incluir `--assignee @me`.
-   Sempre adicionar ao project 7 após criar e preencher campos obrigatórios.

## Diferença vs `flow-refinement`

| Critério                     | `flow-refinement`                                    | `flow-bug-card`                                                    |
| ---------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------ |
| Quando                       | Nova feature, refinamento técnico, milestone         | Bug reportado / defeito                                            |
| Template oficial             | `technical-refinement.yml`                           | `bug-report.yml`                                                   |
| Labels                       | `refinement`, `work: feature`                        | `work: bug` (+ `client:report` se aplicável)                       |
| Render do body               | Headers do template + seções de detalhamento técnico | Headers do form: Descrição / Atual / Esperado / Ambiente / Blocked |
| Detalhamento técnico no card | Sim, exaustivo                                       | Não — vai no retorno de solução depois                             |

Se o usuário pediu "criar bug" mas descreveu uma feature, redirecione para `flow-refinement`. Se pediu "criar refinamento" mas é claramente um defeito, sugira este fluxo.
