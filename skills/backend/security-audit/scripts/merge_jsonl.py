#!/usr/bin/env python3
"""Merge incremental slice JSONL files into a canonical audit bundle."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("slice", nargs="+", help="key::label::path.jsonl")
    args = parser.parse_args()
    meta = json.loads(args.meta.read_text())
    sections = []
    coverage_gaps = list(meta.get("coverageGaps", []))
    for specification in args.slice:
        key, label, path = specification.split("::", 2)
        findings = []
        for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("recordType") == "coverage":
                coverage_gaps.extend(record.get("gaps", []))
            else:
                findings.append(record)
        sections.append({"key": key, "label": label, "findings": findings})
    meta["coverageGaps"] = sorted(set(coverage_gaps))
    args.output.write_text(json.dumps({"meta": meta, "sections": sections}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
