import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINES = Path.home() / ".local/share/security-audit/baselines"
WEIGHTS = {
    "CATASTROFICA": 16,
    "CRITICA": 8,
    "ALTA": 4,
    "MEDIA": 2,
    "BAIXA": 1,
}


class SecurityAuditKpiContract(unittest.TestCase):
    def test_required_package_contract_exists(self):
        required = [
            "SKILL.md",
            "references/audit-policy.md",
            "references/audit-scope.md",
            "references/finding-schema.md",
            "references/report-contract.md",
            "references/aws-infrastructure.md",
            "scripts/normalize_bundle.py",
            "scripts/validate_bundle.py",
            "scripts/gen_html.py",
            "scripts/render_reports.py",
            "scripts/build_manifest.py",
            "scripts/calculate_delta.py",
            "scripts/merge_jsonl.py",
            "scripts/apply_rulings.py",
            "scripts/check_report.py",
            "baselines/manifest.json",
            "baselines/2026-05-11.bundle.json",
            "baselines/2026-07-29.bundle.json",
            "baselines/2026-09-01.bundle.json",
        ]
        missing = [path for path in required if not (ROOT / path).exists() and not (BASELINES.parent / path).exists()]
        self.assertEqual([], missing)

    def test_entrypoint_is_step_driven_and_has_no_stale_contracts(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertLess(len(text.splitlines()), 500)
        for required in [
            "1 · 2 · 4 · 8 · 16",
            "baselines/manifest.json",
            "validate_bundle.py",
            "confirmed | inferred | refuted | unknown",
            "Completion criterion",
        ]:
            self.assertIn(required, text)

        corpus = "\n".join(
            path.read_text(errors="ignore")
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".md", ".py"} and "tests" not in path.parts
        )
        for forbidden in [
            "Exposure = Σ(CATASTRÓFICO×100",
            "P0 — active exploit path",
            "owasp-audit-2026-07-29.md",
            "flow-github-issues",
            "This method audits **application code in one repo**",
        ]:
            self.assertNotIn(forbidden, corpus)
        self.assertFalse((ROOT / "references/gen_html.py").exists())
        self.assertIn(
            "Rescaling sweeps four places",
            (ROOT / "references/report-contract.md").read_text(),
        )

    def test_access_loss_preserves_evidence_and_progress(self):
        entrypoint = (ROOT / "SKILL.md").read_text()
        policy = (ROOT / "references/audit-policy.md").read_text()
        self.assertNotIn("If required access expires, the next user message starts `Blocked:`", entrypoint)
        for required in [
            "quarantines only unfinished checks",
            "continue every independent slice",
            "carry the prior finding forward",
            "never expires merely because the authentication session does",
        ]:
            self.assertIn(required, policy)

    def test_baseline_manifest_and_hashes(self):
        manifest = json.loads((BASELINES / "manifest.json").read_text())
        self.assertEqual(1, manifest["schemaVersion"])
        self.assertEqual(WEIGHTS, manifest["weights"])
        expected = {
            "2026-05-11": (265, 265, 992),
            "2026-07-29": (256, 256, 840),
            "2026-09-01": (265, 254, 810),
        }
        audit_ids = [audit["id"] for audit in manifest["audits"]]
        self.assertTrue(set(expected).issubset(audit_ids))
        self.assertEqual(sorted(set(audit_ids)), audit_ids)
        self.assertTrue(all(audit_id > "2026-09-01" for audit_id in audit_ids if audit_id not in expected))
        self.assertEqual(max(audit_ids), manifest["audits"][-1]["id"])

        for audit in manifest["audits"]:
            bundle_path = BASELINES / audit["bundle"]
            digest = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
            self.assertEqual(audit["sha256"], digest)
            bundle = json.loads(bundle_path.read_text())
            findings = [finding for section in bundle["sections"] for finding in section["findings"]]
            included = [finding for finding in findings if finding.get("scoreIncluded", True)]
            if audit["id"] in expected:
                registry_count, score_count, total = expected[audit["id"]]
            else:
                registry_count, score_count, total = audit["findingCount"], audit["scoreIncludedCount"], audit["totalScore"]
                self.assertEqual(1, bundle["meta"]["reportAmendmentVersion"])
                result = subprocess.run([sys.executable, ROOT / "scripts/validate_bundle.py", bundle_path],
                                        check=True, capture_output=True, text=True)
                self.assertEqual([], json.loads(result.stdout)["errors"])
            self.assertEqual(audit["findingCount"], len(findings))
            self.assertEqual(audit["totalScore"], sum(WEIGHTS[f["severity"]] for f in included))
            privacy_score = sum(WEIGHTS[f["severity"]] for section in bundle["sections"]
                                if section["key"] == "privacidade" for f in section["findings"]
                                if f.get("scoreIncluded", True))
            if "securityScore" in audit:
                self.assertEqual(audit["securityScore"], total - privacy_score)
                self.assertEqual(audit["privacyScore"], privacy_score)
            self.assertEqual(registry_count, len(findings))
            self.assertEqual(score_count, len(included))
            self.assertEqual(total, sum(WEIGHTS[f["severity"]] for f in included))
            finding_ids = [finding["findingId"] for finding in findings]
            self.assertEqual(len(finding_ids), len(set(finding_ids)))

    def test_validator_reproduces_authoritative_kpis(self):
        for audit_id, score in [("2026-05-11", 992), ("2026-07-29", 840), ("2026-09-01", 810)]:
            bundle = BASELINES / f"{audit_id}.bundle.json"
            result = subprocess.run(
                [sys.executable, ROOT / "scripts/validate_bundle.py", bundle, "--historical"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(score, payload["scores"]["total"])
            self.assertEqual(0, len(payload["errors"]))

    def test_html_renderer_uses_only_current_kpi_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "audit.html"
            subprocess.run(
                [
                    sys.executable,
                    ROOT / "scripts/gen_html.py",
                    BASELINES / "2026-07-29.bundle.json",
                    output,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            html = output.read_text()
            self.assertIn("840 pontos", html)
            self.assertIn("Baixa 36", html)
            self.assertNotIn("100/30/8/2", html)
            self.assertNotIn("Grade caps", html)
            self.assertNotIn("P0</th>", html)
            self.assertNotIn("Priority weight", html)
            self.assertIn("Pontos da severidade", html)
            area_header = re.search(r"<tr><th>Área</th>(.*?)</tr>", html, re.S).group(1)
            self.assertEqual(6, area_header.count("<th>"))
            area_table = re.search(r"<h2>Por área</h2>.*?<table>(.*?)</table>", html, re.S).group(1)
            first_area_row = re.search(r"<tr><td class=\"l\">.*?</tr>", area_table, re.S).group(0)
            self.assertEqual(7, first_area_row.count("<td"))

    def test_baseline_free_text_has_no_retired_severity_assertions(self):
        retired_severity = re.compile(r"(?<![A-Z0-9-])P[0-3](?!-?\d)", re.I)
        for bundle_path in BASELINES.glob("*.bundle.json"):
            bundle = json.loads(bundle_path.read_text())
            for section in bundle["sections"]:
                for finding in section["findings"]:
                    for field, value in finding.items():
                        if not isinstance(value, str) or field in {
                            "findingId",
                            "legacyId",
                            "prior",
                            "priorFindingId",
                            "boardPriority",
                            "issueUrl",
                        }:
                            continue
                        text_without_ids = re.sub(r"\bP[0-3]-\d+\b", "LEGACY-ID", value)
                        self.assertIsNone(
                            retired_severity.search(text_without_ids),
                            f"{bundle_path.name}:{finding['findingId']}:{field}",
                        )
                        self.assertNotRegex(text_without_ids, r"\*\*Severity:\*\*\s*P[0-3]\b")

    def test_markdown_actionability_and_manifest_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bundle = BASELINES / "2026-07-29.bundle.json"
            report = tmp / "report.md"
            actionability = tmp / "actionability.md"
            manifest = tmp / "manifest.json"
            subprocess.run(
                [sys.executable, ROOT / "scripts/render_reports.py", bundle, report, actionability],
                check=True,
            )
            subprocess.run(
                [sys.executable, ROOT / "scripts/build_manifest.py", bundle, manifest],
                check=True,
            )
            report_text = report.read_text()
            self.assertIn("**KPI combinado:** 840", report_text)
            self.assertIn("**Segurança:** 768", report_text)
            self.assertIn("**Privacidade:** 72", report_text)
            self.assertIn("Fila por acionabilidade", actionability.read_text())
            manifest_data = json.loads(manifest.read_text())
            self.assertEqual(840, manifest_data["scores"]["total"])
            self.assertEqual(hashlib.sha256(bundle.read_bytes()).hexdigest(), manifest_data["bundleSha256"])

    def test_latest_report_leads_with_itemized_delta(self):
        bundle = BASELINES / "2026-09-01.bundle.json"
        data = json.loads(bundle.read_text())
        delta = data["meta"]["delta"]
        self.assertEqual(840, delta["fromScore"])
        self.assertEqual(810, delta["toScore"])
        self.assertEqual(-30, delta["net"])
        self.assertEqual(-15, delta["totals"]["remediated"])
        self.assertEqual(-15, delta["totals"]["refuted"])
        self.assertEqual(-16, delta["totals"]["reclassified"])
        self.assertEqual(15, delta["totals"]["expanded"])
        self.assertEqual(0, delta["totals"]["introduced"])
        self.assertEqual(1, delta["totals"]["undetermined"])
        self.assertTrue(delta["items"]["remediated"])
        self.assertTrue(delta["items"]["refuted"])
        self.assertTrue(delta["items"]["reclassified"])
        self.assertTrue(delta["items"]["expanded"])

        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.md"
            actionability = Path(tmp) / "actionability.md"
            subprocess.run(
                [sys.executable, ROOT / "scripts/render_reports.py", bundle, report, actionability],
                check=True,
            )
            text = report.read_text()
            self.assertIn("## Delta — o que mudou", text)
            self.assertLess(text.index("## Delta — o que mudou"), text.index("## Aritmética"))
            for heading in ["Remediado", "Refutado/corrigido", "Reclassificado", "Cobertura ampliada", "Introduzido"]:
                self.assertIn(heading, text)

    def test_excluded_current_finding_requires_closure_kind(self):
        data = json.loads((BASELINES / "2026-09-01.bundle.json").read_text())
        excluded = next(
            finding
            for section in data["sections"]
            for finding in section["findings"]
            if not finding.get("scoreIncluded", True)
        )
        excluded.pop("closureKind")
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken.bundle.json"
            broken.write_text(json.dumps(data))
            result = subprocess.run(
                [sys.executable, ROOT / "scripts/validate_bundle.py", broken],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("closureKind", result.stdout)

    def test_rulings_ledger_is_enforced_on_current_bundles(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from validate_bundle import load_rulings, validate_rulings

        rulings = load_rulings()
        self.assertTrue(rulings)
        finding = {"findingId": "ZSA-TEST", "severity": "CRITICA", "scoreIncluded": True, "status": "still-open"}
        cases = [
            ({"decision": "close"}, "closureKind refuted"),
            ({"decision": "accept", "severity": "ALTA"}, "status must be accepted-risk"),
            ({"decision": "severity", "severity": "ALTA"}, "severity must be ALTA"),
        ]
        for ruling, message in cases:
            ruling = {"findingId": "ZSA-TEST", "date": "2026-11-02", "source": "test", **ruling}
            errors = validate_rulings([dict(finding)], [ruling], "2026-11-03T00:00:00Z")
            self.assertTrue(any(message in error for error in errors), errors)
            self.assertEqual([], validate_rulings([dict(finding)], [ruling], "2026-11-01T00:00:00Z"))
        remediated = {**finding, "scoreIncluded": False, "closureKind": "remediated"}
        keep = {"findingId": "ZSA-TEST", "decision": "keep", "date": "2026-11-02", "source": "test"}
        self.assertEqual([], validate_rulings([remediated], [keep], "2026-11-03"))
        self.assertTrue(validate_rulings([finding], [keep], ""))

    def test_security_cards_use_security_specific_taxonomy(self):
        contract = (ROOT / "references/report-contract.md").read_text()
        for label in [
            "work: security",
            "security:low",
            "security:medium",
            "security:high",
            "security:critical",
            "security:catastrophic",
        ]:
            self.assertIn(f"`{label}`", contract)
        taxonomy = contract.split("## GitHub card taxonomy", 1)[1]
        self.assertNotIn("`work: bug`", taxonomy)
        self.assertNotIn("`bug:critical`", taxonomy)


if __name__ == "__main__":
    unittest.main()
