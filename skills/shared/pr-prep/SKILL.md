---
name: pr-prep
description: Prepare a PR for fast human review — post line-anchored WHY-comments on every significant change and pre-mark trivial files (specs, wiring, lockfiles) as Viewed, all via gh CLI. Use when the user says "prep the PR", "run the PR prep", "review prep", "mark trivial files viewed", "add explanation comments to the PR", "prepara o PR pra review", or after opening/rebasing any PR the user will review. Requires the user's explicit permission once per session (viewed-marking writes review state under their identity).
---

# PR Review-Prep

Make a PR reviewable in minutes: the reviewer opens it and finds (a) every noise file already checked off, and (b) a WHY-comment anchored at every change location that needs justification. Everything runs through `gh` — no browser.

**Authorization gate:** viewed-marking mutates the USER's review-tracking state on GitHub. Only run this skill when the user asked for it (this invocation counts). Never approve, request changes, submit review verdicts, resolve threads, or delete existing comments.

**Delegate execution to a subagent** (main thread stays lean); pass it this procedure plus the PR-specific rationale map.

## Procedure

### 0. Inventory

```
gh pr view <N> --repo <owner/repo> --json files,headRefOid
gh pr diff <N> --repo <owner/repo> > /tmp/.../pr<N>.diff     # grep per path; never paste whole diff into context
gh api repos/<owner>/<repo>/pulls/<N>/comments --paginate    # existing comments; never duplicate content
```

### 1. Classify

- **TRIVIAL** → will be marked Viewed: `*.spec.ts` / test files; module-wiring or import-only diffs; renames/DI-swaps with no logic change; `package-lock.json`.
- **SIGNIFICANT** → stays UNVIEWED, gets comments: everything with behavior, structure, or dependency changes (`package.json` dependency changes are significant).
- Be conservative: any logic edit = significant. When in doubt, significant.

### 2. WHY-comments (the diff shows WHAT — comments carry only WHY)

One comment per meaningful hunk, grounded in evidence (production numbers, rulings, design rationale). English or the PR body's language — be consistent within one prep.

- **Every comment answers FOUR questions, compactly** (a sentence or clause each; skip one ONLY when it is genuinely trivial for that hunk, e.g. no alternative exists):
  1. **WHAT** changed (one clause — the diff shows it, so just orient).
  2. **WHY** — the decision process: what made it possible / what forced it.
  3. **REGRESSION HONESTY** — one of two, never a blur: (a) behavior is unchanged → give the equivalence argument (same source of truth, provably identical values, test that pins it); or (b) behavior CHANGES → say so plainly, state the delta, and point to where it is flagged/ruled (PR-body delta number, decision-log entry). Regressions and behavior changes are normal in this work; the sin is a comment that argues "no regression" for a hunk that has one, or stays silent about a delta the reviewer will discover in production. If neither (a) nor (b) can be written, the change is unanalyzed — escalate before prepping.
  4. **WHY NOT THE ALTERNATIVES** — name the nearest alternative a reviewer would think of and why it lost. A comment that cannot answer #4 usually means the change itself wasn't argued — escalate it before prepping it.

- **Prefix every prep comment** with `🤖 [prep]` as the first token of the body, so prep comments are distinguishable at a glance from human review comments.
- **The WHY is the decision process, not the decision restated.** For every removal/reduction: what made it *possible* (which caller died, which invariant now guarantees it, which evidence proved it unused)? For every addition: what *forced* it (which gap, which consumer, which rule)? A comment that explains what was decided but not why it *could* be decided is incomplete — "removed param X" is WHAT; "param X's only consumer was the resolver deleted in this PR, so no caller can supply it" is WHY. Test each comment: could the reviewer reconstruct the reasoning chain from it, or only the conclusion?

```
# line-anchored (new side):
gh api repos/<o>/<r>/pulls/<N>/comments -f body='...' -f commit_id=<headRefOid> \
  -f path=<file> -F line=<n> -f side=RIGHT [-F start_line=<m> -f start_side=RIGHT]

# file-level (deleted files, specs, or when no hunk anchor makes sense):
gh api repos/<o>/<r>/pulls/<N>/comments -f body='...' -f commit_id=<headRefOid> \
  -f path=<file> -f subject_type=file
```

- Anchors must be lines INSIDE the PR's hunks; unchanged context lines can't hold comments — anchor at the nearest in-diff line and name the target in the body.
- **Placement is part of the message**: anchor each comment at the exact line where the decision it explains is visible (the new guard, the changed constant, the call that replaced the block) — not at the top of the file, not on the import, not on the first hunk that happens to exist. A comment the reviewer meets three screens away from what it explains is a badly placed comment. Use file-level comments ONLY for deleted files, whole-file moves, and coverage notes — never as a shortcut when a precise hunk exists.
- **Coverage is per-hunk, not per-file**: one comment per file does NOT satisfy the prep when the file contains several independent non-trivial changes — each meaningful hunk gets its own anchored comment. After posting, re-walk the file's diff hunk by hunk and ask "would the reviewer understand this hunk from the comments present?"; if not, it's uncovered.
- **Never reference finding/debt codes bare** (F-13, H-2, B-2, N7…): spell out what the finding IS in plain words, then optionally cite the code with its doc path as the anchor — e.g. "o guard duplicado de manager (scour: docs/wpp-scour-refactor-edges.md, F-13)". The docs are local to the repo checkout, so the path is the only usable pointer — a bare code is noise to any reviewer.
- Deleted files: one file-level comment saying where the behavior lives now.
- Spec files with meaningful migrations: one file-level comment summarizing what coverage moved/changed (they're still marked Viewed).
- Information diet: comments state the final design as if it was always the design — no reversal history.
- Verify every POST returned a comment id.
- **Large-diff flag:** GitHub auto-collapses large diffs ("Load diff" placeholder), which makes a significant file look like a deletion or an already-handled file — and no API can force-expand it. For every SIGNIFICANT file whose diff GitHub will collapse (roughly >400 changed lines or very large hunks — check `additions+deletions` from the files list), post a file-level comment FIRST in that file, prefixed `🤖 [prep] ⚠ collapsed by size — expand this file`, followed by a 2-4 line map of where the meaningful hunks are (line ranges + one clause each) so the reviewer knows what they're expanding into.
- **Coverage invariant: every UNVIEWED file has ≥1 comment.** Left-unviewed means "something non-trivial here" — if there's nothing non-trivial to say about a file, it's trivial and belongs in the Viewed set instead. After posting, sweep the significant list and fix violations: either post the missing comment (file-level if no hunk stands out) or reclassify the file as trivial and mark it Viewed. Zero files may end the prep both unviewed and uncommented.

### 3. Viewed-marking (GraphQL — no browser)

```
gh api graphql -f query='query{repository(owner:"<o>",name:"<r>"){pullRequest(number:<N>){id}}}'
gh api graphql -f query='mutation{markFileAsViewed(input:{pullRequestId:"<id>",path:"<path>"}){pullRequest{id}}}'
# verify:
gh api graphql -f query='query{repository(owner:"<o>",name:"<r>"){pullRequest(number:<N>){files(first:100){nodes{path viewerViewedState}}}}}'
```

- Mark ONLY the trivial set. Query state first; skip already-VIEWED files.
- If a SIGNIFICANT file is already VIEWED (not by you): report it, do NOT unmark — the mark may be the user's own.
- Only undo marks you yourself made in error this run.

### 4. Re-prep after new commits (rebases/pushes invalidate parts)

- GitHub auto-repositions line comments across pushes; verify with the comments API (`position: null` = outdated). Comments on deleted lines going outdated is CORRECT — leave as history. Re-post (never delete-and-replace) only when the content still applies to the new diff and lost its anchor.
- Pushes reset Viewed on touched files: re-mark only trivial files that were reset. Force-pushes may reset broadly — re-verify the whole trivial set.

### 5. Report

Return to the user: comment inventory (id → path/anchor → one-line gist, new vs pre-existing), final per-file viewed state (trivial=VIEWED / significant=UNVIEWED), explicit confirmation of the coverage invariant (no file both unviewed and uncommented), and any anomaly (pre-existing marks on significant files, anchors that had to fall back to file-level).

## Gotchas

- `gh pr edit` can fail on a Projects-classic GraphQL deprecation in this org — PATCH the body via `gh api repos/<o>/<r>/pulls/<N>` instead.
- Large PRs: paginate `files(first:100)` and the comments API.
- The harness may flag viewed-marking as an external write under the user's identity — expected; it is what the user authorized.
