import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = Path.home() / ".local/share/security-audit/baselines"
LATEST = BASELINES / "2026-10-31.bundle.json"
sys.path.insert(0, str(ROOT / "scripts"))
from apply_rulings import apply_rulings
from calculate_delta import calculate
from check_report import check
from validate_bundle import validate


def findings(bundle):
    return [finding for section in bundle["sections"] for finding in section["findings"]]


def find(bundle, predicate):
    return next(finding for finding in findings(bundle) if predicate(finding))


class RulingsApplication(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads(LATEST.read_text())
        open_findings = [f for f in findings(self.bundle) if f["scoreIncluded"] and f["severity"] == "ALTA"]
        self.closed, self.accepted, self.rerated = open_findings[:3]
        self.remediated = find(self.bundle, lambda f: f.get("closureKind") == "remediated")
        self.rulings = [
            {"findingId": self.closed["findingId"], "decision": "close", "date": "2026-11-02", "source": "test"},
            {"findingId": self.accepted["findingId"], "decision": "accept", "date": "2026-11-02", "source": "test"},
            {"findingId": self.rerated["findingId"], "decision": "severity", "severity": "MEDIA",
             "date": "2026-11-02", "source": "test", "note": "nota"},
            {"findingId": self.remediated["findingId"], "decision": "close", "date": "2026-11-02", "source": "test"},
        ]

    def test_each_decision_reaches_the_shape_the_validator_requires(self):
        remediated_before = copy.deepcopy(self.remediated)
        apply_rulings(self.bundle, self.rulings)
        self.assertFalse(self.closed["scoreIncluded"])
        self.assertEqual(("fixed", "refuted", "refuted"),
                         (self.closed["status"], self.closed["closureKind"], self.closed["evidenceState"]))
        self.assertTrue(self.closed["notes"].endswith(
            "Encerrado como comportamento intencional (decisão de produto em 2026-11-02)."))
        self.assertEqual("accepted-risk", self.accepted["status"])
        self.assertEqual(("MEDIA", "P2"), (self.rerated["severity"], self.rerated["boardPriority"]))
        self.assertEqual({"date": "2026-11-02", "decision": "severity", "source": "test", "note": "nota"},
                         self.rerated["ruling"])
        self.assertEqual(remediated_before, self.remediated)


class PolicyGates(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads(LATEST.read_text())

    def errors(self):
        return validate(self.bundle)["errors"]

    def test_latest_bundle_passes_every_gate(self):
        self.assertEqual([], self.errors())

    def test_broken_fixture_fails_each_policy_gate(self):
        ceiling = find(self.bundle, lambda f: f["scoreIncluded"] and f["precondition"] == "insider")
        ceiling.update(severity="ALTA", boardPriority="P1")
        origin = find(self.bundle, lambda f: f is not ceiling)
        origin["origin"] = "unknown"
        board = find(self.bundle, lambda f: f["severity"] == "CRITICA")
        board["boardPriority"] = "P1"
        catastrophic = find(self.bundle, lambda f: f["scoreIncluded"] and f["precondition"] == "none"
                           and all(f is not other for other in (origin, board)))
        catastrophic.update(severity="CATASTROFICA", boardPriority="CATASTRÓFICO", issueUrl=None)
        self.bundle["meta"]["delta"]["toScore"] += 1
        errors = "\n".join(self.errors())
        for message in ["exceeds the MEDIA ceiling of precondition insider", "invalid origin 'unknown'",
                        "boardPriority must be P0 for CRITICA", "open Catastrófica requires a dedicated issueUrl",
                        "meta.delta.toScore"]:
            self.assertIn(message, errors)

    def test_historical_bundles_skip_policy_gates(self):
        find(self.bundle, lambda f: True)["origin"] = "unknown"
        self.assertEqual([], validate(self.bundle, historical=True)["errors"])

    def test_delta_fails_when_a_prior_finding_disappears(self):
        previous = copy.deepcopy(self.bundle)
        self.bundle["sections"][0]["findings"].pop()
        with self.assertRaisesRegex(ValueError, "prior finding missing from current registry"):
            calculate(previous, self.bundle)


class ReportCheck(unittest.TestCase):
    def render(self, bundle, root):
        path = root / "security-audit-2026-10-31.bundle.json"
        path.write_text(json.dumps(bundle, ensure_ascii=False))
        stem = root / "security-audit-2026-10-31"
        subprocess.run([sys.executable, ROOT / "scripts/render_reports.py", path, f"{stem}.md",
                        f"{stem}-by-actionability.md"], check=True, capture_output=True)
        subprocess.run([sys.executable, ROOT / "scripts/gen_html.py", path, f"{stem}.html"],
                       check=True, capture_output=True)
        return path

    def test_clean_report_passes_and_planted_defects_fail(self):
        bundle = json.loads(LATEST.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual([], check(self.render(bundle, Path(tmp))))
        bundle["meta"]["githubRemediation"]["issues"][0]["assignees"] = ["octo-owner"]
        find(bundle, lambda f: f["scoreIncluded"])["notes"] = "This endpoint returns the token to any caller with no check."
        with tempfile.TemporaryDirectory() as tmp:
            path = self.render(bundle, Path(tmp))
            html_path = path.with_name("security-audit-2026-10-31.html")
            html_path.write_text(html_path.read_text().replace(
                "</head>", '<script src="https://cdn.example.com/x.js"></script></head>'))
            errors = "\n".join(check(path))
        self.assertIn("forbidden 'octo-owner'", errors)
        self.assertIn("English prose 'This endpoint returns the token", errors)
        self.assertIn("HTML: external asset reference", errors)


if __name__ == "__main__":
    unittest.main()
