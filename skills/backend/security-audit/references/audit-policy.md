# Audit policy — threat, evidence, and severity

Read this before rating or deduplicating findings.

## Safety boundary

- Static analysis and read-only enumeration only. Never exploit a live host, access production
  records, assume a vulnerable role, or retrieve a secret value.
- Unit/integration tests against controlled local test infrastructure are the strongest allowed
  reproduction unless Gabriel separately authorizes more.
- Historical evidence is context. Mutable code, AWS, Grafana, database, issue, PR, deployment, and
  traffic claims require a fresh check.
- Grafana datasources can reach production with write capability; the Redis datasource is the
  production ElastiCache cluster. Send only read-only, O(1) commands through them and never write
  back into an observed datastore through Grafana.

## Evidence continuity and access loss

An authentication session is transport, not an evidence lifetime. A captured observation with its
cutoff and `observedAt` never expires merely because the authentication session does.

If access disappears, it quarantines only unfinished checks that require that access:

- preserve every completed observation and partial slice;
- record the exact remaining check and affected scope in `coverageGaps`;
- continue every independent slice, reconciliation step, and report task;
- resume only the unfinished enumeration after reauthentication—never restart completed work.

For a prior open finding that cannot be rechecked, carry the prior finding forward at its prior
severity with `evidenceState: unknown` and state that remediation is unverified. This prevents an
access failure from manufacturing an improvement. New risk that has never been observed remains a
coverage gap and contributes no invented points. The report distinguishes verified-current
findings, unverified carry-forwards, and uncovered scope; access loss alone never halts unrelated
work or invalidates the whole KPI.

Quarantine is a pause, not an outcome. Verify every credential before dispatching slices and have
slices fail loudly on authentication errors. When access expires mid-run, ask Gabriel to
re-authenticate and finish every check that waited on it before rendering. A carry-forward is for
access that cannot be restored during the run; a report whose findings stay unverified only because
a session expired is incomplete. Before calling the audit done, scan the bundle for `unknown`
carry-forwards and close each one or name why it cannot be closed.

## Evidence states

Every material claim is exactly one of:

| State | Meaning |
|---|---|
| `confirmed` | Current primary evidence directly proves the claim. |
| `inferred` | Evidence supports the claim but one named link remains unverified. |
| `refuted` | Current primary evidence disproves it. Remove it from the open score. |
| `unknown` | Access or evidence is insufficient. Do not rate the unverified upside. |

Code evidence uses current `repo@commit:file:line`. Live infrastructure evidence uses account,
region, resource ARN/name, safe command, observation timestamp, and selected output. A cloud
finding does not need a source-code line when the defect exists only in live configuration.

## Threat model

Prioritize:

1. A malicious or compromised customer tenant.
2. An unauthenticated internet caller.
3. A provider/webhook caller with attacker-controlled input.
4. A compromised staff, partner, VPC, AWS, database, or container identity — explicitly lower
   probability because that foothold is already a prerequisite.

`RoleEnum.MASTER` is tenant-scoped. `GlobalRole` is platform-wide. Never infer who can hold a role
from its name: verify guards, token issuance, live user population, and actual callers.

## Business profile before severity

For each service, ingest the previous report's profile, then revalidate drift:

- customer/tenant count and affected denominator;
- whether the service is essential to customer or business continuity;
- current internet/VPC/internal reachability and authentication boundary;
- containment and recovery shape.

Do not ask Gabriel to repeat a stable answer already in the baseline. Ask only about missing or changed
facts. An unverified business profile caps confidence and may cap severity.

Liveness and usage questions (is this route still called, is this feature retired?) are audit work,
not questions for Gabriel. Answer them from Loki, Grafana databases, CloudWatch through Grafana,
Athena ALB logs, git history, and n8n. When a claim depends on data a read-only query can reach,
run the query before reporting the claim. Ask Gabriel only for product rulings.

## Official KPI severity

Weights are immutable for a report series: **Baixa 1 · Média 2 · Alta 4 · Crítica 8 ·
Catastrófica 16**.

| Severity | Decision rule |
|---|---|
| Catastrófica | Plausible extreme systemic loss: broad platform/customer compromise, mass sensitive-data exposure, large fraud, generalized integrity loss, prolonged essential outage, or business-continuity threat. |
| Crítica | Severe compromise, administrative access, auth bypass, material sensitive-data exposure, fraud, or grave outage; strengthened by unauthenticated internet reach. |
| Alta | Relevant exploit probability and significant but containable/recoverable impact. |
| Média | Requires specific authentication, privilege, foothold, interaction, or chaining; restricted and recoverable impact. |
| Baixa | Unlikely and localized, reversible impact. Still tracked and scored. |

### Preconditions and ceilings

| Precondition | Default ceiling |
|---|---|
| none / tenant-auth | none |
| staff-auth / partner-cred | Crítica |
| vpc / container / task-role / db-access / aws-creds / insider | Média |
| dead-code or no live data/caller | Baixa |

Detection gaps have `precondition = n/a — detection gap`: no durable audit record is Alta by
amplification; secondary detection is Média; one constrained missing audit event is Baixa.

Every finding records `riskClass` (`desvio-corrigível` or `risco-residual`) and
`marginalReduction` (`alta`, `média`, `baixa`, `nenhuma`). A fix that does not materially reduce
probability cannot carry a high recommendation solely because its hypothetical impact is large.

`recommendedFix` is the smallest change that reduces probability, at the industry default. Extra
policy (expiry, quotas, additional validation, stricter permissions, UX fallbacks, confirmation
steps) is a new requirement: name it as an option for the owner, never as part of the fix.

## False-positive shields learned from confirmed failures

- Repository Domains and `SessionService` scope tenants by default. Cross-tenant findings require a
  positive escape: skip flag, raw model static, all-company method, caller tenant override, or
  stale/missing session.
- Read every guard/assert/validate failure branch. A named check is not evidence it denies.
- Before saying a table/route/symbol is absent, search its schema/code neighbourhood, singular and
  plural, and Zoppy prefixes (`Wc`, `Wpp`, `Erp`, `Pdv`, `Oauth`). Refutation requires stronger
  evidence than confirmation.
- Declared dependency is not runtime use. Trace imports and deployed consumer versions.
- A failing control in the safe direction is an outage, not automatically a vulnerability. Ask
  who the attacker is and what they gain.
- Missing service-local auth is judged only after current CDK/Terraform/ALB/NLB/SG reachability.
  Network prefix lists restrict source IP; they do not authenticate a caller.
- Task-role/container compromise is a VPC-class foothold. Splitting permissions used by the same
  process is theatre; splitting independent consumers is real risk reduction.
- S3 object ARN (`bucket/*`) enables object actions but not `ListBucket`, which requires the bucket
  ARN. State exact effective actions; never turn `IsPublic=true` into anonymous enumeration.
- Interfaces extending model types strip nothing at runtime. Verify actual serialization.
- `@Roles()` is metadata unless the enforcing guard is present.
- Positional repository booleans are invisible tenancy escapes; inspect every multi-argument call.
- Search for absent controls (`ArrayMaxSize`, captcha, nonce/replay cache, egress allowlist), not
  only suspicious code.
- Before closing a logging finding, trace ingress middleware and exception interceptors as well
  as the application log. A sanitized downstream log does not remove an earlier raw-body or URL
  token log. Reopen a false historical closure as a report correction, with same-cutoff source proof.
- Search spelling variants before refuting a code generator; `generateCupomCode` is a live coupon
  helper. Non-cryptographic randomness alone does not prove a redemption bypass: inspect provider
  restrictions and the actual consumer before assigning severity.
- Dead injection-shaped code is a deletion candidate, not an exploitable finding.
- Preserve distinctions: missing findings vs unfinished metadata, current evidence vs historical
  state, and deployment vs merged code.
- Before closing a deployed finding, account for every active revision selected by host, header,
  cookie or path, including canaries. A pipeline's infrastructure commit is not its application
  commit: link the application SHA to the built image, running digest and routed target.
- Prove a deployment from the running ECS task definition's image (`aws ecs describe-services` →
  task definition → image tag or digest → commit), never from a green CI run or a merged PR. Deploy
  paths change: check which one is live for each repository before judging deploy status.
- A slice's claim is a lead until checked. Give every claim a light first-hand check before
  relaying it.

## Edge and public-dashboard evidence

- For Cloudflare, inspect the active modern ruleset phases, rule order, match fields, skip actions
  and proxied hostname coverage. The legacy WAF flag and Security Center recommendations are not
  current control inventories. Recheck widgets and configurations behind each recommendation.
- Rate a broad edge exception for the protection it demonstrably skips. A skipped phase with no
  active rules does not prove a working rate limit was bypassed. Preserve earlier terminating rules,
  application controls and DDoS protections in the impact statement.
- Public Grafana panels must minimize the saved query result, not only the displayed fields. Inspect
  enabled sharing, query projections and the deployed version's response handling without querying
  production rows or retrieving share tokens. Unknown matching rows remain an explicit limit.
