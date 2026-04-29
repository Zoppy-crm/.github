---
name: flow-bug-card
description: Cria um card de bug no GitHub Issues seguindo o template usado pela organização Zoppy (cabeçalho com cliente/atendente/plano + relato + descrição/comportamento atual/comportamento esperado). Use sempre que o usuário quiser abrir um card de bug, registrar um defeito reportado por cliente, criar uma issue de bug, documentar um problema encontrado em produção. Acione também em frases como "abre um bug", "cria card de bug", "registra esse bug", "abre uma issue de bug", "documenta esse defeito", "cria o card desse bug".
---

# Bug Card

Cria um card de bug no GitHub Issues seguindo o template da organização Zoppy. Diferente de `flow-refinement` (feature/refinement), este fluxo usa um template enxuto focado em sintoma, comportamento atual e esperado — o detalhamento técnico fica pro **retorno de solução** quando o bug for resolvido (ver `flow-bug-solution-reply` / `return-solution`).

## Instruções

O usuário vai descrever o bug. Antes de criar a issue, colete o mínimo necessário (pergunte se não estiver claro):

1. **Repo** — `zoppy-api`, `zoppy-FE` ou outro (ex: `zoppy-app`, `zoppy-command`)
2. **Empresa / cliente reportante** — nome do cliente afetado, ou "N/A" se for interno/QA
3. **Atendente / CSM** — nome de quem repassou, ou "N/A"
4. **Plano** — `Intermediário`, `Avançado`, etc., ou "N/A"
5. **Sintoma** — o que o usuário tentou fazer e o que aconteceu de errado. Pode ser alto nível — não exija reprodução detalhada nem causa raiz; isso vai pro retorno de solução depois
6. **Links** — gravação, ID do registro, screenshot, etc., ou "N/A"
7. **Epic label** — se houver epic relacionado (ex: `epic: whatsapp`, `epic: chat-whatsapp`). Confirme que existe com `gh label list --repo Zoppy-crm/<repo> --search "<termo>"` antes de aplicar

## Título

Formato consistente com os bugs existentes do repo:

```
[<EMPRESA>] [<ÁREA / TELA>] [<descrição curta do problema>]
```

Exemplos:
- `[AIAMI] [MODELOS DE MENSAGENS / WHATSAPP] [Ordem dos cards alterada ao duplicar modelo]`
- `[VINOTECA VINHO PROSA] [MODELOS DE MENSAGENS / WHATSAPP] [Não é possível criar template com Carousel associado]`

Se a empresa for "N/A", use `[INTERNO]` ou descrição da origem.

## Template do body

```markdown
• Atendente: <nome ou N/A>
• Empresa: <empresa ou N/A>
• Plano: <plano ou N/A>

---

**Relato do cliente:**
> <citação do cliente, ou "N/A">

**Interpretação do CSM:**
<reformulação do CSM, ou "N/A">

---

**Descrição:**
<descrição curta e objetiva do bug>

**Comportamento Atual:**
<o que está acontecendo>

**Comportamento Esperado:**
<o que deveria acontecer>
```

Se a informação não existir, escreva "N/A". **Não invente** relato/interpretação se o usuário não forneceu — deixe "N/A".

## Labels

Sempre incluir:

- `work: bug`
- `origin: master`
- `client:report` — se foi reportado por cliente real (empresa preenchida). Se for bug interno/QA, omitir
- `epic: <nome>` — se houver epic relacionado e a label existir no repo

## Criação

```bash
gh issue create --repo Zoppy-crm/<repo> \
  --title "<título no formato acima>" \
  --assignee @me \
  --label "work: bug" --label "origin: master" --label "client:report" --label "epic: <nome>" \
  --body "$(cat <<'EOF'
<body preenchido>
EOF
)"
```

Após criar, **adicionar ao project board** Zoppy Engineering (#7):

```bash
gh project item-add 7 --owner Zoppy-crm --url <URL retornada pelo gh issue create>
```

## Diretrizes

- **Mantenha o card enxuto**. Detalhamento técnico, causa raiz e arquivos afetados **não vão aqui** — vão no `return-solution` / `flow-bug-solution-reply` quando o bug for resolvido
- **Não preencha** seções de detalhamento técnico, critérios de aceite, estratégia de testes ou roteiro de QA — esse template é diferente do refinement
- **Não invente sintoma**. Se o usuário deu pouca informação, peça mais ou registre "N/A" nos campos do relato
- **Confirme labels antes de aplicar** — `gh label list --repo Zoppy-crm/<repo> --search "<termo>"` para validar epic labels
- Sempre incluir `--assignee @me`
- Sempre adicionar ao project 7 após criar

## Diferença vs `flow-refinement`

| Critério | `flow-refinement` | `flow-bug-card` |
|----------|-------------------|-----------------|
| Quando | Nova feature, refinamento técnico, milestone | Bug reportado / defeito |
| Labels | `refinement`, `work: feature` | `work: bug`, `client:report` |
| Template | Resumo / Objetivo / Critérios / Detalhamento técnico extenso | Cabeçalho + Relato + Descrição / Atual / Esperado |
| Detalhamento técnico no card | Sim, exaustivo | Não — vai no retorno de solução depois |

Se o usuário pediu "criar bug" mas descreveu uma feature, redirecione para `flow-refinement`. Se pediu "criar refinamento" mas é claramente um defeito, sugira este fluxo.
