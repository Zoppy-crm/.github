---
name: flow-dev-guide
description: Stack-agnostic development execution companion — reads existing plans from docs/plans/, detects the stack from the "Stack & Skills" section, loads the correct skills dynamically, and executes phase by phase. Works for frontend, backend, fullstack, or any stack. Use when the user says "implementar", "executar", "comecar a codar", "executar fase", "implementar fase", "vamos implementar", "executar o plano", "rodar a fase", or any time the user wants to start implementing from an existing plan.
---

# Dev Guide v2 — Execution (Stack-Agnostic)

Copiloto de execucao **stack-agnostic**: le planos existentes em `docs/plans/`, detecta o stack a partir da secao `## Stack & Skills` do plano geral, carrega dinamicamente as skills corretas e implementa fase por fase. **Foco exclusivo em implementacao** — o planejamento e feito separadamente pela skill `/flow-plan-dev-guide`.

---

## Fase A — Diagnostico inicial

### 1. Localizar o plano

Verifique `docs/plans/` por planos existentes:
- Plano geral (ex: `new-integration-screen.md`)
- Planos detalhados por fase (ex: `fase-01-fundacao-shell.md`, `fase-02-listagem-providers.md`)

Se nao encontrar planos:
> "Nao encontrei planos em `docs/plans/`. Execute `/flow-plan-dev-guide` primeiro para gerar os planos."

### 2. Carregar Stack & Skills

**Ler a secao `## Stack & Skills` do plano geral.** Esta secao define:
- **Workflow** — qual workflow foi escolhido no planejamento
- **Stack** — frontend, backend, fullstack, e2e
- **Skills de implementacao** — quais skills carregar
- **Skills de teste** — quais skills carregar para fases de teste
- **Validacoes especificas** — regras de validacao do stack

Se a secao nao existir no plano geral:
> "O plano geral nao tem a secao 'Stack & Skills'. Qual e o stack desta feature? (frontend / backend / fullstack / e2e)"

Com base na resposta, usar o Stack Skills Map (mesmo da skill `beta-plan-dev-guide-v2`) para inferir as skills.

**Apresentar o que foi detectado:**

```
---------------------------------------------------
Stack: [stack]
Skills que vou carregar: [lista]
Validacoes que vou aplicar: [lista]
---------------------------------------------------
```

### 3. Identificar o progresso

- Verificar se existe `docs/plans/handoff.md` — se existir, **ler primeiro** pois contem o contexto da ultima sessao (decisoes, alertas, artefatos disponiveis)
- Verificar quais fases ja foram implementadas (branches, commits, arquivos existentes)
- Verificar o plano geral por checkboxes marcados `[x]`
- Verificar memory para progresso salvo

Apresentar o status:

```
Plano: [nome do plano]
Stack: [stack detectado]
   Fase 1 — [nome] (implementada)
   Fase 2 — [nome] (implementada)
   Fase 3 — [nome] (proxima)
   Fase 4 — [nome]
   ...
```

### 4. Confirmar a fase a executar

> "A proxima fase e **Fase [N] — [Nome]**. Quer comecar?"

Se o dev quiser pular ou executar outra fase, ajuste sem questionar.

---

## Fase B — Executar uma fase

### 0. Perguntar sobre worktree — OBRIGATORIO E BLOQUEANTE

**PARE AQUI.** Antes de ler o plano, carregar skills, ou escrever qualquer linha de codigo, faca esta pergunta e **aguarde a resposta**:

> "Quer que eu crie um novo worktree isolado para a **Fase [N] — [Nome]**?
> - **Sim** → crio `.worktrees/feature/<nome>-fase-[NN]` (branch: `feature/<nome>-fase-[NN]`)
> - **Nao** → implemento no workspace atual (`[branch-atual]`)"

**NAO PROSSIGA sem receber uma resposta explicita.** Nao assuma, nao interprete silencio como "nao". Pergunte e espere.

**Sinais de que voce esta racionalizando para pular este passo:**
- "o dev disse 'continue' — isso implica 'nao'"
- "ja estou no worktree certo"
- "e so uma fase pequena"
- "vou perguntar depois"

**Todos esses pensamentos significam: PARE. Faca a pergunta.**

Se o dev escolher criar worktree:
```bash
git worktree add .worktrees/feature/<nome>-fase-[NN] -b feature/<nome>-fase-[NN] <base-branch>
```

Se o worktree precisar de dependencias, instala-las conforme o stack:
- **frontend:** `npm install --legacy-peer-deps`
- **backend:** `npm install` (ou o gerenciador do projeto)
- **fullstack:** ambos, conforme estrutura do projeto

**So apos receber a resposta e agir conforme ela, passe para o passo 1.**

### 1. Carregar o plano da fase

Ler o arquivo do plano detalhado (ex: `docs/plans/fase-03-setup-page.md`) completamente.

Verificar se o plano da fase tem `Stack desta fase:` e `Skills de referencia:`:
- **Se sim** — usar essas skills (podem ser um subset ou superset do plano geral)
- **Se nao** — usar as skills do plano geral conforme o stack

### 2. Carregar skills dinamicamente

**Carregar exatamente as skills listadas** no plano da fase (ou herdadas do plano geral). Nao carregar skills que nao estao na lista.

Exemplos por stack:

**frontend:**
```
Carregando skills: design-to-plan, angular-component, angular-signals,
  feature-composition, feature-state, frontend-angular, beta-template-guard
```

**backend:**
```
Carregando skills: nestjs-best-practices
```

**fullstack (fase frontend):**
```
Carregando skills: angular-component, angular-signals, feature-composition,
  feature-state, frontend-angular, beta-template-guard
```

**fullstack (fase backend):**
```
Carregando skills: nestjs-best-practices
```

### 2.5. Executar Template Guard (quando o stack inclui frontend)

Se o stack da fase inclui frontend, **invocar** a skill `beta-template-guard` antes de implementar. Ela analisa o plano, verifica se tem templates e design de referencia, e decide a estrategia (COPIA LITERAL ou PROCESSAMENTO).

**Se o stack for backend ou e2e, pular este passo.**

### 3. Verificar design no plano (quando o stack inclui frontend)

Se o stack da fase inclui frontend:

Se o plano tem uma secao `## Design de Referencia` com imagem e tokens:
> "Encontrei o design no plano. Vou usar como referencia."

Se nao tem:
> "O plano nao tem design. Voce tem imagens do design para esta fase, ou implemento apenas a estrutura funcional?"

**Se o stack for backend ou e2e, pular este passo.**

### 4. Seguir a sequencia de implementacao

O plano detalhado tem uma secao `### Sequencia de Implementacao` com passos numerados. Seguir **exatamente** essa ordem:

```
---------------------------------------------------
Fase [N] — [Nome] | Passo [X] de [Total]
---------------------------------------------------
Stack: [stack da fase]
Executando: [descricao do passo]
---------------------------------------------------
```

Para cada passo:
1. **Criar os arquivos** conforme a estrutura de pastas do plano
2. **COPIAR LITERALMENTE os templates do plano** — usar copy-paste mental exato dos blocos de codigo do plano. NAO reinterpretar, NAO simplificar, NAO remover atributos que "parecem desnecessarios". A tendencia de "limpar" ou "simplificar" ao transcrever e o erro mais comum — combater ativamente.
3. **Aplicar as validacoes especificas do stack** (lidas do plano geral):
   - **frontend:** validar classes Tailwind (nao PascalCase), OnPush, tipagem explicita, ui-text com htmlTag+type+className, ps-icon com [icon] binding
   - **backend:** validar DTOs com class-validator, guards com @UseGuards, services @Injectable
   - **fullstack:** aplicar as validacoes do stack da fase
4. **Aplicar os padroes** do checklist do plano
5. **Validar** que o codigo compila sem erros
6. **Diff de verificacao** — comparar o codigo gerado com o template do plano, atributo por atributo. Se houver divergencia, o plano vence.

### 5. Validar criterios de aceite

Apos implementar todos os passos, percorrer a secao `## Criterios de Aceite` do plano:

```
Verificando criterios de aceite:
- [x] Criterio 1 — OK
- [x] Criterio 2 — OK
- [ ] Criterio 3 — PENDENTE (motivo)
```

Se algum criterio nao foi atendido, corrigir antes de avancar.

### 6. Validar checklist de padroes

Percorrer a secao `## Padroes obrigatorios (checklist)` do plano e verificar cada item.

### 7. Validar no browser / runtime (quando possivel)

Conforme o stack:
- **frontend:** Se o dev server estiver rodando, usar `/agent-browser` para validar visualmente
- **backend:** Se o servidor estiver rodando, testar endpoints com curl/httpie ou ferramenta equivalente
- **fullstack:** ambos

### 8. Testes (quando a fase inclui testes)

Carregar as **skills de teste** do stack (conforme plano geral):
- **frontend/e2e:** invocar `e2e-zoppy` e/ou `playwright-best-practices`
- **backend:** invocar skills de teste do backend (conforme definido no Stack Skills Map)
- **fullstack:** carregar as skills de teste relevantes para o tipo de teste da fase

---

## Fase C — Progressao entre fases

Apos completar uma fase, seguir **obrigatoriamente esta sequencia**. Nao pular etapas, nao mencionar a proxima fase antes de concluir todas elas:

```
---------------------------------------------------
Fase [N] — [Nome] concluida!
---------------------------------------------------
Criterios de aceite: [X]/[Total]
Stack: [stack]
---------------------------------------------------
```

**NAO mencione a proxima fase ainda. Siga os passos abaixo na ordem.**

### Passo C.1 — Revisao de codigo (antes do commit)

**Antes de commitar**, perguntar ao dev:

> "Quer que eu rode a revisao de codigo antes de commitar? (`superpowers:requesting-code-review` + `beta-review-possible-bugs`)"
> - **Sim** — executar ambas as skills e **apresentar o relatorio**
> - **Nao** — pular para as opcoes de commit

**Aguardar resposta antes de continuar.**

**Se o dev escolheu Sim:**

1. Executar os agentes de review (`superpowers:requesting-code-review` + `beta-review-possible-bugs`)
2. **NAO corrigir nada automaticamente.** Consolidar os achados num relatorio unico e apresentar ao dev:

```
## Relatorio de Revisao — Fase [N]

### Problemas encontrados
1. [descricao do problema] — [arquivo:linha]
2. [descricao do problema] — [arquivo:linha]

### Sugestoes (nao-blocantes)
1. [sugestao] — [arquivo:linha]

### Sem problemas
- [areas revisadas que estao OK]
```

3. Perguntar ao dev:
> "Quais itens quer que eu corrija? (numeros, 'todos', ou 'nenhum')"

4. **Aguardar resposta.** Corrigir apenas os itens que o dev escolher. Depois prosseguir para C.2.

### Passo C.2 — Opcoes de commit

Perguntar **tudo de uma vez** para que o dev decida:

> "O que deseja fazer?"
> 1. **Commit + Push + Handoff** — commitar, enviar a branch, atualizar passagem de bastao e docs
> 2. **Commit + Push** — commitar e enviar sem atualizar handoff
> 3. **So commit** — commitar localmente sem push
> 4. **Avancar direto** — ir para a proxima fase sem commitar agora

**Aguardar resposta e executar a opcao escolhida antes de continuar.**

### Passo C.3 — Atualizar handoff (passagem de bastao)

Se o dev escolheu uma opcao com Handoff (ou pediu explicitamente):

1. **Invocar a skill `beta-handoff`** — ela gera/atualiza `docs/plans/handoff.md` com o contexto da fase concluida
2. O handoff e commitado junto com os demais arquivos da fase

Mesmo que o dev nao escolha Handoff agora, **se for a ultima interacao antes de encerrar a sessao**, sugerir:

> "Antes de encerrar, quer que eu atualize o handoff para a proxima sessao?"

### Passo C.4 — Atualizar documentos e issues

Apos o commit/push da fase, **sempre perguntar**:

> "Quer atualizar os documentos do plano e as issues do GitHub?"
> - **Sim** — atualizar checklists do plano da fase atual + issues relacionadas
> - **Sim, e de outras fases tambem** — se houve mudancas que afetaram fases anteriores
> - **Nao** — prosseguir

**Aguardar resposta antes de continuar.**

**Se sim, executar na ordem:**

**C.4.1 — Atualizar o plano da fase** (`docs/plans/fase-XX-*.md`):
- Percorrer a secao `## Padroes obrigatorios (checklist)` e marcar `[x]` os itens concluidos
- Percorrer a secao `## Criterios de Aceite` e marcar `[x]` os itens concluidos
- Se todos marcados, adicionar no topo: `> Fase concluida em [data]`
- Commitar o plano atualizado

**C.4.2 — Marcar a issue da fase como concluida no GitHub** (obrigatorio se existir issue):
- **Invocar a skill `beta-github-issues`** — ela executa a Fase 7 (Mover issue para Done)
- A skill coleta todos os campos obrigatorios do Project Board com o dev: Priority, Size, Estimate, Horas Gastas, Start date, Target date
- **NAO pular este passo** — a issue precisa ser movida para Done e ter os campos preenchidos

**C.4.3 — Verificar impacto em outras fases**:
- Se durante a implementacao houve mudancas que afetaram planos de fases anteriores, perguntar ao dev se quer atualizar esses planos tambem
- Listar quais planos foram afetados antes de atualizar

### Passo C.5 — Criar roteiro de QA

Apos atualizar plano e card, se for a **ultima fase** da feature/bugfix ou tratar-se de um **bugfix de fase unica**, perguntar:

> "Quer que eu gere o roteiro de QA?"
> - **Sim** — crio `docs/plans/<nome>-qa.md` com cenarios de teste + adiciono secao ao body da issue do card
> - **Nao** — pulo

**Se sim:**

1. Gerar o roteiro baseado no plano + report + diff da implementacao, cobrindo:
   - Contexto (resumo do bug/feature)
   - Ambiente (staging/mirror, empresa de teste, fluxo de acesso)
   - Cenarios principais (reproducao do bug, controles positivos, caminho feliz)
   - Regressoes a verificar (o que foi tocado indiretamente)
   - Fora do escopo (o que o fix nao resolve)

2. **Apresentar o draft ao dev** e aguardar confirmacao — o conteudo vai para arquivo versionado e para o body do card (visivel ao time).

3. Apos aprovacao, executar em paralelo:
   - `Write` em `docs/plans/<nome>-qa.md`
   - `gh issue edit <N> --repo <ORG>/<REPO> --body-file <body.md>` (apensando secao `## Roteiro de QA` ao body atual — **sem remover nada existente**)

**Padrao para o nome do arquivo:** `<nome-do-plano>-qa.md` (mesmo prefixo do plan e report).

**Ao atualizar o body do issue:** ler o body atual com `gh issue view --json body --jq .body`, append da nova secao com separador `---` e data, nunca editar secoes pre-existentes.

### Passo C.6 — Propor proxima fase

**So apos concluir os passos C.1 a C.5**, propor a proxima fase:

> "Proxima: **Fase [N+1] — [Nome]**. Quer comecar?"

### Commit entre fases

Usar `--no-verify` tanto no commit quanto no push (hooks de CI sao validados no PR).

Mensagem de commit deve ser detalhada — titulo curto no formato convencional + body listando o que foi criado/alterado:

```
feat(<escopo>): implement phase [N] - [nome da fase]

- Create [models/interfaces criados]
- Add [componentes/services/modules criados]
- Add [state service / rotas / configs / migrations]
- Register [rotas/modules em arquivo X]
```

**Opcao 1 — Commit + Push:**
```bash
git add <arquivos da fase>
git commit --no-verify -m "<mensagem detalhada>"
git push --no-verify -u origin <branch>
```

**Opcao 2 — So commit:**
```bash
git add <arquivos da fase>
git commit --no-verify -m "<mensagem detalhada>"
```

**Opcao 3 — Avancar direto:**
Prosseguir para a proxima fase. O commit pode ser feito depois.

---

## Fase D — Respostas a duvidas durante execucao

Quando o dev fizer uma pergunta:
1. Consultar o plano da fase atual
2. Consultar as skills carregadas (do stack detectado)
3. Consultar as convencoes do projeto (`project-conventions.md`)

**Sempre** voltar ao contexto:

> "Voltando: estavamos na **Fase [N] — Passo [X]**. [O que falta fazer]."

---

## Fase E — Conclusao

Quando todas as fases estiverem implementadas:

```
Implementacao concluida!

Todas as [N] fases implementadas
Criterios de aceite verificados
Stack: [stack]

Proximos passos sugeridos:
  1. superpowers:requesting-code-review — revisar implementacao completa
  2. beta-review-possible-bugs — checar bugs no diff final
  3. Rodar testes conforme o stack:
     - frontend: ng test, playwright test
     - backend: npm test, jest
     - fullstack: ambos
  4. Commitar e criar PR via /beta-commit + /flow-publish
  5. review-pr — revisar a PR criada no GitHub antes de mergear
```

---

## Regras

- **SEMPRE perguntar sobre worktree no passo 0 — e bloqueante** — nenhum codigo e escrito antes de receber a resposta. Sem excecoes. Sem interpretacoes implicitas.
- **Os templates de referencia do plano sao a fonte de verdade** — copiar fielmente. Nunca substituir por nomes "parecidos" ou inventados. Se algo no template nao compila, corrigir pontualmente mas manter a intencao original.
- **Sempre le Stack & Skills do plano geral** — e o contrato com o plan-dev-guide-v2
- **Sempre carrega as skills listadas no plano** — nunca carrega skills que nao estao na lista, nunca assume o stack
- **Passos condicionais por stack** — Template Guard, design, validacoes e testes sao executados apenas quando o stack da fase os exige
- **Sempre le o plano antes de implementar** — nunca implementa de cabeca
- **Segue a sequencia de implementacao** do plano — nao pula passos
- **Verifica criterios de aceite** antes de declarar fase concluida
- **Nunca avanca fase sem confirmacao** do dev
- **Nunca menciona a proxima fase antes de concluir os passos C.1 a C.5** — handoff, docs e roteiro de QA vem antes de propor a proxima fase, sem excecao
- **Fase C e sequencial e bloqueante** — cada passo aguarda resposta do dev antes de avancar. Nao agrupar perguntas de passos diferentes numa unica mensagem
- **Consulta o design no plano** antes de perguntar ao dev por imagens (quando frontend)
- **Nao modifica os planos** — se algo precisa mudar, sugere ao dev atualizar o plano primeiro
- **Adapta o tom**: se o dev parece experiente, seja direto; se parece novo, explique mais
