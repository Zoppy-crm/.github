---
name: notify-chat
description: Posta notificação padronizada de PR no Google Chat do time via incoming webhook. Use esta skill sempre que abrir um PR e quiser comunicar ao time, quando o usuário pedir "avisa no chat", "posta no chat", "notifica o chat", "manda no chat", "avisa a galera", "/notify-pr <numero>", ou após um `gh pr create`. Gera uma mensagem no formato `[TIPO - AMBIENTE] título` com links clicáveis para a issue e o PR.
---

# Notify Google Chat

Envia notificação padronizada de PR para o Google Chat do time via incoming webhook, em **mensagem de texto simples** (não card). O formato é:

```
*<Nome do autor no GitHub>*
[<TIPO> - <AMBIENTE>] <emoji> <título do PR>

🐛 Issue: <url da issue>
🔀 PR: <url do PR>
```

O nome do autor fica em **negrito** (Google Chat renderiza `*texto*` como bold). O nome/avatar do webhook em si é fixo no Google Chat e não muda por requisição — por isso colocamos o autor no corpo da mensagem.

## Webhook

A URL do webhook é pública (dentro do escopo da org Zoppy) e fica inline neste SKILL.md. Todos os repos privados usam o mesmo space do Google Chat:

```
https://chat.googleapis.com/v1/spaces/AAAAPJ28fBk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=L8nNWbJ2DMQ0WFiHqQiRcJlgq7USxIam-TmDJP0GHro
```

Se precisar rotacionar ou trocar o space, edite a URL acima e a sync de skills propaga para todos os repos.

## Derivação do `<TIPO>` a partir do branch

| Prefixo da branch | TIPO    | Emoji |
| ----------------- | ------- | ----- |
| `hotfix/*`        | BUGFIX  | 🐛    |
| `bugfix/*`        | BUGFIX  | 🐛    |
| `fix/*`           | BUGFIX  | 🐛    |
| `task/*`          | FEATURE | ✨    |
| `feature/*`       | FEATURE | ✨    |
| `feat/*`          | FEATURE | ✨    |
| `milestone/*`     | FEATURE | ✨    |
| `epic/*`          | FEATURE | ✨    |
| `chore/*`         | CHORE   | 🔧    |
| outros            | CHANGE  | 🔀    |

## Derivação do `<AMBIENTE>` a partir da base do PR

| Base              | AMBIENTE  |
| ----------------- | --------- |
| `staging`         | STAGING   |
| `master` / `main` | PROD      |
| `mirror`          | MIRROR    |
| `milestone/*`     | MILESTONE |
| `development`     | DEV       |
| outros            | OTHER     |

## Extração da issue

Procure nessa ordem:

1. `Closes #N`, `Fixes #N`, `Resolves #N` (case-insensitive) no body do PR
2. Regex no nome da branch: `(hotfix|bugfix|fix|task|feature|feat|milestone|epic)/(?:[^/]+/)?(\d+)-` — captura `N`
3. Se não achar, omita a linha `🐛 Issue:` e continue com só o link do PR

O link completo da issue é `https://github.com/<ORG>/<REPO>/issues/<N>` — derive `<ORG>/<REPO>` de `gh repo view --json nameWithOwner -q .nameWithOwner`.

## Como executar

Dado um `<N>` (número do PR) — se o usuário não passar, use o PR mais recente aberto pelo usuário (`gh pr list --author @me --limit 1 --json number`):

```bash
# 1) Detecta o repo atual e faz fetch do PR (incluindo author)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
PR_JSON=$(gh pr view <N> --repo "$REPO" --json number,title,url,headRefName,baseRefName,body,author)

# 2) Derive TIPO, EMOJI, AMBIENTE, ISSUE_URL dos campos (use jq + a lógica das tabelas).
#    AUTHOR_NAME: use .author.name, mas faça fallback para .author.login se name
#    estiver null OU string vazia (GitHub retorna "" quando o usuário não tem display name).
#    Exemplo jq: 'if ((.author.name // "") | length) == 0 then .author.login else .author.name end'

# 3) Monte o texto e poste
WEBHOOK="https://chat.googleapis.com/v1/spaces/AAAAPJ28fBk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=L8nNWbJ2DMQ0WFiHqQiRcJlgq7USxIam-TmDJP0GHro"

TEXT="*${AUTHOR_NAME}*
[${TIPO} - ${AMBIENTE}] ${EMOJI} ${TITLE}"
[ -n "${ISSUE_URL}" ] && TEXT="${TEXT}

🐛 Issue: ${ISSUE_URL}"
TEXT="${TEXT}
🔀 PR: ${PR_URL}"

curl -sS -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg text "$TEXT" '{text: $text}')"
```

**Formatação importante:** `*texto*` vira **bold** no Google Chat (markdown leve). Não usar `**texto**` nem `<b>` — não funciona em mensagens de texto.

Se a issue não for encontrada, omita a linha `🐛 Issue:` e mantenha só o link do PR.

## Exemplo preenchido

Repo `Zoppy-crm/zoppy-api`, branch `hotfix/6288-workflow-task-service` → base `staging`, autor `Lucas Roscoe`:

```
*Lucas Roscoe*
[BUGFIX - STAGING] 🐛 fix(workflow): populate customer/address/order on createTask from customerId

🐛 Issue: https://github.com/Zoppy-crm/zoppy-api/issues/6288
🔀 PR: https://github.com/Zoppy-crm/zoppy-api/pull/6297
```

## Diretrizes

- Não quebre o formato da primeira linha — o time filtra mensagens pelo prefixo `[TIPO - AMBIENTE]`
- Não inclua summary do PR ou descrição técnica — o canal do chat é só alerta; o detalhe fica no PR/issue
- Se o usuário pedir pra repostar com outro texto ou adicionar info, mantenha a primeira linha intacta e concatene abaixo dos links
- Ao postar, confirme ao usuário com o status HTTP (200 = sucesso) e ecoe o texto que foi enviado
