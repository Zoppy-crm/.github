---
name: claude-babysit
description: "Supervise a long-running Claude or Fable coding session against explicit deliverables: inspect append-only deltas on a fixed cadence, keep the agent moving, distinguish temporary from hard limits, take over additively when authorized, and leave an evidence-backed ledger and morning delivery package. Use only when the user explicitly asks to babysit, watch, monitor, continue, or take over a Claude session."
---

# Claude babysit

Act as an air-traffic controller, not a second pilot grabbing the controls. Keep the accepted destination, every in-flight deliverable, and the evidence for landing visible. Intervene only when the current path threatens completion or correctness.

Read [references/report-contract.md](references/report-contract.md) before starting. Use [scripts/claude_session_delta.py](scripts/claude_session_delta.py) as an index over transcript deltas; adjudicate relevant raw records and current repository state yourself.

## Priority order

Apply this order at every checkpoint:

1. Complete every explicitly accepted deliverable or slice.
2. Preserve buildability, ancestry, and mergeability of each deliverable.
3. Prevent or repair confirmed bugs introduced by the active work.
4. Run the smallest focused validation that proves the changed risk.
5. Produce the requested reviewer artifacts, PR preparation, validation review, monitoring review, and final report.
6. Record design criticism, inherited debt, and improvement ideas without derailing delivery.

Do not spend the night polishing reports, exploring optional architecture, or correcting stylistic disagreements while required slices are missing. Put non-blocking disapproval in the findings ledger.

## 1. Freeze the supervision contract

Before observing, record:

- exact Claude session UUID or transcript path;
- repository and authorized sibling repositories;
- accepted deliverable count and identifiers, for example R01–R14;
- definition of completion for each deliverable;
- comparison base and expected final head;
- checkpoint cadence and absolute cutoff with timezone;
- permitted feedback, GitHub writes, branch/PR creation, code takeover, staging access, and production access;
- forbidden checks, especially the full test suite;
- requested morning artifacts.

An alternative slice count is a proposal, not completion. Keep the accepted matrix unchanged until the user explicitly approves another count.

## 2. Prove session and model provenance

Resolve one transcript. Confirm its recorded cwd, session id, timestamps, and recent task context. Inspect assistant records and their exact `message.model` values.

Say only:

- “Fable verified through line/timestamp X” when the inspected records contain a `claude-fable-*` model;
- “Claude session verified; model not verified” when the model field is absent;
- a mixed-model inventory when different models appear.

Never guarantee future routing or infer the parent model from a child task. Record subagent provenance separately.

## 3. Create the deliverable matrix first

Each accepted deliverable gets one row:

| Field | Required value |
|---|---|
| id | stable slice/deliverable identifier |
| purpose | one semantic sentence |
| declared base | branch and resolved SHA |
| head | branch and resolved SHA |
| ancestry | exact parent relationship |
| changed paths | complete set |
| buildable | command, tree, exit, timestamp |
| deployable alone | yes, no, or not required; never conflate with buildable |
| focused tests | command, tree, counts, exit |
| PR | URL, live base/head, merge state, checks |
| PR prep | pending, current, or stale |
| review guide | pending, current, or stale |
| blocker | evidence, owner, next action |

No gap, duplicate path, silently consolidated row, stale base, or unproved intermediate build is accepted. A green final tip does not prove its prefixes.

## 4. Establish an observer baseline

Use a separate worktree or clone. Never edit the agent's active worktree.

Capture:

- repository, branch, HEAD, status, worktrees, and remote refs;
- open PR bases, heads, merge state, checks, reviews, and material claims;
- accepted deliverable matrix;
- pre-existing failures and debt;
- requested validation, monitoring, E2E, and architecture artifacts;
- transcript cursor, inode, last event, and model evidence horizon.

For architecture work, graph the comparison base and current final head with identical filters. Do not rerun Graphify every checkpoint; repeat only after architecture-relevant changes or at closeout.

## 5. Run the checkpoint loop

At each cadence boundary:

1. Read only transcript records after the durable cursor.
2. Inspect relevant raw records; the delta script's signal lines are search hints, not findings.
3. Recheck process and child-agent liveness.
4. Recheck repository, accepted slice matrix, PR heads/bases/checks, and new artifacts.
5. Compare claims with code, command exits, and the exact tested tree.
6. Update finding classifications.
7. Send one compact feedback packet only if it changes delivery, correctness, or a material evidence claim.
8. Append the checkpoint to the ledger.
9. Atomically advance transcript cursor and cadence state after the ledger write succeeds.

If a checkpoint is missed, run one catch-up delta from the last durable cursor. Do not fabricate empty checkpoints or reset the cursor to current EOF.

## 6. Keep feedback useful

Send feedback at a completed tool/child-task boundary when possible. Use this shape:

```text
Evidence: exact file/line, command exit, PR state, or transcript record.
Impact: concrete delivery or runtime consequence.
Smallest action: one bounded correction or decision.
Proof: focused command or state that closes it.
```

Do not interrupt for naming, formatting, speculative cleanup, or preference differences. Record those in the report unless they block correctness, buildability, or reviewability.

## 7. Classify findings without pollution

Use exactly:

- `introduced_bug` — confirmed product/code regression from the active work;
- `inherited_debt` — pre-existing or non-eliminated debt;
- `speculative` — plausible, not proved;
- `validation_defect` — false green, broken runner, misleading coverage, or missing assertion;
- `monitoring_defect` — wrong query, threshold, no-data semantics, or runbook claim;
- `review_process_defect` — inaccurate PR/review packaging;
- `evidence_overclaim` — conclusion exceeds the measurement.

Fix confirmed introduced bugs before declaring a deliverable ready. Keep inherited debt in reports unless it blocks correctness or mergeability.

## 8. Validate quickly and honestly

Never run the full test suite unless the user explicitly reverses the restriction.

Use one focused pass after final code/base alignment:

- build only where the accepted matrix requires prefix buildability;
- tests that exercise changed behavior and known failure paths;
- bootstrap/DI smoke only when composition changed;
- static diff and ancestry checks for deletions, moves, and reslicing;
- normal pipeline as the full-suite gate.

A build proves compilation, not bootstrap. A focused suite proves only its paths. A wrapper summary is not evidence if the underlying command timed out or exited non-zero.

## 9. Handle limits

Do not classify a quiet process as limited without direct evidence.

### Temporary allowance reset

If the transcript or CLI states a near-term reset:

- record the exact message and reset time;
- preserve cursor and work state;
- wait through the reset using the product's monitoring mechanism;
- resume the exact session with a concise `Continue` only after the reset;
- verify new assistant records before calling it resumed.

### Weekly, hard, or paid-credit exhaustion

After direct evidence of a hard limit and user authorization to take over:

- preserve every valid Claude commit;
- create a separate successor branch/worktree from the last verified head;
- finish additively;
- push Claude's work before adding your commits when permitted;
- create separate addendum PRs when that preserves attribution and reviewer clarity.

Never continue inside a dirty active worktree. If the last state contains uncommitted edits, inventory and preserve them without claiming ownership; stop for direction when authorship cannot be separated safely.

## 10. Close the run

Before declaring success:

- every accepted deliverable row is complete or explicitly user-deferred;
- live PR heads/bases match the report;
- required focused checks are current for those heads;
- confirmed introduced bugs are fixed;
- PR-prep and review-guide artifacts are current where requested;
- validation and monitoring conclusions distinguish executable proof from manual plans;
- report and state files are durable;
- exact unrun gates and unmeasured surfaces are named.

The final answer leads with deliverables: completed, incomplete, blocked, and handed off. Critique follows. Do not replace concrete PR/artifact links with a long narrative.

## Boundaries

- Session discovery is not authorization to resume or mutate it.
- Monitoring does not authorize production writes.
- Do not expose raw transcripts, credentials, or sensitive payloads in reports.
- Do not merge PRs unless explicitly asked.
- Do not promise universal absence of regressions.
