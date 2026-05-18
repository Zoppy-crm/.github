---
name: retorno-solucao
description: Registra o retorno de solução de um card (issue) do Zoppy em dois lugares — field "Retorno de Solução" do Project v2 "Zoppy Engineering" (#7) com texto alto-nível (cliente/CSM), e um comentário técnico no issue (time). Use sempre que o usuário pedir "dá o retorno no card", "retorno de solução", "retorno técnico do card", "/retorno-solucao <issue>", "dá esse retorno", "gera retorno de solução", "retorno pro cliente", ou qualquer variação para fechar/comunicar a resolução de um bug/card. Também acionado automaticamente via hook post-commit em branches `bugfix/*` e `hotfix/*` — nesse caso, o nº da issue vem do nome da branch. Convenção firme: NUNCA editar o body do issue (a seção `### Retorno de Solução` do template é ignorada pelo time).
---

# Retorno de Solução

Registra o retorno de solução de um card do Zoppy Engineering. Toda vez que o time fecha (ou contorna) um bug/card, o retorno precisa ficar em **dois lugares**:

1. **Field `Retorno de Solução`** do Project v2 "Zoppy Engineering" (#7) — alimenta views/relatórios do time.
2. **Comentário** no próprio issue — garante visibilidade no feed do card para quem acompanha.

## O que NÃO fazer

Não editar a seção `### Retorno de Solução` que aparece no **body do issue** (o template de bug tem essa seção com `_No response_`). O time ignora esse campo do body — o retorno formal é o field do Project v2. Mexer no body não registra no fluxo do time.

## Divisão de conteúdo

Os dois destinos recebem **conteúdos diferentes**, não a mesma coisa copiada:

| Destino                                  | Conteúdo                                                                                                                                                                                                                                                  | Público                                           |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Field "Retorno de Solução"** (project) | Resumo **alto-nível** em 2–4 linhas: o que aconteceu, como foi contornado, qual a resolução definitiva. Sem jargão técnico pesado, sem nomes de arquivo/função.                                                                                           | Produto, CSM, management — lendo em view/planilha |
| **Comentário no issue**                  | Explicação **técnica detalhada**: sequência do incidente, causa raiz (componentes/fluxo), por que é intermitente, plano de correção, eventuais IDs/links. Inclui também **casos de teste propostos** — cenários que QA pode rodar pra validar a correção. | Dev/QA acompanhando o card                        |

Se a solução for trivial (ex: typo, config), o comentário pode ser curto — mas mesmo assim os dois lugares devem ser preenchidos.

## Linguagem

Sempre **português (pt-BR)**, tom direto. Evite marketing/desculpas — o retorno é técnico/operacional.

## IDs fixos (org `Zoppy-crm`, Project "Zoppy Engineering" #7)

-   Project ID: `PVT_kwDOCAubUc4BQdrV`
-   Field "Retorno de Solução" ID: `PVTF_lADOCAubUc4BQdrVzg-wo9s` (tipo TEXT)

Outros fields TEXT do mesmo project (caso o usuário peça para preencher junto):

-   `Evidencias`: `PVTF_lADOCAubUc4BQdrVzg-z4-Y`
-   `Tickets IDs`: `PVTF_lADOCAubUc4BQdrVzg-0GPU`

## Acionamento

Dois caminhos de entrada — o processamento é o mesmo, muda só como a issue é identificada:

**Manual** — usuário pede explicitamente ("dá o retorno no card #6176", "/retorno-solucao 6176"). A issue é informada ou confirmada com o usuário.

**Automático via hook post-commit** — em branches `bugfix/*` e `hotfix/*`, um hook em `settings.json` emite uma notificação após `git commit`. Nesse fluxo, extraia o número da issue do nome da branch:

```bash
git branch --show-current
# Padrões esperados: bugfix/123-descricao, hotfix/123-descricao
```

Pegue o primeiro número. Se não conseguir extrair, pergunte ao dev.

Antes de gerar os textos, leia o contexto:

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
gh issue view <NUMERO> --repo Zoppy-crm/<REPO> --json title,body
git diff HEAD~1                # diff do commit que acabou de sair
git diff main...HEAD           # fallback: diff completo da branch
```

Do body da issue, os campos úteis são `### Descrição`, `### Comportamento Atual`, `### Comportamento Esperado`. Do diff, a causa raiz e os arquivos tocados.

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

### Casos de teste propostos (QA)
1. <cenário> → <resultado esperado>
2. <cenário de regressão adjacente> → <resultado esperado>
3. <edge case / estado intermediário> → <resultado esperado>
EOF
)"
```

Não é obrigatório seguir exatamente esse template — ajuste conforme o caso. O importante é que o comentário seja **técnico** e o campo seja **alto-nível**.

### Casos de teste propostos — orientação

A seção é insumo direto pra QA. Cada caso deve ser acionável, com **setup**, **ação** e **resultado esperado** — mas enxuto, não precisa ser um plano de teste formal.

Regras:

-   **Cobrir o happy path da correção** (o cenário que causava o bug, agora funcionando).
-   **Cobrir pelo menos um caso de regressão adjacente** — algo que poderia ter sido quebrado pela mudança. Ex: se o fix alterou o cálculo do cupom, incluir um teste com cupom em cenário que **já funcionava antes** pra garantir que continua.
-   **Quando fizer sentido, cobrir edge case ou estado intermediário** — dados incompletos, timing específico, concorrência, etc.
-   **Sem jargão de código interno.** Use nomes de funcionalidades/telas que QA reconhece no app, não nomes de método/arquivo.
-   **3 a 5 casos é o ponto doce.** Mais que isso vira barulho; menos que isso não cobre regressão.

Se o bug tinha reprodução **intermitente** ou dependente de estado, mencione explicitamente a condição no caso ("após X rodadas do job", "com cupom aplicado no mesmo ciclo", etc.) — senão QA vai testar uma vez, não reproduzir, e fechar como OK.

## Checklist antes de postar

Como são ações visíveis (impactam shared state), **sempre confirme o texto com o usuário antes de executar** — principalmente o alto-nível do campo, que aparece em views de management.

-   [ ] Alto-nível (campo): 2–4 linhas, sem jargão, cobre: o que aconteceu + contorno + resolução definitiva
-   [ ] Comentário: técnico, cobre causa raiz e plano
-   [ ] Comentário inclui **casos de teste propostos** (3–5 cenários acionáveis pra QA)
-   [ ] Issue `<N>` e repo conferidos
-   [ ] Issue está no Project #7 (passo 1 retornou item com `project.number == 7`)
-   [ ] Body do issue **não** foi editado

## Exemplo preenchido

Issue `Zoppy-crm/zoppy-api#6176` — cupom 100% aplicado mas cliente foi cobrada mesmo assim.

**Campo "Retorno de Solução" (alto-nível):**

> Problema intermitente causado por execuções do billing interrompidas no meio do processamento, deixando estado inconsistente (cupom aplicado + fatura zerada + nova fatura cobrada). Casos esporádicos contornados manualmente (estorno/ajuste). A causa raiz será eliminada pela remodelagem do módulo de billing, já em andamento como iniciativa maior — não será entregue como fix pontual neste card.

**Comentário (técnico):**

> ## Retorno técnico
>
> ### O que aconteceu
>
> O fluxo de billing desta cliente executou de forma inconsistente no dia 10/03:
>
> 1. Cupom de 100% foi aplicado com sucesso → gerou uma `invoice` zerada para o ciclo.
> 2. Uma execução subsequente do job de billing, no mesmo dia, não reconheceu a invoice zerada como fechamento válido do ciclo e gerou uma segunda `invoice` com valor cheio.
> 3. A segunda invoice seguiu o fluxo normal de cobrança e foi debitada do cartão da cliente.
>
> ### Causa raiz
>
> O pipeline atual do billing é composto por múltiplas etapas encadeadas e tem dois problemas estruturais:
>
> -   **Falta de idempotência / chave de ciclo**: a geração de invoice não valida de forma atômica se já existe fechamento para `companyId + ciclo`.
> -   **Sem lock distribuído por ciclo**: quando uma execução é interrompida no meio (deploy, timeout, retry do BullMQ) e outra entra em seguida, as duas avançam sobre o mesmo ciclo sem se enxergar.
>
> O cenário é intermitente porque depende de cupom aplicado perto do momento de geração da invoice + execução interrompida e reentrante.
>
> ### Tratativa
>
> -   **Casos pontuais:** tratados manualmente via estorno/ajuste.
> -   **Solução definitiva:** remodelagem do módulo de billing já em andamento (state machine explícita, chave de idempotência por `companyId + período`, lock distribuído). Não entra como fix pontual deste card.
>
> ### Casos de teste propostos (QA)
>
> 1. **Ciclo de billing normal com cupom 100%** — aplicar cupom, rodar o ciclo, conferir que apenas **uma** invoice zerada é gerada e nenhuma cobrança sai no cartão.
> 2. **Regressão: ciclo com cupom parcial (50%)** — cenário que já funcionava. Conferir que a invoice é gerada com o valor com desconto e cobra corretamente no cartão (nada quebrou).
> 3. **Reentrância do job** — forçar duas execuções sequenciais do job de billing pra mesma company no mesmo dia. Esperado: a segunda execução detecta o fechamento e não gera invoice duplicada.
> 4. **Cupom 100% em company com assinatura em redundância** — cupom aplicado num ciclo onde a recurrency foi filtrada pela janela. Esperado: cupom **não** queima, invoice não é gerada.

## Prompts sugeridos (para gerar os textos via Claude)

Só quando o usuário pedir pra **gerar** os textos (e não trouxer eles prontos). Dois prompts distintos, um pra cada destino.

### Texto alto-nível (campo do project)

```
Escreva um retorno de solução ALTO-NÍVEL para o campo "Retorno de Solução" do Project v2.
Público: CSM, produto, management — pessoas não-técnicas lendo em view/planilha.

Regras:
- Português (pt-BR), tom direto, sem desculpas ou marketing.
- 2 a 4 linhas.
- SEM jargão técnico: não mencione "API", "banco", "query", "endpoint", "migration", "função", "variável", nome de arquivo ou de método.
- Cobrir: (a) o que aconteceu, (b) como os casos em aberto estão sendo contornados, (c) qual a resolução definitiva.

Contexto:
- Título do bug: {title}
- Descrição: {description}
- Comportamento atual: {current_behavior}
- Comportamento esperado: {expected_behavior}
- Correção aplicada (diff): {diff}
```

### Comentário técnico (issue)

```
Escreva um comentário TÉCNICO para postar no issue. Público: dev e QA acompanhando o card.

Formato (markdown):
## Retorno técnico
### O que aconteceu — sequência do incidente
### Causa raiz — componente, fluxo, por que aconteceu
### Tratativa — casos pontuais + solução definitiva
### Casos de teste propostos (QA) — 3 a 5 cenários acionáveis, cobrindo happy path + regressão adjacente + edge case se aplicável

Regras:
- Português (pt-BR), tom técnico, direto.
- Pode citar arquivos/métodos/IDs/PRs — o público é técnico.
- Casos de teste SEM jargão de código: use nomes de tela/funcionalidade que QA reconhece no app.
- Se o bug é intermitente, explicite a condição em cada caso ("após X", "com cupom em Y estado").

Contexto:
- Título: {title}
- Descrição: {description}
- Comportamento atual: {current_behavior}
- Comportamento esperado: {expected_behavior}
- Diff: {diff}
```

Sempre mostre os textos gerados pro usuário antes de publicar.

## Diretrizes

-   **Sempre confirme os textos com o usuário antes de postar** — o campo é visível em views de management e o comentário fica no histórico do card.
-   Se o usuário pedir só "atualiza o campo" ou só "comenta", respeite o pedido — mas lembre que a convenção completa inclui os dois.
-   Se o usuário não especificar a divisão, pergunte se quer alto-nível no campo + técnico no comentário (default) ou outra distribuição.
-   Após postar, ecoe ao usuário: link do issue com o comentário + confirmação de que o field foi atualizado.
-   Se o issue não estiver no Project #7, avise antes de prosseguir — não adicione o item ao project sem confirmar.
