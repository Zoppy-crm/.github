#!/usr/bin/env bash
# Acesso da Central de Ajuda à rede, usado só pelos passos de shell do workflow (nunca pelo agente).
#   help-center.sh taxonomy                     GET da taxonomia do site (público)
#   help-center.sh export                       GET dos artigos publicados (público)
#   help-center.sh validate <arquivo> <pr-url>  confere o draft.json escrito pelo agente
#   help-center.sh send <arquivo>               POST do rascunho em agent-drafts (precisa do token)
#   help-center.sh sanitize <max>               texto do agente (stdin) pronto para comentário do PR
# O ambiente vem de HELP_CENTER_ENV (prod | staging); a URL da API é fixa por ambiente.
set -euo pipefail

case "${HELP_CENTER_ENV:-prod}" in
    prod) API_URL="https://api.zoppy.com.br" ;;
    staging) API_URL="https://api-staging.zoppy.com.br" ;;
    *) echo "help-center.sh: HELP_CENTER_ENV deve ser prod ou staging" >&2; exit 1 ;;
esac
SITE_URL="https://ajuda.zoppy.com.br"
MAX_BYTES=200000

die() {
    echo "help-center.sh: $*" >&2
    exit 1
}

get() {
    curl -fsS --proto '=https' --max-time 60 "$1"
}

validate() {
    local file="${1:-}" pr_url="${2:-}"
    [[ -n "$file" && -f "$file" && ! -L "$file" ]] || die "arquivo do rascunho não encontrado: '$file'"
    [[ -n "$pr_url" ]] || die "uso: validate <arquivo> <pr-url>"
    (( $(wc -c <"$file") <= MAX_BYTES )) || die "'$file' passa de $MAX_BYTES bytes"
    jq -e --arg pr "$pr_url" '
        type == "object"
        and (keys - ["content", "todo", "sourceUrl"] | length == 0)
        and (.content | type == "object")
        and (.content.slug | type == "string" and test("^[a-z0-9]+(-[a-z0-9]+)*$"))
        and (.content.title | type == "string" and length > 0 and length <= 120 and (explode | all(. >= 32 and . != 127)))
        and (.content.body | type == "string")
        and ((.todo // []) | type == "array" and all(type == "string"))
        and .sourceUrl == $pr
    ' "$file" >/dev/null || die "'$file' não tem o formato de rascunho esperado"
}

# Uma linha, sem markdown que vire link, imagem, HTML ou menção: tira `<>[]()!, desarma @ e esquemas de URL.
sanitize() {
    local max="${1:-200}"
    [[ "$max" =~ ^[0-9]+$ ]] || die "uso: sanitize <max>"
    head -n1 | tr -d '\r\000-\037\177`<>[]()!' | sed 's/@/＠/g; s#[A-Za-z][A-Za-z0-9+.-]*://##g' | cut -c1-"$max"
}

send() {
    local file="${1:-}"
    [[ -n "$file" && -f "$file" ]] || die "arquivo do rascunho não encontrado: '$file'"
    [[ -n "${HELP_CENTER_AGENT_TOKEN:-}" ]] || die "HELP_CENTER_AGENT_TOKEN não definido"

    local body status
    body="$(mktemp)"
    trap 'rm -f "$body"' RETURN
    # O header com o token vai pelo stdin, fora da linha de comando e do log.
    status="$(printf 'Authorization: Bearer %s\n' "$HELP_CENTER_AGENT_TOKEN" | curl -sS --proto '=https' --max-time 60 \
        -X POST "$API_URL/api/help-center/agent-drafts" \
        -H @- \
        -H 'Content-Type: application/json' \
        --data-binary "@$file" \
        -o "$body" -w '%{http_code}')" || die "falha de rede ao enviar o rascunho"
    cat "$body"
    echo
    [[ "$status" =~ ^2 ]] || die "a API respondeu HTTP $status"
}

case "${1:-}" in
    taxonomy) get "$SITE_URL/data/taxonomy.json" ;;
    export) get "$API_URL/api/help-center/export" ;;
    validate) validate "${2:-}" "${3:-}" ;;
    send) send "${2:-}" ;;
    sanitize) sanitize "${2:-}" ;;
    *) die "uso: help-center.sh taxonomy | export | validate <arquivo> <pr-url> | send <arquivo> | sanitize <max>" ;;
esac
