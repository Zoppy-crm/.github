---
name: security-audit
description: Run Zoppy's KPI-grade security and privacy audit when asked for a pentest, security/cloud/privacy review, OWASP/LGPD/GDPR scan, current security score, trend, or validation of a new public/auth/paid surface. Produces a versioned finding registry, PT-BR Markdown and self-contained HTML from fresh code, AWS, Grafana, database, and remediation evidence. Read-only unless the user separately authorizes publication or remediation.
---

# Zoppy security and privacy audit

The output is a company KPI. **Reproducibility** is the leading rule: a score is invalid unless the
previous registry was hash-verified, current scope was frozen, every finding passed the schema, and
the arithmetic is regenerable.

Official weights form the **1 · 2 · 4 · 8 · 16** ladder: Baixa 1 · Média 2 · Alta 4 · Crítica 8 ·
Catastrófica 16. Security and
Privacy are reported separately and summed into the combined company KPI. Lower is better.

## Non-negotiable boundary

- Read code and enumerate systems safely. Never exploit a live host, read production records,
  retrieve secrets, assume a vulnerable identity, or mutate AWS/Grafana/database/GitHub.
- Controlled local unit/integration tests are the strongest reproduction unless separately
  authorized.
- Historical evidence never proves current state.
- Access loss quarantines only its dependent unfinished checks. Preserve timestamped observations,
  continue independent work, and expose any unresolved gap in the report.

Read [audit-policy.md](references/audit-policy.md) before rating. It is the single source for threat
model, evidence states, severity, preconditions, and confirmed false-positive shields.

## Step 1 — Verify access and freeze current scope

Read [audit-scope.md](references/audit-scope.md). Verify the three AWS account IDs, GitHub, Cloudflare via `cf` CLI, Grafana,
and every mandatory repository. Clone fresh default branches into a new scratch root; record full
commit hashes, observation time, and access gaps.

Ingest prior business profiles and ask Gabriel only about missing or changed customer count,
essentiality, reachability, or containment.

**Completion criterion:** every mandatory repo/account/surface is scanned, explicitly dismissed, or
named in `coverageGaps` with the evidence needed to close it.

## Step 2 — Ingest and validate the previous KPI

Read [report-contract.md](references/report-contract.md). `baselines/` is the private registry at
`~/.local/share/security-audit/baselines/` (manifest, bundles, rulings ledger), kept outside the
shared skill because it maps every open vulnerability; run scripts from that parent directory.
Select the latest entry in `baselines/manifest.json`, verify its SHA-256, and run:

```bash
python3 scripts/validate_bundle.py baselines/<bundle> --historical
```

Load every prior finding and re-query current code, issues, PRs, deployments, live controls, and
traffic evidence. Capture current GitHub issue/Project/PR state and Cloudflare controls in the
snapshots defined by the report contract. Markdown is not an input registry.

Load `baselines/rulings.json`, Gabriel's product rulings. Every entry binds its finding: `close`
(intended behaviour: unscored, `closureKind=refuted`), `keep` (stays scored; do not ask again),
`accept` (scored as `accepted-risk`), and `severity` (fixed rating). Give slices the rulings for
their findings. Ask Gabriel only about findings with no ruling; Step 4 applies the ledger and
`validate_bundle.py` fails a current bundle that contradicts it.

**Completion criterion:** the prior bundle reproduces its manifest finding count and score with
zero validator errors; otherwise stop because the trend is not reproducible.

## Step 3 — Dispatch independent slices

Use the parallel slices in `references/audit-scope.md`. Every worker receives
[audit-brief-template.md](references/audit-brief-template.md), the fresh cutoff manifest, relevant
prior findings, business profiles, and [finding-schema.md](references/finding-schema.md).

Workers append one complete JSON object at a time to unique JSONL files. They return fixed/refuted
prior records too, with `scoreIncluded=false`.

**Completion criterion:** every assigned path/resource/prior finding is accounted for, every JSONL
parses, and each worker names its exact coverage gaps.

## Step 4 — Reconcile and verify

Merge by stable `findingId`; deduplicate by root cause plus attack path. Evidence from code, AWS,
Grafana, database, and GitHub belongs on one finding unless remediations are independent.

The coordinator independently re-reads every Catastrófica and Crítica. Data-dependent findings get
read-only live confirmation. Every material claim is `confirmed | inferred | refuted | unknown`;
unknown upside is not scored at its worst case. Verify every previously fixed finding for regression.

Apply the rulings ledger to the canonical bundle:

```bash
python3 scripts/apply_rulings.py <canonical.bundle.json>
```

It sets each ruled finding's score state, status and severity, records the decision in the
unrendered `ruling` field, and writes only a neutral PT-BR closure note.

**Completion criterion:** one canonical current bundle contains every prior and new finding exactly
once, every mandatory field is populated, and no high-severity claim depends on inferred
reachability or a missing business profile.

## Step 5 — Backdate and calculate trend

Preserve prior IDs. Classify new records as `already-reported`, `pre-existing-missed`,
`introduced-since`, or `undetermined`. Use full-enough git history for code; do not invent history
for mutable cloud state without evidence.

Compute like-for-like and coverage-change deltas separately. Print counts, weights, Security,
Privacy, Combined, and the reconciliation equation. Run:

```bash
python3 scripts/calculate_delta.py <previous.bundle.json> <canonical.bundle.json> <current.bundle.json>
```

The bundle then contains every score-changing finding grouped as remediated, refuted, reclassified,
coverage expanded, introduced, or undetermined. The script fails when a prior ID is missing from
the current registry, and puts every reopened prior closure in the delta as a regression, report
correction or undetermined reopening.

**Completion criterion:** every changed point is itemized by stable ID with before/after severity
and points; remediation is never conflated with a refuted prior finding; no finding lacks an origin
verdict.

## Step 6 — Fail closed on deterministic gates

Run:

```bash
python3 scripts/validate_bundle.py <current.bundle.json>
python3 -m unittest discover -s tests -v
```

On a current bundle the validator also enforces the policy gates: precondition ceilings from
[audit-policy.md](references/audit-policy.md), a valid origin, board priority matching severity, a
dedicated issue for every open Catastrófica, `meta.delta.toScore` equal to the section totals,
comparability subtotals, and the rulings ledger. The independent re-read of every Catastrófica and
Crítica in Step 4 is the one gate no script covers.

**Completion criterion:** every assertion exits zero. Do not render or publish around a failed gate.

## Step 7 — Render the report package

Follow [report-contract.md](references/report-contract.md). Produce the versioned bundle, manifest,
PT-BR Markdown, self-contained HTML through `scripts/gen_html.py` using the installed zoppy-deck
font and visual tokens, and actionability view. Read the zoppy-deck skill when changing the report's
visual presentation; retain the audit's scrolling layout and filters. Reports
lead with conclusion and the itemized **Delta** section before arithmetic, coverage gaps, findings,
or remediation ordering. Current GitHub remediation and Cloudflare coverage sections follow Delta;
missing access is shown as an explicit snapshot gap.

Check the rendered package, named `<stem>.bundle.json`, `<stem>.md`, `<stem>.html` and
`<stem>-by-actionability.md` side by side:

```bash
python3 scripts/check_report.py docs/security/<stem>.bundle.json
```

It fails on process words, tool names, secret-shaped strings, personal email domains, people's
names, English prose, sections out of the Delta-first order, and external assets.

Publication and issue writes require current explicit authorization. New cards use `gh`, Project #7
Status `To Do`, and the security-specific work/severity taxonomy defined in the report contract;
Project Priority remains a separate scheduling field.

With the same authorization, post the monthly score to Bússola as the report contract describes.

**Completion criterion:** all five artifacts exist, hashes match the manifest, `check_report.py`
exits zero, HTML has no legacy scoring language, and every local deliverable is handed to Gabriel
as a clickable link.

## Step 8 — Learn and synchronize

Append every product ruling Gabriel gave during the run to `baselines/rulings.json` with its date
and source; a ruling recorded only on a finding or in the conversation is lost by the next run.
Ask what this run taught that the next run must not rediscover. Update the single relevant source of
truth, prune superseded sediment, add deterministic regression tests, and rerun the clean fixture
suite. Promote the finalized canonical bundle into `baselines/`, append its verified hash and KPI to
`baselines/manifest.json`, then open a PR with the skill changes against `skills/backend/` in the
`.github` repository, whose sync distributes them. The newest manifest entry is the mandatory basis
for the next audit.

**Completion criterion:** May reproduces 265/992, July reproduces 256/840, September 1 reproduces
265/810 (Security 742 + Privacy 68), the newest audit is the last manifest entry, current tests pass,
and every skill change is in a `.github` PR.
