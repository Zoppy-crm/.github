# AWS CLI forensics (read-only)

Every command takes `--profile zoppy-prd --region us-east-1` (dev: `zoppy-dev`).
Stick to `describe-*`/`get-*`/`list-*`/`lookup-*` — prod is read-only until
diagnosed (doctrine 5).

## 1. ECS capacity — what is actually running

```bash
aws ecs list-clusters
aws ecs list-services --cluster <cluster>
aws ecs describe-services --cluster <cluster> --services <svc> \
  --query 'services[0].{desired:desiredCount,running:runningCount,events:events[:10],deployments:deployments}'
aws ecs describe-task-definition --task-definition <family> \
  --query 'taskDefinition.{cpu:cpu,memory:memory,arch:runtimePlatform}'
```

`events` shows recent scaling actions in plain text. `desiredCount` at the
moment of the incident matters more than now — get history from CloudTrail (§4).

## 2. Autoscaling truth — the three describes

```bash
aws application-autoscaling describe-scalable-targets  --service-namespace ecs
aws application-autoscaling describe-scaling-policies  --service-namespace ecs
aws application-autoscaling describe-scheduled-actions --service-namespace ecs
```

All three empty for a service = it has **no autoscaling at all** — any apparent
schedule comes from somewhere else (§3). Known posture (2026-08): main API
min 3 / max 12, giftcards min 4 / max 8, **partners: nothing**, despite
absorbing the Meta webhook volume. Reactive scaling is also slower than the
traffic it chases: task start + 3×30s health checks vs a 10–15× ramp in 3–4
minutes — a policy can be correct and still arrive after the burst.

## 3. The `zoppy-worker-time-scaler` Lambda — standing trap

A custom Lambda ("Escala os workers ECS do Zoppy baseado em horário", repo
`zoppy-worker-autoscaling`) calls `UpdateService` with hardcoded
`desiredCount` values on a schedule — observed: 2 at 10:00 UTC and 1 at
00:00 UTC, every day. Its service list is **hardcoded in the handler**
(`scale-workers.handler`), not in env vars (`Environment.Variables` is null).
Two consequences:

- It explains "why was this service on one task at 02:00" anomalies — the worst
  error *rates* can land on the smallest traffic waves because capacity was
  scheduled down.
- If a service gains Application Auto Scaling without being removed from the
  Lambda's list, **the two fight**: the Lambda undoes the autoscaling floor at
  its next run. Any scaling change must check this Lambda's list first.

## 4. CloudTrail — who scaled/changed what, when

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=UpdateService \
  --start-time 2026-08-06T00:00:00Z --end-time 2026-08-11T23:59:59Z \
  --max-results 50 --query 'Events[].{t:EventTime,user:Username}'
# or by resource:
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=<service-name>
```

90 days of history. This is how the worker-time-scaler behavior was proven
(daily `desiredCount` writes at 10:00:35 and 00:00:48 UTC) — a schedule claim
without CloudTrail evidence is *inferred*, not *observed*.

## 5. ELB attributes + CloudWatch alarms

```bash
aws elbv2 describe-load-balancer-attributes --load-balancer-arn <arn>   # idle timeout
aws elbv2 describe-target-group-attributes  --target-group-arn <arn>    # deregistration delay, slow start
aws cloudwatch describe-alarms --query 'MetricAlarms[].{name:AlarmName,metric:MetricName,thr:Threshold,per:Period,evals:EvaluationPeriods,state:StateValue}'
aws cloudwatch get-metric-statistics --namespace AWS/ECS ... --period 60 --statistics Maximum
```

Read alarm **periods**, not just thresholds: an avg-over-5-min alarm masks a
3-minute spike entirely — "no alarm fired" is not "no saturation". When
checking a burst, pull the metric at `--period 60` with `Maximum`, not the
default averages.

## 6. RDS Performance Insights (`aws pi get-resource-metrics`)

PI is keyed by `DbiResourceId`, not instance name:

```bash
aws rds describe-db-instances \
  --query 'DBInstances[?starts_with(DBInstanceIdentifier,`zoppy-production`)].{Id:DBInstanceIdentifier,Res:DbiResourceId,PI:PerformanceInsightsEnabled,Class:DBInstanceClass}'
```

**The triage triple** — run all three before theorizing:

```bash
# 1. What kind of overload? (load by wait event)
aws pi get-resource-metrics --service-type RDS --identifier "$RES" \
  --start-time "$START" --end-time "$END" --period-in-seconds 3600 \
  --metric-queries '[{"Metric":"db.load.avg","GroupBy":{"Group":"db.wait_event","Limit":10}}]' \
  --query 'MetricList[].{Wait:Key.Dimensions."db.wait_event.name",Load:DataPoints[0].Value}' --output table
# 2. Which statements? (GroupBy db.sql_tokenized, --output json — statements overflow tables)
# 3. Whose load? (GroupBy db.user, then db.host — app attribution; one box vs fleet)
```

JMESPath details that bite: `MetricList[?Key.Dimensions]` drops the aggregate row
when grouping; DataPoints are unordered — `sort_by(@,&Timestamp)`; `[-1]` = now.
Normalize AAS against `os.general.numVCPUs.avg`.

**Reader hotspots**: the cluster's *readers* can sit above 90% CPU with no alarm
and no writer symptom — observed: `zoppy-production-reader-new-4` crossed 90%
CPU 153 times in 72h, surfacing only as MySQL execution errors in Grafana alert
queries. Before blaming query shape, pull per-instance `CPUUtilization`
(CloudWatch, `AWS/RDS`, dimension `DBInstanceIdentifier`) for **each** reader.

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
