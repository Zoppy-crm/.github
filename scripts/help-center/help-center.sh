#!/usr/bin/env bash
# Único acesso do agente da Central de Ajuda à rede.
#   help-center.sh taxonomy           GET da taxonomia do site
#   help-center.sh export             GET dos artigos publicados
#   help-center.sh send <arquivo>     POST do rascunho (JSON) em agent-drafts
# A URL da API vem de HELP_CENTER_API_URL e o token de HELP_CENTER_AGENT_TOKEN, ambos do workflow.
set -euo pipefail

API_URL="${HELP_CENTER_API_URL:-https://api.zoppy.com.br}"
API_URL="${API_URL%/}"
SITE_URL="https://ajuda.zoppy.com.br"

die() {
    echo "help-center.sh: $*" >&2
    exit 1
}

get() {
    curl -fsS --proto '=https' --max-time 60 "$1"
}

send() {
    local file="${1:-}"
    [[ -n "$file" && -f "$file" ]] || die "arquivo do rascunho não encontrado: '$file'"
    [[ -n "${HELP_CENTER_AGENT_TOKEN:-}" ]] || die "HELP_CENTER_AGENT_TOKEN não definido"
    if command -v jq >/dev/null 2>&1; then
        jq -e 'type == "object" and has("content")' "$file" >/dev/null || die "'$file' não é um JSON com 'content'"
    else
        python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if isinstance(d,dict) and "content" in d else 1)' "$file" \
            || die "'$file' não é um JSON com 'content'"
    fi

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
    send) send "${2:-}" ;;
    *) die "uso: help-center.sh taxonomy | export | send <arquivo.json>" ;;
esac
