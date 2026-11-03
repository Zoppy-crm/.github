import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = Path.home() / ".local/share/security-audit/baselines"
sys.path.insert(0, str(ROOT / 'scripts'))
from deck_theme import load_deck, theme_css


class DeckThemeContract(unittest.TestCase):
    def test_report_embeds_actual_deck_font_and_tokens_without_slide_shell(self):
        deck = load_deck()
        theme = theme_css()
        self.assertIn(base64.b64encode(deck.FONT.read_bytes()).decode(), theme)
        self.assertIn('--purple:#7B3DFF', theme)
        self.assertIn('--blue:#002E73', theme)
        self.assertIn('.brand::before', theme)
        self.assertNotIn('position:fixed', theme)
        self.assertNotIn('overflow:hidden', theme)
        self.assertNotIn('.slide', theme)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'report.html'
            subprocess.run([sys.executable, ROOT / 'scripts/gen_html.py',
                            BASELINES / '2026-09-14.bundle.json', out],
                           check=True, capture_output=True)
            rendered = out.read_text()
        self.assertIn(theme, rendered)
        self.assertIn('class="statrow"', rendered)
        self.assertIn('data-f="all"', rendered)
        self.assertIn('data-x="expand"', rendered)
        self.assertEqual(248, rendered.count('<details class="f"'))
        self.assertIn('<div class="score">694 <span>', rendered)
        self.assertIn('11 issues no escopo', rendered)
        self.assertLess(rendered.index('<h2>Delta'), rendered.index('<h2>GitHub'))


if __name__ == '__main__':
    unittest.main()
