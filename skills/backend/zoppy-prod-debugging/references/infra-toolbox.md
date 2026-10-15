# Infra toolbox (SSM, ALB, ECS, packages)

Observability EC2s (SSM, no SSH): dev `i-0ff0bec1876512e18` (zoppy-dev), prod
`i-03918c5a158642551` (zoppy-prd).

## 1. SSM remote shell — the base64 envelope

No SSH anywhere; the observability EC2s and anything host-level go through SSM.
Inline JSON `commands` strings die on quoting for anything non-trivial; the
envelope kills that permanently. SSM runs `sh` (dash) — `/dev/tcp` and heredocs
break; always invoke explicit `bash`:

```bash
P=(--profile zoppy-prd --region us-east-1)         # bash ARRAY — a plain string fails auth
read -r -d '' REMOTE <<'R'
# arbitrary multi-line script, quotes, heredocs, $vars all safe here
docker logs zoppy_pyroscope --since 20m 2>&1 | grep -iE "error|refused" | tail -8
R
B64=$(printf '%s' "$REMOTE" | base64 -w0)
CID=$(aws ssm send-command "${P[@]}" --instance-ids "$IID" --document-name AWS-RunShellScript \
  --parameters "{\"commands\":[\"echo $B64 | base64 -d | sudo bash\"]}" \
  --query 'Command.CommandId' --output text)
aws ssm wait command-executed "${P[@]}" --command-id "$CID" --instance-id "$IID" || true
aws ssm get-command-invocation "${P[@]}" --command-id "$CID" --instance-id "$IID" \
  --query '{st:Status,out:StandardOutputContent,err:StandardErrorContent}'
```

Fetch `Status` **and** `StandardErrorContent`; `wait` returns non-zero on script
failure (hence `|| true`). Secrets: read on-box, use on-box, never echo back
through SSM output. Mutations: backup → guard-grep → edit → **`docker compose
config` gate** → up. Prod-invasive captures (tcpdump, redis MONITOR) require
explicit user sign-off first.

## 2. ALB target unhealthy — the known-good-twin diff ladder

Diff the broken port against a healthy sibling TG on the same instance at every
rung; stop at the rung where they differ.

1. TG config twin-diff: `aws elbv2 describe-target-groups --names <tg> --query
   'TargetGroups[0].{Port:Port,HCPort:HealthCheckPort,HCPath:HealthCheckPath,Matcher:Matcher.HttpCode,TargetType:TargetType}'`
2. Instance SG inbound for the port.
3. Host: `ss -tlnp | grep ':<port>'`, ufw/iptables/nft (via SSM).
4. Subnet NACL entries.
5. **tcpdump for health-check SYNs** (via SSM, ≤35s, with sign-off):
   `sudo timeout 35 tcpdump -ni any -c 300 'tcp port <bad> or tcp port <good>'` —
   zero SYNs on the bad port = the ALB never sends the probe → problem is
   ALB-side, stop debugging the host.
6. **ALB security-group EGRESS** — the routinely forgotten ending. Prod VPC is
   `192.168.0.0/16`, dev is `10.0.0.0/16` — copying the dev CIDR fails silently.
7. Converge-poll `describe-target-health` every 25s; then curl end-to-end from
   inside the VPC via SSM (`getent hosts` for the R53 alias check).

## 3. "Did my change actually reach prod?" — three-source verification

1. **CloudWatch logs** for the new code's init line:
   `aws logs filter-log-events --log-group-name /ecs/<task> --start-time <ms>
   --filter-pattern '?Pyroscope ?pyroscope ?PYROSCOPE'` — `?term` filters are
   case-sensitive; include casings. Pair with a **positive control** filter for a
   line the app definitely logs at boot, so absence is real.
2. **Staleness math**: `ecs describe-tasks → tasks[0].startedAt` vs
   `ecr describe-images → imagePushedAt`. Task started before image pushed =
   running container is stale even though `:latest` is new.
3. **Backend proof of life**: query the ingest store for the last 10 minutes
   (e.g. Loki count for the new log line). Dashboards lie; recent ingest
   doesn't.

No-AWS-access variant: diff the ECS task IDs embedded in log lines across two
time windows, then watch the error-count buckets go to zero.

Deploy-adjacent idioms: `git merge-base --is-ancestor` (GitHub's
`mergeable=CONFLICTING` caches stale); `npm view <pkg>@<ver> version dist-tags
--registry=https://npm.pkg.github.com`; lockfile truth via
`packages["node_modules/<pkg>"].version`; after a local publish, grep the fix
inside `node_modules/<pkg>/dist/` and `npm ls <pkg>` to prove single-copy dedupe.

## 4. Package archaeology — `npm pack` + dist grep

Verify an SDK's actual runtime behavior from its shipped JS before betting a
design (or a diagnosis) on it:

```bash
npm pack <pkg>@<ver> --silent && tar -xzf <pkg>-<ver>.tgz
grep -rn "wrapWithLabels\|AsyncLocalStorage\|async_hooks" package/dist/
```

The decisive evidence is often the grep that comes back **empty** (e.g. no
AsyncLocalStorage → labels die at the first await). Same trick against installed
`node_modules/**/dist` — that's what prod actually runs, not the repo's src. For
SDK request shapes, grep the `dist-types` of the AWS SDK for the exact field
names before writing the fix.
