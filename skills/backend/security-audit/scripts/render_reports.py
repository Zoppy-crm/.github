#!/usr/bin/env python3
"""Render canonical PT-BR Markdown and actionability views from a bundle."""

import argparse
import json
from collections import Counter
from pathlib import Path

from report_snapshots import snapshots, executive_coverage, anchored_ids, finding_ref


WEIGHTS = {"CATASTROFICA": 16, "CRITICA": 8, "ALTA": 4, "MEDIA": 2, "BAIXA": 1}
LABELS = {
    "CATASTROFICA": "Catastrófica",
    "CRITICA": "Crítica",
    "ALTA": "Alta",
    "MEDIA": "Média",
    "BAIXA": "Baixa",
}
ORDER = list(WEIGHTS)
DELTA_LABELS = {
    "remediated": "Remediado",
    "refuted": "Refutado/corrigido",
    "reclassified": "Reclassificado",
    "expanded": "Cobertura ampliada",
    "introduced": "Introduzido",
    "undetermined": "Data de introdução indeterminada",
}


def included(section):
    return [finding for finding in section.get("findings", []) if finding.get("scoreIncluded", True)]


def evidence_lines(finding):
    lines = []
    for evidence in finding.get("evidence") or finding.get("ev") or []:
        if isinstance(evidence, dict):
            location = evidence.get("location", "")
            quote = evidence.get("quote", "")
            lines.append(f"- `{location}` — {quote}")
        else:
            lines.append(f"- {evidence}")
    return lines or ["- Evidência histórica preservada no bundle; requer revalidação atual."]


def scores(bundle):
    all_findings = [finding for section in bundle["sections"] for finding in included(section)]
    privacy = [finding for section in bundle["sections"] if section.get("key") == "privacidade" for finding in included(section)]
    total = sum(WEIGHTS[finding["severity"]] for finding in all_findings)
    privacy_score = sum(WEIGHTS[finding["severity"]] for finding in privacy)
    return all_findings, total - privacy_score, privacy_score, total


def render_delta(delta, ids):
    if not delta:
        return []
    totals = delta["totals"]
    equation = [str(delta["fromScore"])]
    for category in DELTA_LABELS:
        value = totals.get(category, 0)
        equation.append(f"{'+' if value >= 0 else '−'} {abs(value)} {DELTA_LABELS[category].lower()}")
    equation.append(f"= **{delta['toScore']}**")
    lines = [
        f"## Delta — o que mudou desde {delta.get('fromAudit', 'a avaliação anterior')}",
        "",
        " ".join(equation),
        "",
    ]
    for category, label in DELTA_LABELS.items():
        entries = delta["items"].get(category) or []
        lines += [f"### {label} ({totals.get(category, 0):+d} pts)", ""]
        if not entries:
            lines += ["- Nenhum.", ""]
            continue
        for entry in entries:
            before = entry.get("fromSeverity")
            after = entry.get("toSeverity")
            transition = ""
            if before and after:
                transition = f" · {LABELS[before]} → {LABELS[after]}"
            elif before:
                transition = f" · {LABELS[before]} → fora do score"
            elif after:
                if entry.get("changeKind") == "report-correction":
                    transition = f" · correção de encerramento anterior: fora do score → {LABELS[after]}"
                elif entry.get("changeKind") in {"regression", "reopened"}:
                    transition = f" · reaberto no score como {LABELS[after]}"
                else:
                    transition = f" · novo no score como {LABELS[after]}"
            lines.append(
                f"- {finding_ref(entry['findingId'], ids, 'markdown')} **{entry['title']}**{transition} · **{entry['delta']:+d} pts**"
            )
        lines.append("")
    return lines



def render_action_plan(plan, ids):
    if not plan:
        return []
    lines = ["", f"## {plan.get('title', 'Plano de ação')}", "", plan.get("intro", ""), ""]
    for phase in plan.get("phases", []):
        lines += [f"### {phase['name']} (−{phase['points']} pts → {phase['scoreAfter']})", "", phase.get("summary", ""), "",
                  "| Achado | Severidade | Tamanho | Pontos | Ação |", "|---|---|---|---:|---|"]
        for item in phase["items"]:
            lines.append(f"| {finding_ref(item['findingId'], ids, 'markdown')} {item['title']} | {LABELS[item['severity']]} | {item['size']} | {item['points']} | {item['action']} |")
        lines.append("")
    if plan.get("pending"):
        lines += ["### Pendente de decisão", ""] + [f"- {entry}" for entry in plan["pending"]] + [""]
    return lines


def render_report(bundle):
    meta = bundle.get("meta", {})
    findings, security, privacy, total = scores(bundle)
    counts = Counter(finding["severity"] for finding in findings)
    evidence_counts = Counter(finding.get("evidenceState", "unknown") for finding in findings)
    catastrophic = counts.get("CATASTROFICA", 0)
    ids = anchored_ids(bundle)
    lines = [
        f"# Zoppy — Auditoria de Segurança e Privacidade · {meta.get('date', '')}",
        "",
        f"**Conclusão:** {len(findings)} achados incluídos no score; {catastrophic} Catastróficos mantidos no registro. Verifique o estado da evidência antes de interpretar a exposição operacional.",
        "",
        f"**Segurança:** {security} · **Privacidade:** {privacy} · **KPI combinado:** {total}",
        "",
        f"**Estado da evidência:** {evidence_counts.get('confirmed', 0)} confirmados · {evidence_counts.get('inferred', 0)} inferidos · {evidence_counts.get('unknown', 0)} desconhecidos/conservados.",
        "",
    ]
    if meta.get("actionPlan"):
        lines += ["**[Ir para o plano de ação ↓](#plano-de-ação)**", ""]
    lines += [executive_coverage(bundle, "markdown")]
    lines += render_delta(meta.get("delta"), ids)
    lines += [snapshots(bundle, "markdown")]
    lines += [
        "",
        "## Aritmética",
        "",
        " + ".join(f"{counts.get(severity, 0)}×{WEIGHTS[severity]}" for severity in ORDER) + f" = **{total}**",
        "",
        "| Severidade | Qtd | Peso | Subtotal |",
        "|---|---:|---:|---:|",
    ]
    for severity in ORDER:
        lines.append(f"| {LABELS[severity]} | {counts.get(severity, 0)} | {WEIGHTS[severity]} | {counts.get(severity, 0) * WEIGHTS[severity]} |")

    reconciliation = meta.get("reconciliation") or {}
    if reconciliation and not meta.get("delta"):
        lines += [
            "",
            "## Tendência e reconciliação",
            "",
            (
                f"`{reconciliation.get('baseline', 0)} − {reconciliation.get('remediated', 0)} remediados "
                f"+ ({reconciliation.get('rerating', 0)}) reclassificação "
                f"+ {reconciliation.get('introduced', 0)} introduzidos "
                f"+ {reconciliation.get('coverageChange', 0)} cobertura ampliada "
                f"+ {reconciliation.get('undetermined', 0)} indeterminados = {total}`"
            ),
            "",
            "Uma sessão de autenticação expirada não apaga evidência. Achados anteriores sem revalidação atual permanecem pontuados conservadoramente até serem refutados por evidência primária.",
        ]

    lines += ["", "## Lacunas de cobertura", ""]
    gaps = meta.get("coverageGaps") or []
    lines += [f"- {gap}" for gap in gaps] or ["- Consulte o manifesto e o inventário do bundle para o escopo congelado."]

    lines += ["", "## Achados", ""]
    index = 0
    for section in bundle["sections"]:
        section_findings = included(section)
        if not section_findings:
            continue
        lines += [f"### {section['label']}", ""]
        for finding in sorted(section_findings, key=lambda item: -WEIGHTS[item["severity"]]):
            index += 1
            lines += [
                f"<a id=\"{finding.get('findingId', '')}\"></a>",
                "",
                f"#### {index}. {finding.get('title', '')}",
                "",
                f"**ID:** `{finding.get('findingId', '')}` · **Severidade:** {LABELS[finding['severity']]} ({WEIGHTS[finding['severity']]} pts) · **Size:** {finding.get('size', '')} · **Status:** {finding.get('status', '')}",
                "",
                f"**Evidência:** {finding.get('evidenceState', '')} · **Origem:** {finding.get('origin', '')} · **Pré-condição:** {finding.get('precondition', '')} · **Probabilidade:** {finding.get('likelihood', '')}",
                "",
                f"**Caminho de ataque / impacto.** {finding.get('attackPath') or finding.get('attack') or finding.get('impact') or ''}",
                "",
                "**Evidência.**",
                "",
                *evidence_lines(finding),
                "",
                f"**Correção.** {finding.get('recommendedFix') or finding.get('fix') or ''}",
                "",
                f"**Verificação.** {finding.get('verification') or ''}",
                "",
            ]
            if finding.get("issueUrl"):
                lines += [f"**Issue:** {finding['issueUrl']}", ""]
    lines += render_action_plan(meta.get("actionPlan"), ids)
    return "\n".join(lines).rstrip() + "\n"


def render_actionability(bundle, report_name):
    findings, _, _, _ = scores(bundle)
    ids = anchored_ids(bundle)
    tiers = {"A": [], "B": [], "C": [], "D": []}
    for finding in findings:
        size = finding.get("size", "M")
        tier = "A" if size == "XS" else "B" if size == "S" else "C" if size == "M" else "D"
        tiers[tier].append(finding)
    lines = ["# Fila por acionabilidade", ""]
    labels = {"A": "drop-in", "B": "uma verificação prévia", "C": "coordenação ou migração", "D": "programa grande"}
    for tier in "ABCD":
        lines += [f"## Tier {tier} — {labels[tier]}", ""]
        for finding in sorted(tiers[tier], key=lambda item: -WEIGHTS[item["severity"]]):
            issue = f" · {finding['issueUrl']}" if finding.get("issueUrl") else ""
            lines.append(f"- **{LABELS[finding['severity']]} · {finding.get('size', '')}** — {finding_ref(finding.get('findingId', ''), ids, 'markdown', report_name)} — {finding.get('title', '')}{issue}")
        if not tiers[tier]:
            lines.append("- Nenhum.")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument("actionability", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.bundle.read_text())
    args.report.write_text(render_report(bundle))
    args.actionability.write_text(render_actionability(bundle, args.report.name))


if __name__ == "__main__":
    main()
