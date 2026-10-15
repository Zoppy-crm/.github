# Database & queue incidents (RDS Aurora + BullMQ)

## A. RDS Performance Insights (`aws pi get-resource-metrics`)

PI is keyed by `DbiResourceId`, not instance name:

```bash
aws rds describe-db-instances --profile zoppy-prd \
  --query 'DBInstances[?starts_with(DBInstanceIdentifier,`zoppy-production`)].{Id:DBInstanceIdentifier,Res:DbiResourceId,PI:PerformanceInsightsEnabled,Class:DBInstanceClass}'
```

**The triage triple** — run all three before theorizing:

```bash
# 1. What kind of overload? (load by wait event)
aws pi get-resource-metrics --profile zoppy-prd --service-type RDS --identifier "$RES" \
  --start-time "$START" --end-time "$END" --period-in-seconds 3600 \
  --metric-queries '[{"Metric":"db.load.avg","GroupBy":{"Group":"db.wait_event","Limit":10}}]' \
  --query 'MetricList[].{Wait:Key.Dimensions."db.wait_event.name",Load:DataPoints[0].Value}' --output table
# 2. Which statements? (GroupBy db.sql_tokenized, --output json — statements overflow tables)
# 3. Whose load? (GroupBy db.user, then db.host — app attribution; one box vs fleet)
```

JMESPath details that bite: `MetricList[?Key.Dimensions]` drops the aggregate row
when grouping; DataPoints are unordered — `sort_by(@,&Timestamp)`; `[-1]` = now.
Normalize AAS against `os.general.numVCPUs.avg`.

**Wait-event cheat sheet**: `wait/io/table/sql/handler` = rows-examined cost at
the handler layer — accrues even from buffer-pool reads. It means missing/wrong
indexes or scans, never "buy IOPS".

**Onset pinning**: total `db.load.avg` at `--period-in-seconds 300` over the
suspect window. Prod containers run `TZ=America/Sao_Paulo` — cron names like
`EVERY_DAY_AT_5AM` mean 05:00 BRT = 08:00 UTC.

**The unprecedented-onset check** (skipping this nearly sank a real incident):
7 days hourly, grep the same hours (`grep -E 'T0[4-8]:'`). Every prior morning
quiet → first-run-after-deploy; noisy every day → chronic, the deploy is a
coincidence.

**Time-travel comparison**: the same top-SQL query at a mid-storm window vs now —
PI retains the data; answers "did this wave exist during the storm or only after
the mitigation?"

**Intervention verification**: after pausing/throttling, poll 5-min AAS and the
queue gauges and classify the *trajectory* — crater then decay = backlog
draining; crater then climb = new steady load, you fixed nothing. "It dropped"
is not "it's fixed".

## B. BullMQ ground truth (Prometheus via gcx)

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
- Queue depth sickens **before** the DB looks sick — check backlog onset against
  the DB-load onset to order cause and effect.

## C. Naming the culprit — git + deploy correlation

```bash
git fetch origin   # ALWAYS — stale local master has produced a wrong narrative
git log origin/master --first-parent --format='%h | committed:%ci | %s' --since=<window>
git log origin/master -S '<HotSymbol>'                 # did the deploy touch this path?
git log origin/master --diff-filter=A -- '*<thing>*'   # is it brand new?
git diff <merge>^1 <merge> --name-status               # merge-parent archaeology
git show '<merge>^1:<path>'                            # read the old file
git grep -n "<pattern>" <merge>^1 -- 'src/*.ts'        # enumerate call sites AS THEY WERE
```

Committer date (`%ci`) = when it landed; landing ≠ deployed — the deploy merge PR
timestamps are the real event. For dependency bumps: exact version from
`package-lock.json`, then `git diff <oldTag> <newTag> -- src` in the library repo
(fetch it first; local clones go stale). Ruling *out* (RFM unchanged → backlog,
not regression) is as valuable as ruling in.

**Attribution honesty**: PI's tokenized SQL → code attribution can silently hit a
sibling call-site. A shape mismatch (`IN (...)` vs single id) disqualifies the
match — don't rationalize it. When your own output lists a second candidate
(another queue, another helper), address it before concluding.

Index existence: prefer live `information_schema.STATISTICS` via the SQL proxy
(grafana-toolbox §5); repo migrations are a drift-prone proxy.
