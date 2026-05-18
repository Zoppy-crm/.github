---
name: flow-map-project
description: Scans the current project to detect technologies, architecture, patterns, and conventions, then generates `.claude/custom/project-conventions.md` so the AI always understands the project before implementing code. Use when user wants to map project conventions, set up Claude for a new project, generate project documentation for AI context, or says "mapear projeto", "scan project", "map project", "project conventions", "analise o projeto", "entenda o projeto".
---

## Goal

Scan the current project, identify technologies, patterns, and architecture, and generate `.claude/custom/project-conventions.md` — a document loaded before every implementation so the agent follows the project's conventions.

## Process

### 1. Identify the project root

Look for the main manifest file in this order:

-   `package.json` → Node.js/JavaScript/TypeScript
-   `go.mod` → Go
-   `Cargo.toml` → Rust
-   `pom.xml` / `build.gradle` / `build.gradle.kts` → Java/Kotlin
-   `pyproject.toml` / `setup.py` / `requirements.txt` → Python
-   `composer.json` → PHP
-   `Gemfile` → Ruby
-   `*.csproj` / `*.sln` → C#/.NET
-   `mix.exs` → Elixir
-   `pubspec.yaml` → Dart/Flutter

### 2. Collect project information

Run in parallel:

**Stack and dependencies:**

-   Read the main manifest (package.json, go.mod, etc.)
-   Identify: primary runtime/language, frameworks, test libraries, bundler, linter/formatter

**Folder structure:**

-   List 2–3 levels deep (excluding node_modules, .git, dist, build, **pycache**, .venv)
-   Identify the organization pattern: by feature, by layer (MVC), monorepo, etc.

**Quality configuration:**

-   Read `.eslintrc*`, `.prettierrc*`, `tsconfig.json`, `pyproject.toml[tool.ruff]`, `.rubocop.yml`, `golangci.yml`, `rustfmt.toml`, etc.
-   Identify: style rules, prohibited imports, naming conventions

**Code patterns (sampling):**

-   Read 3–5 representative source files from different parts of the project
-   Prioritize: a controller/handler, a model/entity, a service/usecase, a test
-   Identify: naming conventions (camelCase, snake_case, PascalCase), function structure, type usage, error patterns

**Test patterns:**

-   Read 2–3 existing test files
-   Identify: test framework, organization pattern (describe/it, test suites), mock usage, test file naming convention

**CI/CD:**

-   Check `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `Dockerfile`, `docker-compose.yml`
-   Identify: existing pipelines, environments, build/test/deploy commands

**Existing documentation:**

-   Read `README.md`, `CONTRIBUTING.md`, `docs/` if they exist
-   Extract already-documented conventions

### 3. Generate the conventions document

Create the `.claude/custom/` directory if it doesn't exist.

Write `.claude/custom/project-conventions.md` following this template:

```markdown
# Project Conventions

> Gerado por map-project em [DATA]
> Para atualizar: execute `/map-project`

## Stack Principal

-   **Linguagem:** [ex: TypeScript 5.x]
-   **Runtime:** [ex: Node.js 20]
-   **Framework:** [ex: NestJS 10]
-   **Banco de dados:** [ex: PostgreSQL via Prisma ORM]
-   **Testes:** [ex: Jest + Supertest]
-   **Build:** [ex: esbuild via tsup]
-   **Linting/Format:** [ex: ESLint + Prettier]

## Arquitetura

[Descreva o padrão arquitetural identificado, ex:]

-   Arquitetura hexagonal / Clean Architecture / MVC / CQRS
-   Separação em camadas (ex: controllers → services → repositories)
-   Módulos ou bounded contexts identificados

## Estrutura de Pastas
```

[Cole a estrutura de pastas relevante com descrição de cada diretório]

````

## Convenções de Código

### Nomes
- Arquivos: [ex: kebab-case: user-service.ts]
- Classes: [ex: PascalCase: UserService]
- Funções/métodos: [ex: camelCase: getUserById]
- Variáveis: [ex: camelCase]
- Constantes: [ex: SCREAMING_SNAKE_CASE]
- Tipos/Interfaces: [ex: PascalCase com prefixo I para interfaces: IUserRepository]
- Tabelas DB: [ex: snake_case plural: users, order_items]

### Padrões de Importação
[ex: imports absolutos com @ alias, ordem: externos → internos → relativos]

### Tratamento de Erros
[ex: exceções customizadas em src/errors/, never throw strings, use Result type]

### Tipagem
[ex: strict mode ativo, no any, prefer interface over type for objects]

## Padrões de Teste

- **Framework:** [ex: Jest]
- **Localização:** [ex: arquivos .spec.ts colocalizados com o source]
- **Convenção de describe/it:** [ex: describe('UserService', () => { it('deve criar usuario', ...) })]
- **Mocks:** [ex: apenas em boundaries externos (DB, HTTP), nunca de módulos internos]
- **Coverage mínima:** [se configurada]

## Comandos Essenciais

```bash
# Desenvolvimento
[comando para iniciar dev server]

# Testes
[comando para rodar testes]

# Build
[comando para build]

# Linting
[comando para lint/format]
````

## Padrões Específicos do Projeto

[Qualquer padrão, abstração ou decisão arquitetural importante identificada no código que não se encaixa nas categorias acima. Ex: "Toda query ao banco usa o QueryBuilder customizado em src/db/query-builder.ts, nunca acesse o DB diretamente"]

## O que NÃO Fazer

[Antipadrões identificados no projeto, regras do linter, comentários em código ou README indicando o que deve ser evitado]

````

### 4. Register in the project instructions

Check if a `CLAUDE.md` exists at the project root or at `.claude/CLAUDE.md`.

**If it does not exist**, create `CLAUDE.md` at the root with:

```markdown
# Instruções para o Agente

## Antes de Implementar

Sempre que solicitado a implementar, criar, modificar ou refatorar código:

1. Leia `.claude/custom/project-conventions.md`
2. Siga as convenções de naming, arquitetura e padrões definidos
3. Se o arquivo não existir, avise o usuário e sugira executar `/map-project`
````

**If it already exists**, append at the end (only if the "Antes de Implementar" section does not already exist):

```markdown
## Antes de Implementar

Sempre que solicitado a implementar, criar, modificar ou refatorar código:

1. Leia `.claude/custom/project-conventions.md`
2. Siga as convenções de naming, arquitetura e padrões definidos
3. Se o arquivo não existir, avise o usuário e sugira executar `/map-project`
```

### 5. Report to the user

Present a summary of what was detected:

```
✅ project-conventions.md gerado em .claude/custom/

📦 Stack: [linguagem] + [framework]
🏗️  Arquitetura: [padrão identificado]
🧪 Testes: [framework]
📁 [N] módulos/pacotes identificados

O agente lerá este documento antes de toda implementação.
Para atualizar após mudanças no projeto: /map-project
```

## Important Notes

-   **Do not modify project code** — this skill is read-only (except for `.claude/`)
-   **If the project is large**, prioritize representative sampling rather than reading all files
-   **If there are conflicting conventions** between what is configured (eslint/linter) and what is in the code, document both and flag the conflict
-   **Update rather than replace** — if `.claude/custom/project-conventions.md` already exists, update its content while preserving sections the user may have edited manually (preserve `<!-- manual -->` comments)
