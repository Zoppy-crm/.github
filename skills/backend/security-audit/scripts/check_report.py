#!/usr/bin/env python3
"""Fail closed when a rendered report leaks process, people or secrets, drifts from PT-BR, or breaks layout."""

import argparse
import html
import json
import re
from pathlib import Path

from report_snapshots import GITHUB_TITLE
from validate_bundle import REGISTRY_DIR


NAMES_PATH = REGISTRY_DIR / "names.txt"
GITHUB_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
FORBIDDEN = re.compile(
    r"coordenador|coordinator|\bslices?\b|\bfatias?\b|session expired|sess[aã]o expirad|"
    r"quick ?pass|verifica[cç][aã]o r[aá]pida|projected|projetad|proje[cç](?:[aã]o|[õo]es)|"
    r"\bclaude\b|\bcodex\b|"
    r"ghp_|gho_|github_pat_|xox[bp]-|AKIA[0-9A-Z]{12}|chat\.googleapis\.com/v1/spaces/\S*key=|"
    r"hooks\.slack\.com/services/|eyJ[A-Za-z0-9_-]{15,}\.|-----BEGIN|"
    r"[A-Za-z0-9._%+-]+@(?:gmail|outlook|hotmail|yahoo)\.com",
    re.I,
)
ENGLISH = re.compile(
    r"\b(the|and|which|with|before|only|of|is|are|from|into|that|can|this|when|requires|to|for|not|be|by|"
    r"it|its|was|were|has|have|after|without|still|does|returns|needs)\b",
    re.I,
)
PORTUGUESE = re.compile(r"\b(de|da|do|das|dos|que|não|com|para|uma|um|os|as|em|na|no|nos|é|são|ou|pela|pelo|se|ao|à)\b", re.I)
CODE_LIKE = re.compile(r"[(){}=;<>@\[\]]|=>|\w\.\w+\(")
CODE_LIKE_LIMIT = 3
QUOTED_LITERAL = re.compile(r"'[^']{12,}'")
NUMBERED_LINE = re.compile(r"^\s*\d+:", re.M)
MIN_QUOTED_LINE = 8
EXTERNAL_ASSET = re.compile(r"<(?:script|link|img)[^>]+(?:src|href)=\"https?://", re.I)
MARKDOWN_ORDER = ["## Delta", "## " + GITHUB_TITLE, "## Aritmética", "## Lacunas de cobertura", "## Achados"]
HTML_ORDER = ["<h2>Delta", "<h2>" + GITHUB_TITLE, "<h2>Por área"]


def report_paths(bundle_path):
    stem = bundle_path.name.removesuffix(".bundle.json")
    return {kind: bundle_path.with_name(stem + suffix)
            for kind, suffix in [("md", ".md"), ("html", ".html"), ("actionability", "-by-actionability.md")]}


def people(bundle):
    issues = bundle.get("meta", {}).get("githubRemediation", {}).get("issues", [])
    accounts = [person for issue in issues for person in issue.get("assignees", [])]
    accounts += [item.get("author") for issue in issues for item in [issue, *issue.get("pullRequests", [])]]
    logins = {account.get("login") if isinstance(account, dict) else account for account in accounts}
    names = {login for login in logins if isinstance(login, str) and GITHUB_LOGIN.match(login)}
    if NAMES_PATH.is_file():
        names.update(line.strip() for line in NAMES_PATH.read_text().splitlines() if line.strip())
    return names


def allowed_english(bundle):
    issues = bundle.get("meta", {}).get("githubRemediation", {}).get("issues", [])
    allowed = [issue.get("title", "") for issue in issues]
    allowed += [pull.get("title", "") for issue in issues for pull in issue.get("pullRequests", [])]
    for section in bundle["sections"]:
        for finding in section["findings"]:
            for evidence in finding.get("evidence") or []:
                quote = evidence.get("quote") or ""
                if NUMBERED_LINE.search(quote):
                    allowed += [line.strip() for line in quote.split("\n") if len(line.strip()) > MIN_QUOTED_LINE]
    return sorted({text for text in allowed if text}, key=len, reverse=True)


def visible_html(text, *extra_tags):
    for tag in ("style", "script", *extra_tags):
        text = re.sub(rf"<{tag}>.*?</{tag}>", " ", text, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", "\n", text))


def hygiene_errors(name, text, names):
    pattern = FORBIDDEN
    if names:
        pattern = re.compile(FORBIDDEN.pattern + "|" + "|".join(rf"\b{re.escape(n)}\b" for n in names), re.I)
    return [f"{name}: forbidden {match.group(0)!r} near {text[max(0, match.start() - 60):match.end() + 40]!r}"
            for match in pattern.finditer(text)]


def english_errors(name, text, allowed):
    for phrase in allowed:
        text = text.replace(phrase, " ")
    errors = []
    for line in text.split("\n"):
        for sentence in re.split(r"(?<=[.;!?])\s+|\s+—\s+", line):
            if len(CODE_LIKE.findall(sentence)) > CODE_LIKE_LIMIT or NUMBERED_LINE.match(sentence):
                continue
            if re.search(r"\bSELECT\b.*\bFROM\b", sentence) or re.search(r"^\s*(if|for|def|return)\b.*:\s*$", sentence):
                continue
            sentence = QUOTED_LITERAL.sub(" ", sentence)
            english = len(ENGLISH.findall(sentence))
            if english >= 2 and english > len(PORTUGUESE.findall(sentence)):
                errors.append(f"{name}: English prose {sentence.strip()[:200]!r}")
    return list(dict.fromkeys(errors))


def order_errors(name, text, headings):
    positions = [text.find(heading) for heading in headings]
    if min(positions) < 0 or positions != sorted(positions):
        return [f"{name}: sections must appear in order {headings}"]
    return []


def check(bundle_path):
    bundle = json.loads(bundle_path.read_text())
    paths = report_paths(bundle_path)
    raw_html = paths["html"].read_text()
    markdown = paths["md"].read_text()
    actionability = paths["actionability"].read_text()
    names = people(bundle)
    allowed = allowed_english(bundle)
    errors = []
    for name, text in [("HTML", visible_html(raw_html)), ("MD", markdown), ("actionability", actionability)]:
        errors += hygiene_errors(name, text, names)
    errors += english_errors("HTML", visible_html(raw_html, "code"), allowed)
    for name, text in [("MD", markdown), ("actionability", actionability)]:
        errors += english_errors(name, re.sub(r"`[^`]*`", " ", text), allowed)
    errors += order_errors("MD", markdown, MARKDOWN_ORDER)
    errors += order_errors("HTML", raw_html, HTML_ORDER)
    if EXTERNAL_ASSET.search(raw_html):
        errors.append("HTML: external asset reference")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    errors = check(args.bundle)
    print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
