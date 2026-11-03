# AWS baseline and refresh routes

This is a discovery accelerator, not current truth. Re-run every relevant check. Last material
verification: 2026-08-28 through 2026-08-31.

## Accounts

| Account | ID | Profile | Known role |
|---|---|---|---|
| production | `891377241798` | `zoppy-prd` | customer-facing production |
| development | `654654607244` | `zoppy-dev` | dev, staging, mirror |
| payer/main | `089543940399` | `zoppy-main` | organization, CI/CD, SES |
| zoppy login | `654654603166` | none | coverage gap |
| data sandbox | `407370958965` | none | coverage gap |
| Zoppy WP | `363819825378` | none | coverage gap |

Everything historically observed was in `us-east-1`; sweep other regions instead of assuming that
remains true.

## Production landmarks

- VPC `vpc-04670ff623440a967` (`192.168.0.0/16`).
- One `zoppy-production` image runs multiple API/PVT/partners/giftcards/worker services.
- Separate deployments include workflow, command, event bridge, WhatsApp Commerce, OS, n8n,
  Metabase, Grafana, Airbyte, Glue/DMS/Athena workloads, and CSM agent.
- `nlb-production-services-public` forwards to an internal-named ALB; verify listeners, targets,
  SGs, prefix lists, host rules, and application authentication together.

## Data-lake ownership discovered after July

- `zoppy-terraform-lakehouse-core` imports legacy roles/buckets and owns core IAM, Lake Formation,
  Athena, and bucket objects.
- `zoppy-terraform-lakehouse-analytics` owns Glue jobs/crawlers.
- `zoppy-terraform-lakehouse-shared-dms` owns newer DMS patterns; some legacy production endpoints
  remain outside Terraform.
- `AWSGlueDataLakeAdministratorRoleZoppy` was wildcard-trusted and used by Glue and DMS. Terraform
  PR `zoppy-terraform-lakehouse-core#4` restricts trust to those services and production
  `aws:SourceAccount`; re-query PR, apply, and live trust before status.
- Dedicated DMS roles exist. Verify bucket/prefix and bucket-level ARN correctness before migration.

## Public bucket correction

`zoppy-data-warehouse`, `zoppy-data-warehouse-work`, and `zoppy-lake-warehouse` were last observed
with `IsPublic=true`, `Principal:"*"`, `Action:"s3:*"`, object resources (`bucket/*`), all four
bucket Public Access Block flags false, no account PAB, no server access logging, and no versioning.

Exact semantics: object GET/PUT/overwrite/DELETE are public for known keys. `ListBucket` is not
granted by an object ARN; do not claim anonymous enumeration. Known consumers include Glue, DMS,
Athena, Metabase, Grafana, Airbyte, and internal jobs. Policy removal requires proving independent
IAM. One running DMS CDC path relied on public access because its role targeted another bucket.

## Detection and other July baselines

Last observed absent: durable CloudTrail trail/Lake, GuardDuty, Config, Security Hub, Inspector,
Access Analyzer, VPC flow logs, account-level S3 PAB, and regional WAF. Refresh each; Event History
is not a durable trail.

Other July findings requiring current checks included public databases/SGs, Airbyte wide ingress,
long-lived IAM keys, MFA gaps, unencrypted transport, missing secret rotation, public DMS, Athena
output enforcement, and shared CI identities.

## Safe commands

Use `--query` to select non-secret fields:

```bash
aws sts get-caller-identity --profile <profile>
aws organizations list-accounts --profile zoppy-main
aws cloudtrail describe-trails --include-shadow-trails --profile <profile> --region us-east-1
aws cloudtrail list-event-data-stores --profile <profile> --region us-east-1
aws iam get-account-summary --profile <profile>
aws iam get-role --role-name <role> --profile <profile>
aws iam simulate-principal-policy ...
aws s3api get-bucket-policy-status --bucket <bucket> --profile <profile>
aws s3api get-public-access-block --bucket <bucket> --profile <profile>
aws s3control get-public-access-block --account-id <id> --profile <profile>
aws rds describe-db-instances --profile <profile> --region us-east-1
aws ec2 describe-security-groups --profile <profile> --region us-east-1
aws ecs describe-task-definition --task-definition <family> --profile <profile>
```

Never call `get-secret-value`, print environment values, list/download data objects, run unsigned
public-access probes, assume a vulnerable role, or mutate a resource during the audit.
