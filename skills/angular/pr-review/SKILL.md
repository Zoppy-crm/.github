---
name: pr-review
description: >
    Revisa um pull request contra o que este repositório já decidiu — skills, rules e CLAUDE.md — e
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
    - Bash(bash .claude/skills/pr-review/scripts/org-issue.sh:*)
effort: high
---

# PR review — Zoppy frontend (Angular)

Você revisa **contra o que este repositório já decidiu**, não contra boas práticas genéricas.

Um revisor que escreve "considere usar signals" é ignorado em duas semanas. Um revisor que escreve
"esse componente relê o parâmetro pela `ActivatedRoute` sendo que a rota já entrega como input, e o
guia do repo diz para não fazer isso" é lido.

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
    ela vira a seção "Critérios de aceite" do comentário, verificada critério por critério. Se a issue
    traz print ou link de design, o que ele mostra faz parte do combinado.
-   **Issue de outro repositório.** Referência como `Zoppy-crm/<repo>#n` ou link de issue de outro repo
    não abre com o token padrão da action. Abra pelo script da skill, que usa o token de leitura da org:
    `bash .claude/skills/pr-review/scripts/org-issue.sh <repo> <n>` (ex.: `... org-issue.sh
    zoppy-whatsapp-commerce-FE 142`). Se ainda assim falhar, diga no comentário qual issue não abriu.
-   **PR de `milestone/*`** carrega um épico inteiro. Além das issues citadas, liste as da feature com
    `gh issue list --search "<slug da milestone>" --state all --limit 50 --json number,title,body` e
    leia o PRD/refinamento se houver.
-   **Decisões do repo.** `CLAUDE.md` (Key Patterns), `docs/adr/` quando existir, e as rules em
    `.claude/rules/` (`project-structure`, `style-guide`, `modal-usage-guide`, `e2e-patterns`).

Se não há issue nem contexto, abra o comentário com uma linha dizendo que revisou sem o contexto da
tarefa, e revise só pelo diff. **Não reconstrua a intenção a partir das mensagens de commit** — um
contexto chutado produz achados confiantes sobre regras que ninguém escreveu.

### 2. Leia o diff

`gh pr diff <número>`. Se for grande, leia os arquivos inteiros que importam — diff sem contexto
produz falso positivo. Template, componente e estilo do mesmo componente se leem juntos.

### 3. Carregue as skills relevantes ao que mudou

Elas são a autoridade, não a sua memória. Sempre `frontend-angular`. Conforme a área tocada:
`angular-component`, `angular-signals`, `feature-state`, `feature-composition`, `angular-migration`,
`e2e-zoppy` e `playwright-best-practices` (arquivos em `e2e/`), `test-design`, `test-audit`. Liste
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

As skills e rules carregadas no passo 3 são **critério de reprovação, não leitura de fundo**: regra
objetiva que o diff viola é achado mesmo quando a tela funciona — "funciona" não anistia padrão. Esses
achados entram com severidade menor que dados pessoais e decisão contrariada — mas entram. Omiti-los é
o que transforma o padrão do repo em letra morta.

### O que foi combinado

Só existe quando o passo 1 trouxe issue, PRD ou design. É o único lugar onde código internamente
correto pode ser defeito.

-   **Código que contradiz uma decisão fechada é achado.** Uma regra escrita no refinamento ou no
    `CLAUDE.md` não é sugestão.
-   **Cada critério de aceite é verificado um a um.** Para cada critério da issue, aponte o código que
    o implementa (arquivo e linha) e o teste que o exercita. Critério sem código é achado; critério
    implementado sem teste que o exercite é achado. "Parece coberto" não é veredito — sem evidência
    apontável, o critério conta como não entregue. Nomeie a issue e o critério.
-   **Comportamento que nenhuma issue descreve é achado.** Chegou sem ninguém ter combinado.
-   **Tela que diverge do design citado** — estado vazio, erro, loading ou responsivo ausentes quando o
    design os mostra.

Não é achado: algo que o PR adiou **de propósito e diz isso** no body. Leia o body antes de acusar.

### Arquitetura Angular (decisões do `CLAUDE.md`)

-   Componente novo que não é `standalone`, ou que usa `@Input`/`@Output` em vez de `input()`/
    `output()`/`model()`. Componente antigo tocado que não migrou o que tocou.
-   Estado ou ação de feature threaded por cadeia de `input()`/`output()` entre vários componentes,
    quando o padrão do repo é um serviço injetável (store + editor/controller).
-   Serviço de feature com `providedIn` de página quando algo dele é usado dentro de `<ps-modal />`
    — o modal vive no injector raiz e não enxerga o provider.
-   Transformação de dados escrita dentro do componente ou do serviço em vez de função pura
    testável sem `TestBed`.
-   `ActivatedRoute` injetada só para ler um parâmetro que já chega como input da rota.
-   Página nova sem `*.routes.ts` próprio e lazy no `app.routes.ts`.
-   Modal aberto fora do `ModalService` (ver `modal-usage-guide`).

### Design system e estilo

-   Componente `@Zoppy-crm/<antigo>` em código novo quando existe o `@Zoppy-crm/ui-*` equivalente.
-   Input de componente do design system usado com nome ou valor que a API do pacote não tem —
    confira o pacote antes de acusar, e confira antes de deixar passar.
-   CSS custom onde a classe Tailwind do preset resolve; layout que quebra em mobile (o guia é
    mobile-first).

### Dados pessoais e segredos

-   PII (nome, email, telefone, documento, conteúdo de mensagem) em `console.log`, no telemetry
    (`amplitude`/`telemetry-client`) ou em `localStorage` sem necessidade.
-   Token, chave ou URL interna hardcoded fora de `environments/`.

### Comportamento e rede

-   Subscription sem `takeUntilDestroyed`/`async`/signal, criada em componente que pode ser destruído.
-   Chamada HTTP disparada em `computed`/`effect` sem guarda — dispara a cada recomputo.
-   Erro de rede engolido: request cujo erro não chega nem ao toast nem ao estado do componente.

### Testes

-   Regra nova sem teste unitário (Jasmine) que a exercite é achado. Cobertura genérica não é.
-   Arquivo em `e2e/` que foge dos padrões de `e2e-patterns` (estrutura por domínio, espera de rede,
    seletores).
-   `describe`/`it` em português — o repo escreve descrições de teste em inglês.

## Formato do comentário

**Escreva em pt-BR**, em frases completas. Vocabulário do domínio fica como o time usa: "régua",
"campanha", "modal", "design system". Sem cadeias de setas, sem siglas soltas, sem rótulo que só faz
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
severidade — dados pessoais e segredos primeiro, depois decisão contrariada ou critério não entregue,
depois arquitetura e comportamento, depois o resto:

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
