# Finding registry schema

This is the single source of truth for slice output, deduplication, scoring, trend, and reports.

```json
{
  "findingId": "ZSA-0123456789ABCDEF",
  "legacyId": "optional prior identifier",
  "title": "short defect description",
  "area": "Aplicação — zoppy-api",
  "service": "zoppy-api",
  "severity": "CATASTROFICA | CRITICA | ALTA | MEDIA | BAIXA",
  "boardPriority": "CATASTRÓFICO | P0 | P1 | P2",
  "scoreIncluded": true,
  "size": "XS | S | M | L | XL",
  "sizeRationale": "real audit, coordination, migration, or rollout cost",
  "status": "new | still-open | partially-fixed | fixed | regression | accepted-risk",
  "closureKind": "remediated | refuted | null — required when scoreIncluded=false",
  "priorFindingId": "ZSA-... or null",
  "origin": "already-reported | pre-existing-missed | introduced-since | undetermined",
  "owaspCategory": "API1... or null",
  "regime": "LGPD | GDPR | both | null",
  "articles": ["LGPD Art.46"],
  "precondition": "none | tenant-auth | staff-auth | partner-cred | vpc | container | task-role | db-access | aws-creds | insider | dead-code | n/a — detection gap",
  "likelihood": "alta | média | baixa | muito baixa | n/a",
  "riskClass": "desvio-corrigível | risco-residual",
  "marginalReduction": "alta | média | baixa | nenhuma",
  "evidenceState": "confirmed | inferred | refuted | unknown",
  "confidence": "high | medium | low",
  "evidence": [{
    "type": "code | aws | grafana | database | github | contract",
    "location": "repo@commit:file:line or account/region/resource",
    "observedAt": "ISO-8601",
    "command": "safe regeneration command or null",
    "quote": "selected non-secret evidence"
  }],
  "attackPath": "attacker, prerequisite, action, result, blast radius",
  "recommendedFix": "concrete probability-reducing change",
  "verification": "how to prove remediation in code and runtime",
  "issueUrl": "GitHub issue or null",
  "pullRequests": ["GitHub PR URL"],
  "notes": "optional calibration context"
}
```

## Identity and deduplication

- Preserve a prior `findingId` when root cause and attack path are the same, even if title,
  severity, evidence, or remediation changes.
- New IDs are deterministic: `ZSA-` plus the first 16 uppercase hex characters of SHA-256 over
  `section-key + NUL + normalized-title`; use `scripts/normalize_bundle.py` for historical data.
- Deduplicate by root cause and attack path, not similar wording. One defect observed through code,
  AWS, and Grafana is one finding with multiple evidence entries.
- A consequence of another finding may remain separate only if it has an independent remediation.

## Scoring

`scoreIncluded=false` only after the canonical finding is proven `remediated` or `refuted`; record
that distinction in `closureKind`. Accepted risk and missing revalidation remain scored. Duplicates
are merged rather than emitted into the canonical registry. Keep closed records so trend and
regression checks remain possible.

Severity and board priority are distinct:

| Severity | Points | Board |
|---|---:|---|
| CATASTROFICA | 16 | CATASTRÓFICO |
| CRITICA | 8 | P0 |
| ALTA | 4 | P1 |
| MEDIA | 2 | P2 |
| BAIXA | 1 | P2 |

## Current-run completion criterion

Every current finding has every field shown above except fields explicitly allowing null. The
validator must return zero errors; missing values are not default-filled.
