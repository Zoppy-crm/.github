# Review-plan and integrity contract

The generator renders a validated plan. It must not infer truth from visual plausibility.

## Required manifest identity

```json
{
  "schemaVersion": 2,
  "repo": "owner/repo",
  "pr": 123,
  "baseRef": "branch",
  "baseSha": "40 hex characters",
  "headSha": "40 hex characters",
  "diffSha256": "64 hex characters",
  "language": "pt-BR",
  "designVersion": "zoppy-rx-2"
}
```

The manifest also contains title, thesis, logic/spec LOC, sessions, stops, findings, and optional proof identifiers.

## Stable stops and hunk coverage

Each changed path appears once. A stop id is the SHA-256 of repository, PR, head SHA, path, and optional named range. Browser progress uses that id, never an ordinal.

Only these inputs license prep coverage:

- a line comment whose body starts with exact `🤖 [prep]` and whose current right-side line is inside the hunk;
- a legacy `🤖 [prep n/m]` comment, shown as legacy and counted separately;
- an explicit manifest coverage range naming path, start, end, prep comment id, and rationale for grouped coverage.

A file-level comment never silently covers every hunk. Human, bot, and unclassified review comments are displayed as review context, not author rationale.

## Finding schema

```json
{
  "id": "CR-123",
  "classification": "fixed_introduced_bug",
  "summary": "Concrete failure and current status.",
  "provenance": {
    "baseline": {
      "sha": "...",
      "path": "...",
      "lines": "L10-L18",
      "reading": "Why this state is safe"
    },
    "introduced": {
      "pr": 120,
      "sha": "...",
      "path": "...",
      "lines": "L20-L31",
      "reading": "Exact harmful delta"
    },
    "failure": {
      "evidence": "test, command, trace, or static counterexample",
      "reading": "Observed or mechanically demonstrated consequence"
    },
    "corrected": {
      "pr": 123,
      "sha": "...",
      "path": "...",
      "lines": "L25-L38",
      "reading": "Why the repair closes the mechanism"
    }
  }
}
```

`introduced_bug` and `fixed_introduced_bug` require baseline, introduced, and failure. A fixed bug also requires corrected. URLs may supplement, never replace, revision/path/line identity.

## Integrity sidecar

The sidecar records:

- schema, design, and generator versions;
- repository, PR, base/head SHAs;
- manifest, diff, comments, proof-registry, font, and HTML hashes;
- changed/stopped/missing/extra/duplicate path counts;
- canonical prep, legacy prep, human, bot, and unclassified comment counts;
- meaningful hunks, covered hunks, uncovered hunks, and explicit grouped ranges;
- resolved dependency edges, unresolved import-like references, editorial edges, and cycles;
- finding counts and provenance completeness;
- external asset count;
- generation result and exact failures.

Any integrity failure exits non-zero. Warnings may remain for dependency-model limits, legacy comments, or unavailable live freshness after generation.
