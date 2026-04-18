---
name: flow-handoff
description: Generates or updates the handoff document (docs/plans/handoff.md) at the end of a phase — structured baton-pass so the next session has full context without needing the previous conversation. Use when the user says "handoff", "passagem de bastão", "atualizar handoff", or when invoked automatically by beta-dev-guide at the end of a phase.
---

# Handoff — Passagem de Bastão entre Sessões

Gera/atualiza o documento `docs/plans/handoff.md` com o contexto necessário para que uma **nova sessão** consiga retomar a implementação sem perda de informação.

## Quando executar

- No final de cada fase implementada (invocado pelo `beta-dev-guide`)
- Quando o dev pedir explicitamente (`/flow-handoff`)
- Antes de encerrar uma sessão longa

## Como gerar o handoff

### 1. Coletar contexto da fase concluída

Reunir informações de:
- **Plano da fase** (`docs/plans/fase-XX-*.md`) — o que era esperado
- **Git diff/log** — o que foi realmente implementado
- **Decisões tomadas** — desvios do plano, adaptações, descobertas
- **Erros encontrados e corrigidos** — bugs que podem afetar fases futuras
- **Estado do plano geral** — quais fases estão concluídas

### 2. Escrever/atualizar o handoff

O arquivo é **sempre sobrescrito** (não acumula histórico — apenas o estado atual).

Usar **exatamente** este template:

```markdown
# Handoff — Passagem de Bastão

> Atualizado em: [YYYY-MM-DD] | Sessão encerrada após: Fase [N] — [Nome]

## Status Geral

| Fase | Nome | Status |
|------|------|--------|
| 1 | [nome] | Concluída |
| 2 | [nome] | Concluída |
| 3 | [nome] | Concluída |
| 4 | [nome] | **Próxima** |
| ... | ... | Pendente |

## Última fase concluída: Fase [N] — [Nome]

### O que foi implementado
- [Lista objetiva dos artefatos criados/modificados com caminhos]
- Ex: Criado `src/app/features/integrations/components/foo/foo.component.ts`
- Ex: Atualizado `src/app/features/integrations/integrations.routes.ts` com nova rota

### Decisões tomadas durante a implementação
- [Decisões que divergiram do plano ou que não estavam previstas]
- Ex: Optei por usar Signal em vez de BehaviorSubject porque o componente é standalone
- Ex: O endpoint /api/foo retorna paginação diferente do esperado, adaptei o model

### Problemas encontrados e resolvidos
- [Bugs, incompatibilidades, ou surpresas que foram resolvidas]
- Ex: O ui-select não suportava ngModel, troquei por reactive forms
- Se nenhum: "Nenhum problema relevante."

### Débitos técnicos / pendências não-blocantes
- [TODOs que ficaram para depois, melhorias adiadas]
- Se nenhum: "Nenhum débito técnico pendente."

## Contexto crítico para a próxima fase

### Artefatos-chave já disponíveis
- [Services, models, componentes que a próxima fase vai consumir]
- Ex: `IntegrationStateService` já expõe `selectedProvider$` signal

### Dependências entre fases
- [Se a próxima fase depende de algo específico desta]
- Ex: A fase 5 espera que o model `IntegrationProvider` tenha o campo `configSchema`

### Alertas
- [Qualquer coisa que a próxima sessão PRECISA saber para não errar]
- Ex: Não usar HttpClient direto — todos os services estendem ApiService
- Se nenhum: "Sem alertas."

## Registro de branches por fase

| Fase | Nome | Branch | Worktree |
|------|------|--------|----------|
| 1 | [nome] | `feature/[nome]-fase-01` | `.worktrees/feature/[nome]-fase-01` |
| 2 | [nome] | `feature/[nome]-fase-02` | `.worktrees/feature/[nome]-fase-02` |
| ... | ... | ... | ... |

> Use esta tabela para saber qual branch alterar caso um bug ou ajuste seja encontrado em uma fase já concluída. Sempre atualizar ao concluir cada fase.

## Branch e referências

- **Branch atual**: `feature/[nome]`
- **Último commit**: `[hash curto]` — [mensagem]
- **Plano geral**: `docs/plans/[nome].md`
- **Plano da próxima fase**: `docs/plans/fase-[NN]-[nome].md`
```

### 3. Validar o handoff

Antes de salvar, verificar:
- [ ] A tabela de status reflete a realidade (`git log`, checkboxes dos planos)
- [ ] As decisões listadas são **não-óbvias** (não repetir o que já está no código)
- [ ] O "contexto crítico" realmente ajuda — se remover, a próxima sessão erraria?
- [ ] Branch e commit estão corretos (`git branch --show-current`, `git log -1 --oneline`)

### 4. Salvar

```bash
# O arquivo é sempre docs/plans/handoff.md
```

Se o arquivo já existe, **sobrescrever completamente** com o estado atual.

## Regras

- **Sempre sobrescreve** — o handoff é um snapshot do estado atual, não um log
- **Seja objetivo** — a próxima sessão não tem contexto emocional, apenas fatos
- **Inclua caminhos completos** — `src/app/features/...`, não "o componente foo"
- **Decisões > descrições** — "Usei X porque Y" vale mais que "Implementei o componente"
- **Não repita o plano** — o plano já existe em `docs/plans/`. O handoff complementa com o que aconteceu de diferente ou relevante
- **Alertas são críticos** — se a próxima sessão pode cometer um erro sem essa informação, é um alerta
- **Sempre atualizar o registro de branches** — ao concluir cada fase, adicionar/atualizar a linha correspondente na tabela "Registro de branches por fase". Nunca deixar a tabela incompleta — ela é a referência para correções em fases passadas
