---
name: flow-publish
description: Push changes and create/update a Pull Request on GitHub. Use this skill whenever the user says "publish", "create a PR", "open a PR", "push and create PR", "send to review", "manda pro review", "publica", "cria um PR", "abre um PR", "manda pra remote", or any variation of pushing code and opening a pull request.
---

## Publish Workflow

Push local changes to remote and create or update a Pull Request.

### Step 1: Branch Protection

Complete this step BEFORE anything else — invoking /commit on a protected branch can cause real damage.

Check current branch:

```
git branch --show-current
```

**If on a protected branch** (main, master, develop):

1. Analyze staged changes or working tree to determine the branch type
2. Generate a branch name using conventional patterns:
    - `feat/<description>` — New features, additions
    - `fix/<description>` — Bug fixes
    - `refactor/<description>` — Code restructuring
    - `docs/<description>` — Documentation changes
    - `chore/<description>` — Maintenance, configs
3. Create and checkout immediately: `git checkout -b <generated-branch-name>`
4. Verify you are on the new branch before continuing

You MUST be on a non-protected branch before proceeding to Step 2.

### Step 2: Commit Changes

Check for uncommitted changes:

```
git status --porcelain
```

**If changes exist:** invoke the `/commit` skill to commit them.

**If no changes exist:** skip to Step 3.

### Step 3: Push to Remote

```
git push -u origin <current-branch>
```

### Step 4: Detect Base Branch

Determine which branch the current branch was created from — never assume `main` or `master`.

Use `git reflog` to find the branch that was active before the current branch was created:

```
git reflog show --format='%gs' | grep -m1 'checkout: moving from' | sed 's/checkout: moving from \(.*\) to .*/\1/'
```

If the reflog command returns empty (e.g., branch created outside this clone), fall back to the repository default:

```
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

### Step 4.5: Journey map

If the repo has a `jornadas.yml` at the root, check that every new file under `src/` in this branch has a journey before opening the PR:

```bash
curl -sf https://raw.githubusercontent.com/Zoppy-crm/.github/development/scripts/jornadas/jornadas_check.py -o /tmp/jornadas_check.py
python3 /tmp/jornadas_check.py origin/<base-branch> HEAD jornadas.yml
```

It prints the new files without a journey. For each folder listed, add the path to the right journey in `jornadas.yml` and commit it in this branch. If the right journey is not obvious, ask the user. Do not guess. The `Jornadas` check on the PR runs the same script.

### Step 5: Create or Update PR

Check if a PR already exists:

```
gh pr view --json number,title,body 2>/dev/null
```

**If PR exists:** analyze commits since base branch and update title/body with `gh pr edit`.

**If PR does not exist:**

1. Analyze commits: `git log <base>..HEAD --oneline`
2. Generate title from commits (Conventional Commits style)
3. Generate description summarizing changes
4. Create PR: `gh pr create --base <base-branch> --title "<title>" --body "<description>"`

### PR Language

Title and description MUST be in Portuguese (pt-BR). Technical prefixes (feat, fix, refactor) can stay in English.

### PR Rules

Never include in the PR:

-   AI attribution lines (e.g., "Generated with Claude Code")
-   Co-Authored-By signatures
-   Any automated tool signatures or footers

### PR Description Format

Use this template. Include the optional sections only when the diff actually adds routes or pages — omit them entirely otherwise.

```markdown
## Resumo

[Bullet points resumindo as mudanças com base nos commits]

## Mudanças

[Lista dos commits incluídos]

## Rotas adicionadas

[Incluir APENAS se novas rotas de API foram adicionadas no diff]

-   `METHOD /path/to/route` — Breve descrição do que a rota faz

## Páginas adicionadas

[Incluir APENAS se novas páginas/telas de front-end foram adicionadas no diff]

-   **Nome da página** (`/caminho`) — Breve descrição do que a página faz
```

**Test sections (when the PR adds or changes tests).** If the `test-design` skill ran on this branch, its sections go into the PR body, after "Mudanças" and in this order: `## Entradas testadas`, `## Perguntas feitas`, `## Suposições`, `## Achados`. Copy what it produced; do not summarize or rewrite it.

If the diff adds or changes `*.spec.ts` files and `test-design` did not run, still include the `## Achados` section with the three counter lines at zero (`Bugs pegos na criação dos testes: 0`, `Perguntas feitas: 0 (viraram bug: 0)`, `Suposições corrigidas pelo dev: 0 (viraram bug: 0)`), and tell the user the input table was not built. The text of those lines is fixed: they are counted automatically.

To detect new routes and pages, look at the diff (`git diff <base>..HEAD`) for:

-   **Routes:** new endpoint definitions — e.g., `router.get`, `router.post`, `app.use`, route file additions, controller decorators like `@Get()`, `@Post()`, etc.
-   **Pages:** new page/screen components — e.g., files in `pages/`, `views/`, `screens/`, or route config entries that map paths to components.

### Step 6: QA Report

After the PR is created or updated, invoke the `/qa-report` skill to post a QA report comment on the PR.

### Output

Return the PR URL when complete:

```
Published successfully!

Branch: <branch-name>
PR: <pr-url>
Title: <pr-title>
```
