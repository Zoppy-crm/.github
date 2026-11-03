#!/usr/bin/env python3
"""Build the immutable artifact manifest for an audit bundle."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from validate_bundle import validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    raw = args.bundle.read_bytes()
    bundle = json.loads(raw)
    validation = validate(bundle, historical=True)
    if validation["errors"]:
        raise SystemExit("bundle validation failed: " + "; ".join(validation["errors"]))
    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "bundle": args.bundle.name,
        "bundleBytes": len(raw),
        "bundleSha256": hashlib.sha256(raw).hexdigest(),
        "findingCount": validation["findingCount"],
        "scoreIncludedCount": validation["scoreIncludedCount"],
        "counts": validation["counts"],
        "scores": validation["scores"],
        "cutoffs": bundle.get("meta", {}).get("cutoffs", {}),
        "coverageGaps": bundle.get("meta", {}).get("coverageGaps", []),
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
