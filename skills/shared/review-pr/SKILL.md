# Review de Pull Request

Revisa um Pull Request aplicando as regras de desenvolvimento do zoppy-api.

## Uso

Aceita como argumento:

-   Número da PR: `/review-pr 123`
-   URL da PR: `/review-pr https://github.com/Zoppy-crm/zoppy-api/pull/123`
-   Sem argumento: revisa o diff da branch atual contra a branch base

## Instruções

### 1. Coletar o diff

-   Se recebeu número/URL: use `gh pr diff <number>` para obter o diff e `gh pr view <number>` para contexto (título, descrição, branch)
-   Se sem argumento: use `git diff $(git merge-base HEAD development)..HEAD` para o diff local

### 2. Analisar cada arquivo modificado

Leia os arquivos completos (não só o diff) para entender o contexto. O diff sozinho não mostra se um padrão já existia ou se foi introduzido agora.

### 3. Aplicar o checklist de revisão

Para cada item, marque como aprovado ou reporte o problema com o path:line exato.

## Checklist de Revisão

### Arquitetura

-   [ ] **Camadas respeitadas**: Controller → Application → Domain → RepositoryAdapter. Nenhuma camada pulada.
-   [ ] **Controllers são thin facades**: sem lógica de negócio, apenas delegação para Application
-   [ ] **Sem Application injetando Application**: se precisam de lógica compartilhada, deve estar em Domain, Helper ou Service
-   [ ] **Domain-to-Domain injection**: só para relações pai-filho (foreign key). Domains não-relacionados não devem ser injetados entre si.
-   [ ] **Feature Module quando aplicável**: se a feature tem 2+ services privados, deve ter seu próprio módulo com exports seletivos (padrão UploadDataModule)

### Forbidden Patterns

-   [ ] **Sem Sequelize direto**: nenhum `Model.findOne()`, `Model.create()`, `Model.destroy()`, etc. Tudo via Domain.
-   [ ] **Sem `include`**: nenhum eager loading. Buscar entidades relacionadas separadamente.
-   [ ] **Sem O(n²)**: nenhum `.find()`, `.filter()`, `.some()`, `.includes()` dentro de loops. Usar `Map` ou `Set`.
-   [ ] **Sem hardcoded values**: nenhum magic number, string literal de status, URL inline. Usar enums, constants ou config.
-   [ ] **Sem `console.log`**: usar `LogService`.
-   [ ] **Sem `@Zoppy-crm/api-signatures`** para comunicação interna: usar queue services (BullMQ).

### Performance

-   [ ] **Queries independentes em paralelo**: chamadas async que não dependem uma da outra usam `Promise.all` ou `Promise.allSettled`
-   [ ] **Migrations com índices**: usam `ALGORITHM: 'INPLACE'` e `LOCK: 'NONE'` para evitar lock em tabelas grandes

### Controller

-   [ ] **Decorators obrigatórios**: `@ExceptionInterceptor()`, Swagger (`@ApiOperation`, `@ApiResponse`, `@ApiBearerAuth`)
-   [ ] **Write endpoints com `@UsingTransaction()`**: POST, PUT, PATCH, DELETE
-   [ ] **Input/Output tipados**: Request DTO de `src/access/http/requests/`, Response DTO de `src/access/http/response/`. Nunca retornar model Sequelize direto.

### Application

-   [ ] **`LOG_CONTEXT` definido**: toda Application deve ter `private readonly LOG_CONTEXT`
-   [ ] **Logging em mutações**: create/update/delete logam com `identifier: this.LOG_CONTEXT` e `extraStructuredMetadata`
-   [ ] **Queue dispatches logados**: log antes de cada `queueService.execute()` com nome da queue
-   [ ] **Validation classes**: create/update usam classes de validação dedicadas
-   [ ] **Error handling correto**: 404 para not found, 422 para validation, 400 para bad request. Sem try/catch genéricos que engolem o status code original.

### Domain

-   [ ] **Sem lógica de orquestração**: Domain faz data access, não coordena múltiplos domains
-   [ ] **Queries via RepositoryAdapter**: nenhuma query SQL raw ou Model direto

### Clean Code

-   [ ] **Métodos < 50 linhas**: métodos longos devem ser quebrados em métodos privados
-   [ ] **Nesting < 3 níveis**: extrair para early returns ou métodos auxiliares
-   [ ] **Sem código repetido**: blocos duplicados devem ser extraídos em métodos privados (no final da classe)
-   [ ] **Sem dead code**: imports não usados, branches inalcançáveis, variáveis não utilizadas
-   [ ] **Naming claro**: variáveis descrevem o conteúdo, não o tipo da operação

### Testing

-   [ ] **Testes incluídos**: features novas ou corrigidas têm testes correspondentes
-   [ ] **Sem mock de Domains**: testes usam banco in-memory via `TestUtils`, não `jest.spyOn` em domains
-   [ ] **Um comportamento por `it()`**: cada test case testa uma coisa
-   [ ] **Status codes corretos nos asserts**: 404 para not found (não 422), 400 para bad request

### Migrations

-   [ ] **Uma operação por migration**: não misturar create table com alter table de outra tabela
-   [ ] **`down()` implementado**: rollback deve ser possível
-   [ ] **Índices sem lock**: `ALGORITHM: 'INPLACE'`, `LOCK: 'NONE'`

## Formato do Output

Apresente a revisão no seguinte formato:

```
## Revisão: PR #<number> — <título>

### Aprovado
- <item aprovado com breve nota>

### Problemas encontrados

#### <severidade: BLOCKER | WARNING | SUGGESTION>: <descrição curta>
**Arquivo:** `path/to/file.ts:42`
**Regra:** <qual regra foi violada>
**Problema:** <o que está errado>
**Sugestão:** <como corrigir>

### Resumo
- Blockers: X
- Warnings: X
- Suggestions: X
- Veredicto: APPROVED / CHANGES REQUESTED
```

**Severidades:**

-   **BLOCKER**: viola uma regra crítica (forbidden patterns, arquitetura, segurança). PR não deve ser mergeada.
-   **WARNING**: viola uma boa prática mas não é crítico. Idealmente corrigir antes do merge.
-   **SUGGESTION**: melhoria opcional de clean code ou legibilidade.

Se não houver blockers nem warnings, marque como APPROVED. Se houver apenas suggestions, marque como APPROVED com nota.
