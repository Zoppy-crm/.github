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

Ingest prior business profiles and ask Luis only about missing or changed customer count,
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

Load `baselines/rulings.json`, Luis's product rulings, and apply every entry to its finding:
`close` (intended behaviour: unscored, `closureKind=refuted`), `keep` (stays scored; do not ask
again), `accept` (scored as `accepted-risk`), and `severity` (fixed rating). Give slices the rulings
for their findings. Ask Luis only about findings with no ruling; `validate_bundle.py` fails a
current bundle that contradicts the ledger.

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

**Completion criterion:** one canonical current bundle contains every prior and new finding exactly
once, every mandatory field is populated, and no high-severity claim depends on inferred
reachability or a missing business profile.

## Step 5 — Backdate and calculate trend

Preserve prior IDs. Classify new records as `already-reported`, `pre-existing-missed`,
`introduced-since`, or `undetermined`. Use full-enough git history for code; do not invent history
for mutable cloud state without evidence.

Compute like-for-like and coverage-change deltas separately. Print counts, weights, Security,
Privacy, Combined, and the reconciliation equation. Run `scripts/calculate_delta.py` so the bundle
contains every score-changing finding grouped as remediated, refuted, reclassified, coverage
expanded, introduced, or undetermined.

**Completion criterion:** every changed point is itemized by stable ID with before/after severity
and points; remediation is never conflated with a refuted prior finding; no finding lacks an origin
verdict.

## Step 6 — Fail closed on deterministic gates

Run:

```bash
python3 scripts/validate_bundle.py <current.bundle.json>
python3 -m unittest discover -s tests -v
```

Also assert precondition ceilings, section totals, regression coverage, dedicated issues for open
Catastróficas, and Security + Privacy = Combined.

**Completion criterion:** every assertion exits zero. Do not render or publish around a failed gate.

## Step 7 — Render the report package

Follow [report-contract.md](references/report-contract.md). Produce the versioned bundle, manifest,
PT-BR Markdown, self-contained HTML through `scripts/gen_html.py` using the installed zoppy-deck
font and visual tokens, and actionability view. Read the zoppy-deck skill when changing the report's
visual presentation; retain the audit's scrolling layout and filters. Reports
lead with conclusion and the itemized **Delta** section before arithmetic, coverage gaps, findings,
or remediation ordering. Current GitHub remediation and Cloudflare coverage sections follow Delta;
missing access is shown as an explicit snapshot gap.

Publication and issue writes require current explicit authorization. New cards use `gh`, Project #7
Status `To Do`, and the security-specific work/severity taxonomy defined in the report contract;
Project Priority remains a separate scheduling field.

**Completion criterion:** all five artifacts exist, hashes match the manifest, HTML has no external
assets or legacy scoring language, and every local deliverable is handed to Luis as a clickable link.

After validating a generated or updated HTML deliverable, read and follow [phone-html](../phone-html/SKILL.md) to make it available on Luis's phone by default. Include the literal phone URL alongside the original local path.

## Step 8 — Learn and synchronize

Append every product ruling Luis gave during the run to `baselines/rulings.json` with its date
and source; a ruling recorded only on a finding or in the conversation is lost by the next run.
Ask what this run taught that the next run must not rediscover. Update the single relevant source of
truth, prune superseded sediment, add deterministic regression tests, and rerun the clean fixture
suite. Promote the finalized canonical bundle into `baselines/`, append its verified hash and KPI to
`baselines/manifest.json`, then synchronize the canonical Claude and Codex skill directories
byte-for-byte. The newest manifest entry is the mandatory basis for the next audit.

**Completion criterion:** May reproduces 265/992, July reproduces 256/840, September 1 reproduces
265/810 (Security 742 + Privacy 68), the newest audit is the last manifest entry, current tests pass,
and both installed skill copies have identical file hashes.
