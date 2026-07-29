---
name: security-audit
description: >
    Full security and privacy audit of the Zoppy platform — application code against the OWASP API
    Security Top 10, AWS infrastructure against CIS benchmarks, and a GDPR/LGPD data-protection
    review — producing a scored, trended report in Markdown and local HTML. Use whenever the user
    asks for a pentest, security audit, security review, vulnerability scan, OWASP review, cloud
    or AWS security scan, GDPR/LGPD review, privacy audit, or asks "is this endpoint safe", "can a
    tenant see another tenant's data", "can someone abuse this to burn money", "are we compliant",
    "auditoria de segurança", "fazer um pentest", "revisão de segurança", "isso vaza dados?".
    Also use before shipping any new auth surface, public endpoint, webhook receiver, or paid
    outbound operation. READ-ONLY throughout: it reads code and enumerates cloud resources, and
    never attacks a live host or mutates any resource.
---

# Zoppy Security & Privacy Audit

## Before you start — access checklist

**Ask the user for these in your first message, before scanning anything.** A run without them is
a partial run and must say so in its own scope section. Never silently produce a code-only report
when the user asked for an audit.

1. **AWS profiles** — `zoppy-prd`, `zoppy-dev`, `zoppy-main`. Verify each with
   `aws sts get-caller-identity --profile <p>` before starting. If one fails, say so and ask; do
   not proceed and quietly omit that account.
2. **Repo scope** — the default, `zoppy-api` alone, is a *small fraction* of the platform. Build
   the live-service inventory first (see the AWS section) and confirm scope explicitly.
3. **GitHub access** — `gh auth status`, for the repo inventory and for filing cards.

State the confirmed scope in the report's opening section. An audit that overstates its coverage
is worse than one that admits a gap.

---

## Deliverables — always both formats

In `docs/security/`, every run produces:

1. `owasp-audit-<YYYY-MM-DD>.md` — canonical report.
2. `owasp-audit-<YYYY-MM-DD>.html` — **self-contained** local HTML (inline CSS/JS, no CDN, no
   external assets) with score, per-area breakdown, ROI queue, filterable findings. Generator:
   `references/gen_html.py`, which takes a bundle JSON and emits the page.
3. `owasp-audit-<YYYY-MM-DD>-by-actionability.md` — the shipping-order cut.

Local files only — never claude.ai artifacts. And `docs/` is gitignored and periodically wiped, so
**replicate the report into a GitHub card or it is lost**; the May 2026 report survived only
because it was copied into #7284's comments.

---

## Trend — every run re-grades the previous one

The point of scoring is trajectory, not the number. Each run must:

1. **Retro-date its findings** against the previous audit's commit: `git log -S'<distinctive code
   string>' --oneline` to find the introducing commit, then
   `git merge-base --is-ancestor <commit> <prior-audit-commit>` (exit 0 = predates that audit).
2. Classify each as `pre-existing-missed` (**the important bucket**), `introduced-since`,
   `already-reported`, or `undetermined`.
3. **Restate the previous score.** If findings existed then and were missed, publish the
   correction plainly: *"the 2026-05-11 report implied a score of X; the true figure was at least
   Y."* A score that only measures what was noticed is not a measurement.
4. Separate **"we got worse"** (introduced since) from **"we looked harder"** (pre-existing, newly
   found). Without that split, a better audit reads as a regression and the programme gets
   defunded.

Ambiguous ancestry is `undetermined`, never inflated.

---

## Role

You are auditing the Zoppy platform for security and data-protection defects across three
dimensions — application code, AWS infrastructure, and privacy compliance — all read-only.

**Hard boundaries — these are not negotiable:**

-   **Code analysis only.** Never send traffic to a live host, never run an exploit, never touch
    production data. The deliverable is a report, not a compromise.
-   The strongest proof you may produce is a **unit/integration test** against the in-memory test DB
    demonstrating the defect (see `testing` skill). Write those only for confirmed P0/P1 findings,
    and only when asked.
-   **Never print a real secret value** you find. Cite `file:line` and describe it.
-   Every finding cites a `file:line` you actually read. If you can't point at the line, it isn't a
    finding — delete it. A short list of confirmed findings beats a long list of theoretical ones.

---

## Zoppy's threat model — calibrate severity to this

The adversaries that matter, in order:

1. **A malicious or compromised customer tenant.** Has a valid JWT for their own company. The
   question is always: can they reach another company's data, or spend Zoppy's money?
2. **An unauthenticated internet attacker.** Hits `@IsPublic()` routes and webhook receivers.
3. **A provider / webhook caller** posting attacker-controlled data (40+ integrations do this).

**`RoleEnum.MASTER` is a Zoppy-staff role, not a customer role.** "A MASTER user can do X" is
usually *not* a finding. "A customer-role user (ADMIN / MANAGER / COMMON) can reach a MASTER path"
*is* a finding. Getting this wrong is the #1 source of false positives in this codebase.

### The money-burning class is the priority

The audit programme exists because of an **~R$80,000 incident on a `test-messages` endpoint** — a
paid outbound operation reachable without sufficient guardrails. Any endpoint that **spends money
or sends messages** (WhatsApp, SMS, email, LLM/GPT calls, campaign fan-out) gets audited first.
For each, answer: *who can reach it, how big can one call be, how many calls per minute, and is
the limiter per-tenant?*

---

## Architecture you need to know

NestJS 10 multi-tenant CRM / e-commerce platform. ~4300 non-spec TS files, 213 HTTP controllers,
150 BullMQ processors, 40+ provider integrations.

`src/access/http` (controllers) → `src/application` (orchestration) → `src/domain` (entities
extending `RepositoryAdapter<T>`) → `src/repository` (Sequelize).

### The tenancy invariant — audit this first

Every business entity belongs to a `Company`. `SessionService` carries the request's `companyId`,
and `RepositoryAdapter<T>` **auto-injects `where: { companyId }`** into every query.

That means tenancy defects appear as **escapes from the adapter**, and there are exactly five shapes:

| Escape shape | What to grep |
| --- | --- |
| Explicit skip flag | `skipCompany` |
| Class-level skip | `@SkipCompanyForAllMethods()` |
| Bypassing the adapter | Sequelize model statics: `Model.findOne(`, `.findAll(`, `.create(`, `.update(` outside a Domain |
| Tenant-supplied tenant id | `companyId` read from `@Body()` / `@Query()` / `@Param()` instead of the session |
| Stale/absent session | a processor or cron missing `setSession(job)`, or a `forAllCompanies` loop passing the caller's full session instead of a companyId-only one |

**A tenant-supplied `companyId` reaching a query is a BOLA finding (API1), full stop.**

### The six auth surfaces — check all of them, not just the JWT one

1. **Main API** (8080) — JWT bearer, global `JwtAuthGuard`, passport-jwt with `JWT_SECRET`.
2. **Partners API** (8082) — `PartnersExternalAuthMiddleware` + `ExternalToken` rows.
3. **Service-to-service HMAC** — `hmac-auth.middleware.ts` (strict/non-strict) and
   `tenantless-hmac-auth.middleware.ts` against `ZOPPY_HMAC_SECRET`.
4. **WebSocket** — `chat.gateway.ts`, JWT from a connection header.
5. **Public access tokens** — `public-access-token.middleware.ts`, `zoppy-access-key.guard.ts`.
6. **Newer surfaces** — `wpp-commerce-agent.guard.ts`, `partner-access.guard.ts` /
   `@PartnerAccessible()`, MCP tooling + `UserMcpTokens`, `giftcards-auth.middleware.ts`,
   `dynamic-cors.middleware.ts`, `tech-provider-whatsapp-cloud-api.middleware.ts`,
   `cookie-token-transformer.middleware.ts`.

Everything lives under `src/cross-cutting/guards/`, `src/cross-cutting/middlewares/`,
`src/cross-cutting/Interceptors/` (note the capital I), and `src/cross-cutting/filters/`.

### Decorators with security semantics

-   **`@IsPublic()`** — skips `JwtAuthGuard`. It does **not** skip middlewares. Every use on a
    destructive or paid operation deserves scrutiny.
-   **`@RateLimit({ key, limitPerWindow, windowInSeconds, perCompany? })`** — Redis counter.
    **Historically the default scope was GLOBAL** (every tenant shares one counter), which is both an
    abuse hole and a cross-tenant DoS lever. Always read the decorator + interceptor to confirm
    today's default before judging a callsite.
-   `@MaxFileSize()`, `@Roles()`, `@GlobalRoles()`, `@RequireFeatures()`, `@Plans()`, `@Audit()`.

---

## Method

Run these as **parallel subagents, one per slice** — the codebase is far too large for one context,
and the slices are genuinely independent. Give each agent the threat model above, the "already
fixed" list, and the output schema below.

| Slice | OWASP | Focus |
| --- | --- | --- |
| **Auth & session** | API2 | The six surfaces, JWT lifecycle, refresh tokens, 2FA, password reset, token storage at rest, HMAC replay |
| **Authorization & tenancy** | API1, API3, API5 | `@IsPublic()` inventory, the five escape shapes, role guards failing open, mass assignment, processor sessions |
| **Resource consumption** | API4, API6 | Every paid/outbound endpoint, upload sizes, fan-out caps, the `@RateLimit` inventory, public business flows |
| **Data exposure & secrets** | API3, API8 | Raw model returns, credential storage, PII in responses/logs, error verbosity, hardcoded secrets, debug surfaces |
| **SSRF & integrations** | API7, API10 | Request-supplied and tenant-configured URLs, cloud-metadata reach, auth headers to attacker hosts, inbound webhook authenticity |
| **Config & inventory** | API8, API9 | Bootstraps, CORS, injection, dependencies, route inventory — **plus the regression check** |

**Always include the regression check.** Past fixes have a habit of coming back. Verify each
previously-closed finding is still closed, with a `file:line`, and report any that reverted as
**P0 / status `regression`**.

Then: dedupe across slices (tenancy findings surface in three of them), verify every P0/P1 claim
yourself by reading the cited lines, and only then write the report.

---

## Classification — use the board's taxonomy, not a security-tool taxonomy

Findings are triaged like every other bug at Zoppy, so they land on the Engineering board
(Project #7) with its native fields already set. Do not invent a parallel severity scheme.

### `Priority` — how bad

| Value | Meaning | Test to apply |
| --- | --- | --- |
| **CATASTRÓFICO** | Platform-wide compromise | Unauthenticated or trivially-authenticated path to mass cross-tenant data access, account takeover at scale, infrastructure credential theft, or unbounded money loss. You wake people up for this. |
| **P0** (critical) | Active exploit path, bounded | Exploitable today, but blast radius stops at one tenant or one privilege boundary. Or: a paid/destructive operation reachable right now with insufficient guardrails. |
| **P1** (high) | Latent | One leak, misconfiguration, or chained bug away from active exploitation. Or abuse that needs a valid login and yields limited gain. |
| **P2** (medium) | Hardening | Defense-in-depth. Low individual impact; shrinks the blast radius of future incidents. |

The line between CATASTRÓFICO and P0 is **blast radius, not cleverness**. A trivial bug that
exposes every tenant outranks an elegant chain that exposes one.

**Do not inflate.** A rating you cannot defend with a traced path and a `file:line` costs the whole
report its credibility. If reachability can't be determined from code alone, rate conservatively and
say why in `confidence`.

### `Size` — how much work

| Value | Shape | Effort points |
| --- | --- | --- |
| **XS** | A few lines. No prerequisite, no coordination. Drop-in. | 1 |
| **S** | Small fix gated by one quick check — grep the callers, one telemetry query, ping one team. | 2 |
| **M** | An audit pass over N callsites, a new small component, or one team to coordinate with. Days. | 5 |
| **L** | Design pass, data migration, or cross-repo rollout. A sprint-ish. | 13 |
| **XL** | Multi-week programme, new subsystem, or forces credential re-issue across external parties. | 34 |

Size is dominated by **the prerequisite audit and the rollout, not the diff**. "Flip the flag" is one
line and `M`, because every DTO has to be checked first. Always record a one-line `sizeRationale`
naming the real driver.

---

## Security score

One number per audit, so posture is comparable across runs and the trend is visible.

**Exposure Score** = Σ weights of all *open* findings. Lower is better.

| Priority | Weight |
| --- | --- |
| CATASTRÓFICO | 100 |
| P0 | 30 |
| P1 | 8 |
| P2 | 2 |

Weights are deliberately order-of-magnitude: a pile of P2 hardening must never numerically offset
one critical.

**Grade** from the Exposure Score — then apply the caps, which override the band:

| Exposure | Grade |
| --- | --- |
| 0 | A+ |
| 1–15 | A |
| 16–40 | B |
| 41–80 | C |
| 81–150 | D |
| > 150 | F |

-   **Any open CATASTRÓFICO → grade is F**, whatever the total.
-   **Any open P0 → grade is capped at C.**

The caps exist because a weighted sum alone is gameable: closing twenty P2s while a critical sits
open would otherwise show as improvement. It isn't.

**Report the score three ways**: total, split by priority, and as a delta against the previous
audit (findings closed, still open, newly found, regressed). The delta is the part leadership
actually acts on.

### Remediation ROI

Rank the fix queue by `weight ÷ effort points`. This is the objective answer to "what do we do
Monday" and it routinely disagrees with a pure severity sort — an XS fix on a P0 (30 ÷ 1 = 30)
outranks an XL fix on a CATASTRÓFICO (100 ÷ 34 = 2.9) for the *first* PR, even though the
catastrophic one matters more. Present both orders and say which is which: highest-ROI first for
sequencing, highest-priority first for accountability.

---

## Finding schema

```json
{
    "id": "F-1",
    "title": "short imperative description of the defect",
    "priority": "CATASTROFICO | P0 | P1 | P2",
    "size": "XS | S | M | L | XL",
    "sizeRationale": "what actually drives the effort",
    "owaspCategory": "API1 | API2 | ...",
    "status": "new | still-open | partially-fixed | fixed | regression",
    "priorFindingId": "P0-5 or null",
    "evidence": [{ "location": "src/…/foo.ts:42", "quote": "what that line does" }],
    "attackPath": "who sends what request and what they get back",
    "recommendedFix": "concrete change",
    "confidence": "high | medium | low"
}
```

**Beware the id collision.** The 2026-05-11 audit used `P0`/`P1`/`P2`/`P3` as *risk tiers* in its
finding ids (`P0-1`, `P2-11`, …). Those are **not** the board's Priority values — old-model `P1`
("money-burning") maps to board `P0` or `CATASTRÓFICO` far more often than to board `P1`. When
citing a prior finding, always say which scheme you mean.

---

## Deliverables

1. **Canonical report** at `docs/security/owasp-audit-<YYYY-MM-DD>.md`. Note `docs/` is gitignored
   and transient — so the report must **also** be replicated into the GitHub tracking card, split
   across comments by tier. Structure the doc as: scope & limitations first, then a one-page
   codebase primer for the reader, then remediation status, then severity model, then an index,
   then a section per finding (root cause, reproduction, fix, verification).
2. **An actionability view** — the same findings re-cut by *how to ship* rather than how bad they
   are: Tier A drop-in, Tier B one-prerequisite-check, Tier C hidden coordination cost, Tier D
   genuinely large. This is what makes the audit actually get remediated; the severity cut alone
   does not.
3. **GitHub cards** via the `flow-github-issues` skill: one roadmap/epic card holding the full
   report, sub-issues per finding or natural group, label `epic: security`, Project v2 Status
   **"To Do"**.

### Prior audits — read before starting

-   `docs/security/owasp-audit-2026-07-29.md` — 73 findings (96 before dedup), exposure score 1780,
    grade F. Nine CATASTRÓFICO. All seven May remediations verified as holding.
-   `docs/security/owasp-audit-2026-07-29-by-actionability.md` — ROI queue and tiers.
-   `docs/security/owasp-audit-2026-05-11.md` — 37 findings; the first full audit.
-   `docs/security/owasp-audit-2026-05-11-by-actionability.md` — the shipping-order cut.
-   GitHub: **#7284** (roadmap, full report in comments), **#7282** (P0 JWT), **#7383** (Tier-A bundle).
    Label `epic: security` lists all remediation cards.

**`docs/` is gitignored and transient.** The report must be replicated into a GitHub card or it will
be lost — the May report survived only because it was copied into #7284's comments.

---

## High-yield greps

Ranked by findings-per-minute in practice. Run these first.

```bash
# Tenant-supplied tenant id — the single highest-yield search in the codebase
grep -rn "companyId" src/access/http/requests/ | grep -v spec
grep -rn "@Param('companyId')\|@Query('companyId')" src/access/http/controllers/

# Tenancy escapes: positional booleans on the adapter
grep -rn "skipCompany\|skipConstraints\|findFromAllCompanies\|SkipCompanyForAllMethods" src/ | grep -v spec

# Public surface inventory (expect ~80; most are inert — check middleware bindings in http.module.ts)
grep -rn "@IsPublic()" src/access/http/controllers/ | wc -l

# Handlers declaring @Roles without the guard that enforces it
grep -rn -B4 "@Roles(" src/access/http/controllers/ | grep -c "UseGuards(RoleGuard"

# Response types that strip nothing at runtime
grep -rn "interface .*Response extends" src/access/http/response/

# Raw model spreads into responses
grep -rn "\.\.\..*\.get()" src/application/ | grep -v spec

# Paid/outbound operations lacking a limiter — cross-reference against @RateLimit callsites
grep -rln "emailSendService\|whatsappSend\|smsSend\|openai\|gpt" src/application/
grep -rn "@RateLimit" src/access/http/controllers/ | wc -l

# Missing controls — an empty result IS the finding
grep -rn "@ArrayMaxSize" src/ | wc -l        # 0 as of 2026-07-29: no array DTO is capped
grep -rni "captcha\|turnstile" src/          # only Meta's own error strings — Zoppy has no anti-automation control

# Coverage ratio: 7 @RateLimit callsites across 213 controllers as of 2026-07-29.
# Do not read a low count as "well targeted" — check it against the paid-endpoint inventory above.

# Injection
grep -rn "sequelize.query\|rawQuery\|literal(" src/ | grep -v spec
grep -rnE '\$\{[a-zA-Z_.]+\}' src/domain/*.ts | grep -i "select\|where\|=\s*'"

# Egress: every outbound call not going through a wrapper
grep -rn "axios\.\|fetch(" src/ | grep -v spec | wc -l
grep -rn "maxRedirects\|maxContentLength" src/    # expect almost none

# Verification-disabled flags
grep -rn "rejectUnauthorized: false\|checkServerIdentity" src/
```

Never re-report something the prior audit already closed unless you have evidence it regressed —
check the "already fixed" list first.

---

## Lessons from prior runs — these are where the real bugs were

Each of these cost a full audit cycle to learn. Apply them before you trust anything.

### Verify what a guard *does*, not that it exists

The single worst finding of the 2026-07-29 audit was missed by a first-pass sweep that saw
`assertMember(user, companyId)` being called and concluded the endpoint was safe. The method's
first line is `if (!this.isPortfolioBound(user)) return;` — it **allows** on early return, and
`isPortfolioBound` is false for every ordinary tenant user. It restricted only staff, and was a
no-op against the customers it needed to stop.

**Open every guard, every `assert*`, every `validate*` in the path and read what it does on the
failure branch.** "A check is called here" is not evidence of anything.

### Re-verify accepted exceptions every single audit

The May 2026 audit recorded `extractCompanyIdFromLegacyJwt` as a sanctioned `jwtService.decode()`
carve-out. The sanction covered the decode call. Nobody checked that its only caller is an
`@IsPublic()` endpoint that mints a permanent cross-tenant credential from the decoded claim.

**An exception granted in a previous audit is an input to this one, not a conclusion.** Re-derive
reachability for every carve-out on the known-fixed list.

### A fix for an outage can install a silent fail-open

`rate-limit.helper.ts` wraps its Redis call in `catch { return; }` — almost certainly the fix for a
real incident where the interceptor crashed every request. It stopped the outage and converted it
into every spend limit in the platform silently disabling itself whenever Redis degrades, with no
log line. **When you find a bare catch on a security control, find the incident that caused it and
ask what the control does now.**

### Positional boolean arguments are invisible tenancy escapes

`skipCompany`, `skipConstraints`, `withTrashed`, `skipHooks` are trailing positional booleans on
`RepositoryAdapter`. At a callsite they look like `findById(id, false, true)` — nothing names them.
Several cross-tenant findings were exactly one `true` in the third position.

**Grep for the adapter methods and read every call with more than one positional argument.**

### `interface XResponse extends XModel` strips nothing

This pattern recurs across the codebase and is the root cause of every credential-leak finding.
It reads like a DTO in code review and is a pure compile-time fiction — the application spreads
`model.get()` and every column ships, including `password`, `secret`, `refreshToken`.

**A response type is only real if it is a class with an explicit field list.**

### `@Roles()` without `@UseGuards(RoleGuard)` is inert metadata

`RoleGuard` is not a global `APP_GUARD` in this project — only `JwtAuthGuard` and
`PartnerAccessGuard` are. A handler that declares `@Roles(MASTER)` but omits the `@UseGuards` line
accepts **any authenticated user**. This has shipped at least twice.

**Never read `@Roles` as enforcement. Confirm the `@UseGuards(RoleGuard)` line on the same handler.**

### `companyId` is not a secret

It is embedded in the `List-Unsubscribe` URL of every marketing email the platform sends, and in
public coupon and giftback URLs. Any finding whose only prerequisite is "the attacker knows a
companyId" should be rated as though that prerequisite is free, because it is.

### Grep for absence, not just presence

`@ArrayMaxSize` appears **zero times** in the repository, which means every array-shaped DTO is
bounded only by the 50MB body limit. That finding is invisible to any search for bad code — you
only see it by asking "where is the control that should be here?" Do the same for captcha
(also zero hits), egress allowlists, and nonce/replay caches.

### Dead code with an injection pattern is a trap, not a bug

Four SQL-injection patterns were found in query builders with zero callers. They are not
exploitable — and the right recommendation is **deletion, not repair**, because the code reads like
a working feature and the next person to wire it up ships the injection unknowingly.

### Check header names against the framework's casing

A Nuvemshop LGPD webhook guard reads `req.headers['HTTP_X_LINKEDSTORE_HMAC_SHA256']`. Express
lowercases every header key, so that lookup is permanently `undefined` and the guard fails closed —
silently rejecting real compliance requests for months. **A control that never fires is a finding
too, and fixing the name alone would have turned it into a live unauthenticated destructive
endpoint.** Ship the name fix and the timing-safe compare together, never separately.

### Correct the prior report when it is wrong

This audit downgraded one prior finding to fixed, corrected one that was mis-framed, and
**escalated one that was recorded as bounded but is actually unbounded** (a "50MB cap" that was
the JSON body-parser limit and never applied to the multipart route in question). Reviewers inherit
the previous report's framing; state corrections loudly.

---

## Scope limitations to state explicitly in every report

This method audits **application code in one repo**. It does not cover, and the report must say so:
other Zoppy repos (FE, event-bridge, workflow, command, whatsapp-commerce) and their cross-repo
trust boundaries; AWS infrastructure (IAM, security groups, ALB/WAF, S3 policies, RDS exposure);
CI/CD secret handling; the database layer (stored procs, triggers, backups); process controls
(offboarding, MFA on vendor consoles, shared credentials); supply chain (`npm audit`, base-image
CVEs); and customer-side practices.

Say plainly that these are **known unknowns, not implicitly safe**.
