#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 || ! $1 =~ ^[A-Za-z0-9._-]+$ || ! $2 =~ ^[0-9]+$ ]]; then
    echo "uso: org-issue.sh <repo da Zoppy-crm> <número da issue>" >&2
    exit 2
fi

GH_TOKEN="${GH_ISSUES_TOKEN:?GH_ISSUES_TOKEN ausente nesta execução}" \
    exec gh issue view "$2" -R "Zoppy-crm/$1" --json number,title,state,body,comments
