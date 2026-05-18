---
name: sets
description: >
    Multi-agent code review orchestration for the zoppy-api project. Spawns 4 specialized parallel
    review agents covering code quality, performance, test coverage, and security. Use this skill
    whenever doing a thorough PR review, pre-merge audit, or code quality gate. Triggers on:
    "full review", "thorough review", "parallel review", "run all review agents", "review this PR
    with all agents", "multi-agent review", or when the existing review-pr skill needs deeper analysis
    across multiple dimensions simultaneously.
---

# Multi-Agent Code Review Orchestration

## Role

You are a review orchestrator. When a full code review is requested, spawn the 4 agents below **in a single message** (all in parallel). Do not wait for one to finish before spawning the next.

---

## How to Spawn

Use the `Agent` tool with all 4 calls in one message. Each agent receives the diff or file list under review. Pass the PR number, branch name, or list of changed files in each agent's prompt.

```typescript
// Spawn all 4 in one message — never sequentially
Agent({ description: 'Code quality review', prompt: CODE_QUALITY_PROMPT });
Agent({ description: 'Performance review', prompt: PERFORMANCE_PROMPT });
Agent({ description: 'Test coverage review', prompt: TEST_COVERAGE_PROMPT });
Agent({ description: 'Security review', prompt: SECURITY_PROMPT });
```

After all 4 complete, consolidate their findings into a single report grouped by severity.

---

## Agent 1: Code Quality Reviewer

**Skill:** `skill-code-review` (architecture section)

**Prompt template:**

```
You are reviewing the following changed files for architectural correctness.
Apply the skill at .claude/skills/skill-code-review/SKILL.md — specifically the
Architecture Checklist and Code Quality Checklist sections.

Changed files: [LIST FILES OR DIFF HERE]

Report findings grouped by BLOCKER / WARNING / SUGGESTION with file:line references
and a proposed fix for each BLOCKER.
```

**Focus:**

-   Controller is a thin facade with all required decorators (`@ExceptionInterceptor`, `@UseGuards`, Swagger, `@UsingTransaction` on writes)
-   No Application injecting another Application
-   No direct Sequelize access outside Domain layer
-   No Sequelize `include`
-   All responses use typed Response DTOs, not raw models
-   No `console.log`, no hardcoded values, no `any` types

---

## Agent 2: Performance Reviewer

**Skill:** `skill-code-review` (performance section) + `api-development`

**Prompt template:**

```
You are reviewing the following changed files for performance issues.
Apply the Performance Checklist from .claude/skills/skill-code-review/SKILL.md
and cross-reference with .claude/skills/api-development/SKILL.md.

Changed files: [LIST FILES OR DIFF HERE]

Report each issue with: location (file:line), impact (CRITICAL/HIGH/MEDIUM),
and a concrete fix.
```

**Focus:**

-   O(n²) nested loops — flag and replace with `Map`/`Set`
-   Missing `Promise.all()` for independent async operations
-   Sequelize `include` (N+1 risk)
-   Heavy synchronous computation in request handlers
-   Missing Redis cache for repeated identical queries in hot paths

---

## Agent 3: Test Coverage Reviewer

**Skill:** `skill-tdd` + `testing`

**Prompt template:**

```
You are reviewing the following changed files for test coverage gaps.
Apply the skill at .claude/skills/skill-tdd/SKILL.md.

Changed files: [LIST FILES OR DIFF HERE]

For each new or modified class/method, identify:
1. Whether a corresponding .spec.ts file exists
2. Whether the layer-appropriate test type is used (unit for domain, integration for application, E2E for controller)
3. Which behaviors are untested (happy path, error branches, edge cases: null, empty array, boundary values)

Output: a list of untested paths with a suggested test case for each.
```

**Focus:**

-   New domain methods → unit test in `.spec.ts` using in-memory SQLite
-   New application methods → integration test covering all branches
-   New controller endpoints → E2E test covering 200/201, 400, 401, 403, 404
-   Edge cases: empty results, null fields, duplicate entries, concurrent writes

---

## Agent 4: Security Reviewer

**Skill:** `skill-code-review` (PII/security section)

**Prompt template:**

```
You are reviewing the following changed files for security and PII exposure.
Apply the PII / Security Checklist from .claude/skills/skill-code-review/SKILL.md.

Changed files: [LIST FILES OR DIFF HERE]

Report findings with severity (CRITICAL / HIGH / MEDIUM) and file:line references.
A CRITICAL finding blocks the merge.
```

**Focus:**

-   Response DTOs exposing `email`, `phone`, `cpf`, `document`, `birthDate`, `password`, `accessToken`
-   Controllers returning raw Sequelize models instead of DTOs
-   Exception logs serializing customer data from `request.body`
-   New endpoints missing authentication guards (`@UseGuards`, `@IsPublic()` used incorrectly)
-   Webhooks without HMAC or JWT validation
-   User-supplied input interpolated into log messages (log injection)

---

## Consolidated Report Format

After all 4 agents complete, merge findings into:

```
## Code Review: [PR title or branch]

### BLOCKERS (must fix before merge)
[List from all agents, de-duplicated, with file:line and fix]

### WARNINGS (should fix soon)
[List from all agents]

### SUGGESTIONS (optional improvements)
[List from all agents]

### Test Coverage Gaps
[List from Agent 3]

### Summary
- Quality: [pass/fail with agent 1 finding count]
- Performance: [pass/fail with agent 2 finding count]
- Test coverage: [pass/fail with agent 3 finding count]
- Security: [pass/fail with agent 4 finding count]
- Merge decision: APPROVED / APPROVED WITH COMMENTS / BLOCKED
```
