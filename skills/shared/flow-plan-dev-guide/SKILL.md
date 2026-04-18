---
name: flow-plan-dev-guide
description: Acts as a stack-agnostic planning workflow companion — reads the project's workflow guide, identifies which workflow applies, detects the stack, and walks through planning step by step until all phases are detailed and reviewed. Writes "Stack & Skills" into the general plan so that dev-guide-v2 knows which skills to load. Focused exclusively on planning, not implementation. Use when the user says "me acompanha", "me orienta", "me guia", "por onde começo", "o que faço agora?", "próximo passo", "quero planejar", "preciso criar", "vou começar", or any time the user expresses intent to start planning development work.
---

# Dev Guide v2 — Planning Only

Copiloto de planejamento **stack-agnostic**: identifica qual workflow seguir, detecta o stack, acompanha o progresso do planejamento passo a passo e responde duvidas sem perder o fio do processo. **Foco exclusivo em planejamento** — a implementacao e feita separadamente pela skill `/flow-dev-guide`.

---

## Stack Skills Map

Mapa de referencia que associa cada stack ao kit de skills que o dev-guide-v2 devera carregar durante a implementacao. Este mapa e usado na Fase B para escrever a secao `## Stack & Skills` no plano geral.

### frontend
**Skills de implementacao:**
- `design-to-plan` — analise de design Figma e mapeamento para componentes do design system
- `angular-component` — padroes de componentes Angular v19+ (standalone, signal inputs/outputs, OnPush)
- `angular-signals` — estado reativo com signal(), computed(), linkedSignal(), effect()
- `feature-composition` — estrutura de pastas, smart vs sub-components, regra de ~150 linhas
- `feature-state` — state services colocalizados, scoped providers
- `frontend-angular` — convencoes gerais do projeto FE (TailwindCSS, design system, control flow, lazy loading)
- `beta-template-guard` — valida templates de referencia antes de implementar

**Skills de teste:**
- `e2e-zoppy` — regras e padroes para testes E2E Playwright
- `playwright-best-practices` — boas praticas Playwright

**Validacoes especificas:**
- ui-text exige htmlTag + type + className
- ps-icon com [icon] binding
- Classes Tailwind: nao usar PascalCase (tokens Figma devem ser convertidos)
- OnPush obrigatorio, tipagem explicita em signals

### backend
**Skills de implementacao:**
- `nestjs-best-practices` — padroes NestJS (modules, DI, guards, pipes, interceptors)
- `controller` — padroes de controllers HTTP (guards, decorators, DTOs)
- `application-service` — padroes de application services (orchestracao, DI, erros)
- `clean-code-backend` — separacao de responsabilidades, limites de complexidade, nomenclatura

**Skills de teste:**
- `tdd` — TDD workflow Red-Green-Refactor com in-memory SQLite
- `testing` — regras gerais de testes no zoppy-api (nunca mockar domains, boilerplate)

**Validacoes especificas:**
- DTOs com class-validator
- Guards com @UseGuards
- Services injetaveis via @Injectable
- Extends ApiService para HTTP (se aplicavel ao projeto)

### fullstack
- Combina **frontend** + **backend** (todas as skills de ambos)
- Fases podem ser mistas ou separadas por stack — o plano da fase indica qual

### e2e
**Skills de implementacao:**
- `e2e-zoppy` — regras e padroes para testes E2E Playwright
- `playwright-best-practices` — boas praticas Playwright

**Validacoes especificas:**
- Independencia entre testes
- Resistencia a flaky tests
- Page Object Model quando aplicavel

> **Nota:** Este mapa pode ser estendido. Se o projeto tiver um `docs/stack-skills-map.md` ou `.claude/custom/stack-skills-map.md`, ele tem prioridade sobre este mapa built-in.

---

## Fase A — Diagnostico inicial

### 1. Carregar o workflow do projeto

Procure o arquivo de workflow nesta ordem:
1. `docs/workflow.md` no diretorio atual
2. `.claude/custom/workflow.md`
3. Se nao encontrar nenhum, avise: "Nao encontrei um `docs/workflow.md` neste projeto. Vou usar o workflow padrao."

### 2. Carregar o Stack Skills Map

Procure o mapa de stacks nesta ordem:
1. `docs/stack-skills-map.md` no diretorio atual
2. `.claude/custom/stack-skills-map.md`
3. Se nao encontrar nenhum, usar o mapa built-in desta skill (secao acima)

### 3. Entender o contexto atual

Verifique antes de perguntar:
- Branch atual (`git branch --show-current`) — pode indicar trabalho em andamento
- Arquivos modificados (`git status --short`) — confirma se ha algo em progresso
- Plano existente em `docs/plans/` cujo nome bate com a branch atual
- `project-conventions.md` — se existir, ja revela o stack do projeto

Se o contexto nao estiver claro, pergunte de forma direta:

> "O que voce precisa fazer? (pode descrever em uma frase)"

E se necessario:

> "Voce esta comecando do zero ou esta no meio de algo?"

---

## Fase B — Roteamento para o workflow correto

### 1. Identificar o workflow

Com base na descricao do dev, identifique o workflow e **confirme antes de continuar**:

| Intencao detectada | Workflow |
|--------------------|----------|
| Conhecer projeto novo, primeira vez | **W1: Setup do Projeto** |
| Feature nova com backend + frontend | **W9: Full Stack** |
| So tela, componente ou UI do Figma | **W8: Feature Frontend** |
| Feature de backend/API, complexa ou arquitetural | **W2: Feature Grande (Backend)** |
| Feature de backend/API, pequena e isolada | **W3: Feature Pequena (Backend)** |
| Corrigir comportamento errado | **W4: Bug Fix** |
| Melhorar codigo sem mudar comportamento | **W5: Refactoring** |
| Revisar PR de outra pessoa | **W6: Code Review** |
| Criar ou corrigir testes E2E | **W7: Testes E2E** |

### 2. Detectar o stack

Com base no workflow escolhido, detectar o stack:

| Workflow | Stack |
|----------|-------|
| W1 | (nao se aplica) |
| W2, W3 | `backend` |
| W4, W5 | Perguntar — pode ser frontend, backend ou fullstack |
| W6 | Detectar do PR |
| W7 | `e2e` |
| W8 | `frontend` |
| W9 | `fullstack` |

Se nao for possivel detectar automaticamente:

> "Qual o stack desta feature? (frontend / backend / fullstack / e2e)"

### 3. Confirmar com o dev

Anuncie a escolha:

> "Parece que voce esta no **[Workflow N] — [Nome]** com stack **[stack]**."
> "Skills que serao usadas na implementacao: [listar do Stack Skills Map]"
> "Correto?"

Se o dev corrigir, ajuste sem questionar.

### Passos por Workflow

**Nota sobre detalhamento de fases:** Em workflows que possuem `/prd-to-plan`, apos o plano geral ser criado, cada fase deve ser detalhada individualmente com um plano tecnico granular (arquivos a criar, interfaces, dependencias, exemplos de codigo). Isso permite que agentes executem a implementacao de forma autonoma. O detalhamento e a revisao de cada fase acontecem **antes** de qualquer implementacao — todo o planejamento e concluido primeiro.

**Skills de planejamento por stack:** Ao detalhar fases, **sempre carregar as skills do stack** (conforme o Stack Skills Map) para que os planos sigam os padroes corretos. Exemplos:
- **frontend:** carregar `design-to-plan`, `angular-component`, `angular-signals`, `feature-composition`, `feature-state`, `frontend-angular` — os exemplos de codigo nos planos devem seguir os padroes dessas skills
- **backend:** carregar `nestjs-best-practices` — exemplos devem seguir padroes NestJS
- **fullstack:** carregar todas as skills relevantes

**Design nos planos (quando stack inclui frontend):** Ao detalhar cada fase que envolve frontend, **sempre perguntar ao dev se possui imagens do design (Figma, screenshots) ou informacoes de estilo** para aquela fase antes de escrever o plano:

- **No detalhamento (passo 5a):** Perguntar "Voce tem imagens do design ou informacoes de estilo para esta fase?" antes de escrever o plano. Se o dev fornecer, usar `/design-to-plan` para analisar o design, mapear componentes do design system, e gerar o plano com hierarquia, estado, reuso e template de referencia.
- **Salvar design no plano:** Tentar incorporar a imagem diretamente no markdown do plano via `![descricao](caminho)`. Se nao for possivel, salvar em `docs/plans/assets/<nome-do-plano>/` e referenciar no markdown. O plano deve conter a secao `## Design de Referencia` com: imagem, tokens extraidos, e mapeamento com componentes do design system. Isso serve de fonte de verdade para a implementacao.
- Se o dev nao tiver design, registrar `> Design: nao fornecido — implementar estrutura funcional` no plano.
- **Se o stack for backend ou e2e**, pular esta etapa.

#### W1: Setup do Projeto

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Explorar estrutura e stack
 Passo 3  — Documentar convencoes        → project-conventions.md
```

#### W2: Feature Grande (Backend)

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Escrever o PRD               → /write-a-prd
 Passo 3  — Questionar o PRD             → /grill-me
 Passo 4  — Criar o plano geral          → /prd-to-plan
 Passo 4b — Escrever Stack & Skills      → (no plano geral)

 Para cada Fase do plano:
 +-----------------------------------------------------+
 | Passo 5a — Detalhar plano da fase                   |
 | Passo 5b — Checkpoint: prosseguir ou /grill-me?     |
 | Passo 5c — (se /grill-me) Revisar plano da fase     |
 +-----------------------------------------------------+
 Repetir ate todas as fases detalhadas e revisadas

 Planejamento concluido — planos prontos para implementacao
```

#### W3: Feature Pequena (Backend)

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Escrever o PRD               → /write-a-prd
 Passo 3  — Criar o plano geral          → /prd-to-plan
 Passo 3b — Escrever Stack & Skills      → (no plano geral)

 Planejamento concluido — plano pronto para implementacao
```

#### W4: Bug Fix

> **Principio:** economizar tokens. NAO mapear o projeto inteiro. Partir de uma referencia
> concreta dada pelo dev e investigar cirurgicamente a partir dela.

```
 Passo 1  — Pedir referencia de onde comecar
             Perguntar ao dev PRIMEIRO:
             > "Me passe uma referencia pra eu investigar sem varrer o projeto todo:
             >   - Arquivo/funcao suspeita, OU
             >   - Stack trace / mensagem de erro, OU
             >   - Endpoint / rota / componente afetado, OU
             >   - Passos para reproduzir + comportamento esperado vs atual"

             Fallback: se o dev NAO souber por onde comecar (nao tem stack trace,
             nao sabe o arquivo, nao consegue reproduzir), entao invocar
             /map-project para ganhar contexto minimo sobre a estrutura e voltar
             a tentar localizar o bug. Avisar o dev antes:
             > "Sem referencia, vou rodar /map-project pra entender a estrutura
             >  antes de investigar. Isso consome mais tokens — tudo bem?"

 Passo 2  — Investigar a partir da referencia (ou do mapeamento)
             - Ler somente os arquivos apontados e seus dependentes diretos
             - Reproduzir o bug mentalmente (ou pedir ao dev pra rodar)
             - Identificar causa raiz
             - NAO expandir a investigacao alem do necessario

 Passo 3  — Gerar o RELATORIO de diagnostico (docs/plans/bugfix-<slug>-report.md)
             Conteudo obrigatorio:
             - Resumo do bug (1-2 linhas)
             - Comportamento atual vs esperado
             - Causa raiz (com arquivo:linha quando aplicavel)
             - Arquivos afetados
             - Riscos / efeitos colaterais da correcao
             - Solucao RECOMENDADA (descricao tecnica detalhada)
             - Solucoes ALTERNATIVAS (listar 1-2 com trade-offs:
               por que nao foi escolhida, quando usar)

 Passo 4  — Gerar o PLANO de execucao (docs/plans/bugfix-<slug>-plan.md)
             Este e o documento que a skill /flow-dev-guide vai executar.
             Deve ser AUTO-CONTIDO — o executor nao precisa inferir nada.

             A sequencia de implementacao e OBRIGATORIAMENTE test-first:

               Step 1 — Escrever teste unitario que SIMULA o bug
                         - Deve FALHAR na branch atual (vermelho)
                         - Arquivo: <teste-alvo>
                         - Caso de teste: <nome descritivo do cenario do bug>
                         - Assercao: comportamento ESPERADO (nao o atual)
                         - Exemplo de codigo do teste (esqueleto pronto pra copiar)
               Step 2 — Rodar o teste e confirmar a falha (red)
                         - Comando exato: <npm/yarn/pnpm test ...>
               Step 3 — Implementar a CORRECAO RECOMENDADA
                         - Arquivos: <lista com caminhos absolutos>
                         - Mudanca minima necessaria
                         - Pseudo-codigo ou diff proposto (o suficiente
                           pro executor nao ter que re-investigar)
                         - Se houver alternativa plausivel, citar como
                           fallback: "Se X der errado, tentar Y (ver relatorio)"
               Step 4 — Rodar o teste e confirmar verde
               Step 5 — Rodar a suite completa para checar regressoes
                         - Comando exato: <npm/yarn/pnpm test>

             Diretriz: o plano deve conter codigo/pseudo-codigo suficiente
             pra que o /flow-dev-guide implemente sem precisar ler o
             codigo-fonte de novo. Copiar trechos relevantes do atual
             (antes) e do proposto (depois) quando ajudar.

 Passo 4b — Escrever "## Stack & Skills" no topo do PLANO
             (contrato com /flow-dev-guide — stack detectado + skills a carregar)

 Passo 5  — Oferecer salvar o RELATORIO na issue do GitHub
             Apos report + plan escritos, perguntar ao dev:
             > "Quer que eu salve o relatorio na descricao da issue do card?"

             Se SIM:
             > "Me passa a referencia do card (numero da issue, URL, ou nome do repo#numero)."

             Com a referencia em maos:
             - Usar a skill `/flow-github-issues` (preferencial) ou o `gh` CLI direto
             - Substituir/atualizar a descricao da issue com o CONTEUDO COMPLETO
               do `bugfix-<slug>-report.md` (nao do plan — o plan e interno)
             - Se a issue ja tem uma descricao nao-vazia:
               > "A issue ja tem descricao. Quero SOBRESCREVER ou ANEXAR o relatorio abaixo?"
             - Confirmar com o dev ANTES de sobrescrever
             - Apos sucesso, mostrar o link da issue atualizada

             Se NAO: seguir para o Passo 6.

 Passo 6  — Oferecer criar sub-issues por fase (so se houver fases)
             Inspecionar o PLANO (`bugfix-<slug>-plan.md`) para detectar fases:
             - "Fase" = unidade de trabalho separavel (ex: mudanca em arquivos
               diferentes, refactor independente, migration separada do codigo).
             - Se o plano so tem os Steps 1-5 classicos do W4 em um mesmo escopo
               (teste + fix + verify), NAO ha fases — pular este passo.
             - Se o plano tem secoes tipo "Fase 1:", "Fase 2:" ou subdivisoes
               logicamente independentes, HA fases.

             Se houver fases, perguntar:
             > "O plano tem [N] fases. Quer que eu crie uma sub-issue pra cada fase?"

             Se SIM (requer que o Passo 5 tenha salvado a issue pai, ou que o dev
             passe a referencia do pai agora):
             - Para cada fase: criar uma sub-issue linkada a issue pai
             - Titulo da sub-issue: "[Fase N] <nome da fase>"
             - Descricao da sub-issue: o que a fase faz (copiar a secao da fase
               do plan, incluindo arquivos afetados, pseudo-codigo e critt de
               conclusao dela)
             - Usar a skill `/flow-github-issues` para criar as sub-issues
               linkadas corretamente (parent/child)
             - Apos sucesso, listar os links de todas as sub-issues criadas

             Se NAO: seguir para a conclusao normal.

 Planejamento concluido — relatorio + plano prontos para implementacao
```

**Regras especificas do W4:**
- **PEDIR REFERENCIA PRIMEIRO** — economia de tokens e default.
- **/map-project so como FALLBACK** — quando o dev nao tem nenhuma referencia pra dar. Avisar o dev antes de invocar (consome mais tokens).
- **NAO** escrever codigo da correcao de verdade (nao edita arquivos do projeto). Esta skill so planeja — mas o plano DEVE conter pseudo-codigo, diffs propostos ou esqueletos suficientes pro /flow-dev-guide implementar sem re-investigar.
- **SEMPRE** incluir o teste que simula o bug como **primeiro passo de execucao** do plano. Sem excecao. Se for dificil escrever teste unitario, documente o motivo e proponha integracao ou E2E equivalente — mas algum teste que falhe antes e passe depois precisa existir.
- **SEMPRE** listar pelo menos a solucao recomendada + 1-2 alternativas no RELATORIO, com trade-offs. O PLANO usa a recomendada e pode citar a alternativa como fallback.
- **NAO** pular o Step 2 (confirmar red) no plano — e o que garante que o teste realmente cobre o bug.
- **SEMPRE oferecer salvar o RELATORIO na issue** (Passo 5) apos report+plan escritos — nunca salvar sem confirmar; nunca sobrescrever descricao existente sem confirmar se e pra sobrescrever ou anexar.
- **Sub-issues por fase sao condicionais** (Passo 6) — so oferecer se o plano realmente tiver fases separaveis; nao forcar sub-issues em bugfix simples de steps lineares.
- **Publicacao no GitHub e opt-in** — se o dev disser nao em qualquer um dos passos, seguir para a conclusao sem insistir.

#### W5: Refactoring

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Escrever o PRD               → /write-a-prd
 Passo 3  — Questionar o PRD             → /grill-me
 Passo 4  — Criar o plano geral          → /prd-to-plan
 Passo 4b — Escrever Stack & Skills      → (no plano geral)

 Para cada Fase do plano:
 +-----------------------------------------------------+
 | Passo 5a — Detalhar plano da fase                   |
 | Passo 5b — Checkpoint: prosseguir ou /grill-me?     |
 | Passo 5c — (se /grill-me) Revisar plano da fase     |
 +-----------------------------------------------------+
 Repetir ate todas as fases detalhadas e revisadas

 Planejamento concluido — planos prontos para implementacao
```

#### W6: Code Review

```
 Passo 1  — Carregar o PR                → /flow-code-review
 Passo 2  — Analisar mudancas
 Passo 3  — Publicar feedback

 Review concluido
```

#### W7: Testes E2E

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Identificar fluxos a testar
 Passo 3  — Documentar plano de testes (cenarios, page objects, fixtures)
 Passo 3b — Escrever Stack & Skills      → (no plano de testes)

 Planejamento concluido — plano de testes pronto para implementacao
```

#### W8: Feature Frontend

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Escrever o PRD               → /write-a-prd
 Passo 3  — Questionar o PRD             → /grill-me
 Passo 4  — Criar o plano geral          → /prd-to-plan
 Passo 4b — Escrever Stack & Skills      → (no plano geral)

 Para cada Fase do plano:
 +-----------------------------------------------------+
 | Passo 5a — Detalhar plano da fase                   |
 | Passo 5b — Checkpoint: prosseguir ou /grill-me?     |
 | Passo 5c — (se /grill-me) Revisar plano da fase     |
 +-----------------------------------------------------+
 Repetir ate todas as fases detalhadas e revisadas

 Planejamento concluido — planos prontos para implementacao
```

#### W9: Full Stack (Backend + Frontend)

```
 Passo 1  — Mapear o projeto             → /map-project
 Passo 2  — Escrever o PRD               → /write-a-prd
 Passo 3  — Questionar o PRD             → /grill-me
 Passo 4  — Criar o plano geral          → /prd-to-plan
 Passo 4b — Escrever Stack & Skills      → (no plano geral)

 Para cada Fase do plano:
 +-----------------------------------------------------+
 | Passo 5a — Detalhar plano da fase                   |
 | Passo 5b — Checkpoint: prosseguir ou /grill-me?     |
 | Passo 5c — (se /grill-me) Revisar plano da fase     |
 +-----------------------------------------------------+
 Repetir ate todas as fases detalhadas e revisadas

 Planejamento concluido — planos prontos para implementacao
```

### Passo 4b — Escrever Stack & Skills no plano geral

**Apos o plano geral ser criado** (pelo `/prd-to-plan`), adicionar a secao `## Stack & Skills` no topo do plano geral, logo apos o titulo:

```markdown
## Stack & Skills

**Workflow:** W[N] — [Nome do Workflow]
**Stack:** [frontend | backend | fullstack | e2e]

**Skills de implementacao:**
- [lista do Stack Skills Map para o stack detectado]

**Skills de teste:**
- [lista do Stack Skills Map para o stack detectado]

**Validacoes especificas:**
- [lista do Stack Skills Map para o stack detectado]
```

Para **fullstack**, separar por stack quando relevante:

```markdown
## Stack & Skills

**Workflow:** W9 — Full Stack
**Stack:** fullstack

**Skills de implementacao (frontend):**
- design-to-plan
- angular-component
- angular-signals
- feature-composition
- feature-state
- frontend-angular
- beta-template-guard

**Skills de implementacao (backend):**
- nestjs-best-practices

**Skills de teste:**
- e2e-zoppy
- playwright-best-practices

**Validacoes especificas (frontend):**
- ui-text exige htmlTag + type + className
- ps-icon com [icon] binding
- Classes Tailwind: nao usar PascalCase

**Validacoes especificas (backend):**
- DTOs com class-validator
- Guards com @UseGuards
- Services injetaveis via @Injectable
```

### Passo 5a — Detalhar plano de cada fase

**Antes de escrever o plano**, carregar as skills do stack relevantes para a fase usando a `Skill` tool. Isso garante que os exemplos de codigo e padroes no plano sigam as convencoes corretas.

**Skills a carregar por stack:**
- **frontend:** `angular-component`, `angular-signals`, `feature-composition`, `feature-state`, `frontend-angular` (carregar as que forem relevantes para a fase, nao todas sempre)
- **backend:** `nestjs-best-practices`, `controller`, `application-service`, `tdd`, `testing` (sempre carregar as skills de teste junto com as de implementacao)
- **fullstack:** combinar frontend + backend conforme a fase
- **e2e:** `e2e-zoppy`, `playwright-best-practices`

> **Regra:** Nao detalhar uma fase sem ter carregado ao menos as skills principais do stack. Os planos devem refletir os padroes das skills (ex: OnPush, signals, state services scoped, sem `standalone: true`).

> **Regra TDD:** Para fases backend, os planos de teste devem seguir TDD (Red-Green-Refactor). Os testes devem ser escritos ANTES da implementacao e devem FALHAR ate a implementacao estar completa. A sequencia de implementacao deve refletir isso: testes primeiro, depois implementacao. Para fases frontend, os testes unitarios seguem o padrao existente (Jasmine + Karma).

Ao detalhar cada fase, incluir no topo do plano da fase:

```markdown
**Stack desta fase:** [frontend | backend | fullstack]
**Skills de referencia:** [subset das skills do plano geral relevantes para esta fase]
```

Para fases fullstack, indicar claramente quais partes sao frontend e quais sao backend na sequencia de implementacao.

### Passo 5b — Checkpoint: prosseguir ou /grill-me?

**Apos escrever o plano detalhado da fase**, sempre perguntar ao dev:

> "Plano da Fase [N] escrito. Quer prosseguir para a proxima fase ou rodar `/grill-me` para revisar este plano antes?"

- Se o dev disser "prosseguir", "proximo", "ok", "avanca" → avance para o Passo 5a da proxima fase
- Se o dev disser "grill-me", "revisar", "quero revisar" → execute o `/grill-me` no plano da fase (Passo 5c)
- Apos o `/grill-me`, aplique os ajustes necessarios no plano e volte a perguntar se quer prosseguir

**Objetivo:** Garantir que nenhum detalhe ficou para tras antes de avançar, sem forcar uma revisao quando o dev esta confiante no plano.

### Confirmacao do workflow

Anuncie a escolha do workflow:

> "Parece que voce esta no **[Workflow N] — [Nome]**. Correto?"

Se o dev corrigir, ajuste sem questionar.

---

## Fase C — Acompanhamento passo a passo

### Formato do passo atual

Para cada passo, apresente sempre no mesmo formato:

```
---------------------------------------------------
Passo [N] de [Total] — [Nome do Passo]
---------------------------------------------------
O que fazer: [instrucao direta]
Skill: /nome-da-skill
Produz: [o que sai deste passo]
Concluido quando: [criterio objetivo]
---------------------------------------------------
```

### Progressao

- Avance **somente** quando o dev confirmar ("feito", "pronto", "ok", "conclui", "proximo", "avanca")
- Nunca pule passos sozinho, mas **sugira pulos explicitamente** quando o passo for opcional para a complexidade do trabalho:
  > "Este passo (/grill-me) e opcional para features pequenas. Quer pular?"
- Se o dev pular sem avisar, registre o risco:
  > "Voce pulou o /write-a-prd. Tudo bem para features simples, mas se surgir duvida sobre escopo no meio da implementacao, pode ser sinal de que valeria ter documentado antes."

### Se houver plano em `docs/plans/`

Substitua os passos genericos do workflow pelas fases do plano:

```
---------------------------------------------------
Fase [N] — [Nome da Fase do Plano]
---------------------------------------------------
```

Marque as fases concluidas quando o dev confirmar.

---

## Fase D — Respostas a duvidas durante o processo

Quando o dev fizer uma pergunta fora do passo atual, responda com base em:
1. O workflow em andamento
2. As convencoes do projeto (`project-conventions.md` se existir)
3. Seu conhecimento do stack detectado

**Sempre** termine a resposta voltando ao contexto:

> "Voltando: voce estava no **Passo [N] — [Nome]**. [Relembrando o que fazer]."

---

## Fase E — Conclusao

Quando todas as fases estiverem detalhadas e revisadas:

```
Planejamento concluido!

Artefatos gerados:
  - PRD em docs/prds/
  - Plano geral em docs/plans/ (com Stack & Skills definido)
  - [N] planos detalhados por fase em docs/plans/
  - Assets de design em docs/plans/assets/ (se aplicavel)

Pronto para implementacao:
  Os planos estao suficientemente detalhados para que
  agentes ou desenvolvedores executem fase por fase.

  Stack: [stack]
  Skills que o dev-guide-v2 carregara: [lista]

Quer comecar algo novo?
```

---

## Regras

- **Nunca implementa codigo** — esta skill so planeja
- **Nunca avanca sem confirmacao** do dev
- **Bug fix (W4) sempre comeca pedindo referencia** — economia de tokens e investigacao cirurgica. `/map-project` so como fallback quando o dev nao tem nenhuma pista, e com aviso previo.
- **Bug fix (W4) sempre inclui teste que simula o bug como primeiro passo de execucao** — red antes de green, sem excecao
- **Bug fix (W4) sempre inclui solucoes concretas no plano** — solucao recomendada com pseudo-codigo/diff + alternativas no relatorio, pra que /flow-dev-guide implemente sem precisar re-investigar
- **Nunca perde o contexto** do passo atual — mesmo apos responder duvidas, volta ao passo
- **Sempre escreve Stack & Skills no plano geral** — e o contrato com o dev-guide-v2
- **Sempre carrega skills do stack antes de detalhar fases** — para que os planos sigam os padroes corretos
- **Sempre pergunta sobre design quando o stack inclui frontend** — antes de detalhar cada fase
- **Nao assume stack** — detecta ou pergunta
- **Adapta o tom**: se o dev parece experiente (respostas curtas, pula confirmacoes), seja mais direto; se parece novo, explique mais
- **Nao repete instrucoes completas** desnecessariamente — apos o dev confirmar que sabe o que esta fazendo, seja conciso
- **Se o dev der contexto suficiente**, nao faca perguntas obvias — infira e confirme
- **O output final sao planos documentados** — nao codigo, nao PRs, nao commits
