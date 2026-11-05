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

The AWS profile names (`zoppy-prd`, `zoppy-dev`, `zoppy-main`) and gcx contexts (`zoppy`,
`zoppy-dev`) used throughout this skill are defaults, not requirements. Use your own names; the
account IDs returned by `sts get-caller-identity` are what must match.

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
13. `zoppy-ops-infra`
14. `zoppy-github-runners-infra`
15. `zoppy-auth-fe`
16. `zoppy-csm-agent`
17. `zoppy-fe`
18. `zoppy-terraform-lakehouse-core`

Default branch is not always what production runs. `zoppy-pixel-lambda` production runs `master`,
not `development`. Production n8n is upstream n8n on Fargate built by
`zoppy-ops-infra/lib/n8n-stack.ts`; `zoppy-n8n` is not its production source.

Do not treat libraries as fleet-wide from `package.json`; count current import sites and deployed
consumer pins. Read both sides of shared datastore relationships.

For backdating, a shallow clone is acceptable only if it contains the required cutoff. Otherwise
deepen or unshallow before `git log -S` / `merge-base` conclusions.

## Cloud and live-data scope

- Enumerate production, development, and payer/main accounts read-only. The organization has seven
  accounts; the four without profiles remain quantified coverage gaps unless access changes.
- Audit Grafana as an attack surface and as a read-only validation surface. MySQL tables are
  PascalCase and require `zoppy.` qualification when the datasource has no default schema.
- Map ECS/Lambda/EC2/RDS/Redis/OpenSearch/Keyspaces/S3/DMS/Glue/Athena/CloudFront/CI resources to
  source repositories and identities. Unattributed workloads remain named gaps.
- Never retrieve secret values or broad credential-bearing configuration. Query names, ARNs,
  effective policies, selected non-secret fields, counts, and timestamps only.

## Grafana data sources

Query through `gcx api /api/ds/query -d @query.json`. Known datasource UIDs:

| Datasource | UID | Notes |
|---|---|---|
| Loki | `een6csa5t4gzkc` | Queries over windows of about 6h time out; count over longer ranges with ALB logs in Athena or MySQL instead. |
| MySQL `zoppy` | `een6cmg0t4xkwf` | No default schema: prefix every table, join and variable query with `zoppy.`. |
| Redis Zoppy | `den98dq5sdfk0e` | Production ElastiCache cluster; no dev Redis datasource exists. |
| Zoppy-OS Postgres | `ffrzlqi7z7aiof` | |
| CloudWatch | `eena9byc4tqm8b` | |
| Athena ALB logs | `ees4kgkh4m2v4c` | Long-range request counts. |
| Athena `zoppy_silver` | `cengw3mbfj5z4f` | Lake mirror of MySQL. |

Redis: BullMQ keys use the `bull:{zoppy}::` prefix with a double colon; production queue names
have no environment prefix. Use `type: "cli"` targets (`ZCARD`, `MEMORY USAGE`), because
`type: "command"` returns empty for them; wrap keys with special characters in escaped double
quotes. One request holds at most about 5,000 targets.

`zoppy_silver`: tables are `db_<lowercased table>` with lowercased columns, and MySQL booleans are
integers (`= 1`, never `= true`). Tables can sit at slightly different snapshots, so cross-table
joins can show false inconsistencies. `db_wppcommercesessions` and `db_wppcommerceagents` are not
ingested. `db_wppconversations.sessionexpiration` is a millisecond-epoch string:
`from_unixtime(TRY(CAST(x AS BIGINT)) / 1000)`.

## Cloudflare scope via cf CLI

Enumerate accounts and zones, DNS proxy status, TLS/HTTPS controls, WAF and rate-limit rules,
DDoS/security settings, Access/Zero Trust policies, Workers/routes, and audit-log availability.
Discover commands through `cf --help`; use safe read operations and selected non-secret fields.
Cloudflare is a mandatory surface: record every unavailable product, zone, permission, or account
as a named gap, including whether a feature is unsupported by the account plan. Never expose token
values, Workers secrets, tunnel credentials, private keys, or broad configuration exports.
Save the observed controls in `meta.cloudflare` using the report contract. A missing permission
means unknown control state, not an absent control.

Account `ee03ce5757268c78ccd6103554a2526e` owns `zoppy.com.br` (zone
`cca669edfe47c3013f690bcfc47e2db3`) and `zpy.vc`; Turnstile widgets are
`zoppy-giftback-{prod,mirror,staging,dev}`.

- Workers Logs (`cf observability telemetry query`) keep only 2–3 days; `view: events` caps at
  2,000 rows, and `groupBys` output is unsorted and can silently drop groups, so count one group per
  query with an `eq` filter.
- Zone GraphQL (`httpRequestsAdaptiveGroups` at `api.cloudflare.com/client/v4/graphql`) spans at
  most 4 weeks 2 days per query and is rate-limited. Rows with protocol `UNK`, status 504, origin
  status 0 and `requestSource: earlyHintsCache` are Cloudflare-internal; `HTTP/1.1` rows that mirror
  client counts are Worker subrequests.
- Status 499 is mostly client cancellations; only 499 minus the ALB 460 count for the same hour
  approximates requests that hung at the edge.

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
- explicitly dismissed by Gabriel for this run; or
- named in `coverageGaps` with the exact access/evidence needed to close it.

Never publish a comparable KPI if current coverage is materially smaller than the baseline without
showing both the like-for-like score and the expanded/contracted-scope score separately.

## Lessons that must not be rediscovered

- **Latest audit = last `baselines/manifest.json` entry**, never the newest `docs/security` filename: report
  files carry the report reference date, so the 2026-10-02 run is named `security-audit-2026-09-30.*`.
- **Canary green provenance:** no canary-green service runs in production now. If one returns, its
  image tags `green-master-green-<hash>` are shared by api and workflow and are not application
  commits; prove a fix is on the canary by checking it is an ancestor of the last
  `origin/master-green` commit before the canary task definitions' `registeredAt`.
- **Search tooling:** in this environment `grep`/`find` may be shell functions; `grep -rl` can silently
  return nothing. Workers use `/usr/bin/grep` (and avoid zsh `--include=*.ts` globbing).
- **Label every finding against the previous run** (new / still open / fixed / newly visible because access
  expanded) before relaying it as urgent; known-open items are not new discoveries.
