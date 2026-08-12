# Datasource recipes (MySQL, Prometheus/BullMQ, Tempo, Redis)

## 1. Prod SQL through the Grafana datasource proxy

There is no direct DB client; this replaces it. Heredoc the JSON (single-quoted
SQL literals inside), POST to `/api/ds/query`:

```bash
q() { cat > /tmp/q.json <<EOF
{"queries":[{"refId":"A","datasource":{"uid":"een6cmg0t4xkwf"},"rawSql":"$1","format":"table"}]}
EOF
gcx api /api/ds/query -X POST -d @/tmp/q.json --jq '.results.A.frames[0].data.values | transpose'; }

q "SELECT id, name FROM zoppy.Companies WHERE name LIKE '%<customer>%' LIMIT 10"
```

- Every table needs the **`zoppy.` schema prefix** (no default DB); probe with
  `SELECT DATABASE()` if lost, or `information_schema.tables`.
- Response is column-major — `transpose` (jq) or `zip(*values)` (python).
- Timestamps are ms-epoch — `FROM_UNIXTIME(col/1000)` or convert client-side.
- Discriminating saves without history: `MD5(col)`, `CHAR_LENGTH(col)` between a
  row and its suspected source/copy tell you *what* changed and *whether* two
  rows are byte-identical. `CHAR_LENGTH` on a JSON column measures MySQL's
  normalized text (spaces after `:` and `,`), not the compact wire form — don't
  compare it byte-for-byte against a request payload.
- Live index truth: `SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, CARDINALITY
  FROM information_schema.STATISTICS WHERE TABLE_SCHEMA='zoppy' AND TABLE_NAME='…'`
  — has corrected "missing index" claims already written into PR bodies.
- On partial errors the real payload hides in `json.loads(outer['error']['details'])`.

## 2. BullMQ ground truth (Prometheus, uid `fen6jmubhxwjkd`)

```bash
PROM=fen6jmubhxwjkd
# Discover metric names / label vocabulary — never guess
gcx metrics query -d $PROM 'group by (__name__) ({__name__=~".*([Bb]ull|[Qq]ueue|[Jj]ob).*"})'
gcx metrics query -d $PROM 'group by (queue) (bullmq_job_count{job="zoppy_api_bullmq"})'
# The decisive causality query
gcx metrics query -d $PROM 'topk(15, bullmq_job_count{job="zoppy_api_bullmq",state="waiting"})'
# Backlog onset per queue
gcx metrics query -d $PROM 'sum(bullmq_job_count{job="zoppy_api_bullmq",queue="<X>_QUEUE",state="waiting"})' \
  --from <2d-before-suspect> --to now --step 2h
# Deploy-boundary processing-time regression (sample at a pre-saturation hour!)
gcx metrics query -d $PROM 'sum(rate(bullmq_job_processing_time_seconds_sum{job="zoppy_api_bullmq"}[30m]))
  / sum(rate(bullmq_job_processing_time_seconds_count{job="zoppy_api_bullmq"}[30m]))'
```

Traps, all hit live:
- Queue label values carry the `_QUEUE` suffix (`OPEN_SEARCH_QUEUE`, not
  `OPENSEARCH`). **Empty PromQL ≠ zero load — enumerate label values first.**
- `bullmq_job_event_total` has shipped broken (stuck at 1) — before inferring
  "0 jobs ran", check that *any* queue shows completions.
- A series' **birth timestamp is a deploy fingerprint** — a net-new queue's
  metric not existing before T tells you when the feature landed.
- Historical instant queries misbehave — use a 1-point range query
  (`--from X --to X+40m --step 40m`) instead of `--to <past>`.
- Prometheus `rate()` over ALB-scraped multi-process counters interleaves and is
  garbage — non-prod = `DEVELOPMENT_/MIRROR_/STAGING_` prefixes, prod job is
  `zoppy_api_bullmq`.
- The BullMQ exporter is **one target for the whole platform** — queue depth
  cannot be attributed to a specific worker pipeline from the metric alone.
- Queue depth sickens **before** the DB looks sick — check backlog onset against
  the DB-load onset to order cause and effect.

## 3. Tempo (uid `benaeh95iw6pse`) — proxy route + ~100 min retention

The normal query routes (`gcx traces …`, `/api/ds/query`) return **HTTP 500**
for this datasource. Use the datasource **proxy** route:

```bash
gcx api '/api/datasources/proxy/uid/benaeh95iw6pse/api/v2/search/tags'
gcx api '/api/datasources/proxy/uid/benaeh95iw6pse/api/search/tag/service.name/values'
gcx api '/api/datasources/proxy/uid/benaeh95iw6pse/api/search?q=<urlencoded TraceQL>'
```

**Retention is ~100 minutes** (verified by walking backwards: traces present at
−90 min, zero at −105 min and beyond). Post-hoc incident analysis via traces is
impossible — capture traces *during* the incident or not at all. Sampling and
New Relic coexistence mean logged trace_ids often don't resolve anyway;
sanity-check any negative with a query for a request you know occurred.

What traces answer that logs can't (within the window):

- The exact SQL statements a request executed (`db.statement` spans) — "the
  UPDATE ran, inside a transaction, and committed".
- Truncated exceptions: LogService swallows `ex` payloads; the trace still has
  the failing call sequence.
- **Payload forensics**: `http.request_content_length_uncompressed` on the root
  span discriminates "client never sent it" from "server dropped it".

Walk `trace.resourceSpans[].scopeSpans[].spans[]`; attributes are
`{key, value:{stringValue|intValue}}` pairs.

## 4. Redis (uid `den98dq5sdfk0e`) — PRODUCTION, read-only

This datasource points at **production ElastiCache** (cluster mode, TLS); there
is no dev/staging Redis datasource. Keep every command read-only and O(1) —
never writes, never MONITOR, no SCAN sweeps on a dashboard refresh loop.

- Query via `/api/ds/query` with target shape
  `{"refId":"A","datasource":{"type":"redis-datasource","uid":"den98dq5sdfk0e"},"type":"cli","query":"ZCARD <key>"}`.
- `type:"cli"` runs any raw command reliably. `type:"command"` works for
  `llen`/`xlen` but returns **empty** for `zcard` and `memory usage` — use cli.
- **BullMQ key prefix is `bull:{zoppy}::` (double colon)** — the configured
  prefix already ends in `:` and BullMQ adds its own separator. Per-queue keys:
  `bull:{zoppy}::<QUEUE_NAME>:completed|failed|wait|events|<jobId>`. Prod queue
  names have no env prefix (dev/staging prepend `DEVELOPMENT_`/`STAGING_`).
- Keys with special characters (JSON-blob cache keys) need double quotes with
  escaped inner quotes: `cli 'MEMORY USAGE "{\"key\":...}"'`.
- `/api/ds/query` caps ~5k targets per request — batch larger sweeps.
