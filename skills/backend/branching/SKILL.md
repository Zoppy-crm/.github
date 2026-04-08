---
name: branching
description: >
  Branch naming conventions, PR workflow, and PR size policy for zoppy-api. Use this skill
  whenever creating a branch, opening a PR, naming a branch, reviewing PR size, or understanding
  the milestone/task/hotfix branch workflow. Triggers on: "create branch", "branch name", "nome
  da branch", "abrir PR", "open PR", "pull request", "how to branch", "PR too big", "PR grande",
  "milestone", "task branch", "hotfix", "GitHub Projects", "vinculação issue", "fatiamento de PR",
  "fluxo de branches", "staging", "tamanho de PR".
---

# Branching & Pull Requests

## Branch Naming Convention

| Type | Pattern | Example |
|---|---|---|
| Feature/Milestone | `milestone/<feature-name>` | `milestone/coupon-engine` |
| Task (sub-branch) | `task/<feature-name>/<issue-number>-<task-name>` | `task/coupon-engine/456-create-endpoint` |
| Hotfix | `hotfix/<issue-number>-<description>` | `hotfix/789-fix-order-sync-null` |

**Rules:**
- Always include the issue number in `task/*` and `hotfix/*` branches — this creates the automatic GitHub Projects link
- Names are kebab-case, short, and descriptive
- `milestone/*` branches are protected — no direct push, all changes enter via PR
- `task/*` branches are created from their corresponding `milestone/*`

---

## Branch Flow

```
milestone/<feature>  ← task/<feature>/<task-1>  (PR)
                     ← task/<feature>/<task-2>  (PR)
                     ← task/<feature>/<task-3>  (PR)

staging ← milestone/<feature>  (PR final)
master  ← staging
```

1. Create `milestone/<feature>` from `development`
2. For each unit of work, create `task/<feature>/<task>` from the milestone branch
3. Open PR: `task/...` → `milestone/...` — review and merge
4. When the feature is complete, open PR: `milestone/...` → `staging` → `master`

---

## Linking to GitHub Projects

The issue number in the branch name creates the automatic link. To close the card on merge, use keywords in the PR description:

```markdown
Closes #456
```

Valid keywords: `Closes`, `Fixes`, `Resolves` — on merge, the issue closes and the card moves automatically in GitHub Projects.

---

## PR Size Policy

**Target: ~200–400 lines changed per PR** (excluding unit tests).

Signs a PR is too large:
- Many unrelated files changed together
- Mixing refactor + feature + bugfix in the same PR
- Hard to describe the change in 2–3 sentences

If the PR is too large: **slice it** into smaller PRs. Each PR should be one well-defined change.

---

## PR Best Practices

**When opening a PR:**
- Write a clear, short description: what changes, why, how to test
- One PR = one well-defined change (bugfix, sub-feature, or focused refactor)
- Don't mix different concerns in the same PR
- Make sure CI is green before requesting review

**When reviewing a PR:**
- Give a thorough, objective review — not just "LGTM"
- Request slicing when the PR is too large or mixes concerns
- Verify there are sufficient tests for the changes
- Minimum 2 approvals before merge

**What NOT to do:**
- "Big bang" PRs with the entire feature at once
- Direct push to protected branches (`milestone/*`, `staging`, `master`)
- Merging without green CI or without enough reviews
- Leaving a PR open for days without action — review and integrate as soon as possible
