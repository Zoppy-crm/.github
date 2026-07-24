---
name: prod-debugging
description: Use when investigating ANY production incident or customer bug report in Zoppy — regressions, outages, 500s, latency spikes, error bursts, "data not saving", "worked yesterday", queue backlogs, database saturation, "no logs found" — even if the user only pastes a GitHub issue or customer complaint. Also use before declaring a root cause, before asserting that logs/traces/data don't exist, and when verifying a fix landed in prod. Covers Loki, Tempo, Prometheus, prod MySQL via Grafana proxy, RDS Performance Insights, BullMQ metrics, SSM, and regression-dating git archaeology. Complements root-cause (which walks the code layers).
---

# Production Debugging (Zoppy)

Get ground truth from production instead of inferring from code. The `root-cause`
skill walks the code layers; this skill operates the instruments. Grade every claim
as **observed / eliminated / inferred**, and only assert a root cause when code,
timeline, and at least one production observation agree — with at least one
alternative hypothesis eliminated by data.

## Constants (verified 2026-07; re-verify with `gcx datasources list` if a query 404s)

| Thing | Value |
| --- | --- |
| Loki datasource | `een6csa5t4gzkc` |
| Tempo datasource | `benaeh95iw6pse` |
| Prometheus datasource | `fen6jmubhxwjkd` |
| MySQL (prod read replica, via proxy) | `een6cmg0t4xkwf` — tables need the `zoppy.` prefix |
| API service label | `service_name="production_zoppy-api_API"` |
| Worker service labels | see the Service topology table below |
| BullMQ metrics | `bullmq_job_count{job="zoppy_api_bullmq", queue="…_QUEUE", state=…}` — queue names carry the `_QUEUE` suffix |
| Loki retention | ~7 days (app logs have burned at ~3 days before — query flood windows immediately) |
| Tempo retention | ~7 days, sampled; error traces may be absent entirely |
| Observability EC2s (SSM, no SSH) | dev `i-0ff0bec1876512e18` (zoppy-dev), prod `i-03918c5a158642551` (zoppy-prd) |

All Grafana access goes through the `gcx` CLI (never `mcp__grafana__*`). The
universal output adapter — gcx prints a `hint:` line that corrupts JSON:

```bash
gcx <anything> -o json 2>/dev/null | sed '/^hint:/d' | python3 -c "..."
```

## Service topology — where logs land

Pick the `service_name` by where the code *runs*, not where the feature lives.
A public HTTP request logs in `API`; a service-to-service call in `PVT`; a queue
job in its worker pipeline — never in `API`.

| `service_name` (prefix `production_zoppy-api_`) | What runs there |
| --- | --- |
| `API` | Public HTTP API (customer/dashboard traffic) |
| `PVT` | Private API — service-to-service calls |
| `GIFTCARDS`, `PARTNERS` | Their dedicated public API surfaces |
| `WORKER_MESSAGE_PIPELINE` | Campaign/message-send queue processors |
| `WORKER_WORKFLOW_PIPELINE` | Workflow-engine queue processors |
| `WORKER_INTEGRATION_CORE_PIPELINE`, `WORKER_INTEGRATION_PROVIDER_PIPELINE` | Provider/data-sync queue processors |
| `WORKER_QUEUE_LIGHT_PIPELINE`, `WORKER_QUEUE_HEAVY_PIPELINE` | Everything else, split by job weight (safety evaluations, enrichment, reports…) |

Sibling services log under their own names: `production_zoppy-workflow`,
`production_zoppy-command`, `production_zoppy-event-bridge`,
`production_zoppy-pixel-lambda`. Which queue runs in which pipeline is defined in
`zoppy-api/src/access/queues/` (`queue-pool/queue-light|heavy.module.ts`,
`message-pipeline.module.ts`, `workflow-pipeline.module.ts`) — grep the
processor's module registration when unsure, or census live:
`gcx logs labels -d <loki> -l service_name`.

## Doctrine — the rules that have decided real incidents

1. **This codebase mixes very old legacy anti-patterns with modern conforming
   code — expect strange names and strange behavior.** Real examples: email
   template content is persisted only through a route named `sync-whatsapp`;
   rows have multiple independent writers (ancient double-write debt), so a
   fresh write can be silently overwritten by a background job holding a stale
   snapshot. When data behaves impossibly (saves that revert, values from
   nowhere), enumerate *every* code path that writes the row — queue processors,
   enrichment/safety jobs, denormalizers — and compare the row's `updatedAt`
   against all of their timestamps, not just the obvious route's.
2. **Queue depth outranks the database's top-SQL ranking for causality.** Under
   DB saturation, RDS Performance Insights ranks *symptoms* — everything looks
   slow and the loudest statement wins your attention.
   `topk(15, bullmq_job_count{state="waiting"})` tells you where work is
   accumulating faster than it drains, which is the causal fact.
3. **Date the regression before naming the culprit.** Daily `count_over_time`
   buckets over 30–60d for the error string, matched against
   `git log --first-parent` merge/deploy timestamps, plus the "was every prior
   morning quiet?" 7-day same-hour baseline. First-run-after-deploy and chronic
   load look identical in a single snapshot.
4. **If you don't find the data, don't conclude it doesn't exist — persist.**
   Absence has many boring causes that all return the same empty set: wrong
   `service_name` (see topology above), wrong label value (queue names carry a
   `_QUEUE` suffix), filtering structured metadata as if it were a label,
   retention horizons (Loki ~7d, sometimes less), trace sampling/ingestion gaps
   (logged trace_ids often don't resolve in Tempo; whole windows can be missing),
   or a broken exporter (a BullMQ counter once shipped stuck at 1). Before
   accepting absence as evidence: run a positive control (the same query shape
   for an event you *know* happened) and try a second instrument (Loki↔Tempo↔DB).
5. **Prod is read-only until diagnosed; everywhere else, experiment freely.**
   Reproduce at will in dev, staging, and mirror — including UI-driven repros
   with the authenticated browser (`lg chrome`). In prod: no writes "just to
   watch it throw", and invasive captures (tcpdump, redis MONITOR) need explicit
   user sign-off. A correct diagnosis should *predict* what a probe will show
   before you run it — state the prediction first.
6. **After the fix: sweep the surface, file separately, pin with a spec.**
   Sweep the same route family / code surface for adjacent latent bugs (Loki
   over 30d, DB integrity queries) — refactors rarely break exactly one thing.
   File each finding as its own card; never widen the fix. The fix must ship
   with a spec pinning the corrected behavior (obligatory). An alert on the
   error class is often worth it — **suggest it to the user; it's their call.**

## Workflow by symptom

**Customer reports wrong behavior / data loss** →
map the screen's exact HTTP routes from `zoppy-fe` service code first (all later
queries key off route strings) → Loki timeline for the company/entity → prod DB
via the SQL proxy to see what is *actually persisted* (MD5/CHAR_LENGTH comparisons
between rows date and discriminate saves) → Tempo for the request's span tree and
`http.request_content_length_uncompressed` (payload-size forensics: did the client
even send it?). See `references/grafana-toolbox.md`.

**Error burst / 500s / regression** →
regression-onset dating (doctrine 3) → merge-parent git archaeology
(`git diff <merge>^1 <merge>`, `git grep <sym> <merge>^1`, `-S` pickaxe,
`git log --diff-filter=A`) → library-version diff via package-lock when the bump
is in a package → close the loop with a live provider probe *with a control
entity*. See `references/grafana-toolbox.md` §6–7.

**DB saturation / slow queries / RDS alarms** →
`aws pi get-resource-metrics` triage triple (wait-event %, top SQL, db.user/db.host
attribution) → BullMQ ground truth → deploy-boundary processing-time detector →
intervention with trajectory verification (crater ≠ fixed; drain vs regrow).
See `references/database-incidents.md`.

**Queue backlog / jobs stuck** → `references/database-incidents.md` §B.

**Redis memory / buffer events** → the standing runbook:
`~/Zoppy/docs/redis-client-buffer-incidents-2026-07/report.md` §7 (2 minutes to
ground truth: `zoppy redis clients`, inspect burst, SSM MONITOR burst).

**Infra: target unhealthy / service unreachable / "did my change deploy?"** →
known-good-twin diff ladder, three-source deploy verification, SSM base64
envelope. See `references/infra-toolbox.md`.

## Reference files

- `references/grafana-toolbox.md` — gcx recipes: Loki (line-filter doctrine,
  dedup + caps, onset dating with retention control), Tempo (TraceQL, span-tree
  walking, payload forensics), prod SQL via `/api/ds/query`, dashboards
  round-trip, alert provisioning via REST.
- `references/database-incidents.md` — RDS Performance Insights, wait-event
  cheat sheet, BullMQ metrics, deploy-boundary detectors, named pitfalls.
- `references/infra-toolbox.md` — SSM remote shell, ALB health-check ladder,
  ECS/ECR deploy verification, package archaeology (`npm pack` + dist grep).
