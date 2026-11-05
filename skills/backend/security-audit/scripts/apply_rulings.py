#!/usr/bin/env python3
"""Apply the product rulings ledger to a canonical bundle before delta and validation."""

import argparse
import json
from pathlib import Path

from validate_bundle import BOARD_PRIORITY, load_rulings


CLOSURE_NOTE = "Encerrado como comportamento intencional (decisão de produto em {date})."


def apply_rulings(bundle, rulings):
    by_id = {finding["findingId"]: finding for section in bundle["sections"] for finding in section["findings"]}
    for ruling in rulings:
        finding = by_id[ruling["findingId"]]
        if finding.get("closureKind") == "remediated":
            continue
        if ruling["decision"] == "close":
            finding.update(scoreIncluded=False, status="fixed", closureKind="refuted", evidenceState="refuted")
            finding["notes"] = " ".join(filter(None, [finding.get("notes"), CLOSURE_NOTE.format(date=ruling["date"])]))
        if ruling["decision"] == "accept":
            finding["status"] = "accepted-risk"
        if ruling.get("severity"):
            finding["severity"] = ruling["severity"]
            finding["boardPriority"] = BOARD_PRIORITY[ruling["severity"]]
        finding["ruling"] = {key: ruling.get(key, "") for key in ["date", "decision", "source", "note"]}
    return bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    bundle = apply_rulings(json.loads(args.bundle.read_text()), load_rulings())
    args.bundle.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
