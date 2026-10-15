---
name: diagnose-email-dns
description: >
  Diagnose why a Zoppy customer can't verify their email sending domain
  (Amazon SES) — DKIM, custom MAIL FROM, SPF, DMARC records. Use whenever a
  customer reports they can't add the MX/TXT for MAIL FROM, the registrar
  complains about a "duplicate CNAME" / "can't have a TXT with the same name
  as a CNAME", the domain is "stuck on Pending", or emails aren't being
  delivered after a domain change. Pings the customer's live DNS, proves the
  conflict, and produces the fix + a ready-to-send PtBR message for the CSM.
  Triggers: "DNS pendente", "não consigo configurar MX/TXT", "CNAME duplicado",
  "MAIL FROM não verifica", "domínio travado no pendente", "SPF não aceita".
---

# Diagnose email-auth DNS (Amazon SES)

Personal ops skill. Zoppy sends email through **Amazon SES** (region `us-east-1`).
A customer authenticates their domain by publishing four record groups (the
Zoppy email-config screen shows them):

| Group | Type | Name | Value |
|---|---|---|---|
| DKIM ×3 | CNAME | `<token>._domainkey.<domain>` | `<token>.dkim.amazonses.com` |
| MAIL FROM | MX | `<mailfrom-sub>` (default `mail.<domain>`) | `10 feedback-smtp.us-east-1.amazonses.com` |
| MAIL FROM / SPF | TXT | `<mailfrom-sub>` | `"v=spf1 include:amazonses.com ~all"` |
| DMARC | TXT | `_dmarc.<domain>` | `"v=DMARC1; p=none;"` |

## The #1 root cause: CNAME coexistence

DNS forbids a name that owns a **CNAME** from owning **any other record type**
(RFC 1034 §3.6.2 / RFC 2181 §10.1). Zoppy's default MAIL FROM subdomain is
`mail.<domain>` — and that name is very often *already* a CNAME the customer set
up long ago and forgot:

- **`ghs.google.com`** → Google Workspace "custom URL" for branded webmail
  (`mail.<domain>` → Gmail). Confirm with the apex MX pointing to
  `*.aspmx.l.google.com`.
- registrar webmail (KingHost, cPanel, Zimbra) → `webmail.<provider>`.

When the customer then tries to add the SES **MX** and **SPF TXT** on that same
name, the registrar refuses → *"you can't have a TXT with the same name as a
CNAME"* / *"CNAME duplicado"*. Nothing is broken — it's a name collision.

## How to run

```bash
~/.claude/skills/diagnose-email-dns/diagnose-email-dns.sh <domain> [mailfrom-sub] [--dkim t1,t2,t3] [--region r]
# e.g.
~/.claude/skills/diagnose-email-dns/diagnose-email-dns.sh intibrand.com
~/.claude/skills/diagnose-email-dns/diagnose-email-dns.sh intibrand.com envio.intibrand.com
```

It queries the live DNS (via `1.1.1.1`, system-resolver fallback) and reports
per-record PASS/WARN/FAIL: the CNAME conflict, MX, SPF, apex-SPF duplication,
DMARC enforcement, and a list of **free subdomains** to use instead.

Manual cross-check if needed:
```bash
dig +short mail.<domain> CNAME      # if this returns anything → that's the blocker
dig +short <domain> MX              # who runs their real email (Google? etc.)
dig +short <domain> TXT             # apex SPF must be a SINGLE v=spf1 record
```

## The fix (two options)

1. **Recommended — change the MAIL FROM subdomain** to a free name (`envio.`,
   `bounce.`, `news.`). In Zoppy's email-domain-config screen edit the MAIL FROM
   prefix and re-verify (`reverifyDomain(mailFromSubDomain)` → SES
   `setIdentityMailFromDomain`). Then the customer adds the MX + SPF on the new
   subdomain. Leaves their existing `mail.` (Google/webmail) untouched — zero risk.
2. **Delete the conflicting CNAME** — only if `mail.<domain>` is no longer used
   as a webmail shortcut. Then add the SES MX + SPF on `mail.`. Risk: breaks the
   webmail link if anyone uses it.

Always set the 3 DKIM CNAMEs too. If DMARC is `p=quarantine`/`p=reject`, DKIM
**must** be valid or SES mail gets quarantined/rejected.

## Registrar gotchas (look like "duplicate"/broken)

- **Host-only field**: many panels auto-append the zone. Enter `envio`, not
  `envio.<domain>` — else you get `envio.<domain>.<domain>`.
- **MX split fields**: priority `10` and target `feedback-smtp.us-east-1.amazonses.com`
  are usually separate inputs; don't paste the `10` into the host/value.
- **One SPF TXT per name** (RFC 7208). Never add a second `v=spf1` on the same
  name — merge includes into the existing one.

## CSM message template (PtBR)

> Olá! Analisamos o DNS do domínio de vocês e já sabemos por que o MX/TXT do
> envio não estão sendo aceitos.
>
> O subdomínio **`<mailfrom>`** já tem um registro **CNAME** apontando para
> `<destino>` (provavelmente de um serviço configurado há algum tempo e nunca
> mais alterado). Pela regra do DNS, um nome que já tem um CNAME **não pode ter
> nenhum outro tipo de registro** (MX, TXT…). Por isso o painel recusa a criação
> — não é erro de digitação, é um conflito de nomes.
>
> Recomendamos usar outro subdomínio para o envio, por exemplo **`envio.<domain>`**
> (está livre), assim não mexemos no `<mailfrom>` atual. Vocês adicionam:
>
> - **MX** — nome: `envio` · prioridade: `10` · valor: `feedback-smtp.us-east-1.amazonses.com`
> - **TXT** — nome: `envio` · valor: `"v=spf1 include:amazonses.com ~all"`
> - os **3 CNAMEs de DKIM** que aparecem na tela de configuração da Zoppy
>
> Dica: no campo "nome/host" digite só `envio` (sem repetir o domínio) — alguns
> painéis completam o domínio sozinhos e isso gera registros duplicados.

## Notes
- Region is `us-east-1` (`AWS_REGION`); MAIL FROM MX target is region-specific.
- Zoppy's UI shows the 3 DKIM CNAMEs (dynamic) + static MAIL FROM/SPF/DMARC rows.
  Source: `zoppy-fe/.../email-config.service.ts`, `zoppy-email/.../aws.service.ts`.
