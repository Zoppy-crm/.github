import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = Path.home() / ".local/share/security-audit/baselines"
sys.path.insert(0, str(ROOT / 'scripts'))
from report_snapshots import GITHUB_TITLE, CLOUDFLARE_TITLE, snapshots, validate_snapshots
from render_reports import render_report, scores
from calculate_delta import calculate
from validate_bundle import validate


class CurrentSecuritySnapshots(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads((BASELINES / '2026-09-01.bundle.json').read_text())
        finding = next(f for s in self.bundle['sections'] for f in s['findings'] if f['scoreIncluded'])
        self.issue = {'repository': 'Zoppy-crm/zoppy-api', 'number': 123, 'title': '<script>alert(1)</script> | [x]',
                      'url': 'https://github.com/Zoppy-crm/zoppy-api/issues/123', 'state': 'CLOSED',
                      'assignees': ['owner'], 'projectStatus': 'Done', 'severityLabels': ['security:high'],
                      'findingIds': [finding['findingId']], 'pullRequests': [
                          {'number': 456, 'url': 'https://github.com/Zoppy-crm/zoppy-api/pull/456',
                           'state': 'MERGED', 'baseRefName': 'staging', 'mergedAt': '2026-09-14T00:00:00Z'}],
                      'deployment': {'state': 'unknown', 'evidence': None}}
        self.bundle['meta'].update({'reportAmendmentVersion': 1,
            'githubRemediation': {'observedAt': '2026-09-14T00:00:00Z', 'status': 'complete', 'query': 'work: security',
                                  'coverageGaps': [], 'issues': [self.issue]},
            'cloudflare': {'observedAt': '2026-09-14T00:00:00Z', 'status': 'partial', 'accounts': [], 'zones': [],
                          'checks': [{'surface': 'WAF', 'state': 'unknown', 'summary': '<absent permission>', 'evidence': 'cf safe read'}],
                          'coverageGaps': ['WAF: acesso insuficiente']}})

    def test_markdown_order_and_closed_issue_keeps_risk(self):
        before = scores(self.bundle)[-1]
        rendered = render_report(self.bundle)
        self.assertLess(rendered.index('## Delta'), rendered.index('## ' + GITHUB_TITLE))
        self.assertLess(rendered.index('## ' + GITHUB_TITLE), rendered.index('## Aritmética'))
        self.assertIn('permanece no score', rendered)
        self.assertIn('CLOSED', rendered)
        self.assertIn('MERGED · base staging', rendered)
        self.assertIn('Done', rendered)
        self.assertEqual(810, before)
        self.assertEqual(before, scores(self.bundle)[-1])
        self.assertNotIn('<script>', rendered)
        self.assertIn('\\| \\[x\\]', rendered)
        self.assertIn('WAF: acesso insuficiente', rendered)

    def test_user_selected_issue_scope_does_not_expand_from_registry(self):
        other = next(f for s in self.bundle['sections'] for f in s['findings']
                     if f['findingId'] not in self.issue['findingIds'])
        other['issueUrl'] = 'https://github.com/Zoppy-crm/zoppy-api/issues/99999'
        self.bundle['meta']['githubRemediation']['query'] = 'Exact user-selected issue #123'
        for fmt in ['markdown', 'html']:
            rendered = snapshots(self.bundle, fmt)
            self.assertIn('Exact user-selected issue #123', rendered)
            self.assertIn('1 issues no escopo', rendered)
            self.assertNotIn('/issues/99999', rendered)
        self.assertEqual(810, scores(self.bundle)[-1])

    def test_html_order_escaping_and_safe_links(self):
        self.issue['url'] = 'javascript:alert(1)'
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path, output = Path(tmp) / 'fixture.json', Path(tmp) / 'report.html'
            bundle_path.write_text(json.dumps(self.bundle))
            subprocess.run([sys.executable, ROOT / 'scripts/gen_html.py', bundle_path, output], check=True, capture_output=True)
            rendered = output.read_text()
        self.assertLess(rendered.index('<h2>Delta'), rendered.index('<h2>' + GITHUB_TITLE))
        self.assertLess(rendered.index('<h2>Delta'), rendered.index('KPI combinado ='))
        self.assertLess(rendered.index('<h2>' + CLOUDFLARE_TITLE), rendered.index('<h2>Por área'))
        self.assertNotIn('<script>alert(1)</script>', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('permanece no score', rendered)
        self.assertTrue('<div class="score">810 <span' in rendered)

    def test_roi_rows_link_to_existing_finding_cards(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path, output = Path(tmp) / 'fixture.json', Path(tmp) / 'report.html'
            bundle_path.write_text(json.dumps(self.bundle))
            subprocess.run([sys.executable, ROOT / 'scripts/gen_html.py', bundle_path, output], check=True, capture_output=True)
            rendered = output.read_text()
        roi = re.search(r'<h2>Fila de remediação por ROI</h2>.*?</table>', rendered, re.S).group(0)
        targets = re.findall(r'href="#(ZSA-[^"]+)"', roi)
        self.assertTrue(targets)
        self.assertEqual(roi.count('<tr>') - 1, len(targets))
        card_ids = set(re.findall(r'<details class="f" id="([^"]+)"', rendered))
        self.assertLessEqual(set(targets), card_ids)

    def test_missing_legacy_snapshots_are_explicit_gaps(self):
        self.bundle['meta'].pop('githubRemediation')
        self.bundle['meta'].pop('cloudflare')
        rendered = snapshots(self.bundle, 'html')
        self.assertIn('Snapshot atual do GitHub ausente', rendered)
        self.assertIn('Snapshot atual do Cloudflare ausente', rendered)
        self.assertIn('ausência de registros não comprova', rendered)
        self.assertEqual(2, len(validate_snapshots(self.bundle['meta'])))
        self.bundle['meta'].pop('reportAmendmentVersion')
        self.assertEqual([], validate_snapshots(self.bundle['meta']))

    def test_partial_and_verified_snapshots_require_evidence(self):
        self.assertEqual([], validate_snapshots(self.bundle['meta']))
        self.bundle['meta']['cloudflare']['coverageGaps'] = []
        self.issue['deployment']['state'] = 'verified'
        errors = validate_snapshots(self.bundle['meta'])
        self.assertTrue(any('requires coverageGaps' in e for e in errors))
        self.assertTrue(any('verified deployment requires evidence' in e for e in errors))

    def test_executive_coverage_warning_precedes_delta_without_changing_score(self):
        weights = {'CATASTROFICA': 16, 'CRITICA': 8, 'ALTA': 4, 'MEDIA': 2, 'BAIXA': 1}
        findings = [f for s in self.bundle['sections'] for f in s['findings'] if f.get('scoreIncluded', True)]
        components = {state: sum(weights[f['severity']] for f in findings if f['evidenceState'] == state)
                      for state in ['confirmed', 'inferred', 'unknown']}
        total = scores(self.bundle)[-1]
        self.bundle['meta']['coverageSummary'] = 'AWS não revalidada: 58 achados conservados; acesso <expirado>. Não é medição completa da postura atual.'
        self.bundle['meta']['comparability'] = {'previousRegistryScore': 810, 'currentPriorIdScore': 800,
            'newCoverageScore': total - 800, 'evidenceScores': components}
        report = render_report(self.bundle)
        self.assertLess(report.index('KPI conservador'), report.index('## Delta'))
        self.assertIn('800 pts + novos IDs/cobertura: 10 pts = 810 pts', report)
        self.assertIn('AWS não revalidada', report)
        self.assertIn('Pontos por evidência atual:', report)
        self.assertEqual(total, scores(self.bundle)[-1])
        self.assertEqual([], validate(self.bundle)['errors'])
        with tempfile.TemporaryDirectory() as tmp:
            path, output = Path(tmp) / 'fixture.json', Path(tmp) / 'fixture.html'
            path.write_text(json.dumps(self.bundle))
            subprocess.run([sys.executable, ROOT / 'scripts/gen_html.py', path, output], check=True, capture_output=True)
            html = output.read_text()
        self.assertLess(html.index('KPI conservador'), html.index('<h2>Delta'))
        self.assertTrue('AWS não revalidada' in html)
        self.assertTrue('&lt;expirado&gt;' in html)
        self.bundle['meta']['comparability']['newCoverageScore'] += 1
        self.assertTrue(any('subtotals must equal KPI' in e for e in validate(self.bundle)['errors']))
        self.bundle['meta']['comparability']['evidenceScores']['unknown'] += 1
        self.assertTrue(any('must reproduce current' in e for e in validate(self.bundle)['errors']))

    def test_false_refutation_reopened_is_report_correction(self):
        previous = copy.deepcopy(self.bundle)
        finding = next(f for s in previous['sections'] for f in s['findings']
                       if not f.get('scoreIncluded', True) and f.get('closureKind') == 'refuted')
        current = copy.deepcopy(previous)
        reopened = next(f for s in current['sections'] for f in s['findings'] if f['findingId'] == finding['findingId'])
        reopened.update(scoreIncluded=True, status='open', evidenceState='confirmed')
        reopened.pop('closureKind')
        calculate(previous, current)
        delta = current['meta']['delta']
        self.assertEqual([], delta['items']['introduced'])
        self.assertEqual([], delta['items']['refuted'])
        self.assertEqual(1, len(delta['items']['reclassified']))
        item = delta['items']['reclassified'][0]
        self.assertEqual('report-correction', item['changeKind'])
        self.assertEqual(0, item['fromPoints'])
        self.assertGreater(item['delta'], 0)
        self.assertEqual(delta['fromScore'] + item['delta'], delta['toScore'])
        self.assertIn('correção de encerramento anterior', render_report(current))
        with tempfile.TemporaryDirectory() as tmp:
            path, output = Path(tmp) / 'fixture.json', Path(tmp) / 'fixture.html'
            path.write_text(json.dumps(current))
            subprocess.run([sys.executable, ROOT / 'scripts/gen_html.py', path, output], check=True, capture_output=True)
            self.assertTrue('correção de encerramento anterior' in output.read_text())

    def test_previous_remediation_error_and_real_regression_are_distinct(self):
        for previous_closure in ['remediated', 'refuted']:
            with self.subTest(previous_closure=previous_closure):
                previous = copy.deepcopy(self.bundle)
                finding = next(f for s in previous['sections'] for f in s['findings'] if not f.get('scoreIncluded', True))
                finding['closureKind'] = previous_closure
                current = copy.deepcopy(previous)
                reopened = next(f for s in current['sections'] for f in s['findings'] if f['findingId'] == finding['findingId'])
                reopened.update(scoreIncluded=True, status='open', evidenceState='confirmed',
                                reopenReason='prior-report-error', reopenNotes='Same vulnerable code exists at both pinned cutoffs.')
                reopened.pop('closureKind')
                calculate(previous, current)
                delta = current['meta']['delta']
                self.assertEqual([], delta['items']['introduced'])
                self.assertEqual('report-correction', delta['items']['reclassified'][0]['changeKind'])
                self.assertEqual(previous_closure, delta['items']['reclassified'][0]['previousClosureKind'])
                reopened.pop('reopenNotes')
                with self.assertRaisesRegex(ValueError, 'confirmed current evidence and reopenNotes'):
                    calculate(previous, current)
                if previous_closure == 'remediated':
                    reopened.pop('reopenReason')
                    for origin, category in [('introduced-since', 'introduced'), ('undetermined', 'undetermined')]:
                        reopened['origin'] = origin
                        calculate(previous, current)
                        self.assertEqual([], current['meta']['delta']['items']['reclassified'])
                        self.assertEqual(1, len(current['meta']['delta']['items'][category]))

    def test_instructions_preserve_progress_and_require_both_surfaces(self):
        scope = (ROOT / 'references/audit-scope.md').read_text()
        self.assertNotIn('the next message starts `Blocked:`', scope)
        self.assertIn('continue every independent slice', scope)
        self.assertIn('Cloudflare scope via cf CLI', scope)
        self.assertIn('live GitHub remediation-state ingestion', scope)


if __name__ == '__main__':
    unittest.main()
