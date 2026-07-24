---
name: prod-debugging
description: Production debugging playbook for Zoppy — how to get ground truth from Grafana (Loki, Tempo, Prometheus, MySQL-via-proxy), RDS Performance Insights, BullMQ metrics, ECS/SSM, and git archaeology, with the epistemic rules that prevent wrong root causes. Use this skill whenever investigating ANY production incident, customer bug report, regression, outage, latency spike, error burst, "data not saving", "worked yesterday", queue backlog, or database saturation — even if the user only pastes a GitHub issue or a customer complaint. Also use it before asserting "no logs/no errors found", before declaring a root cause, and when verifying a fix landed in prod. Complements root-cause (code trace path) — root-cause tells you where to read code; this skill tells you how to observe production.
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
| Worker labels | `production_zoppy-api_WORKER`, `production_zoppy-api_WORKER_QUEUE_LIGHT_PIPELINE`, others — **census first** (below) |
| BullMQ metrics | `bullmq_job_count{job="zoppy_api_bullmq", queue="…_QUEUE", state=…}` — queue names carry the `_QUEUE` suffix |
| Loki retention | ~7 days (app logs have burned at ~3 days before — query flood windows immediately) |
| Tempo retention | ~7 days, sampled; error traces may be absent entirely |
| Observability EC2s (SSM, no SSH) | dev `i-0ff0bec1876512e18` (zoppy-dev), prod `i-03918c5a158642551` (zoppy-prd) |

All Grafana access goes through the `gcx` CLI (never `mcp__grafana__*`). The
universal output adapter — gcx prints a `hint:` line that corrupts JSON:

```bash
gcx <anything> -o json 2>/dev/null | sed '/^hint:/d' | python3 -c "..."
```

## Doctrine — the rules that have decided real incidents

1. **An empty query result is not elimination until the same query shape finds a
   known-positive.** Wrong service label, wrong Prometheus label value, wrong span
   attribute, and retention horizons all return the same empty set as "it never
   happened". Before treating absence as evidence: run the label census
   (`gcx logs labels -d <loki> -l service_name`, `group by (queue) (bullmq_job_count{...})`)
   and re-run the query for an event you know exists (a control probe). This has
   flipped conclusions more than once — including a safety-queue clobber that was
   "eliminated" because the query hit `_API` while the writer lived in
   `_WORKER_QUEUE_LIGHT_PIPELINE`.
2. **"UPDATE ran and returned 200" does not mean "the request's values were
   written".** When data reverts or "doesn't save", hunt for a **second writer**:
   list every code path that writes the row (queue processors, safety/enrichment
   jobs, denormalizers), and check whether any does a full-row write from an
   entity loaded earlier (stale-snapshot clobber). Compare the row's `updatedAt`
   against the timestamps of *all* candidate writers, not just the obvious route.
3. **When a diff makes a write "more conservative" (stops nulling, stops
   deleting, adds an `if !== undefined` guard), ask which downstream consumer
   depended on the old destructive behavior.** A nulled column can be the very
   thing that made a background job skip; keeping the value arms the job.
4. **Queue depth outranks query text for causality.** Under DB saturation,
   Performance Insights' top-SQL is a symptom ranking — everything looks slow and
   the loudest digest wins your attention. `topk(15, bullmq_job_count{state="waiting"})`
   tells you where work is accumulating faster than it drains.
5. **Date the regression before naming the culprit.** Daily
   `count_over_time` buckets over 30–60d for the error string, matched against
   `git log --first-parent` merge/deploy timestamps, plus the "was every prior
   morning quiet?" 7-day same-hour baseline. First-run-after-deploy and chronic
   load look identical in a single snapshot.
6. **Trust the instrument only as far as you've validated it.** Tempo drops error
   traces (sampling + New Relic coexistence) — empty TraceQL means "unknown", not
   "no errors"; pivot to Loki. `bullmq_job_event_total` has shipped broken
   (stuck at 1). `rate()` over ALB-scraped multi-process counters is garbage.
   Loki `count(sum by(id)(...))` hits a 500-series cap on wide windows — ladder
   1h→6h→12h→24h to find the ceiling.
7. **Read-only until diagnosed; predictions before probes.** Never fire a prod
   write "just to watch it throw". When your diagnosis is right it should
   *predict* observations before you make them (e.g. why the user's repro fails).
   Prod-invasive diagnostics (tcpdump, MONITOR) need explicit user sign-off.
8. **Sweep, then triage.** After the fix, sweep the whole route family
   (Loki 30d + traces + DB integrity query) for adjacent failure modes, and file
   each as its own card. Ship the fix together with a spec pinning the behavior
   and an alert on the error *class* — the alert you create today catches the
   next bug (this has literally happened the same evening).

## Workflow by symptom

**Customer reports wrong behavior / data loss** →
map the screen's exact HTTP routes from `zoppy-fe` service code first (all later
queries key off route strings) → Loki timeline for the company/entity → prod DB
via the SQL proxy to see what is *actually persisted* (MD5/CHAR_LENGTH comparisons
between rows date and discriminate saves) → Tempo for the request's span tree and
`http.request_content_length_uncompressed` (payload-size forensics: did the client
even send it?). See `references/grafana-toolbox.md`.

**Error burst / 500s / regression** →
regression-onset dating (doctrine 5) → merge-parent git archaeology
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
