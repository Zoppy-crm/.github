---
name: flow-bug-solution-reply
description: Gera o retorno de solução para issues de bug — texto alto nível para o cliente (campo "Retorno de Solução" no Project V2) e detalhe técnico para o time (seção no body da issue). Use sempre que resolver um bug em branches bugfix/* ou hotfix/* ou quando o usuário pedir para gerar o retorno de solução de um bug. Acionado automaticamente via hook após commits nessas branches.
---

# Retorno de Solução

Gera dois textos ao resolver um bug e publica em dois lugares:

| Destino | Audiência | Conteúdo |
|---------|-----------|----------|
| Campo "Retorno de Solução" no **Project V2** | Cliente / CSM | Alto nível, não-técnico, 3-4 frases |
| Seção "Retorno de Solução" no **body da issue** | Time técnico | Causa raiz, o que foi alterado, pontos de atenção |

## Constantes

- **Project ID:** `PVT_kwDOCAubUc4BQdrV`
- **Field ID:** `PVTF_lADOCAubUc4BQdrVzg-wo9s`
- **Org:** `Zoppy-crm`
- **Project Number:** `7`

## Instruções

### 1. Identificar a issue

Tente extrair o número da issue do nome da branch atual:

```bash
git branch --show-current
```

Padrões esperados: `bugfix/123-descricao`, `hotfix/123-descricao`. Extrai o primeiro número da branch.

Se não encontrar, pergunte ao dev: "Qual o número da issue no GitHub?"

### 2. Identificar o repositório

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

### 3. Ler o contexto do bug

```bash
gh issue view <NUMERO> --repo Zoppy-crm/<REPO> --json title,body
```

Do body da issue, extraia as seções:
- `### Descrição`
- `### Comportamento Atual`
- `### Comportamento Esperado`

### 4. Ler o diff da correção

```bash
git diff HEAD~1
```

Se o diff estiver vazio (commit inicial da branch), use:

```bash
git log --oneline -5
git diff main...HEAD
```

### 5. Gerar os dois textos

Use o diff e o contexto do bug para gerar dois textos distintos.

**Texto A — Alto nível (para o cliente):**

Prompt:
```
Você é um assistente que explica correções de bugs para clientes não-técnicos.

Contexto do bug:
- Título: {title}
- Descrição: {description}
- Comportamento atual: {current_behavior}
- Comportamento esperado: {expected_behavior}

Correção aplicada (diff técnico):
{diff}

Escreva um retorno de solução para o cliente em português. Regras:
1. Máximo 3-4 frases
2. Linguagem simples, sem termos técnicos (nada de API, banco de dados, endpoint, migration, função, variável, etc.)
3. Foque no que o cliente vai perceber de diferente
4. Comece com "O problema foi identificado e corrigido."
5. Explique brevemente o que causava o comportamento incorreto (de forma abstrata)
6. Termine com o que o cliente pode esperar agora
```

**Texto B — Detalhe técnico (para o time):**

Prompt:
```
Você é um assistente técnico que documenta correções de bugs para o time de desenvolvimento.

Contexto do bug:
- Título: {title}
- Descrição: {description}
- Comportamento atual: {current_behavior}
- Comportamento esperado: {expected_behavior}

Correção aplicada (diff):
{diff}

Escreva um resumo técnico da correção em português para o time. Inclua:
1. Causa raiz do bug (o que exatamente estava errado)
2. O que foi alterado para corrigir (arquivos, lógica, query, etc.)
3. Qualquer efeito colateral ou ponto de atenção
Seja direto e técnico. Máximo 5-8 frases.
```

### 6. Apresentar ao dev para aprovação

Mostre os dois textos gerados e aguarde aprovação. O dev pode:
- Aprovar (publicar como está)
- Editar o Texto A, o Texto B ou ambos antes de publicar
- Cancelar

### 7. Encontrar o itemId da issue no Project V2

```bash
ITEM_ID=$(gh api graphql -f query='
query($org: String!, $number: Int!) {
  organization(login: $org) {
    projectV2(number: $number) {
      items(first: 200) {
        nodes {
          id
          content {
            ... on Issue {
              number
              repository { name }
            }
          }
        }
      }
    }
  }
}' -f org=Zoppy-crm -F number=7 \
  --jq ".data.organization.projectV2.items.nodes[] | select(.content.number == <NUMERO_ISSUE> and .content.repository.name == \"<REPO>\") | .id")
```

Se `ITEM_ID` estiver vazio, a issue não está no projeto. Avise o dev:
> "A issue #N não está no Project #7. Deseja adicioná-la antes de continuar?"

Para adicionar ao projeto:
```bash
gh project item-add 7 --owner Zoppy-crm \
  --url https://github.com/Zoppy-crm/<REPO>/issues/<NUMERO>
```

Depois re-execute a query para obter o itemId.

### 8. Publicar Texto A no campo do Project V2

```bash
gh api graphql -f query='
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $text: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: { text: $text }
  }) {
    projectV2Item { id }
  }
}' \
  -f projectId=PVT_kwDOCAubUc4BQdrV \
  -f itemId="$ITEM_ID" \
  -f fieldId=PVTF_lADOCAubUc4BQdrVzg-wo9s \
  -f text="<TEXTO_A>"
```

### 9. Publicar Texto B no body da issue

Ler o body atual:

```bash
BODY=$(gh issue view <NUMERO> --repo Zoppy-crm/<REPO> --json body -q .body)
```

Substituir o conteúdo da seção `### Retorno de Solução` pelo Texto B. A seção existe no body no formato:

```
### Retorno de Solução

_No response_
```

Usar o Claude para fazer o replace (mais seguro que sed em conteúdo multilinha):

```bash
gh issue edit <NUMERO> --repo Zoppy-crm/<REPO> --body "<BODY_ATUALIZADO>"
```

Onde `<BODY_ATUALIZADO>` é o body original com o conteúdo entre `### Retorno de Solução` e a próxima `###` (ou fim do body) substituído pelo Texto B.

### Confirmação

Após publicar, confirme ao dev:
- ✅ Campo "Retorno de Solução" no Project V2 atualizado
- ✅ Seção "Retorno de Solução" na issue #N atualizada
