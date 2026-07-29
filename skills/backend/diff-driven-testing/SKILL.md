---
name: diff-driven-testing
description: Audit and adjust the test suite so it covers exactly what the working state changed relative to origin/master — adding tests for new behavior, modifying tests for changed contracts, deleting tests for removed code. Use whenever the user asks to "update tests for my changes", "add tests for what I changed", "review test coverage of this branch", "tests for this diff", "ajustar testes", or before opening a PR.
---

# Diff-Driven Testing

## Definition of "working state"

**Working state = HEAD + staged + unstaged + untracked files.** This explicitly includes uncommitted but saved changes. Any diff command used here MUST surface those — if you only diff committed history you will miss the user's in-flight work and write the wrong tests.

## The Rule

For every behavioral change introduced in the working state vs `origin/master`, the test suite must change in lockstep:

| Change in working state | Test action |
|---|---|
| New public method / endpoint / branch | **Add** tests covering it (happy path + edge cases) |
| Signature or behavior changed (new param, new return shape, relaxed/tightened guard) | **Modify** existing tests; add new ones for the new behavior; assert the old behavior is gone |
| Public method / endpoint / branch removed | **Delete** tests that reference it |
| Pure refactor with identical behavior | No test change required — but verify by running the existing suite |

A diff that touches production code without a corresponding test diff is the default failure mode this skill exists to prevent.

## Workflow

### 1. Capture the working-state diff

Always include uncommitted work. Run, in order:

```bash
git fetch origin master
git status                       # see staged / unstaged / untracked
git diff --stat origin/master    # everything: committed + staged + unstaged
git diff origin/master           # full unified diff
```

Then check for **untracked** new files (they don't appear in `git diff` until added):

```bash
git ls-files --others --exclude-standard
```

If the user is on a feature branch, also confirm `origin/master` is up to date — never compare against `origin/staging` (per repo convention, staging is behind and produces noisy diffs).

### 2. Inventory the behavioral changes

For each changed file, list every behavioral change as a short bullet:

- New method / endpoint / queue processor / branch
- Changed signature, return type, or guard composition
- Changed business rule (validation, default value, condition)
- Removed code

Skip purely cosmetic changes (formatting, renames with no semantic impact, comment edits).

### 3. Map each change to its test layer

In zoppy-api, layers map to spec types:

- **Domain change** (`src/domain/*.ts`) → `*.domain.spec.ts` (unit-style, in-memory DB, single entity focus)
- **Application change** (`src/application/*.ts`) → `*.application.spec.ts` (integration, real domains, mock only external integrations)
- **Controller change** (`src/access/http/controllers/**/*.ts`) → `*.controller.spec.ts` (HTTP contract, supertest, status codes — never error message strings)
- **Queue processor change** (`src/access/queues/processors/*.ts`) → `*.processor.spec.ts`
- **Helper change** → `*.helper.spec.ts`

Always check the `testing` skill for the full layer-specific conventions before writing.

### 4. For each change, decide: add / modify / delete

For every behavioral change, search for existing tests:

```bash
grep -rn "<methodName>\|<endpointPath>" src --include="*.spec.ts"
```

Then:

- **Found and still correct** → modify only if assertions need updating.
- **Found but now wrong** (signature changed, behavior diverged) → modify the test to match new contract; if the old behavior is now impossible, delete the obsolete `it()` block.
- **Not found** → add it. Match the file's existing setup boilerplate; don't invent a new pattern.
- **Method/endpoint deleted in working state** → delete the corresponding `it()` blocks (and the whole spec file if nothing remains).

### 5. Surface bugs and asymmetries before writing

While reading the diff, watch for:

- A new param accepted at the controller/service layer but **not forwarded** through every branch of the call site (classic "added withTrashed but only one branch uses it" bug).
- A guard removed from one endpoint but kept on a sibling — intentional or oversight?
- New optional params with defaults that silently change behavior for old callers.

Flag these to the user before writing tests. Writing tests that lock in a bug is worse than writing none.

### 6. Write tests respecting project conventions

- Minimize mocks: use the in-memory DB via `TestUtils`. Never mock Domain classes.
- Match the spec file's existing setup; copy `beforeAll` / `beforeEach` / `afterEach` patterns.
- One behavior per `it()` block.
- Assert on status codes / error classes — never on error message strings (flaky).
- For write operations, verify side effects by querying the DB after the act.

### 7. Verify

- Run only the affected specs: `npm run test -- --testPathPattern="<file>"`.
- **Never run `npx tsc`** in this repo (extremely slow). Trust the test command's TS check.
- **Never weaken assertions** to make a failing test pass — fix the code instead.

## Forbidden commands

These are non-negotiable in this skill, regardless of any reasoning that seems to justify them:

- **No git mutation or state-juggling commands**, ever. That includes `git stash`, `git checkout`, `git reset`, `git restore`, `git revert`, `git rebase`, `git commit`, `git push`, `git merge`, `git cherry-pick`, `git clean`, and any flag combination that changes the working tree or refs. If you find yourself thinking "I'll just stash to peek at the prior state" — STOP. Read the diff, the file, or the history with read-only commands (`git log`, `git show`, `git diff`, `git blame`). The user handles all git operations themselves.
- **No `npx tsc`**. Extremely slow in this repo. Trust the test command's TS check.

If you genuinely cannot make progress without one of these, ask the user — do not run it.

## Decision boundaries — what you may NOT decide on your own

When a test asserts behavior that doesn't match what the code actually does, you have found a discrepancy between three possible truths:

1. The test is correct and the code is buggy (fix the code).
2. The code is correct and the test is wrong (fix the test).
3. Both are wrong and the actual intent is something else (fix both).

**You do not know which one is right.** That is a business-rule decision. You MUST ask the user before:

- Changing what a test asserts (changing expected values, renaming the test, deleting assertions).
- Marking a test as `it.skip` or removing it.
- "Updating the test to match current behavior" — that is a business-rule decision dressed up as a refactor.
- Changing production code to match a test that you assume is correct.
- Inferring intent from a test's name or description and acting on it.

Use `AskUserQuestion` with a clear description of the discrepancy and 2-3 concrete options. Examples of legitimate decisions you may make WITHOUT asking:

- Updating a test's type annotations to match a changed return type, when the asserted *behavior* is unchanged.
- Renaming a variable in a test for clarity, with no assertion change.
- Adding test infrastructure (model registration, provider mocks) needed to make existing-correct tests run.

Examples of decisions that REQUIRE asking:

- A test named "should clamp X to 10" asserts the clamped value, but no clamp logic exists. Is clamping intended? Or is the test wrong?
- A test seeds row A but the code-under-test requires rows A and B to coexist. Is the seeding incomplete or the code over-restrictive?
- A test asserts `errorMessage` contains the raw cause string, but the code wraps errors. Should the wrapper expose the raw string or is the wrap intentional?

## Anti-patterns

- Diffing against `origin/staging` instead of `origin/master`.
- Diffing only `HEAD` (committed) and missing the user's working tree changes.
- Ignoring untracked files (new spec files the user already created, new source files needing tests).
- Adding tests for code that didn't change "while you're in there" — out of scope.
- Writing tests that pin a bug instead of flagging the bug.
- Mocking Domains (forbidden in this repo) to make tests easier.
- **Implementation-coupled processor/controller tests.** When the application/service is mocked, do NOT also assert on `toHaveBeenCalledWith(...)`, `toHaveBeenCalledTimes(N)`, or `not.toHaveBeenCalled()` unless that call is the *behavior* under test. The processor's behavior toward BullMQ is its return value and side effects (DB writes, log lines) — those are what to assert. Internal call shape is implementation detail.
- **Reaching for `git stash` to "peek" at prior state.** Forbidden. Read the file or the diff instead.
