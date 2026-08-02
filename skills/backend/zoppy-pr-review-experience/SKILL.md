---
name: zoppy-pr-review-experience
description: "Produce a deterministic, self-contained Zoppy review guide for a pull request: one dependency-ordered reading plan, line-anchored PR preparation, explicit evidence and finding provenance, and a revision-pinned HTML artifact. Use for large, stacked, architectural, or corrective PRs, or when the user asks for a review experience, guided review, reviewer bundle, PR walkthrough, or reviewer-facing before/after."
---

# Zoppy PR review experience

Turn a difficult PR into an auditable reading sequence. The output helps a human understand the code; GitHub remains the only place for comments, Viewed state, and review verdicts.

## Fixed contracts

Read these files before generating anything:

- [references/design-contract.md](references/design-contract.md) — the embedded Zoppy visual system. Do not rediscover it from a live product screen.
- [references/pt-br-contract.md](references/pt-br-contract.md) — controlled technical Portuguese for reviewer-facing text.
- [references/review-plan-contract.md](references/review-plan-contract.md) — manifest, finding, provenance, coverage, and integrity rules.

Use the shipped [scripts/generate-review-experience.mjs](scripts/generate-review-experience.mjs) and [assets/Inter-Regular.otf](assets/Inter-Regular.otf). Do not improvise another shell for each PR.

## Outcome

Deliver two aligned but separate surfaces:

1. `pr-prep`: compact `🤖 [prep]` explanations and conservative Viewed marking on GitHub.
2. A local, self-contained HTML review guide generated from the same rationale map.

Never paste the HTML guide or its long-form content into the PR description or comments unless the user explicitly asks. Never approve, request changes, resolve threads, or treat local checkboxes as review state.

## Workflow

### 1. Freeze the revision

Record repository, PR number, base reference and SHA, full head SHA, changed paths, diff hash, comment-export hash, and generation time. Recheck the live head immediately before any GitHub write and immediately before generation.

A new head invalidates anchors and the artifact. Regenerate; do not describe the old guide as current.

### 2. Build one rationale map

Read the full diff once. For every meaningful hunk record:

- what changed;
- why it was possible or necessary;
- whether behavior is equivalent or deliberately different;
- why the nearest plausible alternative lost;
- evidence source and exact scope;
- finding class, if relevant.

This map is the sole source for both PR preparation and the HTML guide. Do not let two agents independently invent explanations. If `pr-prep` delegates GitHub mutations, delegate only the frozen write plan; keep analysis and wording with the review-experience owner.

### 3. Classify findings before writing prose

Use exactly these classes:

- `introduced_bug` — confirmed regression introduced by this change or stack and still open;
- `fixed_introduced_bug` — confirmed regression introduced earlier in this change or stack and corrected here;
- `inherited_debt` — pre-existing or non-eliminated debt;
- `speculative` — plausible concern without enough proof;
- `rollout_constraint` — confirmed sequencing or operational condition;
- `assessment` — bounded statement that no introduced bug was confirmed in the reviewed scope.

Do not soften an introduced bug into debt. Do not upgrade suspicion to a bug.

For `introduced_bug` and `fixed_introduced_bug`, include the provenance record required by the review-plan contract. If the baseline-to-introduction contrast is missing, classification remains `speculative`.

### 4. Prepare GitHub

Follow `pr-prep` exactly. In particular:

- use the exact prefix `🤖 [prep]`;
- explain each meaningful hunk, not merely each file;
- mark only mechanically trivial files Viewed;
- keep logic files Unviewed;
- leave historical or unrelated review comments distinct from author rationale;
- never delete existing comments; use corrective replies when a prior explanation became misleading.

Write reviewer-facing prose in the PR's established language. For PT-BR, apply the controlled-language contract before posting.

### 5. Order the review

Use explicit dependency facts first: definitions, schemas, invariants, operations, callers, wiring, then tests. Record unresolved imports and editorial relationships separately; do not call a partial import extractor an exact dependency graph.

Each changed path appears exactly once. Each session has:

- one goal;
- 6–20 minutes of work;
- ordered stops;
- two to four falsifiable checkpoint statements.

Specs follow the behavior they prove unless a test defines the contract more clearly than the implementation.

### 6. Generate and validate

Run the shipped generator against the pinned manifest, diff, comments, proof registry, repository tree, and bundled Inter font.

The generator must exit non-zero for:

- head/base/diff disagreement;
- duplicate, missing, or extra changed paths;
- invalid finding classes;
- introduced-bug claims without provenance;
- missing proof identifiers;
- meaningful hunks without a hunk-specific prep explanation or an explicit manifest coverage range;
- non-prep comments being counted as prep;
- progress keys not bound to repository, PR, full head SHA, and stable stop identity.

Produce:

- `<artifact>.html` — self-contained reviewer guide;
- `<artifact>.integrity.json` — input hashes, revision pins, coverage, dependency limits, and artifact hash.

### 7. Visual verification policy

Do not request an authenticated Zoppy screen. The design contract and bundled font are the approved reference.

For an ordinary PR run, perform deterministic structural checks only: embedded font, required tokens/components, no external asset requests, valid responsive CSS, and no integrity failures. Do not take four screenshots or repeatedly judge aesthetics.

Run browser-based desktop/mobile visual regression only when the generator, design contract, or font asset changes. One representative golden fixture is sufficient. Inspect both themes only when theme code changes. Record the structural defect found; do not perform open-ended visual taste review.

### 8. Report

Return:

- exact PR and full head SHA;
- artifact and integrity-sidecar paths;
- session/stop counts and logic/spec LOC split;
- prep comment inventory and Viewed coverage;
- introduced bugs, fixed introduced bugs, inherited debt, and speculative concerns as separate groups;
- provenance completeness for every introduced-bug claim;
- any stale input or unmeasured surface.

Do not claim “no regressions.” State the bounded validation actually performed.

## Corrective PRs

A corrective PR must make introduction provenance visually obvious:

```text
safe baseline -> introducing PR/commit and exact harmful delta -> observed failure -> corrective PR and exact repair
```

Show small source-linked snippets or line ranges for the safe and harmful states, the narrow failure mechanism, and the repair. The correction itself is not proof that the prior change introduced the bug.

When a correction can be folded into the introducing unmerged slice without hiding independent behavior, report that option. Distinguish:

- easy fold: same owner/file and no later dependency;
- cross-slice fold: introduction and manifestation span multiple slices;
- emergent correction: the fix depends on architecture introduced later and deserves a visible slice.

Do not rewrite published stack history unless the user explicitly chooses the clean-history alternative.

## Non-goals

- No hosted review workspace.
- No AI chat inside the artifact.
- No locally recorded approval or change request.
- No decorative diagram without source-linked deterministic edges.
- No visual-reference discovery on each invocation.
- No full test suite merely to create review documentation.
