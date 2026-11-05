#!/usr/bin/env python3
"""Fail closed when an audit bundle cannot support the company KPI."""

import argparse
import json
from collections import Counter
from pathlib import Path

from report_snapshots import validate_snapshots


WEIGHTS = {
    "CATASTROFICA": 16,
    "CRITICA": 8,
    "ALTA": 4,
    "MEDIA": 2,
    "BAIXA": 1,
}
BOARD_PRIORITY = {
    "CATASTROFICA": "CATASTRÓFICO",
    "CRITICA": "P0",
    "ALTA": "P1",
    "MEDIA": "P2",
    "BAIXA": "P2",
}
PRECONDITION_CEILINGS = {
    "none": "CATASTROFICA",
    "tenant-auth": "CATASTROFICA",
    "staff-auth": "CRITICA",
    "partner-cred": "CRITICA",
    "n/a — detection gap": "ALTA",
    "n/a — lacuna de detecção": "ALTA",
    "vpc": "MEDIA",
    "container": "MEDIA",
    "task-role": "MEDIA",
    "db-access": "MEDIA",
    "aws-creds": "MEDIA",
    "insider": "MEDIA",
    "dead-code": "BAIXA",
}
ORIGINS = {"already-reported", "pre-existing-missed", "introduced-since", "undetermined"}
SIZES = {"XS", "S", "M", "L", "XL"}
EVIDENCE_STATES = {"confirmed", "inferred", "refuted", "unknown", "historical"}
CURRENT_REQUIRED = {
    "findingId",
    "title",
    "severity",
    "boardPriority",
    "scoreIncluded",
    "size",
    "sizeRationale",
    "status",
    "origin",
    "service",
    "area",
    "precondition",
    "likelihood",
    "riskClass",
    "marginalReduction",
    "evidenceState",
    "evidence",
    "attackPath",
    "recommendedFix",
    "verification",
    "confidence",
}


REGISTRY_DIR = Path.home() / ".local/share/security-audit/baselines"
RULINGS_PATH = REGISTRY_DIR / "rulings.json"
RULING_DECISIONS = {"close", "keep", "accept", "severity"}


def load_rulings(path=RULINGS_PATH):
    return json.loads(path.read_text())["rulings"]


def validate_rulings(findings, rulings, generated_at):
    if not generated_at:
        return ["meta.generatedAt: required to apply the rulings ledger"]
    errors = []
    by_id = {finding.get("findingId"): finding for finding in findings}
    for ruling in rulings:
        finding_id = ruling.get("findingId")
        decision = ruling.get("decision")
        label = f"ruling {finding_id}"
        if decision not in RULING_DECISIONS or not ruling.get("date") or not ruling.get("source"):
            errors.append(f"{label}: needs decision in {sorted(RULING_DECISIONS)}, date and source")
            continue
        if ruling["date"] > generated_at[:10]:
            continue
        finding = by_id.get(finding_id)
        if finding is None:
            errors.append(f"{label}: finding missing from bundle")
            continue
        if decision == "close":
            if finding.get("scoreIncluded", True) or finding.get("closureKind") != "refuted":
                errors.append(f"{label}: closed by ruling, must be unscored with closureKind refuted")
            continue
        if finding.get("closureKind") == "remediated":
            continue
        if not finding.get("scoreIncluded", True):
            errors.append(f"{label}: {decision} ruling keeps the finding scored until remediated")
        if decision == "accept" and finding.get("status") != "accepted-risk":
            errors.append(f"{label}: accepted by ruling, status must be accepted-risk")
        if ruling.get("severity") and finding.get("severity") != ruling["severity"]:
            errors.append(f"{label}: severity must be {ruling['severity']}")
    return errors


def validate_policy(finding):
    label = finding.get("findingId")
    severity = finding["severity"]
    errors = []
    if finding.get("origin") not in ORIGINS:
        errors.append(f"{label}: invalid origin {finding.get('origin')!r}")
    if finding.get("boardPriority") != BOARD_PRIORITY[severity]:
        errors.append(f"{label}: boardPriority must be {BOARD_PRIORITY[severity]} for {severity}")
    if not finding.get("scoreIncluded", True):
        return errors
    ceiling = PRECONDITION_CEILINGS.get(finding.get("precondition"))
    if ceiling is None:
        errors.append(f"{label}: invalid precondition {finding.get('precondition')!r}")
    elif WEIGHTS[severity] > WEIGHTS[ceiling]:
        errors.append(f"{label}: {severity} exceeds the {ceiling} ceiling of precondition {finding['precondition']}")
    if severity == "CATASTROFICA" and not finding.get("issueUrl"):
        errors.append(f"{label}: open Catastrófica requires a dedicated issueUrl")
    return errors


def validate(bundle, historical=False):
    errors = [] if historical else validate_snapshots(bundle.get("meta", {}))
    sections = bundle.get("sections")
    if not isinstance(sections, list) or not sections:
        return {"errors": ["sections must be a non-empty list"]}

    findings = []
    privacy_ids = set()
    for section in sections:
        section_findings = section.get("findings") or []
        findings.extend(section_findings)
        if section.get("key") == "privacidade":
            privacy_ids.update(f.get("findingId") for f in section_findings)

    ids = [finding.get("findingId") for finding in findings]
    missing_ids = [index for index, finding_id in enumerate(ids) if not finding_id]
    if missing_ids:
        errors.append(f"missing findingId at indexes {missing_ids[:10]}")
    duplicates = sorted(finding_id for finding_id, count in Counter(ids).items() if finding_id and count > 1)
    if duplicates:
        errors.append(f"duplicate findingId values: {duplicates[:10]}")

    counts = Counter()
    total = 0
    privacy = 0
    for finding in findings:
        severity = finding.get("severity")
        if severity not in WEIGHTS:
            errors.append(f"{finding.get('findingId')}: invalid severity {severity!r}")
            continue
        if finding.get("scoreIncluded", True):
            counts[severity] += 1
            total += WEIGHTS[severity]
            if finding.get("findingId") in privacy_ids:
                privacy += WEIGHTS[severity]
        if finding.get("evidenceState") not in EVIDENCE_STATES:
            errors.append(f"{finding.get('findingId')}: invalid evidenceState")
        if not historical:
            if finding.get("reopenReason") == "prior-report-error" and (
                finding.get("evidenceState") != "confirmed" or not finding.get("evidence") or not finding.get("reopenNotes")
            ):
                errors.append(f"{finding.get('findingId')}: prior-report-error requires confirmed current evidence and reopenNotes")
            missing = sorted(key for key in CURRENT_REQUIRED if finding.get(key) in (None, "", []))
            if missing:
                errors.append(f"{finding.get('findingId')}: missing {', '.join(missing)}")
            if finding.get("size") not in SIZES:
                errors.append(f"{finding.get('findingId')}: invalid size {finding.get('size')!r}")
            if not finding.get("scoreIncluded", True) and finding.get("closureKind") not in {"remediated", "refuted"}:
                errors.append(f"{finding.get('findingId')}: excluded finding needs closureKind remediated|refuted")
            errors.extend(validate_policy(finding))

    if not historical:
        errors.extend(validate_rulings(findings, load_rulings(), bundle.get("meta", {}).get("generatedAt", "")))

    delta = bundle.get("meta", {}).get("delta")
    if not historical and delta is not None and delta.get("toScore") != total:
        errors.append(f"meta.delta.toScore: {delta.get('toScore')} must equal the section totals {total}")

    comparison = bundle.get("meta", {}).get("comparability")
    if comparison is not None:
        numeric_fields = ["previousRegistryScore", "currentPriorIdScore", "newCoverageScore"]
        if not isinstance(comparison, dict):
            errors.append("meta.comparability: object required")
        elif any(type(comparison.get(field)) is not int or comparison[field] < 0 for field in numeric_fields):
            errors.append("meta.comparability: non-negative integer score components required")
        else:
            if comparison["currentPriorIdScore"] + comparison["newCoverageScore"] != total:
                errors.append("meta.comparability: prior-ID plus new-coverage subtotals must equal KPI")
            evidence_scores = {state: sum(WEIGHTS[f["severity"]] for f in findings
                                         if f.get("scoreIncluded", True) and f.get("evidenceState") == state
                                         and f.get("severity") in WEIGHTS)
                               for state in ["confirmed", "inferred", "unknown"]}
            if comparison.get("evidenceScores") != evidence_scores or sum(evidence_scores.values()) != total:
                errors.append("meta.comparability.evidenceScores: must reproduce current confirmed/inferred/unknown points")

    return {
        "schemaVersion": bundle.get("meta", {}).get("schemaVersion"),
        "findingCount": len(findings),
        "scoreIncludedCount": sum(1 for finding in findings if finding.get("scoreIncluded", True)),
        "counts": dict(counts),
        "scores": {"security": total - privacy, "privacy": privacy, "total": total},
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--historical", action="store_true")
    args = parser.parse_args()
    result = validate(json.loads(args.bundle.read_text()), historical=args.historical)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    raise SystemExit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
