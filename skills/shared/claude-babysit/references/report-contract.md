# Claude babysit report contract

Keep the artifact set proportional to the request. The control plane is always required; thematic reports exist only when requested.

## Required files

- `README.md` — scope, identities, current verdict, and links.
- `state/session-cursor.json` — transcript path, inode, last adjudicated line, model horizon.
- `state/cadence.json` — checkpoint, last/next/cutoff timestamps, process state, limit state.
- `deliverables.md` and `deliverables.json` — accepted matrix and completion evidence.
- `findings.md` and `findings.json` — stable classification registry.
- `ledger.md` — append-only checkpoints and corrections.
- `final-review.md` — final delivery and quality verdict.

For substantive Zoppy work, generate linked HTML versions of human-facing Markdown reports.

## Optional requested reports

- `validation-review.md` — executable gates, manual tests, false-green risks.
- `monitoring-review.md` — query/rule/runbook semantics and live-health evidence.
- `e2e-live-test-design.md` — local, staging, and production-safe scenarios.
- `architecture-review.md` — reproducible base/head/final graph comparison.
- `review-delivery-matrix.md` — PR prep and review-guide artifacts per slice.

Do not create empty thematic reports merely because a template lists them.

## Checkpoint schema

```markdown
## YYYY-MM-DD HH:MM TZ — checkpoint N

- Cursor: lines A-B; latest event timestamp
- Model evidence through: exact line/timestamp and model values
- Claude state: active, waiting, stopped, limited, or unknown
- Deliverable delta: completed, changed, stale, blocked
- Repo/PR delta: branch, SHA, dirty paths, base/head/check changes
- Commands observed: exact cwd/tree, command, exit, bounded result
- Claims verified:
- Claims contradicted:
- Findings opened, fixed, or reclassified:
- Feedback sent:
- Next delivery target:
```

Append corrections; never rewrite a prior judgment invisibly.

## Finding registry

| Field | Required value |
|---|---|
| id | stable identifier |
| class | one class from `SKILL.md` |
| severity | blocker, high, medium, low, informational |
| status | open, fixed, accepted, disproved, needs decision |
| introduced by | commit/PR or `pre-existing` |
| surface | runtime, data, tests, monitoring, release, docs |
| evidence | file/line, command, PR/check, log, query |
| counter-evidence | strongest evidence against the claim |
| impact | concrete failure mode |
| smallest action | correction or decision |
| proof of closure | exact focused check |

## Evidence rules

- A transcript record proves what was said or executed, not that the claim is true.
- A Git diff proves source state, not runtime behavior.
- A focused test proves its path and exact tree only.
- A build proves compilation/type composition, not application bootstrap.
- No observed data is not zero without a proven query scope.
- A PR body is not independent evidence.
- Disclose stale branches, missing checks, expired credentials, inaccessible systems, and unrun gates.

## Atomic state rule

Append the checkpoint first. Write each JSON state to a temporary file in the same directory, fsync when available, and rename it over the prior state. Advance the cursor only after every required checkpoint artifact succeeds.
