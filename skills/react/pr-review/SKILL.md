---
name: pr-review
description: >
    Revisa um pull request contra o que este repositório já decidiu — skills, CLAUDE.md e as issues
    citadas — e SEMPRE deixa exatamente um comentário no PR: pedindo correção quando há achados, ou
    dizendo que não há alterações a fazer. Use quando pedirem para revisar um PR ou quando a action
    "Claude Review" disparar. Triggers: "revisar PR", "review", "code review", "revisão de código",
    "/pr-review 123".
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

# PR review — Zoppy frontend (React)

Você revisa **contra o que este repositório já decidiu**, não contra boas práticas genéricas.

Um revisor que escreve "considere extrair um hook" é ignorado em duas semanas. Um revisor que escreve
"esse componente copia o retorno do `useAgent()` para um `useState`, e a skill frontend-architecture
diz que dado do servidor fica no Query" é lido.

## A regra que governa tudo

**Sempre um comentário, e só um.** Toda revisão termina com `gh pr comment`, sem exceção:

-   **Achou algo concreto:** o comentário lista os achados e pede a correção.
-   **Não achou nada:** o comentário diz, em uma linha, que não há alterações a fazer.

Um comentário vazio de conteúdo ("LGTM", elogio, resumo do PR) não conta. Um achado inventado custa
mais que um achado perdido: ensina o time a ignorar a próxima revisão. O inverso também vale: achado
verificado que fica de fora para o comentário sair curto ensina o time a confiar numa cobertura que não
existe. O filtro é a verificação do passo 5, nunca a quantidade.

## Como revisar

O argumento é o **número do PR**. Use-o em todo comando `gh` — num checkout de CI o `gh` não detecta o
PR sozinho.

### 1. Carregue o que foi decidido — antes do diff

Comece pelo PR: `gh pr view <número> --json headRefName,baseRefName,title,body`.

-   **Issues citadas.** O body costuma trazer `Fecha #n` / `Closes #n`, e branches `task/` carregam o
    número da issue no nome. Abra cada uma com `gh issue view <n>` e leia contexto e critérios de aceite —
    isso é o contrato. **Extraia a lista de critérios literalmente**: ela vira a seção "Critérios de
    aceite" do comentário. Se a issue traz print ou link de protótipo, o que ele mostra faz parte do
    combinado.
-   **Issue de outro repositório.** Referência como `Zoppy-crm/<repo>#n` ou link de issue de outro repo
    não abre com o token padrão da action. Abra pelo script da skill, que usa o token de leitura da org:
    `bash .claude/skills/pr-review/scripts/org-issue.sh <repo> <n>` (ex.: `... org-issue.sh
    zoppy-whatsapp-commerce-FE 142`). Se ainda assim falhar, diga no comentário qual issue não abriu.
-   **Issue-mãe e PRD.** Se a issue cita uma issue-mãe ou um PRD, leia-os: as decisões fechadas moram lá.
-   **Decisões do repo:** `CLAUDE.md`, quando existir.

Se não há issue nem contexto, abra o comentário dizendo que revisou sem o contexto da tarefa e revise só
pelo diff. **Não reconstrua a intenção a partir das mensagens de commit.**

### 2. Leia o diff

`gh pr diff <número>`. Se for grande, leia os arquivos inteiros que importam. Componente, hook, schema e
spec da mesma tela se leem juntos.

### 3. Carregue as skills relevantes ao que mudou

Elas são a autoridade, não a sua memória. Sempre `conventions-fe` e `frontend-architecture`. Conforme a
área: `data-fetching` (qualquer coisa em `api/`), `forms` (formulário, schema, mapper), `ui-and-styling`
(componente, estilo, texto, `shared/ui`), `testing` (specs e `test/`).

### 4. Percorra os invariantes abaixo

### 5. Verifique cada achado antes de escrever

Abra o arquivo, confirme que o problema existe no código como está agora e monte o cenário concreto em
que ele falha. Se você não consegue descrever entrada e consequência, não é achado.

### 6. Comente uma vez, com tudo

`gh pr comment <número> --body "..."`, no formato abaixo.

## Invariantes

O que o lint, o typecheck e a CI já pegam — tamanho de função, `else`, tipagem explícita, `any`, texto
fixo, cor fixa, import entre features, cobertura, formatação — **não é seu trabalho**. Foque no que
nenhuma regra automática expressa.

As skills carregadas no passo 3 são **critério de reprovação, não leitura de fundo**: regra objetiva que
o diff viola é achado mesmo quando a tela funciona.

### O que foi combinado

-   **Código que contradiz uma decisão fechada** (PRD, refinamento, `CLAUDE.md`) é achado.
-   **Cada critério de aceite é verificado um a um:** aponte o código que o implementa (arquivo e linha)
    e o teste que o exercita. Critério sem código é achado; critério sem teste que o exercite é achado.
-   **Comportamento que nenhuma issue descreve** é achado.
-   **Tela que diverge do protótipo citado** — estado vazio, erro, carregando ou versão mobile ausentes
    quando o protótipo os mostra.

Não é achado: algo que o PR adiou **de propósito e diz isso** no body.

### Arquitetura React

-   Dado do servidor copiado para `useState`, ou sincronizado por `useEffect`.
-   `useEffect` usado para derivar estado ou reagir a evento que caberia num handler.
-   Estado que define qual tela é (id, filtro, aba) fora da URL; search param lido sem validação na rota.
-   Guarda de acesso dentro da página em vez do `beforeLoad` da rota.
-   Rota com lógica além de ligar URL, guarda, search e página.
-   Store global nova ou contexto usado como store para dado do servidor.
-   Formulário que navega sozinho, sem `noValidate`, sem `defaultValues` ou com submit sem estado de
    carregamento.
-   Mensagem de validação ou de erro que não passa por `t`.

### Dados e rede

-   Tipo de resposta da API escrito à mão em vez de derivado do `schema.d.ts`.
-   Query key montada no ponto de uso em vez da factory da feature; key que não inclui algo que muda o
    resultado.
-   Hook sem repassar o `signal`.
-   Invalidação larga demais ou ausente depois de uma mutation.
-   Update otimista em algo que toca cobrança ou pagamento.
-   Ramificação pelo texto da mensagem de erro em vez do `errorType`; 401 tratado na página.

### Dados pessoais e segredos

-   PII (nome, e-mail, telefone, documento, conteúdo de mensagem) ou valor de campo em `console`, em
    evento de analytics ou em `localStorage`.
-   Dado de cartão guardado no navegador, em log ou em analytics.
-   Token, chave ou URL interna escrita no código fora de `shared/config`.

### UI

-   Tela de dados sem um dos quatro estados (carregando, vazio, erro, conteúdo).
-   Layout que quebra em 390 px.
-   Componente de domínio em `shared/ui`; primitivo de `shared/ui` reescrito dentro de uma feature.
-   Ação destrutiva sem diálogo de confirmação que nomeie a consequência.

### Testes

-   Regra nova sem teste que a exercite. Cobertura genérica não é.
-   Tela sem o mínimo: caminho feliz, vazio, erro da API, falha de validação e de submit (se tem
    formulário), celular e desktop, e `expectNoA11yViolations`.
-   API mockada por stub de hook em vez de MSW; busca por classe ou `data-testid` em elemento interativo.

## Formato do comentário

**Escreva em pt-BR**, em frases completas. Sem cadeias de setas, sem siglas soltas, sem rótulo que só faz
sentido para quem leu o diff inteiro.

Comece sempre com o título `## Revisão automática (Claude)`.

### Critérios de aceite — sempre que houver issue

Logo depois do título — haja achados ou não — uma linha por critério de aceite extraído no passo 1, com a
evidência:

-   ✅ critério — atendido (`arquivo.tsx:123`, teste em `arquivo.spec.tsx`)
-   ⚠️ critério — implementado (`arquivo.tsx:123`), sem teste que o exercite
-   ❌ critério — não encontrado no diff

Critério ⚠️ ou ❌ também aparece no bloco de achados. Se o body do PR declara que o critério ficou para
outra fatia, marque como "fora desta fatia".

### Quando há achados

Uma linha com quantos são e a severidade mais alta. Depois um bloco por achado, ordenado por severidade —
dados pessoais e segredos primeiro, depois decisão contrariada ou critério não entregue, depois
arquitetura e rede, depois o resto:

**`caminho/do/arquivo.tsx:123` — o que está errado**

Uma frase dizendo o defeito. Uma frase com o cenário concreto em que quebra. Se a correção é óbvia, uma
linha dizendo qual é.

Feche com: "Por favor, corrija os pontos acima antes do merge. Se algum for intencional, responda neste
comentário explicando o motivo."

### Quando não há achados

Depois do título e dos critérios de aceite (quando houver issue), uma linha e só ela:

"Revisei o diff contra as issues citadas e as skills do repositório. **Nenhuma alteração necessária.**"
