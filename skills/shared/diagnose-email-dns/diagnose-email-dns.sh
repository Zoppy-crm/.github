#!/usr/bin/env bash
#
# diagnose-email-dns.sh — Diagnose a customer's Amazon SES email-authentication DNS
# (the records Zoppy asks them to publish: DKIM, custom MAIL FROM / SPF, DMARC).
#
# The #1 support issue: the registrar refuses the MAIL FROM MX/TXT because the
# MAIL FROM name already owns a CNAME. DNS forbids a CNAME from coexisting with
# any other record type (RFC 1034 §3.6.2 / RFC 2181 §10.1). This script proves it.
#
# Usage:
#   ./diagnose-email-dns.sh <domain> [mailfrom-subdomain] [--dkim t1,t2,t3] [--region r]
#
# Examples:
#   ./diagnose-email-dns.sh intibrand.com
#   ./diagnose-email-dns.sh intibrand.com envio.intibrand.com
#   ./diagnose-email-dns.sh vikingbrand.com.br mail.vikingbrand.com.br --dkim abc,def,ghi
#
# Env overrides: SES_REGION (default us-east-1), DNS_RESOLVER (default 1.1.1.1).

set -uo pipefail

DOMAIN="" ; MAILFROM="" ; DKIM_TOKENS="" ; REGION="${SES_REGION:-us-east-1}"
RESOLVER="${DNS_RESOLVER:-1.1.1.1}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dkim)   DKIM_TOKENS="${2:-}"; shift 2 ;;
    --region) REGION="${2:-}"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) if [ -z "$DOMAIN" ]; then DOMAIN="$1"; elif [ -z "$MAILFROM" ]; then MAILFROM="$1"; fi; shift ;;
  esac
done

[ -z "$DOMAIN" ] && { echo "usage: $0 <domain> [mailfrom-subdomain] [--dkim t1,t2,t3] [--region r]"; exit 2; }
[ -z "$MAILFROM" ] && MAILFROM="mail.${DOMAIN}"
command -v dig >/dev/null 2>&1 || { echo "error: 'dig' not found (install dnsutils/bind-tools)"; exit 3; }

SES_MX="feedback-smtp.${REGION}.amazonses.com"
SES_SPF='v=spf1 include:amazonses.com ~all'

if [ -t 1 ]; then R=$'\e[31m'; G=$'\e[32m'; Y=$'\e[33m'; B=$'\e[36m'; D=$'\e[2m'; X=$'\e[0m'; BOLD=$'\e[1m'
else R=""; G=""; Y=""; B=""; D=""; X=""; BOLD=""; fi
FAILS=0; WARNS=0
ok()   { echo "  ${G}✓ PASS${X} $*"; }
bad()  { echo "  ${R}✗ FAIL${X} $*"; FAILS=$((FAILS+1)); }
warn() { echo "  ${Y}! WARN${X} $*"; WARNS=$((WARNS+1)); }
info() { echo "  ${D}· $*${X}"; }

# Query helper: public resolver first, fall back to the system resolver.
q() { # q <name> <type>
  local out
  out=$(dig @"$RESOLVER" +short "$1" "$2" 2>/dev/null)
  [ -z "$out" ] && out=$(dig +short "$1" "$2" 2>/dev/null)
  printf '%s' "$out"
}

echo "${BOLD}${B}━━━ SES email-auth DNS diagnosis ━━━${X}"
echo "  domain        : ${BOLD}$DOMAIN${X}"
echo "  MAIL FROM     : ${BOLD}$MAILFROM${X}"
echo "  SES region    : $REGION   (expected MX target: $SES_MX)"
echo "  resolver      : $RESOLVER (system fallback)"
echo

# ── 1. The critical check: CNAME conflict on the MAIL FROM name ───────────────
echo "${BOLD}1) MAIL FROM CNAME conflict${X}  ${D}(the usual culprit)${X}"
MF_CNAME=$(q "$MAILFROM" CNAME)
if [ -n "$MF_CNAME" ]; then
  bad "$MAILFROM is a CNAME → ${BOLD}${MF_CNAME%.}${X}"
  echo "       A name that owns a CNAME can own NO other record type (RFC 1034/2181)."
  echo "       This is why the registrar refuses the MX and the SPF/TXT here."
  echo "       Fix → either delete this CNAME, or use a MAIL FROM subdomain that is free."
else
  ok "$MAILFROM has no conflicting CNAME — MX/TXT can be added here"
fi
echo

# ── 2. MAIL FROM MX ───────────────────────────────────────────────────────────
echo "${BOLD}2) MAIL FROM MX${X}  ${D}(expected: 10 $SES_MX)${X}"
MF_MX=$(q "$MAILFROM" MX)
if [ -n "$MF_CNAME" ]; then
  warn "cannot evaluate MX — $MAILFROM resolves to the CNAME above, not a real MX"
elif [ -z "$MF_MX" ]; then
  bad "no MX record on $MAILFROM"
elif echo "$MF_MX" | grep -qi "$SES_MX"; then
  ok "MX present → $(echo "$MF_MX" | tr '\n' ' ')"
else
  bad "MX present but wrong target → $(echo "$MF_MX" | tr '\n' ' ')"
  echo "       expected: 10 $SES_MX"
fi
echo

# ── 3. MAIL FROM SPF (TXT) ──────────────────────────────────────────────────────
echo "${BOLD}3) MAIL FROM SPF / TXT${X}  ${D}(expected: \"$SES_SPF\")${X}"
MF_TXT=$(q "$MAILFROM" TXT | tr -d '"')
MF_SPF=$(echo "$MF_TXT" | grep -i '^v=spf1' || true)
if [ -z "$MF_SPF" ]; then
  [ -n "$MF_CNAME" ] && warn "no SPF TXT (blocked by the CNAME above)" || bad "no SPF TXT on $MAILFROM"
elif echo "$MF_SPF" | grep -qi 'include:amazonses.com'; then
  ok "SPF present and includes amazonses.com → \"$MF_SPF\""
else
  bad "SPF present but missing amazonses.com → \"$MF_SPF\""
fi
echo

# ── 4. DKIM (3 CNAMEs) ─────────────────────────────────────────────────────────
echo "${BOLD}4) DKIM CNAMEs${X}  ${D}(<token>._domainkey.$DOMAIN → <token>.dkim.amazonses.com)${X}"
if [ -n "$DKIM_TOKENS" ]; then
  IFS=',' read -ra TOKS <<< "$DKIM_TOKENS"
  for t in "${TOKS[@]}"; do
    name="${t}._domainkey.${DOMAIN}"; want="${t}.dkim.amazonses.com"
    got=$(q "$name" CNAME)
    if [ -z "$got" ]; then bad "$name → missing (expected CNAME $want)"
    elif [ "${got%.}" = "$want" ]; then ok "$name → $want"
    else bad "$name → ${got%.} (expected $want)"; fi
  done
else
  info "DKIM tokens are per-domain — copy the 3 from Zoppy's email-config screen"
  info "then re-run with: --dkim token1,token2,token3"
fi
echo

# ── 5. Apex SPF sanity (must be a single record) ────────────────────────────────
echo "${BOLD}5) Apex SPF sanity${X}  ${D}($DOMAIN — at most ONE v=spf1 TXT allowed)${X}"
APEX_SPF=$(q "$DOMAIN" TXT | tr -d '"' | grep -ci '^v=spf1' || true)
APEX_SPF_VAL=$(q "$DOMAIN" TXT | tr -d '"' | grep -i '^v=spf1' || true)
if [ "${APEX_SPF:-0}" -gt 1 ]; then
  bad "$DOMAIN has ${APEX_SPF} SPF records — RFC 7208 allows only ONE; merge them"
  echo "$APEX_SPF_VAL" | sed 's/^/       /'
elif [ "${APEX_SPF:-0}" -eq 1 ]; then
  ok "single apex SPF → \"$APEX_SPF_VAL\""
else
  info "no apex SPF (fine — SES SPF lives on the MAIL FROM subdomain, not the apex)"
fi
echo

# ── 6. DMARC ────────────────────────────────────────────────────────────────────
echo "${BOLD}6) DMARC${X}  ${D}(_dmarc.$DOMAIN)${X}"
DMARC=$(q "_dmarc.$DOMAIN" TXT | tr -d '"')
if [ -z "$DMARC" ]; then
  warn "no DMARC record (SES delivery still works; recommended: v=DMARC1; p=none;)"
else
  ok "DMARC → \"$DMARC\""
  echo "$DMARC" | grep -qiE 'p=(quarantine|reject)' && \
    echo "       ${Y}note: policy is enforcing — DKIM must be valid or SES mail gets quarantined/rejected.${X}"
fi
echo

# ── 7. Suggest free MAIL FROM subdomains if there was a conflict ─────────────────
if [ -n "$MF_CNAME" ]; then
  echo "${BOLD}7) Free MAIL FROM alternatives${X}  ${D}(pick one, set it in Zoppy, then add MX+SPF there)${X}"
  for s in envio bounce news mailer email mkt; do
    cand="${s}.${DOMAIN}"
    if [ -z "$(q "$cand" CNAME)$(q "$cand" A)$(q "$cand" MX)$(q "$cand" TXT)" ]; then
      ok "$cand is free"
    else
      info "$cand is in use — skip"
    fi
  done
  echo
fi

# ── Verdict ─────────────────────────────────────────────────────────────────────
echo "${BOLD}━━━ verdict ━━━${X}"
if [ "$FAILS" -eq 0 ] && [ "$WARNS" -eq 0 ]; then
  echo "  ${G}${BOLD}All checks passed.${X} If SES still shows Pending, allow up to 72h for propagation."
elif [ -n "$MF_CNAME" ]; then
  echo "  ${R}${BOLD}Root cause: CNAME on $MAILFROM blocks the SES MAIL FROM records.${X}"
  echo "  Tell the customer to EITHER delete the '${MAILFROM} → ${MF_CNAME%.}' CNAME,"
  echo "  OR switch the MAIL FROM subdomain in Zoppy to a free name above, then add:"
  echo "      MX   <mailfrom>  →  10 $SES_MX"
  echo "      TXT  <mailfrom>  →  \"$SES_SPF\""
else
  echo "  ${Y}${BOLD}$FAILS failure(s), $WARNS warning(s).${X} See the records flagged above."
fi
echo "  ${D}registrar tips: enter HOST-ONLY (not the FQDN) if the panel auto-appends the zone;${X}"
echo "  ${D}MX priority (10) and target are usually separate fields.${X}"
exit $([ "$FAILS" -gt 0 ] && echo 1 || echo 0)
