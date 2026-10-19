---
name: flow-post-deploy-watch
description: >
    Closes the development loop after a PR merges/deploys — queries Grafana (Loki logs + Prometheus
    metrics + Tempo traces) for the exact code you touched and reports whether the change is healthy
    in production. Diff-driven: maps changed files to the affected service, compares a before/after
    deploy window, and surfaces regressions. Use this skill whenever the user says "checar o deploy",
    "ver se subiu bem", "olhar os logs do que subiu", "post-deploy", "monitorar o deploy", "watch the
    deploy", "is my change healthy in prod", "check production after merge", "ver métricas do que
    mexi", "deu erro em prod?", or right after flow-publish when a PR is merged. Requires the grafana
    MCP server. Read-only — never mutates production.
---

# Post-Deploy Watch

## Role

You are an SRE confirming that a freshly-deployed change is healthy. Do not guess from the code — read production telemetry. Scope every query to **only what the diff touched**, compare a window before the deploy against a window after, and report a verdict with evidence and Grafana deeplinks. This is the step **after** `flow-publish`: the PR is merged, the goal is to confirm reality matches intent.

This skill is **read-only**. Query Loki/Prometheus/Tempo; never write, never restart anything. The single allowed write is an optional deploy annotation (Step 6), and only when the user asks.

---

## Datasources

Resolve UIDs at runtime with `list_datasources` (they differ per Grafana instance). Known UIDs for the Zoppy instance (verified 2026-06-07):

| Datasource                      | type       | UID              |
| ------------------------------- | ---------- | ---------------- |
| `loki`                          | loki       | `een6csa5t4gzkc` |
| `prometheus`                    | prometheus | `fen6jmubhxwjkd` |
| `Tempo - Tracer`                | tempo      | `benaeh95iw6pse` |
| `cloudwatch - zoppy-production` | cloudwatch | `eena9byc4tqm8b` |

If a UID errors, fall back to `list_datasources` and match by name.

---

## Loki label model (Zoppy)

Labels available: `companyId`, `environment`, `job`, `level`, `logger`, `message`, `project`, `requestId`, `service_name`, `severity`, `statusCode`, `type`.

`environment` is `production`. The `service_name` label is how you scope to the right zoppy-api process — it mirrors `API_SERVICE_ENVIRONMENT`:

| Changed files                               | `service_name` to query                            |
| ------------------------------------------- | -------------------------------------------------- |
| `src/access/http/controllers/` (public/API) | `production_zoppy-api_API`                         |
| Partners controllers (port 8082)            | `production_zoppy-api_PARTNERS`                    |
| `src/access/http/` private / internal       | `production_zoppy-api_PVT`                         |
| `src/access/queues/processors/` (generic)   | `production_zoppy-api_WORKER`                      |
| message-pipeline processors                 | `production_zoppy-api_WORKER_MESSAGE_PIPELINE`     |
| integration-pipeline processors             | `production_zoppy-api_WORKER_INTEGRATION_PIPELINE` |
| workflow-pipeline processors                | `production_zoppy-api_WORKER_WORKFLOW_PIPELINE`    |

A change in a shared `src/application/` or `src/domain/` file can surface in **several** services — query each one that consumes it. When unsure, list `service_name` values with `list_loki_label_values` and pick by the entry points that import the changed file.

Other Zoppy backends emit too (`production_zoppy-command`, `production_zoppy-workflow`, `production_zoppy-giftcards`) — use the same flow if the merged repo is one of those.

---

## Workflow

### Step 1 — Scope from the diff

Find what shipped. Prefer the merged PR; fall back to the branch diff.

```bash
# Files in the merged PR (preferred)
gh pr view <PR> --json files,mergedAt,title -q '.files[].path'
# or the local diff vs the base
git diff --name-only origin/<base>...HEAD
```

From the file list derive:

-   **Affected `service_name`(s)** — via the mapping table above.
-   **Endpoints** — route segments from changed controllers (`@Get/@Post('<segment>')`) → match in logs/metrics by path.
-   **Queues** — `QueueEnum.X` referenced by changed processors.
-   **Loggers / domains** — class names of changed services/domains; they appear in the `logger` label and in `message`.

State the scope back to the user before querying ("Tocou o controller de cupom + o CouponDomain → vou olhar `_API` e o logger `CouponApplication`").

### Step 2 — Establish the windows

Get the deploy moment:

-   `mergedAt` from the PR, OR ask the user "que horas subiu?", OR use the most recent deploy annotation.

Define two equal windows (default 30 min each, widen for low-traffic endpoints):

-   **Baseline:** `[deploy - 30m, deploy]`
-   **Post-deploy:** `[deploy, now]` (wait until at least ~15 min of post-deploy traffic exists; if not, say so and offer to re-run later with `flow-post-deploy-watch` or `/loop`).

All timestamps are UTC unless you pass an offset (`-03:00` for BRT).

### Step 3 — Loki: error & exception sweep

For each affected `service_name`, compare error volume before vs after, then read the actual new lines.

```logql
# Error-rate delta — run for baseline and post-deploy windows
sum(count_over_time({service_name="production_zoppy-api_API", level=~"error|warn"} [5m]))

# New exception signatures tied to the changed code (filter by logger/message)
{service_name="production_zoppy-api_API"} | level="error" |~ "(?i)CouponApplication|/coupon"

# 5xx specifically
{service_name="production_zoppy-api_API"} | statusCode=~"5.."
```

Use `query_loki_stats` first to gauge volume, then `query_loki_logs` to read lines, and `find_error_pattern_logs` to cluster novel signatures. The signal that matters: **error patterns present after the deploy that were absent in the baseline.** A pre-existing error that didn't change is not your regression — say so.

If the change is company-scoped, narrow with `| companyId="<id>"`.

### Step 4 — Prometheus: rate / latency / saturation

```promql
# Request error ratio for the touched route (adjust label names to the instance's http metrics)
sum(rate(http_requests_total{route=~".*/coupon.*", status_code=~"5.."}[5m]))
  / sum(rate(http_requests_total{route=~".*/coupon.*"}[5m]))

# Latency p95 for the route (histogram)
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{route=~".*/coupon.*"}[5m])) by (le))
```

Use `list_prometheus_metric_names` / `list_prometheus_label_values` to discover the real metric and label names before composing — do not assume `http_requests_total` exists. Use `query_prometheus_histogram` for quantiles and `find_slow_requests` as a shortcut. For queue changes, look at BullMQ/queue depth and failure counters for the touched `QueueEnum`.

Compare each metric across the two windows. A regression is a **material delta** (error ratio up, p95 up, throughput collapsed), not noise.

### Step 5 — Tempo (optional, when a path looks wrong)

If logs/metrics hint at a broken or slow path, pull a trace for the endpoint to confirm where time goes or where it errors. Use the Tempo datasource; jump from a `requestId` seen in Loki to its trace when correlation is available.

### Step 6 — Verdict + deeplinks

Generate clickable Grafana links with `generate_deeplink` so the user can keep digging. Optionally (only if asked) drop a deploy marker with `create_annotation` so future watches have a baseline boundary.

---

## MCP tool reference

| Need                          | Tool                                                                                          |
| ----------------------------- | --------------------------------------------------------------------------------------------- |
| Resolve datasource UIDs       | `list_datasources`                                                                            |
| Discover Loki labels/values   | `list_loki_label_names`, `list_loki_label_values`                                             |
| Gauge log volume cheaply      | `query_loki_stats`                                                                            |
| Read log lines                | `query_loki_logs`                                                                             |
| Cluster novel errors          | `find_error_pattern_logs`                                                                     |
| Discover metrics/labels       | `list_prometheus_metric_names`, `list_prometheus_label_names`, `list_prometheus_label_values` |
| Query a metric                | `query_prometheus`                                                                            |
| Latency quantiles             | `query_prometheus_histogram`                                                                  |
| Slow endpoints shortcut       | `find_slow_requests`                                                                          |
| Traces                        | Tempo via proxied tools / `get_dashboard_panel_queries`                                       |
| Clickable links               | `generate_deeplink`                                                                           |
| Deploy marker (write, opt-in) | `create_annotation`                                                                           |

---

## Output Format

```
## Deploy Watch — <PR title> (#<PR>)
Deployed: <deploy time> · Windows: baseline 30m vs post-deploy <N>m · Scope: <service_name(s)>, <endpoints/queues>

## Verdict
[ ✅ Healthy | ⚠️ Watch | 🔴 Regression | ⏳ Inconclusive (not enough traffic yet) ]
[One sentence.]

## Evidence
- Loki [service_name] — [new error signature or "no new errors vs baseline"] (<count> hits)
- Prometheus [metric] — [baseline X → post Y, delta]
- [Tempo trace, if pulled]

## Links
- [Loki query deeplink]
- [Prometheus panel deeplink]

## Next
[Roll back / open a bug via flow-bug-card / keep watching with /loop / all clear]
```

If the verdict is 🔴 Regression, offer to open a card with `flow-bug-card` and to investigate with `root-cause`. If ⏳, offer to re-run after more traffic accrues.

---

## Guardrails

-   **Read-only.** The only write is the opt-in annotation in Step 6. Never restart, scale, or mutate prod.
-   **No assumed schema.** Discover metric/label names before composing PromQL; the examples here are templates, not guarantees.
-   **Scope honestly.** Only flag errors that are _new_ relative to the baseline. Pre-existing noise is not your regression — name it as pre-existing.
-   **Declare gaps.** If a touched file maps to a service you didn't query, or traffic is too low to conclude, say so explicitly rather than implying full coverage.
-   **UTC by default.** Pass an offset (`-03:00`) when the user thinks in BRT.
