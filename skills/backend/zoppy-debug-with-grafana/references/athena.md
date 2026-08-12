# Athena datasources

Both are queried through `/api/ds/query` (same heredoc pattern as MySQL — see
`references/datasource-recipes.md`, swap the uid) or dashboard panels.
Trino/Presto SQL dialect.

## 1. ALB access logs (uid `ees4kgkh4m2v4c`) — standing rulings

These two rulings have each already shipped a broken query/alert; they are not
suggestions:

- **Query `alb_production_services_internal_2` ONLY.** The non-`_2` table
  (`alb_production_services_internal`) has a broken RegexSerDe: row counts look
  right, **every column parses as NULL** — silent garbage. Same S3 location and
  partitions; only `_2` parses.
- **NEVER filter on `domain_name`.** It is EMPTY on this internal ALB (no TLS
  SNI captured); `domain_name = 'api-partners.zoppy.com.br'` matches zero rows
  — an alert built on it computed 0/0 and could never fire. The host lives
  inside `request_url` (full URL, e.g.
  `https://api-partners.zoppy.com.br:443/whatsapp-tech-provider/webhook`) —
  match the host there, and extract paths with
  `url_extract_path(request_url)`.

Working knowledge:

- ~90 days of data, fresh to the minute. Useful columns: `time`,
  `elb_status_code`, `target_status_code`, `request_verb`, `request_url`,
  `target_processing_time`, `user_agent`, `client_ip`.
- When grouping routes, normalize UUID/numeric path segments and exclude
  OPTIONS.
- **Coverage caveat**: only the `api` / `api-partners` / `api-event-bridge` /
  `api-workflow` domains transit this ALB. Meta webhooks and whatsapp-commerce
  enter via other ingress — `POST /api/whatsapp-webhook` shows 0 hits while
  obviously hot. Zero rows here ≠ dead route; identify the ingress first.
- This is the instrument for **route liveness** (dead-code audits: 90d of
  traffic per route) and **per-request forensics** ("did the client call us,
  when, with what status and latency") — Loki has no access logs and Tempo
  holds ~100 minutes.

## 2. zoppy_silver lake (uid `cengw3mbfj5z4f`)

Mirrors the MySQL DB for analytics/dashboards.

- Tables are `db_<lowercased-tablename>` (`db_wppcontacts`, `db_companies`, …);
  column names are lowercased (`lastwppconversationid`, `createdat`).
- **MySQL booleans are stored as INTEGER** — `unread = 1` /
  `COALESCE(hasunread,0) = 1`, never `= true` (errors
  `Cannot apply operator: integer = boolean`).
- Tables can sit at slightly different ingest snapshots — cross-table joins can
  show false "inconsistencies". Check freshness with
  `date_diff('minute', max(updatedat), current_timestamp)` before trusting a
  join.
- `sessionexpiration` on `db_wppconversations` is a 13-digit ms-epoch STRING:
  `from_unixtime(CAST(x AS BIGINT)/1000)`, guarded with `TRY(CAST(...))`.
- **Not ingested** (as of 2026-06): `db_wppcommercesessions`,
  `db_wppcommerceagents` — carve those flows out as unverifiable from the lake.
