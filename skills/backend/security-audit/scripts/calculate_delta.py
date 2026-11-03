#!/usr/bin/env python3
"""Calculate and embed an itemized KPI delta between two canonical bundles."""

import argparse
import json
from pathlib import Path


WEIGHTS = {"CATASTROFICA": 16, "CRITICA": 8, "ALTA": 4, "MEDIA": 2, "BAIXA": 1}
CLOSURE_KINDS = {"remediated", "refuted"}


def indexed(bundle):
    return {
        finding["findingId"]: finding
        for section in bundle["sections"]
        for finding in section.get("findings", [])
    }


def score(findings):
    return sum(
        WEIGHTS[finding["severity"]]
        for finding in findings.values()
        if finding.get("scoreIncluded", True)
    )


def item(finding_id, title, before, after, **extra):
    result = {
        "findingId": finding_id,
        "title": title,
        "fromPoints": before,
        "toPoints": after,
        "delta": after - before,
    }
    result.update(extra)
    return result


def calculate(previous, current, closure_overrides=None):
    previous_findings = indexed(previous)
    current_findings = indexed(current)
    closure_overrides = closure_overrides or {}
    items = {
        "remediated": [],
        "refuted": [],
        "reclassified": [],
        "expanded": [],
        "introduced": [],
        "undetermined": [],
    }

    for finding_id, old in previous_findings.items():
        new = current_findings.get(finding_id)
        if not new:
            raise ValueError(f"prior finding missing from current registry: {finding_id}")
        before = WEIGHTS[old["severity"]] if old.get("scoreIncluded", True) else 0
        after = WEIGHTS[new["severity"]] if new.get("scoreIncluded", True) else 0
        if before and not after:
            closure_kind = new.get("closureKind") or closure_overrides.get(finding_id)
            if closure_kind not in CLOSURE_KINDS:
                raise ValueError(f"{finding_id}: excluded prior finding needs closureKind remediated|refuted")
            new["closureKind"] = closure_kind
            items[closure_kind].append(
                item(
                    finding_id,
                    new["title"],
                    before,
                    0,
                    fromSeverity=old["severity"],
                    status=new.get("status"),
                    evidenceState=new.get("evidenceState"),
                )
            )
        elif not before and after:
            report_error = new.get("reopenReason") == "prior-report-error"
            if report_error and (new.get("evidenceState") != "confirmed" or not new.get("evidence") or not new.get("reopenNotes")):
                raise ValueError(f"{finding_id}: prior-report-error requires confirmed current evidence and reopenNotes")
            if report_error or old.get("closureKind") == "refuted":
                category, change_kind = "reclassified", "report-correction"
            elif new.get("origin") == "introduced-since":
                category, change_kind = "introduced", "regression"
            else:
                category, change_kind = "undetermined", "reopened"
            items[category].append(
                item(
                    finding_id, new["title"], 0, after,
                    toSeverity=new["severity"], previousClosureKind=old.get("closureKind"),
                    changeKind=change_kind, evidenceState=new.get("evidenceState"),
                )
            )
        elif before and after and old["severity"] != new["severity"]:
            items["reclassified"].append(
                item(
                    finding_id,
                    new["title"],
                    before,
                    after,
                    fromSeverity=old["severity"],
                    toSeverity=new["severity"],
                    evidenceState=new.get("evidenceState"),
                )
            )

    for finding_id, finding in current_findings.items():
        if finding_id in previous_findings or not finding.get("scoreIncluded", True):
            continue
        after = WEIGHTS[finding["severity"]]
        origin = finding.get("origin")
        if origin == "introduced-since":
            category = "introduced"
        elif origin in {"pre-existing-missed", "already-reported"}:
            category = "expanded"
        else:
            category = "undetermined"
        items[category].append(
            item(
                finding_id,
                finding["title"],
                0,
                after,
                toSeverity=finding["severity"],
                origin=origin,
                evidenceState=finding.get("evidenceState"),
            )
        )

    totals = {category: sum(entry["delta"] for entry in entries) for category, entries in items.items()}
    from_score = score(previous_findings)
    to_score = score(current_findings)
    calculated = from_score + sum(totals.values())
    if calculated != to_score:
        raise ValueError(f"delta does not reconcile: {from_score} + {sum(totals.values())} != {to_score}")

    previous_id = previous.get("meta", {}).get("date") or previous.get("meta", {}).get("baselineId")
    current_id = current.get("meta", {}).get("date")
    delta = {
        "fromAudit": previous_id,
        "toAudit": current_id,
        "fromScore": from_score,
        "toScore": to_score,
        "net": to_score - from_score,
        "totals": totals,
        "items": items,
    }
    current.setdefault("meta", {})["delta"] = delta
    current["meta"]["reconciliation"] = {
        "baseline": from_score,
        "remediated": -totals["remediated"],
        "refuted": -totals["refuted"],
        "rerating": totals["reclassified"],
        "introduced": totals["introduced"],
        "coverageChange": totals["expanded"],
        "undetermined": totals["undetermined"],
    }
    return current


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("previous", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--closure-map", type=Path)
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text())
    current = json.loads(args.current.read_text())
    closure_map = json.loads(args.closure_map.read_text()) if args.closure_map else {}
    result = calculate(previous, current, closure_map)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["meta"]["delta"]["totals"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
