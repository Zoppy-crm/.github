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

O inverso também vale: achado verificado que fica de fora para o comentário sair curto ensina o time
a confiar numa cobertura que não existe. O filtro é a verificação do passo 5, nunca a quantidade — se
dez achados sobrevivem à verificação, os dez entram no comentário.

## Como revisar

O argumento é o **número do PR**. Use-o em todo comando `gh` — num checkout de CI o `gh` não detecta o
PR sozinho, e um comando sem o número falha ou revisa a coisa errada.

### 1. Carregue o que foi decidido — antes do diff

As decisões não estão no diff. Leia-as primeiro, ou você vai checar o código contra ele mesmo e perder
a única coisa que vale pegar: código que entrega algo diferente do combinado.

Comece pelo PR: `gh pr view <número> --json headRefName,baseRefName,title,body`.

-   **Issues citadas.** O body costuma trazer `Closes #n` / `Fixes #n`, e branches `task/`, `bugfix/` e
    `hotfix/` carregam o número da issue no nome. Abra cada uma com `gh issue view <n>` e leia contexto
    e critérios de aceite — isso é o contrato. **Extraia a lista de critérios de aceite literalmente**:
    ela vira a seção "Critérios de aceite" do comentário, verificada critério por critério.
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
-   **Cada critério de aceite é verificado um a um.** Para cada critério da issue, aponte o código que
    o implementa (arquivo e linha) e o teste que o exercita. Critério sem código é achado; critério
    implementado sem teste que o exercite é achado. "Parece coberto" não é veredito — sem evidência
    apontável, o critério conta como não entregue. Nomeie a issue e o critério.
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

### Arquitetura e clean code

As skills carregadas no passo 3 são **critério de reprovação, não leitura de fundo**: regra objetiva
que o diff viola é achado mesmo quando o código funciona — "funciona" não anistia padrão. Em
particular, percorra `clean-code-backend`, `code-conventions` e `module-architecture` contra cada
arquivo tocado:

-   **Lógica na camada errada.** Query com filtro de regra de negócio montada na Application em vez de
    virar método do Domain; regra de negócio em controller ou processor; Domain injetando Domain de
    outro contexto (orquestração cross-context é serviço de Application).
-   **Método que acumula responsabilidades** ou mistura níveis de abstração onde `clean-code-backend`
    manda extrair; aninhamento onde early return resolve; nome que mente sobre o que o método faz.
-   **Duplicação do que o repo já tem.** Antes de aceitar helper, mapper ou validação nova, procure o
    equivalente existente — reimplementar o que já existe é achado.
-   **Convenções objetivas de `code-conventions`**: log fora do `LogService` ou fora do inglês,
    import de model fora de `@Zoppy-crm/models`, validação que pertence a uma
    `ApplicationValidationBase`/`DomainValidation` escrita inline.

Esses achados entram com severidade menor que dinheiro, PII e multi-tenant — mas entram. Omiti-los é o
que transforma o padrão do repo em letra morta.

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

### Critérios de aceite — sempre que houver issue

Logo depois do título — haja achados ou não — uma linha por critério de aceite extraído no passo 1,
com a evidência:

-   ✅ critério — atendido (`arquivo.ts:123`, teste em `arquivo.spec.ts`)
-   ⚠️ critério — implementado (`arquivo.ts:123`), sem teste que o exercite
-   ❌ critério — não encontrado no diff

Critério ⚠️ ou ❌ também aparece no bloco de achados, com o detalhe. Se o body do PR declara que o
critério ficou para outra fatia, marque-o como "fora desta fatia" em vez de ❌ — fatia declarada não é
defeito.

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

Depois do título e da seção de critérios de aceite (quando houver issue), uma linha e só ela:

"Revisei o diff contra as issues citadas e as skills do repositório. **Nenhuma alteração necessária.**"

Se revisou sem contexto de issue, diga isso na mesma frase. Não acrescente resumo do PR, elogio ou
lista do que foi checado.
