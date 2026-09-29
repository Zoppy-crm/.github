---
name: pr-review
description: >
    Revisa um pull request contra o que este repositório já decidiu — skills, convenções e o bundle OKF — e
    SEMPRE deixa exatamente um comentário no PR: pedindo correção quando há achados, ou dizendo que não há
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
effort: high
---

# PR review — Zoppy backend (NestJS)

Você revisa **contra o que este repositório já decidiu**, não contra boas práticas genéricas.

Um revisor que escreve "considere adicionar testes" é ignorado em duas semanas. Um revisor que escreve
"isso contraria a regra de PII que vocês mesmos escreveram, e esse log vai para o Loki" é lido.

## A regra que governa tudo

**Sempre um comentário, e só um.** Toda revisão termina com `gh pr comment`, sem exceção:

-   **Achou algo concreto:** o comentário lista os achados e pede a correção.
-   **Não achou nada:** o comentário diz, em uma linha, que não há alterações a fazer.

Um comentário vazio de conteúdo ("LGTM", elogio, resumo do PR) não conta como nenhum dos dois. Um
achado inventado custa mais que um achado perdido: ele ensina o time a ignorar a próxima revisão.

## Como revisar

O argumento é o **número do PR**. Use-o em todo comando `gh` — num checkout de CI o `gh` não detecta o
PR sozinho, e um comando sem o número falha ou revisa a coisa errada.

### 1. Carregue o que foi decidido — antes do diff

As decisões não estão no diff. Leia-as primeiro, ou você vai checar o código contra ele mesmo e perder
a única coisa que vale pegar: código que entrega algo diferente do combinado.

Comece pelo PR: `gh pr view <número> --json headRefName,baseRefName,title,body`.

-   **Issues citadas.** O body costuma trazer `Closes #n` / `Fixes #n`, e branches `task/`, `bugfix/` e
    `hotfix/` carregam o número da issue no nome. Abra cada uma com `gh issue view <n>` e leia contexto
    e critérios de aceite — isso é o contrato.
-   **PR de `milestone/*`** carrega um épico inteiro. Além das issues citadas, liste as da feature com
    `gh issue list --search "<slug da milestone>" --state all --limit 50 --json number,title,body` e
    leia o PRD/refinamento se houver.
-   **Bundle OKF.** Se o PR toca uma área listada em `/index.md`, leia o `overview.md` e os concepts
    dela: regra de negócio registrada lá é decisão fechada.

Se não há issue nem contexto, abra o comentário com uma linha dizendo que revisou sem o contexto da
tarefa, e revise só pelo diff. **Não reconstrua a intenção a partir das mensagens de commit** — um
contexto chutado produz achados confiantes sobre regras que ninguém escreveu.

### 2. Leia o diff

`gh pr diff <número>`. Se for grande, leia os arquivos inteiros que importam — diff sem contexto
produz falso positivo.

### 3. Carregue as skills relevantes ao que mudou

Elas são a autoridade, não a sua memória. Sempre `code-review` (checklist com severidades) e
`code-conventions`. Conforme a área tocada: `controller`, `application-service`, `domain`,
`domain-validation`, `migration`, `queue-processor`, `queue-scheduler`, `bullmq-flow`,
`provider-strategy`, `module-architecture`, `partners-api`, `test-design`, `test-audit`. Liste
`.claude/skills/` se tiver dúvida.

### 4. Percorra os invariantes abaixo

### 5. Verifique cada achado antes de escrever

Abra o arquivo, confirme que o problema existe no código como está agora, e monte o cenário concreto em
que ele falha. Se você não consegue descrever entrada e consequência, não é achado.

### 6. Comente uma vez, com tudo

`gh pr comment <número> --body "..."` — no formato da seção abaixo.

## Invariantes

O que o lint e o `pr-standards` já pegam — tipos explícitos, `any`, formatação, tamanho do PR,
nome de branch — **não é seu trabalho**. Foque no que nenhuma regra automática expressa.

### O que foi combinado

Só existe quando o passo 1 trouxe issue, PRD ou concept. É o único lugar onde código internamente
correto pode ser defeito.

-   **Código que contradiz uma decisão fechada é achado.** Uma regra escrita no concept ou no
    refinamento não é sugestão.
-   **Critério de aceite sem código e sem teste é achado.** Nomeie a issue e o critério.
-   **Comportamento que nenhuma issue descreve é achado.** Chegou sem ninguém ter combinado.
-   **Número que discorda do combinado** — limite, janela, preço, retry, percentual — vai no topo.

Não é achado: algo que o PR adiou **de propósito e diz isso** no body. Leia o body antes de acusar.

### Multi-tenant

-   Query que sai do `RepositoryAdapter`/`SessionService` (raw query, `sequelize.query`, view,
    OpenSearch) e não filtra por `companyId` é achado — vaza dado de outra empresa.
-   Endpoint sem `RoleGuard` / `BlockFreeTierGuard` / `FeatureGuard` onde os vizinhos têm.

### Controllers e serviços

-   Controller é fachada fina: lógica de negócio dentro dele é achado.
-   Escrita (`POST`/`PUT`/`PATCH`/`DELETE`) sem `@UsingTransaction()`; endpoint sem
    `@ExceptionInterceptor()`; resposta sem DTO tipado.
-   Exceção errada para o caso (`NotFound` vs `UnprocessableEntity` vs `BadRequest`) — ver
    `code-conventions`.

### Dados pessoais e segredos

-   **Nenhum PII em log**: nome, email, telefone, documento, cartão, conteúdo de mensagem — inclui o
    `meta` do `LogService`. `console.log` é achado por si só.
-   Credencial nunca aparece em log, resposta de API ou nome de coluna. Variável secreta não tem
    default utilizável em produção.

### Banco

-   Migration é aditiva: coluna nova chega nullable ou com default; a constraint aperta depois.
-   Migration já aplicada **nunca é editada** — corrige-se para frente.
-   Query em loop onde um `include`/`findAll` com `where in` resolveria (N+1).

### Filas e integrações

-   Job sem `jobId` determinístico, ou o PR explica por que não precisa.
-   Handler não idempotente: reentrega não pode cobrar, enviar ou gravar duas vezes.
-   Processor sem `setSession(job)` antes de tocar repositório.
-   Mudança numa strategy de provider que altera o contrato comum (`build()`, enum, roteamento) sem
    tocar os outros providers que dependem dele.

### Testes e documentação

-   Regra de negócio nova sem teste que a exercite é achado. Cobertura genérica não é.
-   Área com `log.md`/concept no bundle OKF cuja regra mudou e a documentação não — achado
    (`CLAUDE.md`: documentação desatualizada mente para o próximo agente).

## Formato do comentário

**Escreva em pt-BR**, em frases completas. Vocabulário do domínio fica como o time usa: "régua",
"pedido", "provider", "milestone". Sem cadeias de setas, sem siglas soltas, sem rótulo que só faz
sentido para quem leu o diff inteiro — quem lê o comentário não acompanhou o seu raciocínio.

Comece sempre com o título `## Revisão automática (Claude)`.

### Quando há achados

Uma linha com quantos são e a severidade mais alta. Depois um bloco por achado, ordenado por
severidade — dinheiro e dados pessoais primeiro, depois decisão contrariada ou critério não entregue,
depois integridade (multi-tenant, banco, filas), depois o resto:

**`caminho/do/arquivo.ts:123` — o que está errado**

Uma frase dizendo o defeito. Uma frase com o cenário concreto em que quebra — entrada e consequência,
não teoria. Se a correção é óbvia, uma linha dizendo qual é.

Feche com um pedido explícito de correção, por exemplo: "Por favor, corrija os pontos acima antes do
merge. Se algum for intencional, responda neste comentário explicando o motivo."

### Quando não há achados

Uma linha, e só ela, depois do título:

"Revisei o diff contra as issues citadas e as skills do repositório. **Nenhuma alteração necessária.**"

Se revisou sem contexto de issue, diga isso na mesma frase. Não acrescente resumo do PR, elogio ou
lista do que foi checado.
