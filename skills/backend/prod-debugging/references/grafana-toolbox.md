# Grafana toolbox (gcx)

Every recipe assumes the constants from SKILL.md. gcx quirks that apply to all of
them: strip the `hint:` line before parsing JSON (`sed '/^hint:/d'` or use
`--jq`/`--json`); never pipe with `2>&1` into a JSON parser (hints go to stderr on
some commands, stdout on others); RFC3339 timestamps with explicit offsets
(`2026-07-24T12:30:00-03:00`) — some relative forms are silently ignored.

## 1. Loki — line-filter doctrine and the company timeline

`company_id`, `trace_id`, `request_id`, `route` are **structured metadata, not
indexed labels**. Selector-matching them (`{company_id="…"}`) errors or returns
nothing. Use line filters:

```bash
DS=een6csa5t4gzkc
# Company-scoped timeline (the single highest-yield instrument for customer bugs)
gcx logs query -d $DS '{service_name="production_zoppy-api_API"} |= "<companyId>"' \
  --from now-48h --to now --limit 500 -o json
# Zoom into one request: full body + stack trace
gcx logs query -d $DS '{service_name="production_zoppy-api_API"} |= "<trace_id>"' --from now-24h --to now -o json
```

Pipe to python, sort chronologically, print `ts | level | route | line`.

**Service-label census before any negative claim** (doctrine 1):

```bash
gcx logs labels -d $DS -l service_name -o json
```

Workers log under different `service_name`s than the API — queue processors
(e.g. template safety) live in `production_zoppy-api_WORKER_QUEUE_LIGHT_PIPELINE`.
An "eliminating" query against `_API` proves nothing about a queue-side writer.

## 2. Regression-onset dating (+ retention control)

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

## 3. Dedup + cardinality caps (retry-inflated errors)

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
cardinality-free fallback is Prometheus: `failed/(completed+failed)` on the BullMQ
counters (validate the counter first — see database-incidents §B).
For `unwrap` percentiles, `drop request_id, trace_id, ...` before `unwrap`.

## 4. Tempo — traces, span trees, payload forensics

```bash
gcx traces labels -d benaeh95iw6pse          # discover span attribute names first
gcx traces query -d benaeh95iw6pse '{span.http.target =~ ".*<route>.*" && span.http.status_code >= 400}' \
  --from now-72h --to now
gcx traces get <traceId> -d benaeh95iw6pse > trace.json   # or --llm for a compact view
```

Walk `trace.resourceSpans[].scopeSpans[].spans[]`; attributes are
`{key, value:{stringValue|intValue}}` pairs. What traces answer that logs can't:

- The exact SQL statements a request executed (`db.statement` spans) — e.g.
  "the UPDATE ran, inside a transaction, and committed".
- Truncated exceptions: LogService swallows `ex` payloads; the trace still has
  the failing call sequence.
- **Payload forensics**: `http.request_content_length_uncompressed` on the root
  span discriminates "client never sent it" from "server dropped it", and
  byte-identical sizes across "different" saves suggest identical payloads.

Trust caveats (doctrine 6): sampling + New Relic coexistence mean logged
trace_ids often don't resolve and error traces may be wholly absent; ingestion
gaps happen (whole mornings missing). Sanity-check any negative with a query for
a request you know occurred.

## 5. Prod SQL through the Grafana datasource proxy

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

## 6. Dashboards — get → mutate → update

```bash
gcx dashboards get <uid> -o json 2>/dev/null | sed '/^hint:/d' > live.json
# edit panels in python (walk d['spec']['panels'], recurse into rows)
gcx dashboards update <uid> -f live-fixed.json
```

Re-`get` before every update (fresh `resourceVersion`). Steal styling from a
sibling panel instead of hand-writing fieldConfig. Panel snapshot rendering
requires the image-renderer plugin (not installed) — verify by re-running the
panel's query instead.

## 7. Alerts — provision via REST, not `gcx alert rules` (read-only)

```bash
gcx api "/api/v1/provisioning/alert-rules" -X POST -H "X-Disable-Provenance: true" -d @rule.json
gcx api "/api/v1/provisioning/folder/<folderUid>/rule-groups/<URL-encoded name>" -X PUT ...  # eval interval
gcx api "/api/v1/provisioning/alert-rules/<uid>" -X PUT ...                                   # edit in place
```

Clone an existing sibling rule as the template (read its notification policy and
label conventions first); **ask before attaching contact points**. Hard-won
rules: math-expr severity **bands** (`($B > 10) && ($B <= 20)`) so exactly one of
info/warning/critical fires; `or vector(0)` on sparse counters (exporters stop
emitting the series → `increase()` returns No Data, not 0); volume guard
(`&& ($M >= 2)`) against low-traffic ratio inflation; nil-safe
`{{ with $values.B }}` templates (else Google Chat renders `%!f()`);
`execErrState: OK` so transient Loki hiccups don't page. Verify after every batch:
`gcx alert rules list -o json` → per-rule `health | state` until clean, waiting
one evaluation interval (`sleep 75`) before judging.
