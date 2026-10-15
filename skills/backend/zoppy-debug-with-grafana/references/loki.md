# Loki (uid `een6csa5t4gzkc`)

## 1. Line-filter doctrine and the company timeline

`company_id`, `trace_id`, `request_id`, `route`, `identifier`, `channel` are
**structured metadata, not indexed labels**. Selector-matching them
(`{company_id="…"}`) errors or returns nothing. Use line filters, or label-style
filters *after* the pipe:

```bash
DS=een6csa5t4gzkc
# Company-scoped timeline (the single highest-yield instrument for customer bugs)
gcx logs query -d $DS '{service_name="production_zoppy-api_API"} |= "<companyId>"' \
  --from now-48h --to now --limit 500 -o json
# Zoom into one request: full body + stack trace
gcx logs query -d $DS '{service_name="production_zoppy-api_API"} |= "<trace_id>"' --from now-24h --to now -o json
# Filter on structured metadata after the pipe
gcx logs query -d $DS '{project="campaign"} | identifier="ENQUEUE_MESSAGES"' --from now-6h --to now
```

Pipe to python, sort chronologically, print `ts | level | route | line`.

**There are no per-request HTTP access logs in Loki** — only what the app
explicitly logs via LogService. "Did the request reach us, with what
status/latency?" is an **ALB Athena** question (`references/athena.md`); Tempo
only holds ~100 minutes.

Workers log under different `service_name`s than the API — an "eliminating"
query against `_API` proves nothing about a queue-side writer. See the topology
table in `zoppy-prod-debugging`.

## 2. The identical-line dedup trap (fakes losses)

Loki keeps at most **one byte-identical line per stream per millisecond**. A
constant log line (same identifier, empty payload fields) emitted in bursts
silently loses occurrences — proven live: 338 stored lines across 338 distinct
milliseconds, never two in one, while an entity whose line carries a unique ID
showed a perfect zero gap over the same window. End-to-end DB accounting
confirmed nothing was actually lost.

Consequences: before building any count, ratio, or "X% vanished" claim on a log
line, check whether the line is byte-unique per occurrence. If it isn't, Loki
counts are **floors, not totals** — and the fix is a one-liner at the emission
site (put anything unique in the line), not an alert threshold.

## 3. The emission-granularity trap (never ratio unverified identifiers)

The same identifier can be emitted at **different granularities by different
processors**. Real case: `ENQUEUE_MESSAGES` is written only by fetch-entities,
once per batch of up to 50 recipients; `VALIDATE_MESSAGES` is written per-batch
by fetch-entities *and* per-recipient by the sender processors — one identifier,
five processors, three granularities. A ratio between them compared apples to
oranges and kept an alert firing for 39 of 72 hours on healthy traffic.

Before any cross-identifier ratio: grep **every** emission site of both
identifiers in the codebase and confirm like units. Structured metadata can
discriminate emitters (e.g. `channel` is present only on sender processors —
`| channel=""` isolates the per-batch writer).

## 4. The flow-log contract and `DISABLED_FLOW_STEPS`

Workflow/campaign flow logs follow the contract in
`zoppy-api/src/services/log/flow-log-contract.ts`: message format
`[FLOW] <STAGE>/<STEP>: …` with stages `ENTRY|RUN|EFFECT` and core keys
(`flowId`, `companyId`, `stage`, `step`, `reason`, …).

**Trap**: steps listed in that file's `DISABLED_FLOW_STEPS` set are **never
emitted** — they never reach Loki. A query or alert on a disabled step returns
permanent zero and can never fire (this shipped a dead alert once). Check the
set before querying, counting, or alerting on any flow step.

## 5. Regression-onset dating (+ retention control)

```bash
gcx logs query -d $DS \
 'sum(count_over_time({service_name="production_zoppy-api_API"} |= "<error string>" [1d]))' \
 --from now-30d --to now --step 24h -o json
```

Always pair with a **retention control** on an always-present line (e.g.
`|= "Success validating email"`) so "first occurrence on day X" is honestly
"within a window that starts at day Y". Timestamps come back in mixed units —
normalize with `while t > 1e11: t /= 1000`.

The same query re-run after deploy, buckets at 30m/15m going to zero, is the fix
verification — one instrument, both ends of the incident.

## 6. Dedup + cardinality caps (retry-inflated errors)

BullMQ retries log the same failure ~4×. Dedup by the stable key (probe stability
first):

```bash
SEL='{service_name="production_zoppy-api_WORKER", level="error"} | identifier="<IDENT>"'
gcx logs query -d $DS "max(sum by (request_id)(count_over_time($SEL [1h])))" ...   # 3-5 ⇒ stable key
gcx logs query -d $DS "count(sum by (request_id)(count_over_time($SEL [6h])))" ... # deduped count
```

`count(sum by(k)(...))` materializes one series per distinct value → **Loki
~500-series cap**; ladder windows 1h→6h→12h→24h to find the ceiling, keep alert
queries at `[1h]`, and remember it breaks hardest *during* incidents. The
cardinality-free fallback is Prometheus: `failed/(completed+failed)` on the
BullMQ counters (validate the counter first — see
`references/datasource-recipes.md`). For `unwrap` percentiles,
`drop request_id, trace_id, ...` before `unwrap`.
