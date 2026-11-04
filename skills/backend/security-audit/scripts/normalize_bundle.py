#!/usr/bin/env python3
"""Normalize an audit bundle into the versioned KPI schema."""

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


SEVERITY_ALIASES = {
    "CATASTROFICA": "CATASTROFICA",
    "CATASTROFICO": "CATASTROFICA",
    "CRITICA": "CRITICA",
    "CRITICO": "CRITICA",
    "ALTA": "ALTA",
    "MEDIA": "MEDIA",
    "BAIXA": "BAIXA",
}


def ascii_upper(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in normalized if not unicodedata.combining(char)).upper()


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", ascii_upper(value).lower()).strip("-")


def normalize_bundle(bundle):
    bundle.setdefault("meta", {})["schemaVersion"] = 1
    seen = set()
    for section in bundle.get("sections", []):
        section_key = section.get("key") or slug(section.get("label"))
        section["key"] = section_key
        for finding in section.get("findings", []):
            raw_severity = finding.get("severity") or finding.get("priority")
            severity = SEVERITY_ALIASES.get(ascii_upper(raw_severity))
            if not severity:
                raise ValueError(f"unknown severity {raw_severity!r}: {finding.get('title')}")
            finding["severity"] = severity
            finding["priority"] = severity
            finding.setdefault("legacyId", finding.get("id"))
            identity = f"{section_key}\0{finding.get('title', '').strip()}"
            finding_id = "ZSA-" + hashlib.sha256(identity.encode()).hexdigest()[:16].upper()
            if finding_id in seen:
                raise ValueError(f"duplicate deterministic finding id {finding_id}")
            seen.add(finding_id)
            finding["findingId"] = finding_id
            finding.setdefault("evidenceState", "historical")
    return bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    bundle = normalize_bundle(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
