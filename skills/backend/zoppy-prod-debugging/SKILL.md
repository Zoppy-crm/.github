---
name: zoppy-prod-debugging
description: Use when investigating ANY production incident or customer bug report in Zoppy — regressions, outages, 500s, latency spikes, error bursts, scaling anomalies, "data not saving", "worked yesterday", queue backlogs, database saturation — even if the user only pastes a GitHub issue or customer complaint. Also use before declaring a root cause, before asserting that logs/traces/data don't exist, and when verifying a fix or deploy landed in prod. Covers evidence discipline, service topology, read-only AWS CLI forensics (ECS, autoscaling, CloudTrail, RDS), SSM, and regression-dating git archaeology. Complements root-cause (code layers) and zoppy-debug-with-grafana (the Grafana instruments).
---

# Production Debugging (Zoppy)

Get ground truth from production instead of inferring from code. The `root-cause`
skill walks the code layers; this skill runs the investigation. The Grafana
instruments — Loki, Athena (ALB access logs + lake), prod MySQL, Prometheus/BullMQ,
Tempo, alert rules — live in the sibling skill
[`zoppy-debug-with-grafana`](../zoppy-debug-with-grafana/SKILL.md); load it the
moment an investigation touches Grafana. Grade every claim as
**observed / eliminated / inferred**, and only assert a root cause when code,
timeline, and at least one production observation agree — with at least one
alternative hypothesis eliminated by data.

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
   service label, wrong label value, retention horizons, silent dedup, a broken
   exporter, a disabled log step. The Grafana-specific checklist lives in
   `zoppy-debug-with-grafana`. Before accepting absence as evidence: run a
   positive control (the same query shape for an event you *know* happened) and
   try a second instrument (Loki ↔ ALB Athena ↔ DB).
5. **Prod is read-only until diagnosed; everywhere else, experiment freely.**
   Reproduce at will in dev, staging, and mirror — including UI-driven repros
   with the authenticated browser (`lg chrome`). In prod: no writes "just to
   watch it throw", and invasive captures (tcpdump, redis MONITOR) need explicit
   user sign-off. A correct diagnosis should *predict* what a probe will show
   before you run it — state the prediction first.
6. **After the fix: sweep the surface, file separately, pin with a spec.**
   Sweep the same route family / code surface for adjacent latent bugs (logs
   over 30d, DB integrity queries) — refactors rarely break exactly one thing.
   File each finding as its own card; never widen the fix. The fix must ship
   with a spec pinning the corrected behavior (obligatory). An alert on the
   error class is often worth it — **suggest it to the user; it's their call.**

## Service topology — where code runs and logs land

Pick the service by where the code *runs*, not where the feature lives. A public
HTTP request runs in `API`; a service-to-service call in `PVT`; a queue job in
its worker pipeline — never in `API`. Loki labels these as
`service_name="production_zoppy-api_<SUFFIX>"`.

| Suffix | What runs there |
| --- | --- |
| `API` | Public HTTP API (customer/dashboard traffic) |
| `PVT` | Private API — service-to-service calls |
| `GIFTCARDS`, `PARTNERS` | Their dedicated public API surfaces (PARTNERS absorbs the Meta webhook traffic, ~700k–1M req/day) |
| `WORKER_MESSAGE_PIPELINE` | Campaign/message-send queue processors |
| `WORKER_WORKFLOW_PIPELINE` | Workflow-engine queue processors |
| `WORKER_INTEGRATION_CORE_PIPELINE`, `WORKER_INTEGRATION_PROVIDER_PIPELINE` | Provider/data-sync queue processors |
| `WORKER_QUEUE_LIGHT_PIPELINE`, `WORKER_QUEUE_HEAVY_PIPELINE` | Everything else, split by job weight (safety evaluations, enrichment, reports…) |

Sibling services log under their own names: `production_zoppy-workflow`,
`production_zoppy-command`, `production_zoppy-event-bridge`,
`production_zoppy-pixel-lambda`. Which queue runs in which pipeline is defined in
`zoppy-api/src/access/queues/` (`queue-pool/queue-light|heavy.module.ts`,
`message-pipeline.module.ts`, `workflow-pipeline.module.ts`) — grep the
processor's module registration when unsure.

Scaling posture differs wildly per service (API has real autoscaling, PARTNERS
has none — only a cron Lambda). Never assume; read it with the three
`application-autoscaling describe-*` calls in `references/aws-toolbox.md`.

## Workflow by symptom

**Customer reports wrong behavior / data loss** →
map the screen's exact HTTP routes from `zoppy-fe` service code first (all later
queries key off route strings) → Loki timeline for the company/entity → prod DB
via the SQL proxy to see what is *actually persisted* → ALB Athena for "did the
client even call us". Instruments in `zoppy-debug-with-grafana`.

**Error burst / 500s / regression** →
regression-onset dating (doctrine 3, Loki recipe in the sibling skill) →
merge-parent git archaeology → library-version diff via package-lock when the
bump is in a package → close the loop with a live provider probe *with a control
entity*. See `references/code-archaeology.md`.

**Latency spikes / burst 5xx / capacity questions** →
what is actually running and how it scales: ECS desired/running counts, the
three autoscaling describes, CloudTrail for who changed `desiredCount`, the
`zoppy-worker-time-scaler` Lambda trap. See `references/aws-toolbox.md`.

**DB saturation / slow queries / RDS alarms** →
`aws pi get-resource-metrics` triage triple (wait-event %, top SQL, db.user/db.host
attribution) → reader-hotspot check → BullMQ ground truth (sibling skill) →
deploy-boundary processing-time detector → intervention with trajectory
verification (crater ≠ fixed; drain vs regrow). See `references/aws-toolbox.md`.

**Queue backlog / jobs stuck** → BullMQ metrics in `zoppy-debug-with-grafana`,
then doctrine 2.

**Redis memory / buffer events** → the standing runbook:
`~/Zoppy/docs/redis-client-buffer-incidents-2026-07/report.md` §7 (2 minutes to
ground truth: `zoppy redis clients`, inspect burst, SSM MONITOR burst).

**Infra: target unhealthy / service unreachable / "did my change deploy?"** →
known-good-twin diff ladder, three-source deploy verification, SSM base64
envelope. See `references/infra-toolbox.md`.

## Reference files

- `references/aws-toolbox.md` — read-only AWS CLI forensics: ECS capacity,
  autoscaling truth, the worker-time-scaler Lambda trap, CloudTrail, ELB
  attributes, CloudWatch alarm traps, RDS Performance Insights + reader
  hotspots.
- `references/code-archaeology.md` — regression dating with git: merge-parent
  archaeology, pickaxe, deploy correlation, attribution honesty.
- `references/infra-toolbox.md` — SSM remote shell (base64 envelope), ALB
  health-check ladder, ECS/ECR deploy verification, package archaeology
  (`npm pack` + dist grep).
