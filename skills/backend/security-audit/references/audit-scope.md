# Audit scope and access contract

Read this during access setup, fresh cloning, and coverage reconciliation.

## Access verification

Before scanning, verify:

- `aws sts get-caller-identity` for `zoppy-prd` (`891377241798`), `zoppy-dev`
  (`654654607244`), and `zoppy-main` (`089543940399`);
- `gh auth status` for repository and remediation-state inventory;
- `gcx --context zoppy api /api/org` for Grafana;
- clone/read access to every mandatory repository;
- `cf` CLI identity, accounts, and zones using the cloudflare-cli skill and current `cf --help`.

Access loss quarantines only unfinished checks that depend on that credential. Preserve timestamped
observations, continue every independent slice, and name the unresolved surface and required access
in `coverageGaps`. Label reduced coverage explicitly; a partial audit cannot claim complete coverage.
A user may explicitly dismiss a gap; record that dismissal in `coverageGaps`.

## Mandatory fresh repositories

Clone current default branches into a new scratch root and record full commit hashes before work:

1. `zoppy-api`
2. `zoppy-workflow`
3. `zoppy-event-bridge`
4. `zoppy-command`
5. `zoppy-pixel-lambda`
6. `zoppy-whatsapp-commerce`
7. `zoppy-mcp-server`
8. `zoppy-model`
9. `zoppy-utilities`
10. `zoppy-shared`
11. `zoppy-os`
12. `zoppy-n8n`

Do not treat libraries as fleet-wide from `package.json`; count current import sites and deployed
consumer pins. Read both sides of shared datastore relationships.

For backdating, a shallow clone is acceptable only if it contains the required cutoff. Otherwise
deepen or unshallow before `git log -S` / `merge-base` conclusions.

## Cloud and live-data scope

- Enumerate production, development, and payer/main accounts read-only. The organization has six
  known accounts; the three without profiles remain quantified coverage gaps unless access changes.
- Audit Grafana as an attack surface and as a read-only validation surface. MySQL tables are
  PascalCase and require `zoppy.` qualification when the datasource has no default schema.
- Map ECS/Lambda/EC2/RDS/Redis/OpenSearch/Keyspaces/S3/DMS/Glue/Athena/CloudFront/CI resources to
  source repositories and identities. Unattributed workloads remain named gaps.
- Never retrieve secret values or broad credential-bearing configuration. Query names, ARNs,
  effective policies, selected non-secret fields, counts, and timestamps only.

## Cloudflare scope via cf CLI

Enumerate accounts and zones, DNS proxy status, TLS/HTTPS controls, WAF and rate-limit rules,
DDoS/security settings, Access/Zero Trust policies, Workers/routes, and audit-log availability.
Discover commands through `cf --help`; use safe read operations and selected non-secret fields.
Cloudflare is a mandatory surface: record every unavailable product, zone, permission, or account
as a named gap, including whether a feature is unsupported by the account plan. Never expose token
values, Workers secrets, tunnel credentials, private keys, or broad configuration exports.
Save the observed controls in `meta.cloudflare` using the report contract. A missing permission
means unknown control state, not an absent control.

## Required audit slices

Run independently and in parallel:

1. Auth and session
2. Authorization and tenancy
3. Resource consumption and paid flows
4. Data exposure and secrets
5. SSRF, egress, and integrations
6. Configuration, inventory, dependencies, and regression
7. Cloud production
8. Cloud development/main and cross-account bleed
9. Privacy LGPD/GDPR
10. Grafana and live-data validation
11. Coverage map and live GitHub remediation-state ingestion
12. Cloudflare edge, DNS, and access controls via cf CLI

All slices receive the same cutoff manifest, business profiles, previous-finding subset, evidence
contract, and output schema. Each writes incremental JSONL so an interrupted agent loses analysis
time, not findings.

## Coverage completion criterion

The scope step is complete only when every mandatory repo/account/surface is either:

- scanned at a recorded current cutoff;
- explicitly dismissed by Luis for this run; or
- named in `coverageGaps` with the exact access/evidence needed to close it.

Never publish a comparable KPI if current coverage is materially smaller than the baseline without
showing both the like-for-like score and the expanded/contracted-scope score separately.

## Lessons that must not be rediscovered

- **Latest audit = last `baselines/manifest.json` entry**, never the newest `docs/security` filename: report
  files carry the report reference date, so the 2026-10-02 run is named `security-audit-2026-09-30.*`.
- **Canary green provenance:** image tags `green-master-green-<hash>` are shared by api and workflow and are
  not application commits. Prove a fix is on the canary by checking it is an ancestor of the last
  `origin/master-green` commit before the canary task definitions' `registeredAt`.
- **Search tooling:** in this environment `grep`/`find` may be shell functions; `grep -rl` can silently
  return nothing. Workers use `/usr/bin/grep` (and avoid zsh `--include=*.ts` globbing).
- **Label every finding against the previous run** (new / still open / fixed / newly visible because access
  expanded) before relaying it as urgent; known-open items are not new discoveries.
