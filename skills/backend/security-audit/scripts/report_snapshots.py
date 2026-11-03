"""Render observed work tracking and edge controls without changing risk arithmetic."""
import html
from collections import Counter
from urllib.parse import urlsplit

GITHUB_TITLE = 'GitHub — estado atual das correções de segurança'
CLOUDFLARE_TITLE = 'Cloudflare — controles e cobertura atuais'
GITHUB_NOTE = ('O risco auditado vem do registro de achados. Status do board, issue encerrada e PR merged '
               'descrevem o trabalho; a retirada de pontos exige evidência independente da correção. '
               'Deploy verificado é informado separadamente.')
STATUS = {'complete': 'completo', 'partial': 'parcial', 'unknown': 'desconhecido',
          'verified': 'verificado', 'unverified': 'não verificado',
          'confirmed': 'confirmado', 'inferred': 'inferido', 'refuted': 'refutado'}


def md(value):
    value = html.escape(str(value if value is not None else 'Desconhecido'))
    for char in ('\\', '`', '*', '_', '[', ']', '|'):
        value = value.replace(char, '\\' + char)
    return value.replace('\n', ' ').replace('\r', ' ')


def safe_url(value):
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.netloc or any(c.isspace() for c in value):
        return None
    return value.replace('(', '%28').replace(')', '%29')


def link(label, url, fmt):
    target = safe_url(url)
    text = html.escape(str(label)) if fmt == 'html' else md(label)
    if not target:
        return text
    return f'<a href="{html.escape(target, quote=True)}">{text}</a>' if fmt == 'html' else f'[{text}]({target})'


def anchored_ids(bundle):
    return {f.get('findingId') for s in bundle['sections'] for f in s['findings'] if f.get('scoreIncluded', True) and f.get('findingId')}


def finding_ref(finding_id, ids, fmt, target=''):
    if fmt == 'html':
        code = f'<code>{html.escape(str(finding_id))}</code>'
        return f'<a href="#{html.escape(str(finding_id), quote=True)}">{code}</a>' if finding_id in ids else code
    code = f'`{finding_id}`'
    return f'[{code}]({target}#{finding_id})' if finding_id in ids else code


def finding_risk(bundle, issue, fmt):
    escape = html.escape if fmt == 'html' else md
    ids = issue.get('findingIds') or []
    found = {f.get('findingId'): f for s in bundle['sections'] for f in s['findings']}
    anchors = anchored_ids(bundle)
    if not ids:
        return escape('Sem vínculo confirmado com achado; risco não reconciliado')
    parts = []
    for key in ids:
        finding = found.get(key)
        ref = finding_ref(key, anchors, fmt)
        if not finding:
            parts.append(ref + escape(': achado não localizado'))
        elif finding.get('scoreIncluded', True):
            parts.append(ref + escape(f': permanece no score ({finding["severity"]}; evidência {finding.get("evidenceState", "unknown")})'))
        else:
            parts.append(ref + escape(f': fora do score ({finding.get("closureKind", "desconhecido")})'))
    return '; '.join(parts)


def executive_coverage(bundle, fmt):
    meta = bundle.get('meta', {})
    summary = meta.get('coverageSummary')
    comparison = meta.get('comparability')
    if not summary and not comparison:
        return ''
    parts = ['KPI conservador.']
    if summary:
        parts.append(str(summary))
    if comparison:
        parts.append(
            f"Registro anterior: {comparison['previousRegistryScore']} pts. "
            f"Subtotal atual dos mesmos IDs: {comparison['currentPriorIdScore']} pts + "
            f"novos IDs/cobertura: {comparison['newCoverageScore']} pts = "
            f"{comparison['currentPriorIdScore'] + comparison['newCoverageScore']} pts. "
            'Comparamos os mesmos achados entre auditorias. Os casos sem revalidação conclusiva mantêm a pontuação anterior e estão identificados como não verificados.'
        )
        evidence = comparison['evidenceScores']
        parts.append(
            f"Pontos por evidência atual: {evidence['confirmed']} confirmados · "
            f"{evidence['inferred']} inferidos · {evidence['unknown']} desconhecidos/conservados."
        )
    text = ' '.join(parts)
    return '<div class="note"><b>Cobertura e comparabilidade.</b> ' + html.escape(text) + '</div>' if fmt == 'html' else '**Cobertura e comparabilidade.** ' + md(text) + '\n'


def snapshots(bundle, fmt):
    escape = html.escape if fmt == 'html' else md
    lines = []

    def heading(title):
        lines.append(f'<h2>{title}</h2>' if fmt == 'html' else f'\n## {title}\n')

    def paragraph(value):
        lines.append(f'<p>{escape(str(value))}</p>' if fmt == 'html' else f'{escape(value)}\n')

    def table(headers, rows):
        if fmt == 'html':
            lines.append('<div class="scroll"><table><thead><tr>' + ''.join(f'<th>{escape(h)}</th>' for h in headers) + '</tr></thead><tbody>')
            lines.extend('<tr>' + ''.join(f'<td class="l">{v}</td>' for v in row) + '</tr>' for row in rows)
            lines.append('</tbody></table></div>')
        else:
            lines.extend(['| ' + ' | '.join(headers) + ' |', '|' + '|'.join('---' for _ in headers) + '|'])
            lines.extend('| ' + ' | '.join(row) + ' |' for row in rows)
            lines.append('')

    meta = bundle.get('meta', {})
    gh = meta.get('githubRemediation') or {}
    heading(GITHUB_TITLE)
    paragraph(GITHUB_NOTE)
    paragraph(f"Observado em: {gh.get('observedAt') or 'Desconhecido'} · Cobertura: {STATUS.get(gh.get('status'), 'desconhecido')}")
    if gh.get('query'):
        paragraph('Consulta: ' + str(gh['query']))
    issues = gh.get('issues') or []
    if issues:
        states = Counter(issue.get('state') or 'Desconhecido' for issue in issues)
        boards = Counter(issue.get('projectStatus') or 'Desconhecido' for issue in issues)
        paragraph(f"{len(issues)} issues no escopo · {states.get('OPEN', 0)} abertas · {states.get('CLOSED', 0)} encerradas")
        paragraph('Project #7: ' + ' · '.join(f'{state}: {count}' for state, count in sorted(boards.items())))
        risk = gh.get('riskSummary')
        if risk:
            paragraph(f"Nos {risk['findingCount']} achados vinculados: {risk['remediated']} remediados, {risk['refuted']} refutados, {risk['partiallyFixed']} parcialmente corrigidos e {risk['remaining']} ainda abertos. Pontos deste recorte: {risk['previousScore']} → {risk['currentScore']}.")
        rows = []
        for issue in issues:
            pull_requests = []
            for pr in issue.get('pullRequests') or []:
                pull_requests.append(link(f"#{pr.get('number', '?')}", pr.get('url'), fmt) + escape(f" · {pr.get('state') or 'Desconhecido'} · base {pr.get('baseRefName') or 'Desconhecida'} · merge {pr.get('mergedAt') or 'não confirmado'}"))
            deployment = issue.get('deployment') or {}
            deployment_text = STATUS.get(deployment.get('state'), 'desconhecido')
            if deployment.get('evidence'):
                deployment_text += ': ' + str(deployment['evidence'])
            rows.append([
                link(f"{issue.get('repository', '')}#{issue.get('number', '?')} — {issue.get('title', '')}", issue.get('url'), fmt),
                escape(issue.get('state') or 'Desconhecido'),
                escape(', '.join(issue.get('assignees') or []) or 'Sem responsável atribuído'),
                escape(issue.get('projectStatus') or 'Desconhecido'),
                escape(', '.join(issue.get('severityLabels') or []) or 'Sem label de severidade'),
                finding_risk(bundle, issue, fmt),
                ('<br>' if fmt == 'html' else '; ').join(pull_requests) or 'Nenhum PR vinculado confirmado',
                escape(deployment_text),
            ])
        table(['Issue', 'Estado', 'Responsável', 'Status no Project #7', 'Severidade no GitHub', 'Risco auditado', 'PRs vinculados / base', 'Deploy'], rows)
    else:
        paragraph('Nenhuma issue encontrada no escopo consultado.' if gh.get('status') == 'complete' else 'Inventário de issues indisponível ou incompleto; ausência de registros não comprova ausência de pendências.')
    for gap in gh.get('coverageGaps') or ([] if gh else ['Snapshot atual do GitHub ausente.']):
        paragraph('Lacuna: ' + str(gap))

    cf = meta.get('cloudflare') or {}
    heading(CLOUDFLARE_TITLE)
    paragraph(f"Observado em: {cf.get('observedAt') or 'Desconhecido'} · Cobertura: {STATUS.get(cf.get('status'), 'desconhecido')} · Fonte: cf CLI, somente leitura")
    for field, label in [('accounts', 'Contas'), ('zones', 'Zonas')]:
        values = cf.get(field) or []
        paragraph(label + ': ' + (', '.join(f"{v.get('name', '')} ({v.get('id', '')})" for v in values) or 'Inventário não confirmado'))
    checks = cf.get('checks') or []
    if checks:
        table(['Superfície', 'Evidência', 'Estado observado', 'Fonte'], [
            [escape(str(check.get('surface', ''))), escape(STATUS.get(check.get('state'), 'desconhecido')),
             escape(str(check.get('summary', ''))), escape(str(check.get('evidence', 'Desconhecida')))] for check in checks])
    else:
        paragraph('Controles ainda não verificados; nenhuma conclusão de segurança é inferida da falta de acesso.')
    for gap in cf.get('coverageGaps') or ([] if cf else ['Snapshot atual do Cloudflare ausente.']):
        paragraph('Lacuna: ' + str(gap))
    if meta.get('qualitativeChanges'):
        heading('Mudanças observadas sem alteração de pontos')
        for change in meta['qualitativeChanges']:
            paragraph(change)
    if meta.get('unscoredCandidates'):
        heading('Investigações pendentes — fora do KPI')
        for candidate in meta['unscoredCandidates']:
            paragraph(f"{candidate['candidateId']} — {candidate['title']}")
            paragraph(candidate['reasonUnscored'])
            paragraph('Caminho observado: ' + candidate['attackPath'])
            paragraph('Correção proposta: ' + candidate['recommendedFix'])
            paragraph('Verificação necessária: ' + candidate['verification'])
    return '\n'.join(lines)


def validate_snapshots(meta):
    errors = []
    if meta.get('reportAmendmentVersion') != 1:
        return errors
    for name in ['githubRemediation', 'cloudflare']:
        snapshot = meta.get(name)
        if not isinstance(snapshot, dict):
            errors.append(f'meta.{name}: current snapshot or explicit unknown gap required')
            continue
        if not snapshot.get('observedAt'):
            errors.append(f'meta.{name}: observation timestamp required')
        for field in ['observedAt', 'status', 'coverageGaps']:
            if field not in snapshot:
                errors.append(f'meta.{name}: missing {field}')
        if snapshot.get('status') not in {'complete', 'partial', 'unknown'}:
            errors.append(f'meta.{name}: invalid status')
        if snapshot.get('status') in {'partial', 'unknown'} and not snapshot.get('coverageGaps'):
            errors.append(f'meta.{name}: incomplete snapshot requires coverageGaps')
        fields = ['issues'] if name == 'githubRemediation' else ['accounts', 'zones', 'checks']
        for field in fields + ['coverageGaps']:
            if not isinstance(snapshot.get(field), list):
                errors.append(f'meta.{name}.{field}: list required')
        if name == 'githubRemediation':
            issues = snapshot.get('issues')
            for issue in issues if isinstance(issues, list) else []:
                if not isinstance(issue, dict):
                    errors.append('meta.githubRemediation.issues: each issue must be an object')
                    continue
                for field in ['repository', 'number', 'title', 'url', 'state', 'assignees', 'projectStatus', 'severityLabels', 'findingIds', 'pullRequests', 'deployment']:
                    if field not in issue:
                        errors.append(f'meta.githubRemediation issue {issue.get("number")}: missing {field}')
                for field in ['assignees', 'severityLabels', 'findingIds', 'pullRequests']:
                    if not isinstance(issue.get(field), list):
                        errors.append(f'meta.githubRemediation issue {issue.get("number")}: {field} must be a list')
                deploy = issue.get('deployment') or {}
                if not isinstance(deploy, dict):
                    errors.append(f'meta.githubRemediation issue {issue.get("number")}: deployment must be an object')
                    continue
                if deploy.get('state') not in {'verified', 'unverified', 'unknown'}:
                    errors.append(f'meta.githubRemediation issue {issue.get("number")}: invalid deployment state')
                if deploy.get('state') == 'verified' and not deploy.get('evidence'):
                    errors.append(f'meta.githubRemediation issue {issue.get("number")}: verified deployment requires evidence')
    return errors
