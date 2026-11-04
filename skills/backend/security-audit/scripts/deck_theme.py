"""Reuse the installed zoppy-deck visual source without its slide navigation/layout."""
import base64
import importlib.util
import re
from pathlib import Path


def load_deck():
    roots = [Path(__file__).resolve().parents[2]]
    roots.extend(Path.home() / name / 'skills' for name in ['.codex', '.agents', '.claude'])
    for root in roots:
        script = root / 'zoppy-deck/scripts/build_deck.py'
        if script.is_file():
            spec = importlib.util.spec_from_file_location('zoppy_deck_theme_source', script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError('Install zoppy-deck before rendering the security audit HTML.')


def theme_css():
    deck = load_deck()
    tokens = re.search(r':root\s*\{[^}]+\}', deck.CSS)
    if not tokens:
        raise ValueError('zoppy-deck CSS has no root design tokens.')
    font = base64.b64encode(deck.FONT.read_bytes()).decode('ascii')
    font_face = ("@font-face{font-family:'InterEmbedded';src:url(data:font/otf;base64," + font +
                 ") format('opentype');font-weight:400;font-style:normal;font-display:block}")
    selectors = ['.brand', '.brand::before', '.eyebrow', '.statrow', '.stat',
                 '.stat .n', '.stat .k', '.stat .d', '.pill', '.p-cat', '.p-cri',
                 '.p-alt', '.p-med', '.p-bai', '.note', '.note.warn', '.note.ok', '.note.crit']
    rules = []
    for selector in selectors:
        rule = re.search(r'(?m)^' + re.escape(selector) + r'\s*\{[^}]+\}', deck.CSS)
        if not rule:
            raise ValueError(f'zoppy-deck CSS is missing {selector}.')
        rules.append(rule.group(0))
    return '\n'.join([font_face, tokens.group(0), *rules])
