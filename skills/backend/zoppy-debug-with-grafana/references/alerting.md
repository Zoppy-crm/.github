# Alerting + dashboards (provisioning, history, templating, design doctrine)

## 1. Provision via REST, not `gcx alert rules` (read-only)

```bash
gcx api "/api/v1/provisioning/alert-rules" -X POST -H "X-Disable-Provenance: true" -d @rule.json
gcx api "/api/v1/provisioning/alert-rules/<uid>" -X PUT ...                                   # edit in place
gcx api "/api/v1/provisioning/alert-rules/<uid>"                                              # read current rule
gcx api "/api/v1/provisioning/folder/<folderUid>/rule-groups/<URL-encoded name>" -X PUT ...   # eval interval
```

Clone an existing sibling rule as the template (read its notification policy and
label conventions first); **ask before attaching contact points**. Verify after
every batch: `gcx alert rules list -o json` → per-rule `health | state` until
clean, waiting one evaluation interval (`sleep 75`) before judging.

Rule mechanics that have each fixed a real misfire:

- Math-expr severity **bands** (`($B > 10) && ($B <= 20)`) so exactly one of
  info/warning/critical fires.
- `or vector(0)` on sparse counters — exporters stop emitting the series and
  `increase()` returns No Data, not 0.
- `execErrState: OK` so transient Loki hiccups don't page.
- Rules without a **reduce node** may render `$values` empty — add the reduce
  node; don't rewrite the message around it.

## 2. State history — the annotations API

Reconstruct what fired, when, and with what values — the raw material for any
alert audit or firing ledger:

```bash
FROM=$(date -d "2 days ago" +%s)000; TO=$(date +%s)000
gcx api "/api/annotations?type=alert&from=$FROM&to=$TO&limit=500" -o json
```

Each transition carries the rendered values at fire/resolve time. Cross-check
against the *current* rule text via the provisioning read — rules edited
mid-flight resolve with the **old** annotations (snapshotted at fire time);
that's a transition artifact, not a failing template.

## 3. `$values` templating + the resolved-state rendering gap

- Fractional shares: `{{ humanizePercentage $values.X.Value }}` — a share query
  returns 0.078, so `printf "%.0f%%"` renders "0%". Use `printf` on `.Value`
  only for counts/seconds/rates.
- **Resolved-state gap**: Grafana re-renders annotations at resolution time,
  when `$values` is empty — firing messages render numbers fine, "Resolvido:"
  messages leak the raw `{{ $values }}` template. Don't guard every rule; fix
  it **once at the contact point**: resolved notifications render the
  title/summary (no value placeholders), firing notifications render the
  value-bearing description.

## 4. Alert-design doctrine — each learned from a real swallow or misfire

- **Volume gates swallow incidents.** With a proportional threshold, a minimum
  on the numerator OR denominator implicitly floors the other — a gate sized to
  "avoid noise" can hide a real drop entirely (a 5,000-messages-in-30-min gate
  meant a total send failure below that rate could never page). Prefer **small
  floors plus `for:` duration** to ride out low-traffic noise windows.
- **Low-traffic share trap** (the same coin's other face): one 5xx on a
  17-call/hour route is 5.9% — a share threshold with *no* volume floor
  converts a single failure into a critical. Gates must exist, but small and
  paired with `for:` — never sized anywhere near normal traffic.
- **A rule must be green on the status quo.** Run the exact query over the
  current period before arming; if it fires on today's normal, the rule or the
  baseline is wrong — either way, don't arm it. Replay recent history (§2)
  against the new thresholds before arming.
- **Test the query BEFORE the PUT; verify green after.** If a test can't be
  made to pass, skip that rule and report it — never apply unverified.
- **Like units only.** Never build a ratio between two log identifiers before
  verifying every emission site emits at the same granularity
  (`references/loki.md` §3).
- **Flow-step alerts**: check `DISABLED_FLOW_STEPS` first
  (`references/loki.md` §4) — an alert on a disabled step can never fire, and
  has shipped.
- **Cardinality**: `count(sum by(k)(...))` Loki queries hit the ~500-series cap
  hardest *during* incidents — keep alert queries at `[1h]` windows
  (`references/loki.md` §6).

## 5. Dashboards — get → mutate → update

```bash
gcx dashboards get <uid> -o json 2>/dev/null | sed '/^hint:/d' > live.json
# edit panels in python (walk d['spec']['panels'], recurse into rows)
gcx dashboards update <uid> -f live-fixed.json     # falls back: gcx api /api/dashboards/db -d @payload.json
```

Re-`get` before every update (fresh `resourceVersion`). Steal styling from a
sibling panel instead of hand-writing fieldConfig. Panel snapshot rendering
requires the image-renderer plugin (not installed) — verify by re-running the
panel's query instead.

Multi-select SQL variables: never `IN (${var:singlequote})` — a query variable
with zero options interpolates to `IN ()`, a syntax error that breaks every
panel. Use `col REGEXP '${var:regex}'` with `allValue: ".*"` (Loki labels:
`".+"`).
