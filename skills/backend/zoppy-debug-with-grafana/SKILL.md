---
name: zoppy-debug-with-grafana
description: Use when pulling ANY evidence out of Zoppy's Grafana — Loki logs, prod MySQL via the datasource proxy, Athena (ALB access logs, zoppy_silver lake), Prometheus/BullMQ metrics, Tempo traces, Redis — and when creating, tuning, or auditing Grafana alert rules or dashboards. Also use whenever a gcx/Grafana query errors or comes back empty, before asserting "no logs/traces/rows found", and before building any ratio or loss claim on log counts. Carries the datasource UIDs, gcx quirks, Loki label semantics, the ALB Athena table rulings, flow-log traps, and alert-design doctrine. Pairs with zoppy-prod-debugging (investigation doctrine + AWS-side instruments).
---

# Debug with Grafana (Zoppy)

All of Zoppy's observability flows through a self-hosted Grafana
(`https://grafana.zoppy.com.br`, v11.6) operated via the `gcx` CLI (never
`mcp__grafana__*`). The sibling skill
[`zoppy-prod-debugging`](../zoppy-prod-debugging/SKILL.md) carries the
investigation doctrine, service topology, and AWS-side instruments; this skill
operates the Grafana ones.

## Operating gcx

- **Version-warning trap**: `gcx config check` complains that Grafana <12 is
  unsupported. That only gates the high-level resource verbs — **`gcx api` is a
  thin HTTP passthrough that works fine on 11.6**. When a wrapper command
  refuses or misbehaves, drop to `gcx api <path> [-X POST -d @payload.json]`.
- **Hint line corrupts JSON**: gcx prints a `hint:` line (stderr on some
  commands, stdout on others). Prefer `--jq '<expr>'`; otherwise
  `2>/dev/null | sed '/^hint:/d'`. Never pipe `2>&1` into a JSON parser.
- **Spill-to-file**: large responses aren't printed — gcx writes
  `/tmp/gcx-results-<ts>.json` and prints `{"spilled_to": "...", "bytes": N}`
  plus a hint. Read the named file; `-o json` forces inline output.
- **Timestamps**: RFC3339 with explicit offsets (`2026-08-11T12:30:00-03:00`) —
  some relative forms are silently ignored.

## Datasources (verified 2026-08; re-verify via `gcx api /api/datasources` if a query 404s)

| Datasource | uid | Quirks |
| --- | --- | --- |
| Loki (app logs) | `een6csa5t4gzkc` | ~7d retention (has burned at ~3d — query flood windows immediately); `references/loki.md` |
| MySQL (prod read replica) | `een6cmg0t4xkwf` | every table needs the `zoppy.` prefix; `references/datasource-recipes.md` |
| Athena — ALB access logs | `ees4kgkh4m2v4c` | table rulings in `references/athena.md` — read them BEFORE the first query |
| Athena — zoppy_silver lake | `cengw3mbfj5z4f` | `db_<table>` naming, INT booleans; `references/athena.md` |
| Prometheus (BullMQ metrics) | `fen6jmubhxwjkd` | queue label values carry the `_QUEUE` suffix; `references/datasource-recipes.md` |
| Tempo (traces) | `benaeh95iw6pse` | normal query routes return HTTP 500 — use the datasource **proxy** route; retention **~100 minutes**; `references/datasource-recipes.md` |
| Redis (PRODUCTION ElastiCache) | `den98dq5sdfk0e` | read-only, O(1) commands only; BullMQ keys use the double-colon prefix `bull:{zoppy}::`; `references/datasource-recipes.md` |

Service labels follow `service_name="production_zoppy-api_<SUFFIX>"` — the full
where-does-code-run table is in `zoppy-prod-debugging`. Census live:
`gcx logs labels -d een6csa5t4gzkc -l service_name`.

## The empty-result rule

An empty Grafana result is a fact about your query until proven otherwise.
Before treating it as evidence of absence, walk the causes that all return the
same empty set:

- wrong `service_name` (workers log under pipeline names, never `API`);
- structured metadata filtered as if it were an indexed label (`references/loki.md`);
- queue label missing the `_QUEUE` suffix — enumerate label values first;
- retention horizon: Loki ~7d, **Tempo ~100 min**, ALB Athena ~90d;
- Loki's identical-line dedup silently dropping byte-identical burst lines (`references/loki.md`);
- the log step disabled in `DISABLED_FLOW_STEPS` — it never reaches Loki (`references/loki.md`);
- ALB Athena: the broken non-`_2` table, the empty `domain_name` column, or traffic entering via other ingress (`references/athena.md`);
- a broken exporter (a BullMQ counter once shipped stuck at 1).

Then run a positive control (same query shape for an event you *know* happened)
and try a second instrument (Loki ↔ ALB Athena ↔ DB).

## Reference files

- `references/loki.md` — line-filter doctrine, structured metadata
  (`identifier`, `channel`, …), the identical-line dedup trap, the
  emission-granularity trap, the flow-log contract, onset dating, cardinality
  caps.
- `references/athena.md` — ALB access-log standing rulings (`_2` table only,
  never filter `domain_name`) and zoppy_silver lake conventions.
- `references/datasource-recipes.md` — prod SQL through `/api/ds/query`,
  Prometheus/BullMQ metric truth, Tempo proxy routes and payload forensics,
  Redis datasource quirks.
- `references/alerting.md` — alert provisioning via REST, state
  history/annotations API, `$values` templating and the resolved-state
  rendering gap, alert-design doctrine, dashboards round-trip.

If the gcx plugin's skills are installed they complement this one: `gcx:gcx`
(full command surface), `gcx:setup-gcx` (auth/contexts — use when gcx itself
errors). For designing dashboards from scratch, the shared `grafana-dashboard`
skill covers panel and JSON conventions.
