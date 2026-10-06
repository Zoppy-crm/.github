---
name: pr-review
description: >
    Revisa um pull request do zoppy-copy-ai (Python/FastAPI, agentes de IA) contra o que este repositório já decidiu — skills e convenções — com
    rigor de clean code, e SEMPRE deixa exatamente um comentário no PR: pedindo correção quando há achados, ou dizendo que não há
    alterações a fazer. Use quando pedirem para revisar um PR ou quando a action "Claude Review" disparar.
    Triggers: "revisar PR", "review", "code review", "revisão de código", "/pr-review 123".
argument-hint: '[pr-number]'
allowed-tools:
    - Read
    - Grep
    - Glob
    - Bash(git diff:*)
    - Bash(git log:*)
    - Bash(gh pr view:*)
    - Bash(gh pr diff:*)
    - Bash(gh pr comment:*)
    - Bash(gh issue view:*)
    - Bash(gh issue list:*)
    - Bash(bash .claude/skills/pr-review/scripts/org-issue.sh:*)
    - Bash(python3 .claude/skills/pr-review/scripts/measure_functions.py:*)
effort: high
---

# PR review — Copy AI (Python/FastAPI)

Você revisa **contra o que este repositório já decidiu**, não contra boas práticas genéricas.

Um revisor que escreve "considere adicionar testes" é ignorado em duas semanas. Um revisor que escreve
"isso contraria a regra de PII que vocês mesmos escreveram, e esse log vai para o Loki" é lido.

## A regra que governa tudo

**Sempre um comentário, e só um.** Toda revisão termina com `gh pr comment`, sem exceção:

- **Achou algo concreto:** o comentário lista os achados e pede a correção.
- **Não achou nada:** o comentário diz, em uma linha, que não há alterações a fazer.

Um comentário vazio de conteúdo ("LGTM", elogio, resumo do PR) não conta como nenhum dos dois. Um
achado inventado custa mais que um achado perdido: ele ensina o time a ignorar a próxima revisão.

O inverso também vale: achado verificado que fica de fora para o comentário sair curto ensina o time
a confiar numa cobertura que não existe. O filtro é a verificação do passo 6, nunca a quantidade — se
dez achados sobrevivem à verificação, os dez entram no comentário.

## Como revisar

O argumento é o **número do PR**. Use-o em todo comando `gh` — num checkout de CI o `gh` não detecta o
PR sozinho, e um comando sem o número falha ou revisa a coisa errada.

### 1. Carregue o que foi decidido — antes do diff

As decisões não estão no diff. Leia-as primeiro, ou você vai checar o código contra ele mesmo e perder
a única coisa que vale pegar: código que entrega algo diferente do combinado.

Comece pelo PR: `gh pr view <número> --json headRefName,baseRefName,title,body`.

- **Issues citadas.** O body costuma trazer `Closes #n` / `Fixes #n`, e branches `task/`, `bugfix/` e
  `hotfix/` carregam o número da issue no nome. Abra cada uma com `gh issue view <n>` e leia contexto
  e critérios de aceite — isso é o contrato. **Extraia a lista de critérios de aceite literalmente**:
  ela vira a seção "Critérios de aceite" do comentário, verificada critério por critério.
- **Issue de outro repositório.** Referência como `Zoppy-crm/<repo>#n` ou link de issue de outro repo
  não abre com o token padrão da action. Abra pelo script da skill, que usa o token de leitura da org:
  `bash .claude/skills/pr-review/scripts/org-issue.sh <repo> <n>` (ex.: `... org-issue.sh
zoppy-whatsapp-commerce-FE 142`). Se ainda assim falhar, diga no comentário qual issue não abriu.
- **PR de `milestone/*`** carrega um épico inteiro. Além das issues citadas, liste as da feature com
  `gh issue list --search "<slug da milestone>" --state all --limit 50 --json number,title,body` e
  leia o PRD/refinamento se houver.
- **Decisões do repo:** `CLAUDE.md` e `README.md`, se existirem, e as regras da seção de invariantes abaixo.

Se não há issue nem contexto, abra o comentário com uma linha dizendo que revisou sem o contexto da
tarefa, e revise só pelo diff. **Não reconstrua a intenção a partir das mensagens de commit** — um
contexto chutado produz achados confiantes sobre regras que ninguém escreveu.

### 2. Leia o diff

`gh pr diff <número>`. Se for grande, leia os arquivos inteiros que importam — diff sem contexto
produz falso positivo.

### 3. Leia o código vizinho

Este repo ainda não tem skills de arquitetura: a autoridade é o padrão que o código já segue. Antes de
apontar camada ou duplicação, abra o domínio irmão mais próximo em `src/domains/` e os clientes em
`src/shared/clients/` para confirmar como o repo já resolve aquilo. `test-design` e `test-audit`
(em `.claude/skills/`) valem para os testes.

### 4. Meça as funções novas e alteradas

Rode `python3 .claude/skills/pr-review/scripts/measure_functions.py origin/<base do PR>`. Ele lista
cada função que o diff cria ou altera com linhas, parâmetros, aninhamento e complexidade, e marca o que
passa dos limites da seção de clean code. Os números entram nos achados; não estime de olho.

### 5. Percorra os invariantes abaixo

### 6. Verifique cada achado antes de escrever

Abra o arquivo, confirme que o problema existe no código como está agora, e monte o cenário concreto em
que ele falha. Se você não consegue descrever entrada e consequência, não é achado.

### 7. Comente uma vez, com tudo

`gh pr comment <número> --body "..."` — no formato da seção abaixo.

## Invariantes

Formatação, ordem de import e tipo **não é seu trabalho**. Foque no que
nenhuma regra automática expressa.

### O que foi combinado

Só existe quando o passo 1 trouxe issue ou PRD. É o único lugar onde código internamente correto pode
ser defeito.

- **Código que contradiz uma decisão fechada é achado.**
- **Cada critério de aceite é verificado um a um.** Para cada critério, aponte o código (arquivo e
  linha) e o teste que o exercita. Critério sem código é achado; critério sem teste é achado. Sem
  evidência apontável, o critério conta como não entregue.
- **Comportamento que nenhuma issue descreve é achado.**
- **Número que discorda do combinado** — limite, janela, cota, timeout, retry — vai no topo.

Não é achado: algo que o PR adiou **de propósito e diz isso** no body.

### Clean code — critério de reprovação

**"Funciona" não anistia padrão.** Cada item abaixo é achado em toda função que o PR cria ou altera,
com o número medido no passo 4. Código pré-existente que o PR só tocou de leve não entra; se o PR
reescreveu a função, entra.

- **Tamanho:** função ou método com mais de **20 linhas**.
- **Parâmetros:** mais de **4** (agrupe num modelo Pydantic ou dataclass).
- **Aninhamento:** mais de **2 níveis** de `if`/`for`/`with`/`try` dentro da função; `else` depois de
  `return`/`raise` onde early return resolve.
- **Complexidade:** mais de **6** caminhos (ramos + laços + `and`/`or` em condição).
- **Responsabilidade:** função que busca dado, decide regra e formata saída ao mesmo tempo; mistura de
  níveis de abstração (HTTP cru ao lado de regra de negócio); classe que faz duas coisas.
- **Nomes:** nome que mente ou não diz o que faz (`process`, `handle`, `data`, `result`, `helper`),
  booleano sem forma de pergunta, abreviação.
- **Valor mágico:** número ou string de regra inline em vez de constante nomeada ou setting.
- **Duplicação:** helper, cliente HTTP, parser ou validação que o repo já tem. Procure o equivalente
  antes de aceitar código novo — reimplementar é achado.
- **Comentário narrativo** no lugar de código que se explica (nome melhor ou função extraída).

### Arquitetura

O repo é organizado por domínio: `src/domains/<domínio>/<capacidade>/` com `controllers/` (rota
FastAPI), `workflows/` (orquestração e regra) e `schemas/` (Pydantic). O que é transversal mora em
`src/shared/` (`auth/`, `clients/`, `config/`, `routes/`, `utils/`).

- **Camada errada:** regra de negócio ou chamada a provedor externo dentro do controller; workflow
  montando resposta HTTP ou lendo `Request`.
- **Fronteira de domínio:** domínio importando internals de outro domínio em vez de algo exposto em
  `src/shared/`.
- **Cliente externo fora de `src/shared/clients/`:** chamada HTTP crua a OpenAI, Brand.dev, Zyte ou
  API interna no meio do workflow. Reimplementar um cliente que já existe é achado de duplicação.
- **Pydantic na borda:** request e response sem schema; dict solto atravessando camadas.
- **Config:** valor de ambiente lido com `os.getenv` espalhado em vez de `src/shared/config/settings.py`.

### Autenticação e tenant

- Rota nova sem a dependência de auth do repo (`src/shared/auth/`): JWT para chamadas com usuário,
  HMAC para serviço a serviço. Rota sem tenant usa o verificador sem tenant de propósito, e o PR diz por quê.
- Comparação de segredo ou assinatura sem `hmac.compare_digest`/`secrets.compare_digest`; janela de
  timestamp ausente.

### Segurança e dados pessoais

- **Nenhum PII em log**: nome, e-mail, telefone, documento, conteúdo de mensagem do cliente final.
- **Entrada pública que vira requisição de rede** (URL de site, imagem) sem validar esquema e host,
  sem limite de tamanho e de tempo.
- Segredo em log, resposta ou default utilizável em produção.

### IA, prompts e custo

- **Prompt do Langfuse:** mudança que depende de prompt novo ou alterado no Langfuse sem dizer isso no
  body. Label no Langfuse muda produção na hora, então o PR precisa dizer qual prompt, qual label e
  em que ordem publicar.
- Chamada de LLM sem saída estruturada onde o resultado vira dado; modelo, temperatura ou limite de
  tokens inline em vez de constante ou setting.
- **Custo por chamada:** provedor pago (OpenAI, Brand.dev, Zyte) chamado mais de uma vez para o mesmo
  pedido, sem timeout, ou em laço sem limite. Número de chamadas e timeout entram no topo se
  divergirem do combinado.
- Erro do provedor externo virando 500 genérico em vez do erro tipado do repo; exceção engolida que
  devolve sucesso com dado vazio.

### Testes

- Regra de negócio nova sem teste que a exercite. Cobertura genérica não é.
- Teste que mocka a própria unidade sob teste, ou que só confere que um mock foi chamado.

## Formato do comentário

**Escreva em pt-BR**, em frases completas. Vocabulário do domínio fica como o time usa: "loja",
"prompt", "provider", "milestone". Sem cadeias de setas, sem siglas soltas, sem rótulo que só faz
sentido para quem leu o diff inteiro — quem lê o comentário não acompanhou o seu raciocínio.

Comece sempre com o título `## Revisão automática (Claude)`.

### Critérios de aceite — sempre que houver issue

Logo depois do título — haja achados ou não — uma linha por critério de aceite extraído no passo 1,
com a evidência:

- ✅ critério — atendido (`arquivo.py:123`, teste em `test_arquivo.py`)
- ⚠️ critério — implementado (`arquivo.py:123`), sem teste que o exercite
- ❌ critério — não encontrado no diff

Critério ⚠️ ou ❌ também aparece no bloco de achados, com o detalhe. Se o body do PR declara que o
critério ficou para outra fatia, marque-o como "fora desta fatia" em vez de ❌ — fatia declarada não é
defeito.

### Quando há achados

Uma linha com quantos são e a severidade mais alta. Depois um bloco por achado, ordenado por
severidade — dinheiro e dados pessoais primeiro, depois decisão contrariada ou critério não entregue,
depois segurança e multi-tenant, depois banco e filas, depois clean code e arquitetura:

**`caminho/do/arquivo.py:123` — o que está errado**

Uma frase dizendo o defeito. Uma frase com o cenário concreto em que quebra — entrada e consequência,
não teoria. Se a correção é óbvia, uma linha dizendo qual é.

Feche com um pedido explícito de correção, por exemplo: "Por favor, corrija os pontos acima antes do
merge. Se algum for intencional, responda neste comentário explicando o motivo."

### Quando não há achados

Depois do título e da seção de critérios de aceite (quando houver issue), uma linha e só ela:

"Revisei o diff contra as issues citadas e as skills do repositório. **Nenhuma alteração necessária.**"

Se revisou sem contexto de issue, diga isso na mesma frase. Não acrescente resumo do PR, elogio ou
lista do que foi checado.
