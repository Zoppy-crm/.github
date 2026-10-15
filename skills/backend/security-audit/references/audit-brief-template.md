# zoppy-api security context — read this before auditing

You are doing a **code-analysis-only** security review of the `zoppy-api` repository (run from its checkout root).
Hard rules:

- **Never** send traffic to any live host, never run exploits, never touch prod. Read code only.
- You MAY run `npm run test -- --testPathPattern=...` on an existing spec if you need to confirm behavior.
- Do **not** modify production code. Do not write files outside your scratchpad path.
- Every finding must cite `file:line` you actually read. **No speculation.** If you cannot point at
  the line, it is not a finding.
- Prefer a short list of confirmed, exploitable findings over a long list of theoretical ones.

## What this codebase is

NestJS 10 multi-tenant CRM / e-commerce integration platform. ~4300 non-spec TS files,
213 HTTP controllers, 150 BullMQ processors, 40+ e-commerce provider integrations.

Layers: `src/access/http` (controllers) → `src/application` (orchestration) → `src/domain`
(entities extending `RepositoryAdapter<T>`) → `src/repository` (Sequelize).

## Tenancy model — the single most important invariant

Every business entity belongs to a `Company` (the tenant). `SessionService` carries the
authenticated request's `companyId`. `RepositoryAdapter<T>` **auto-injects `where: { companyId }`**
into every query.

The tenancy escape hatches — each one is an audit hotspot:

- `skipCompany = true` argument on repository/domain methods
- `@SkipCompanyForAllMethods()` decorator (`src/cross-cutting/decorators/skip-company-for-all-methods.decorator.ts`)
- Any domain method that queries a model directly instead of through the adapter
- Any endpoint that accepts `companyId` from the request body/query instead of the session
- A stale or unset session in a queue processor / cron (`setSession`) — the job then reads or
  writes under the wrong tenant

**A tenant-supplied `companyId` reaching a query is a BOLA finding (OWASP API1), full stop.**

## Auth surfaces (there are six — check them all)

1. **Main API** (port 8080): JWT `Authorization: Bearer`, global `JwtAuthGuard`
   (`src/cross-cutting/guards/jwt-auth.guard.ts`), passport-jwt with `JWT_SECRET`.
2. **Partners API** (port 8082): separate Nest module, `PartnersExternalAuthMiddleware` +
   `ExternalToken` rows in DB.
3. **Service-to-service HMAC**: `hmac-auth.middleware.ts` (strict/non-strict variants) and
   `tenantless-hmac-auth.middleware.ts`, validating against `ZOPPY_HMAC_SECRET`.
4. **WebSocket**: `chat.gateway.ts`, JWT from a connection header.
5. **Public access tokens**: `public-access-token.middleware.ts`, `zoppy-access-key.guard.ts`.
6. **Newer surfaces added since the May 2026 audit** — treat as unaudited greenfield:
   `wpp-commerce-agent.guard.ts`, `partner-access.guard.ts` / `@PartnerAccessible()`,
   `mcp-exception.filter.ts` and the MCP tooling (`UserMcpTokens`),
   `giftcards-auth.middleware.ts`, `dynamic-cors.middleware.ts`,
   `tech-provider-whatsapp-cloud-api.middleware.ts`, `cookie-token-transformer.middleware.ts`.

## Roles

- `RoleEnum.MASTER` — tenant owner. **In practice only Zoppy employees and internal service flows
  hold MASTER, not customers.** So "MASTER can do X" is usually *not* a finding on its own;
  "a customer-role user can reach a MASTER path" *is*.
- `GlobalRole` (MANAGER/MEMBER/…) — platform-wide privilege, Zoppy staff.
- Customer-facing tenant roles: ADMIN, MANAGER, COMMON.

Calibrate severity to that threat model. The real adversaries are: a malicious/compromised
**customer tenant**, an **unauthenticated internet attacker**, and a **provider/webhook caller**
posting attacker-controlled data.

## Decorators that matter

- `@IsPublic()` (`is-public.decorator.ts`) — skips `JwtAuthGuard`. It does **not** skip middlewares.
  Every `@IsPublic()` on a destructive or paid operation is worth a look.
- `@RateLimit({ key, limitPerWindow, windowInSeconds, perCompany? })` — Redis counter.
  **Default scope is GLOBAL** (all tenants share one counter) unless `perCompany: true`.
  A global limiter on a per-tenant paid action is both a DoS lever and an abuse hole.
- `@MaxFileSize()`, `@RequireFeatures()`, `@Roles()`, `@GlobalRoles()`, `@Plans()`, `@Audit()`.

## The money-burning threat class (this is what triggered the first audit)

An ~R$80,000 incident on a `test-messages` endpoint: a paid outbound operation reachable without
sufficient guardrails. Treat any endpoint that **spends money or sends messages** as high-priority:
WhatsApp/SMS/email sends, campaign fan-out, LLM/GPT calls, file uploads that fan out to paid sends.
Ask: who can reach it, how large can one call be, how many calls per minute, and is the limiter
per-tenant?

## Known-fixed as of 2026-05-22 — do NOT re-report unless you find a regression

- `jwtService.decode()` → `verifyAsync()` everywhere (one intentional legacy exception:
  `extractCompanyIdFromLegacyJwt`). JWT algorithm pinning added.
- HMAC compare uses `timingSafeEqual`. `MASTER_PASSWORD` compare too.
- `ExceptionInterceptor` log-body redaction.
- `helmet` middleware added.
- Cepaberto token moved to `CEPABERTO_TOKEN` env var.
- `.env.example` real secrets swapped for placeholders (values still need rotation — separate
  workstream, not a code finding).

**If you find any of these reverted, that is a P0 regression — report it loudly.**

## Still-open findings from the May 2026 audit — VERIFY current state, don't assume

For each, confirm against today's code whether it is still true, partially fixed, or fixed.
Report the current state with a `file:line`.

P0-2 `@IsPublic()` destructive endpoints accepting tenant-supplied companyId ·
P0-3 user endpoints returning the raw `User` model (password hash leak) ·
P0-4 Partners API `ValidationPipe` whitelist disabled (mass assignment) ·
P0-5 `UserDomain.findByEmail` strips tenant scope ·
P0-6 reflective SSRF in the webhook-definition test endpoint ·
P0-7 CORS `origin: '*'` (note: `dynamic-cors.middleware.ts` now exists — check what it actually does) ·
P1-1 public registration/lead endpoints with no abuse controls ·
P1-2 password-reset send unauthenticated and unlimited ·
P1-3 `POST /campaign/file*` 50MB CSV → paid send ·
P1-4 `POST /campaign/ia/*` paid LLM, no rate limit ·
P1-5 `POST /upload-data/**/inference` 80MB → GPT ·
P1-6 `@RateLimit` default scope global, not per-tenant ·
P2-3 no server-side refresh-token validation / cannot revoke ·
P2-4 50-year MASTER JWT expiry ·
P2-5 login rate-limiter keyed per-email only ·
P2-6 `loginMaster` missing `registerLoginAction` audit log ·
P2-7 `MigrateController` / `E2ETestsController` reachable in production ·
P2-8 `InternalServerErrorExceptionFilter` echoes the raw exception message ·
P2-10 WhatsApp media download forwards the bearer token to a provider-supplied URL ·
P2-11 SSRF via tenant-configured provider base URLs ·
P3-2 password reset enumerates users, tokens not single-use ·
P3-3 Partners `ExternalToken.hash` stores the raw JWT ·
P3-4 Shopify `shop` validator uses `String.includes` ·
P3-5 default-cred bypass on Swagger / Bull dashboard basic-auth ·
P3-7 Redis prod TLS `rejectUnauthorized: false` ·
P3-9 Meta WhatsApp inbound webhook lacks signature verification ·
P3-10 `cookieParser()` configured without a secret, cookie flags unverified ·
P3-13 no MFA on any auth path (note: a 2FA epic shipped since — check what landed).

## Severity model to use

- **P0 — active exploit path.** End-to-end exploitable today by a remote attacker. Data or money at risk.
- **P1 — money-burning.** Paid or destructive operation reachable without sufficient guardrails.
- **P2 — latent.** One leak, misconfig, or chained bug away from active exploitation.
- **P3 — hardening.** Defense-in-depth, cheap to fix, low individual impact.

## Output format

Return JSON only, matching the schema you were given. For each finding:
`id`, `title`, `severity` (P0/P1/P2/P3), `owaspCategory`, `status`
(`new` | `still-open` | `partially-fixed` | `fixed` | `regression`), `priorFindingId` (or null),
`evidence` (array of `file:line` with a one-line quote of what the line does),
`attackPath` (concrete: who, what request, what they get), `recommendedFix`, `confidence`
(`high` | `medium` | `low`).
