# KPI and report contract

Read this during previous-report ingestion, reconciliation, rendering, and publication.

## KPI definition

`Zoppy Security and Privacy Exposure` is the sum of official points for open, score-included
security and privacy findings at a frozen cutoff. Lower is better.

Always report Security, Privacy, Combined company KPI, counts/arithmetic per severity, and delta
explained as remediation, introductions, re-rating, and coverage change. No letter grades.

## Delta is the first substantive section

Immediately after the executive conclusion and current score, render `## Delta — o que mudou` in
both Markdown and HTML. It appears before arithmetic, coverage gaps, inventory, ROI, and findings.

The canonical bundle stores the machine-readable comparison at `meta.delta`. Generate it with
`scripts/calculate_delta.py <previous.bundle> <current.bundle> <output.bundle>`. The section must:

- show the exact equation from previous score to current score;
- itemize every changed finding by stable ID, title, previous/current severity and point delta;
- separate **remediated** findings from **refuted/report-correction** findings;
- separate **coverage expanded** from findings actually **introduced since** the previous cutoff;
- show reclassifications individually, including increases, and identify undetermined dates;
- use an explicit “Nenhum” when a category is empty.

A numerical equation without the itemized causes fails the report contract. Calling refuted prior
claims “remediation” also fails it: that would credit engineering work that may never have happened.

## Ingest the previous registry first

1. Read `baselines/manifest.json` and select the latest audit.
2. Verify its SHA-256 and run `python3 scripts/validate_bundle.py baselines/<bundle> --historical`.
3. Load every prior finding, status, severity, evidence, business profile, remediation link, and
   coverage gap before dispatching slices.
4. Re-query current GitHub issues/PRs, source commits, deployments, and live controls. A merged PR
   is not production verification.
5. Freeze current repo commits, access state, and observation timestamps in the new bundle.

Markdown is presentation, never the machine source. If the manifest/bundle is missing or its hash
fails, stop: the KPI cannot be reproduced.

## Trend rules

- Preserve stable IDs and classify each record as `already-reported`, `pre-existing-missed`,
  `introduced-since`, or `undetermined`.
- Backdate code with full-enough history. Backdate AWS only from history that exists.
- Separate like-for-like risk change from coverage change.
- Reopening a previously refuted finding is a positive `reclassified` report correction, with
  `changeKind=report-correction`; it is not a newly introduced vulnerability. A previously remediated
  finding whose prior closure was incorrect uses current `reopenReason=prior-report-error`,
  `reopenNotes` explaining the pinned before/after proof, `evidenceState=confirmed`, and nonempty
  current `evidence`; it receives the same report-correction classification. Preserve historical
  closure records. A real regression requires fresh evidence and explicit `origin=introduced-since`;
  unknown introduction stays `undetermined`. Every reopened point must appear in the delta equation.
- Print reconciliation. July fixture: `May 992 − 222 remediated + 70 introduced = July 840`.
- Never compare intermediate scores or materially different unqualified coverage.

## Deterministic gates

Before rendering or publishing:

```bash
python3 scripts/validate_bundle.py <current.bundle.json>
python3 -m unittest discover -s tests -v
```

Also assert section totals, precondition ceilings, independent coordinator review of every
Catastrófica/Crítica, regression checks for prior fixed findings, dedicated issues for current
Catastróficas, Security + Privacy = Combined, and reconciled coverage.

## Rescaling sweeps four places, not one

When weights or labels change, the Markdown numbers are the easiest part and never the whole job.
A retired scheme survives in:

1. **The Markdown reports** — summary table, arithmetic line, per-area points, ROI queue, and the
   `(N pts)` on every finding header.
2. **`scripts/gen_html.py`** — it hardcodes its own prose: the scoring-formula note, the per-area
   table header, the ROI blurb, and any grading helper. HTML is generated, so a stale string here
   survives every regeneration and outlives the Markdown fix.
3. **The finding bundles** — retired labels sit in free text inside attack paths, fixes, and rating
   notes. HTML rebuilds from the bundle, so fixing only the Markdown leaves the HTML wrong and the
   two silently disagree.
4. **Rationale prose inside findings** — a phrase such as "which is why this is P2" asserts a
   severity in the retired vocabulary and contradicts the current header. Rewrite each from the
   finding's *actual current* severity. Never map old labels mechanically: re-rating moves findings
   between levels, so an old P1 is not reliably today's Alta.

Grep retired labels across `*.md`, `*.html`, the generator, and the bundles before calling a
rescale done. Strip embedded base64 fonts before grepping HTML because they yield false positives.

**Prior-report IDs are not severities.** Identifiers such as `P0-1` and `P2-11` are provenance and
must survive a rescale. State once in the report that they are identifiers from the original
document, not grades on the current scale.

**Re-check column counts when the number of levels changes.** Going from four severity levels to
five made the per-area table emit five `<td>` cells under a four-`<th>` header, shifting every
rendered value by one column.

## Deliverables

Write coworker-facing artifacts in PT-BR; speak to Luis in English.

The HTML uses the installed **zoppy-deck** visual source: its embedded Inter font, design tokens,
brand mark, metric cards, severity pills and callouts. `scripts/deck_theme.py` reads that source
at render time; keep audit-specific layout in `gen_html.py`. Preserve the scrolling report,
expandable findings, filters, itemized Delta, and the explicit GitHub scope. The slide shell's
viewport locking and navigation do not apply to the report. Install zoppy-deck before rendering;
an absent theme dependency is an error rather than a fallback to unrelated styling.

1. `docs/security/security-audit-<YYYY-MM-DD>.bundle.json`
2. `docs/security/security-audit-<YYYY-MM-DD>.md`
3. `docs/security/security-audit-<YYYY-MM-DD>.html`
4. `docs/security/security-audit-<YYYY-MM-DD>-by-actionability.md`
5. `docs/security/security-audit-<YYYY-MM-DD>.manifest.json`

After final validation, copy the canonical bundle into `baselines/` and append a hash-verified entry
to `baselines/manifest.json`. The newest chronological entry is the sole starting registry for the
next run; older fixtures remain for regression and long-term trend.

`docs/` is transient. After explicit publication authorization, replicate the report and manifest
to the roadmap issue and create/update one issue per actionable finding through `gh`; new Project
#7 cards start at Status `To Do`. Audit generation itself is read-only and does not implicitly
authorize GitHub/AWS/Grafana/database writes.

## Executive coverage qualification

When current verification is materially smaller than the baseline, put a short qualification in
the executive conclusion before Delta, without adding a section heading. `meta.coverageSummary`
is PT-BR prose naming unverified surfaces and conservative carry-forward counts. It must state
that the conservative registry KPI is not a complete measurement of the current posture.

`meta.comparability` contains `previousRegistryScore`, `currentPriorIdScore`, `newCoverageScore`,
and `evidenceScores` with `confirmed`, `inferred`, and `unknown` integer point totals. Compute the
current subtotal of previous finding IDs from the validated baseline registry; all other included
IDs form the new-coverage subtotal. Both subtotals must sum to the current KPI. Evidence components
must reproduce the included findings' current evidence states and sum to that same KPI. Report
them as point subtotals, not finding counts. Matching IDs permits a like-for-like registry comparison;
it does not assert equivalent live verification when access has contracted.

## Current remediation and Cloudflare snapshots

After the complete itemized Delta, render **GitHub — estado atual das correções de segurança**
and **Cloudflare — controles e cobertura atuais** in Markdown and HTML. Both use canonical bundle
metadata, with observation time, scope, explicit unknowns, and coverage gaps. The GitHub section
shows current issues, assignees, Project #7 Status, severity labels, linked PR state and base branch,
and independently verified deployment state. An issue closed, board Done, or PR merged never
changes `scoreIncluded`; derive risk from linked finding IDs and current audit evidence.

Set `meta.reportAmendmentVersion=1` for new audits. Snapshots have these deterministic shapes:

```json
{
  "githubRemediation": {
    "observedAt": "ISO-8601 UTC", "status": "complete|partial|unknown",
    "query": "repositories, labels, and issue/PR query scope", "coverageGaps": [],
    "issues": [{
      "repository": "Zoppy-crm/zoppy-api", "number": 123, "title": "...",
      "url": "https://github.com/Zoppy-crm/zoppy-api/issues/123", "state": "OPEN|CLOSED",
      "assignees": [], "projectStatus": null, "severityLabels": [], "findingIds": [],
      "pullRequests": [{"number": 456, "url": "https://github.com/...",
        "state": "OPEN|CLOSED|MERGED", "baseRefName": "master", "mergedAt": null}],
      "deployment": {"state": "verified|unverified|unknown", "evidence": null},
      "updatedAt": "ISO-8601 UTC"
    }]
  },
  "cloudflare": {
    "observedAt": "ISO-8601 UTC", "status": "complete|partial|unknown", "coverageGaps": [],
    "accounts": [{"id": "...", "name": "..."}], "zones": [{"id": "...", "name": "..."}],
    "checks": [{"surface": "TLS", "state": "confirmed|inferred|refuted|unknown",
      "summary": "selected non-secret observed controls", "evidence": "timestamped evidence path"}]
  }
}
```

If Luis specifies an issue set or the issues created in a prior session, verify that exact set
from primary evidence and limit the GitHub report section to it. Record the explicit issue URLs
and scope provenance in the snapshot; do not expand it into an organization-wide backlog.
Existing finding links outside that set remain provenance in the registry, not extra report rows.
Otherwise, use read-only `gh` to collect current `work: security` and `epic: security` issues, then reconcile
all prior issue URLs and security/privacy issues discovered across mandatory repositories. Record
pagination and query coverage; include closed issues linked to prior findings to expose unresolved
risk behind closed cards. Link PRs from explicit GitHub relationships or cited references and retain
base branch; shared keywords alone do not prove a remediation relationship. Read Project #7 fields
independently from issue state. Missing board access is unknown status and an explicit gap.

An empty complete inventory means no issues in the recorded query scope; an empty partial or unknown
inventory means unavailable evidence. A verified deployment requires a current source/runtime or
control observation in `deployment.evidence`. GitHub snapshot data is a work queue, never a separate
source of KPI points. Store the exact read evidence alongside the bundle. Legacy bundles render
explicit snapshot gaps and remain valid historical fixtures.

## GitHub card taxonomy

Security vulnerabilities are their own work type, not bugs. Every security remediation card uses
`work: security`, `epic: security`, and exactly one security severity label:

| Finding severity | GitHub label | Project Priority |
|---|---|---|
| Baixa | `security:low` | P2 |
| Média | `security:medium` | P2 |
| Alta | `security:high` | P1 |
| Crítica | `security:critical` | P0 |
| Catastrófica | `security:catastrophic` | CATASTRÓFICO |

The security label expresses audit severity; Project Priority expresses scheduling. Keep both and
do not substitute one for the other. Existing provenance, AI-assistance, epic, Size, assignment,
and Status conventions still apply. Migrate a reused remediation card to this taxonomy when it is
the canonical owner of a security finding.

## Fixture acceptance

A skill release is invalid unless a clean execution reproduces exactly:

- May: 265 findings, total 992
- July: 256 findings, Security 768, Privacy 72, total 840
- September: 265 registry findings, 254 score-included, Security 742, Privacy 68, total 810
- no legacy 100/30/8/2 formula, P0/P1/P2 severity columns, or letter-grade language in HTML
