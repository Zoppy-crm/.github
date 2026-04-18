---
name: flow-code-review
description: Performs a comprehensive pull request review covering bugs, project conventions, test quality, and architecture. Use when the user says "revisar PR", "fazer code review", "review do PR", "checar o PR", "analisar as mudanças", "code review", "revisar o diff", "revisa essa PR", "dá uma olhada na PR #123", "faz o review", "revisa o diff da branch atual", or when reviewing someone else's pull request — this skill goes beyond bug detection to check conventions, test coverage, and architectural concerns.
---

# Code Review Skill

Performs a structured review of a pull request across five dimensions: bugs, conventions, tests, architecture, and PR quality. Produces a report that can be posted directly as a GitHub review.

## Uso

Aceita como argumento:

- Número da PR: `/flow-code-review 123`
- URL da PR: `/flow-code-review https://github.com/Zoppy-crm/zoppy-api/pull/123`
- Sem argumento: revisa o diff da branch atual contra a branch base

## Workflow

### 1. Collect PR data

```bash
gh pr view --json number,title,body,baseRefName,headRefName,additions,deletions
gh pr diff
```

If no PR number is provided and there is no open PR on the current branch, ask the user for the PR number. Fallback local: `git diff $(git merge-base HEAD development)..HEAD`.

### 2. Load project conventions

Read `.claude/custom/project-conventions.md` if it exists. This is the reference for naming, patterns, and antipatterns. If it does not exist, skip convention checks and note this in the report.

### 3. Analyze each modified file

Leia os arquivos completos (não só o diff) para entender o contexto. O diff sozinho não mostra se um padrão já existia ou se foi introduzido agora.

### 4. Analyze the diff

Analyze in parallel across five categories:

#### A. Bugs
Check for real defects — not style issues:
- Logic errors: inverted conditions, wrong comparisons, off-by-one
- Missing error handling: unhandled promises, silenced exceptions
- State and side effects: mutations on shared state, race conditions
- Null/undefined: unchecked access on values that can be null
- Security: SQL injection, XSS, hardcoded secrets, missing input validation
- Type coercion: implicit `==` comparisons, unintended falsy checks
- Edge cases: empty arrays, zero values, empty strings not handled

#### B. Conventions
Compare diff against `project-conventions.md`:
- Naming: files, functions, variables, types follow project patterns
- File structure: new files in the correct directories
- Import patterns: correct aliases, correct ordering
- Error handling: follows project's error pattern
- Antipatterns: any pattern listed in the "O que NÃO Fazer" section

#### C. Tests
- New behavior introduced — is it tested?
- Tests follow project's test patterns (describe/it style, file naming, co-location)
- Tests verify behavior through public interfaces, not implementation details
- No `test.only` or `test.skip` left behind
- Mock usage consistent with project conventions

#### D. Architecture
- Does the change respect the existing layer boundaries (controller → service → repository)?
- Is new logic placed in the correct layer/module?
- Are new abstractions necessary, or is existing code reused?
- Does the change introduce undesirable coupling?

#### E. PR Quality
- Title follows Conventional Commits format
- Description explains the "why", not just the "what"
- PR scope is focused (not mixing features with refactoring)
- No debug artifacts (console.log, commented-out code, TODO without tracking)

### 5. Build the report

Use this structure. Only include categories with findings — omit empty categories.

```markdown
## Code Review — PR #<número>: <título>

### 🐛 Bugs
**[CRÍTICO | ALTO | MÉDIO | BAIXO]** `path/to/file.ts:linha`
> Descrição do problema e risco concreto.
`` `suggestion
código corrigido sugerido (opcional)
` ``

### 📐 Convenções
**[ALTO | MÉDIO | BAIXO]** `path/to/file.ts`
> O que desrespeita a convenção e qual é a convenção esperada.

### 🧪 Testes
**[ALTO | MÉDIO | BAIXO]**
> O que está faltando em cobertura ou o que está errado no padrão.

### 🏗️ Arquitetura
**[ALTO | MÉDIO | BAIXO]**
> Problema arquitetural identificado.

### 📋 Qualidade do PR
**[BAIXO]**
> Observações sobre o PR em si.

---
**Resumo:** X bugs · Y problemas de convenção · Z problemas de teste
**Recomendação:** ✅ Aprovar | 🔄 Aprovar com ajustes | ❌ Solicitar mudanças
```

### 6. Post the review (optional)

Ask the user if they want to post the review on GitHub:

> "Quer que eu poste esse review como comentário no PR #<número>?"

If yes:
```bash
gh pr review <number> --comment --body "<report>"
```

## Severity Guide

| Nível | Quando usar |
|-------|------------|
| CRÍTICO | Bug que causa perda de dados, falha de segurança, ou crash em produção |
| ALTO | Bug que causa comportamento incorreto em casos normais, ou convenção central violada |
| MÉDIO | Bug em casos de borda, convenção secundária violada, test quality issue |
| BAIXO | Sugestão de melhoria, nit, PR quality |

## Checklist detalhado — zoppy-api (backend NestJS)

Use este checklist como referência concreta quando o PR for do `zoppy-api` (ou repo backend NestJS similar) e o `project-conventions.md` não detalhar todos os pontos.

### Arquitetura
- [ ] **Camadas respeitadas**: Controller → Application → Domain → RepositoryAdapter. Nenhuma camada pulada.
- [ ] **Controllers são thin facades**: sem lógica de negócio, apenas delegação para Application
- [ ] **Sem Application injetando Application**: se precisam de lógica compartilhada, deve estar em Domain, Helper ou Service
- [ ] **Domain-to-Domain injection**: só para relações pai-filho (foreign key). Domains não-relacionados não devem ser injetados entre si.
- [ ] **Feature Module quando aplicável**: se a feature tem 2+ services privados, deve ter seu próprio módulo com exports seletivos (padrão UploadDataModule)

### Forbidden Patterns
- [ ] **Sem Sequelize direto**: nenhum `Model.findOne()`, `Model.create()`, `Model.destroy()`, etc. Tudo via Domain.
- [ ] **Sem `include`**: nenhum eager loading. Buscar entidades relacionadas separadamente.
- [ ] **Sem O(n²)**: nenhum `.find()`, `.filter()`, `.some()`, `.includes()` dentro de loops. Usar `Map` ou `Set`.
- [ ] **Sem hardcoded values**: nenhum magic number, string literal de status, URL inline. Usar enums, constants ou config.
- [ ] **Sem `console.log`**: usar `LogService`.
- [ ] **Sem `@Zoppy-crm/api-signatures`** para comunicação interna: usar queue services (BullMQ).

### Performance
- [ ] **Queries independentes em paralelo**: chamadas async que não dependem uma da outra usam `Promise.all` ou `Promise.allSettled`
- [ ] **Migrations com índices**: usam `ALGORITHM: 'INPLACE'` e `LOCK: 'NONE'` para evitar lock em tabelas grandes

### Controller
- [ ] **Decorators obrigatórios**: `@ExceptionInterceptor()`, Swagger (`@ApiOperation`, `@ApiResponse`, `@ApiBearerAuth`)
- [ ] **Write endpoints com `@UsingTransaction()`**: POST, PUT, PATCH, DELETE
- [ ] **Input/Output tipados**: Request DTO de `src/access/http/requests/`, Response DTO de `src/access/http/response/`. Nunca retornar model Sequelize direto.

### Application
- [ ] **`LOG_CONTEXT` definido**: toda Application deve ter `private readonly LOG_CONTEXT`
- [ ] **Logging em mutações**: create/update/delete logam com `identifier: this.LOG_CONTEXT` e `extraStructuredMetadata`
- [ ] **Queue dispatches logados**: log antes de cada `queueService.execute()` com nome da queue
- [ ] **Validation classes**: create/update usam classes de validação dedicadas
- [ ] **Error handling correto**: 404 para not found, 422 para validation, 400 para bad request. Sem try/catch genéricos que engolem o status code original.

### Domain
- [ ] **Sem lógica de orquestração**: Domain faz data access, não coordena múltiplos domains
- [ ] **Queries via RepositoryAdapter**: nenhuma query SQL raw ou Model direto

### Clean Code
- [ ] **Métodos < 50 linhas**: métodos longos devem ser quebrados em métodos privados
- [ ] **Nesting < 3 níveis**: extrair para early returns ou métodos auxiliares
- [ ] **Sem código repetido**: blocos duplicados devem ser extraídos em métodos privados (no final da classe)
- [ ] **Sem dead code**: imports não usados, branches inalcançáveis, variáveis não utilizadas
- [ ] **Naming claro**: variáveis descrevem o conteúdo, não o tipo da operação

### Testing
- [ ] **Testes incluídos**: features novas ou corrigidas têm testes correspondentes
- [ ] **Sem mock de Domains**: testes usam banco in-memory via `TestUtils`, não `jest.spyOn` em domains
- [ ] **Um comportamento por `it()`**: cada test case testa uma coisa
- [ ] **Status codes corretos nos asserts**: 404 para not found (não 422), 400 para bad request

### Migrations
- [ ] **Uma operação por migration**: não misturar create table com alter table de outra tabela
- [ ] **`down()` implementado**: rollback deve ser possível
- [ ] **Índices sem lock**: `ALGORITHM: 'INPLACE'`, `LOCK: 'NONE'`

## Rules

- Focus on the diff — do not comment on pre-existing code outside the changed lines
- Report real problems, not subjective preferences
- Include file path and line reference for every finding
- Recommend fixes where possible — do not just point out problems
- If `project-conventions.md` does not exist, skip categories B and D and mention this limitation in the report
- Do not post the review without explicit user confirmation
