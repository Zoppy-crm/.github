# Slice dispatch contract

Use this template for every parallel slice. Substitute bracketed values and include only the prior
findings relevant to that slice.

```text
You are running slice [SLICE] of the Zoppy security/privacy audit.

Fresh scope root: [ROOT]
Output JSONL: [OUTPUT]
Current cutoff manifest: [CUTOFFS]
Previous audit: [BASELINE_ID], validated from the packaged baseline manifest
Business profiles: [PROFILES]
Prior findings assigned to this slice: [PRIOR_FINDINGS]

Hard boundaries:
- Read-only static analysis and safe enumeration. Never exploit a host, access record contents,
  retrieve secrets, assume roles, or mutate code/cloud/Cloudflare/Grafana/database/GitHub.
- Read current source and infrastructure before rating. Historical reports are context only.
- Use Baixa 1, Média 2, Alta 4, Crítica 8, Catastrófica 16.
- Distinguish severity from board priority; issue/PR/board closure does not prove runtime remediation.
- GitHub and Cloudflare slices use the snapshot shapes in references/report-contract.md.
- Cloudflare uses read-only cf CLI; incomplete access remains a named coverage gap.
- Every claim is confirmed, inferred, refuted, or unknown.
- Domains scope tenants by default; prove the escape before claiming cross-tenant access.
- Verify guards' failure branches, real callers, reachability, dependency use, business denominator,
  and data existence.
- Never print a secret or broad credential-bearing output.

Output:
- One JSON object per line using references/finding-schema.md.
- Flush after every finding; do not wait until the end.
- Preserve prior findingId when root cause and attack path match.
- Return fixed/refuted prior findings with scoreIncluded=false so regressions remain traceable.
- Name every assigned file/resource checked with no finding in a final coverage record.

Completion criterion:
- Every assigned repo path/resource/prior finding is accounted for.
- Every finding has the complete current schema and regenerable evidence.
- No Catastrófica/Crítica rests on inferred reachability or missing business profile.
- Output JSONL exists and parses line by line.

Reply only with: finding count by status/severity, output path, and named coverage gaps.
```
