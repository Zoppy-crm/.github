#!/usr/bin/env python3
"""Render the Zoppy security audit report to a single self-contained HTML file.

Reads a combined JSON bundle and emits HTML with no external assets (works offline,
survives being emailed around). Usage: gen_html.py <bundle.json> <out.html>
"""
import json, sys, html, datetime
from report_snapshots import snapshots, executive_coverage, anchored_ids, finding_ref
from deck_theme import theme_css

W = {'CATASTROFICA': 16, 'CRITICA': 8, 'ALTA': 4, 'MEDIA': 2, 'BAIXA': 1}
E = {'XS': 1, 'S': 2, 'M': 5, 'L': 13, 'XL': 34}
LB = {'CATASTROFICA': 'Catastrófica', 'CRITICA': 'Crítica', 'ALTA': 'Alta', 'MEDIA': 'Média', 'BAIXA': 'Baixa'}
ORDER = ['CATASTROFICA', 'CRITICA', 'ALTA', 'MEDIA', 'BAIXA']
COLOR = {'CATASTROFICA': 'var(--crit)', 'CRITICA': 'var(--crit)', 'ALTA': 'var(--warn)', 'MEDIA': 'var(--info)', 'BAIXA': 'var(--neutral)'}
PILL = {'CATASTROFICA': 'p-cat', 'CRITICA': 'p-cri', 'ALTA': 'p-alt', 'MEDIA': 'p-med', 'BAIXA': 'p-bai'}
DELTA_LABELS = {
    'remediated': 'Remediado',
    'refuted': 'Refutado/corrigido',
    'reclassified': 'Reclassificado',
    'expanded': 'Cobertura ampliada',
    'introduced': 'Introduzido',
    'undetermined': 'Data de introdução indeterminada',
}


def alert(counts):
    if counts.get('CATASTROFICA'):
        return '\u26a0', 'Há vulnerabilidade Catastrófica em aberto: exige resposta emergencial e escalonamento executivo.'
    if counts.get('CRITICA'):
        return '\u26a0', 'Há vulnerabilidade Crítica em aberto: mitigação ou correção imediata.'
    return '', ''


def esc(s):
    return html.escape(str(s if s is not None else ''))


def bar(counts, total):
    segs = []
    for p in ORDER:
        n = counts.get(p, 0)
        if not n:
            continue
        pts = n * W.get(p,1)
        pct = pts / total * 100 if total else 0
        segs.append(f'<div class="seg" style="width:{pct:.2f}%;background:{COLOR[p]}" '
                    f'title="{LB[p]}: {n} findings, {pts} pts"></div>')
    return '<div class="bar">' + ''.join(segs) + '</div>'


def finding_card(i, f, kind):
    pr = f.get('severity') or f.get('priority', 'MEDIA')
    ev = f.get('evidence') or f.get('ev') or []
    rows = []
    for e in ev[:10]:
        if isinstance(e, dict):
            loc, q = e.get('location', ''), e.get('quote', '')
            rows.append(f'<li><code>{esc(loc)}</code> — {esc(q)}</li>')
        else:
            rows.append(f'<li>{esc(e)}</li>')
    extra = ''
    if f.get('regime'):
        extra += f'<span class="tag regime">{esc(f["regime"])}</span>'
    if f.get('articles'):
        extra += f'<span class="tag">{esc(f["articles"])}</span>'
    if f.get('account'):
        extra += f'<span class="tag">{esc(f["account"])}</span>'
    body = f.get('attackPath') or f.get('impact') or ''
    why = f.get('sizeRationale') or f.get('why') or ''
    return f'''
<details class="f" id="{esc(f.get('findingId',''))}" data-pri="{pr}" data-kind="{kind}" data-size="{esc(f.get('size',''))}">
  <summary>
    <span class="pill {PILL[pr]}">{LB[pr]}</span>
    <span class="size">{esc(f.get('size',''))}</span>
    <span class="ttl">{i}. {esc(f.get('title',''))}</span>
  </summary>
  <div class="fb">
    <p class="meta"><code>{esc(f.get('findingId',''))}</code> · {esc(f.get('owasp') or f.get('owaspCategory') or f.get('category') or '')}
       · status: {esc(f.get('status',''))} · evidência: {esc(f.get('evidenceState','unknown'))} · confiança: {esc(f.get('confidence',''))} {extra}</p>
    {f'<p><b>Contexto da avaliação.</b> {esc(f.get("notes"))}</p>' if f.get('notes') else ''}
    <p><b>Caminho de ataque / impacto.</b> {esc(body)}</p>
    <p><b>Evidência.</b></p><ul class="ev">{''.join(rows)}</ul>
    <p><b>Correção.</b> {esc(f.get('recommendedFix',''))}</p>
    <p><b>Como verificar.</b> {esc(f.get('verification',''))}</p>
    {f'<p class="why"><b>Why {esc(f.get("size",""))}.</b> {esc(why)}</p>' if why else ''}
  </div>
</details>'''



def action_plan_html(plan, ids):
    if not plan:
        return ''
    parts = [f'<h2 id="plano-de-acao">{esc(plan.get("title", "Plano de ação"))}</h2>', f'<p class="sub" style="margin:0 0 8px">{esc(plan.get("intro", ""))}</p>']
    for phase in plan.get('phases', []):
        rows = ''.join(
            f'<tr><td>{finding_ref(i["findingId"], ids, "html")}<br>{esc(i["title"])}</td><td>{esc(LB[i["severity"]])}</td><td>{esc(i["size"])}</td><td>{i["points"]}</td><td>{esc(i["action"])}</td></tr>'
            for i in phase['items'])
        parts.append(f'<h3>{esc(phase["name"])} · −{phase["points"]} pts → {phase["scoreAfter"]}</h3><p class="sub" style="margin:0 0 8px">{esc(phase.get("summary", ""))}</p>'
                     f'<div class="scroll"><table><tr><th>Achado</th><th>Severidade</th><th>Tamanho</th><th>Pontos</th><th>Ação</th></tr>{rows}</table></div>')
    if plan.get('pending'):
        parts.append('<h3>Pendente de decisão</h3><div class="note"><ul>' + ''.join(f'<li>{esc(entry)}</li>' for entry in plan['pending']) + '</ul></div>')
    return '\n'.join(parts)


def main():
    bundle = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    sections = bundle['sections']          # [{key,label,findings:[...]}]
    meta = bundle.get('meta', {})

    allf = [(s['key'], f) for s in sections for f in s['findings'] if f.get('scoreIncluded', True)]
    ids = anchored_ids(bundle)
    counts = {}
    for _, f in allf:
        p = f.get('severity') or f.get('priority', 'MEDIA')
        counts[p] = counts.get(p, 0) + 1
    total = sum(counts.get(p, 0) * W.get(p,1) for p in ORDER)
    privacy_total = sum(
        W.get(f.get('severity') or f.get('priority'), 1)
        for s in sections if s.get('key') == 'privacidade'
        for f in s['findings'] if f.get('scoreIncluded', True)
    )
    security_total = total - privacy_total
    g, gnote = alert(counts)
    if counts.get('CATASTROFICA') and all(f.get('evidenceState') == 'unknown' for _, f in allf if f.get('severity') == 'CATASTROFICA'):
        gnote = f"{counts['CATASTROFICA']} achados Catastróficos mantidos conservadoramente; o estado operacional de todos aguarda revalidação."

    # per-section subtotals
    sec_rows = []
    for s in sections:
        c = {}
        for f in s['findings']:
            if not f.get('scoreIncluded', True):
                continue
            p = f.get('severity') or f.get('priority', 'MEDIA')
            c[p] = c.get(p, 0) + 1
        sub = sum(c.get(p, 0) * W.get(p,1) for p in ORDER)
        cells = ''.join(f'<td>{c.get(p,0) or "—"}</td>' for p in ORDER)
        sec_rows.append(f'<tr><td class="l">{esc(s["label"])}</td>{cells}<td><b>{sub}</b></td></tr>')

    # ROI queue
    roi = sorted(allf, key=lambda kf: -(W.get(kf[1].get('severity') or kf[1].get('priority'),1) / E.get(kf[1].get('size', 'M'), 5)))
    roi_rows = ''.join(
        f'<tr><td><span class="pill sm {PILL[f.get("severity") or f.get("priority","MEDIA")]}">{LB[f.get("severity") or f.get("priority","MEDIA")]}</span></td>'
        f'<td>{esc(f.get("size",""))}</td><td>{W.get(f.get("severity") or f.get("priority"),1)}</td>'
        f'<td>{W.get(f.get("severity") or f.get("priority"),1)/E.get(f.get("size","M"),5):.1f}</td>'
        f'<td>{finding_ref(f.get("findingId",""), ids, "html")}<br>{esc(f.get("title",""))}</td></tr>'
        for k, f in roi[:30])

    trend = bundle.get('trend_html', '')
    delta = meta.get('delta') or {}
    if delta:
        totals = delta['totals']
        equation = [str(delta['fromScore'])]
        for category, label in DELTA_LABELS.items():
            value = totals.get(category, 0)
            equation.append(f'{"+" if value >= 0 else "−"} {abs(value)} {label.lower()}')
        equation.append(f'= {delta["toScore"]}')
        blocks = []
        for category, label in DELTA_LABELS.items():
            entries = delta['items'].get(category) or []
            if entries:
                rows = []
                for entry in entries:
                    before, after = entry.get('fromSeverity'), entry.get('toSeverity')
                    transition = ''
                    if before and after:
                        transition = f' · {LB[before]} → {LB[after]}'
                    elif before:
                        transition = f' · {LB[before]} → fora do score'
                    elif after:
                        if entry.get('changeKind') == 'report-correction':
                            transition = f' · correção de encerramento anterior: fora do score → {LB[after]}'
                        elif entry.get('changeKind') in {'regression', 'reopened'}:
                            transition = f' · reaberto no score como {LB[after]}'
                        else:
                            transition = f' · novo no score como {LB[after]}' 
                    rows.append(f'<li>{finding_ref(entry["findingId"], ids, "html")} <b>{esc(entry["title"])}</b>{transition} · <b>{entry["delta"]:+d} pts</b></li>')
                content = '<ul>' + ''.join(rows) + '</ul>'
            else:
                content = '<p>Nenhum.</p>'
            blocks.append(f'<h3>{label} ({totals.get(category, 0):+d} pts)</h3>{content}')
        trend = f'''<h2>Delta — o que mudou desde {esc(delta.get('fromAudit', 'a avaliação anterior'))}</h2>
<div class="note"><b>{esc(' '.join(equation))}</b></div>{''.join(blocks)}'''
    reconciliation = meta.get('reconciliation') or {}
    if not trend and reconciliation:
        trend = f'''<h2>Tendência e reconciliação</h2>
<div class="note"><code>{reconciliation.get('baseline', 0)} − {reconciliation.get('remediated', 0)} remediados
+ ({reconciliation.get('rerating', 0)}) reclassificação + {reconciliation.get('introduced', 0)} introduzidos
+ {reconciliation.get('coverageChange', 0)} cobertura ampliada + {reconciliation.get('undetermined', 0)} indeterminados = {total}</code><br><br>
Achados anteriores sem revalidação atual permanecem pontuados conservadoramente até serem refutados por evidência primária.</div>'''
    gaps = meta.get('coverageGaps') or []
    gap_html = ''
    if gaps:
        gap_html = '<h2>Lacunas de cobertura</h2><div class="note"><ul>' + ''.join(
            f'<li>{esc(gap)}</li>' for gap in gaps
        ) + '</ul></div>'
    inv = bundle.get('inventory_html', '')

    cards = []
    n = 0
    for s in sections:
        cards.append(f'<h3 class="sech">{esc(s["label"])} <span class="cnt">{len(s["findings"])}</span></h3>')
        for f in sorted((f for f in s['findings'] if f.get('scoreIncluded', True)), key=lambda x: -W.get(x.get('severity') or x.get('priority'),1)):
            n += 1
            cards.append(finding_card(n, f, s['key']))

    doc = f'''<!doctype html>
<html lang="pt-BR"><head>
<link rel="icon" href="data:,"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Zoppy — Auditoria de Segurança e Privacidade — {esc(meta.get("date",""))}</title>
<style>
{theme_css()}
*{{box-sizing:border-box}}
:root{{--bg:var(--page);--fg:var(--ink);--mut:var(--neutral);--line:var(--border);--card:var(--surface);--accent:var(--purple)}}
body{{margin:0;background:var(--page);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1240px;margin:0 auto;padding:44px 32px 80px}}
.brand{{margin-bottom:28px}}
h1{{font-size:clamp(30px,4.4vw,52px);line-height:1.12;font-weight:700;color:var(--blue);letter-spacing:-.02em;margin:0 0 16px}}
h2{{font-size:clamp(21px,2.5vw,32px);line-height:1.2;font-weight:700;color:var(--blue);letter-spacing:-.01em;margin:48px 0 20px}}
h3{{color:var(--blue);font-size:17px;margin:26px 0 12px}}
h3.sech{{font-size:13px;color:var(--neutral);text-transform:uppercase;letter-spacing:.07em;margin-top:32px}}
a{{color:var(--purple);text-underline-offset:3px}}a:hover{{color:var(--purple-hover)}}
strong,b{{font-weight:600}}
.cnt{{background:var(--selected);border-radius:999px;padding:2px 8px;font-size:12px;color:var(--purple)}}
.sub{{color:var(--neutral);font-size:13.5px;line-height:1.55;margin:0 0 24px;max-width:100ch}}
.hero{{margin:28px 0}}
.statrow{{grid-template-columns:repeat(3,minmax(0,1fr))}}
.stat .n{{color:var(--blue)}}.stat.total{{border-color:var(--purple);background:var(--selected)}}
.score{{font-size:clamp(34px,5vw,62px);line-height:1;font-weight:700;color:var(--purple);letter-spacing:-.03em;font-variant-numeric:tabular-nums}}
.score span{{font-size:14px;color:var(--neutral);font-weight:400;letter-spacing:0}}
.bar{{display:flex;height:10px;border-radius:999px;overflow:hidden;margin:20px 0 8px;background:var(--border)}}.seg{{height:100%}}
.severity-summary{{font-size:13px;color:var(--neutral)}}
.scroll{{overflow-x:auto;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 20px;margin:16px 0;max-width:100%}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.55;margin:0}}
th,td{{text-align:right;padding:12px 10px;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums;vertical-align:top}}
th:first-child,td:first-child,td.l,td:last-child{{text-align:left}}
th{{color:var(--neutral);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.07em;border-bottom-color:var(--border-strong)}}
tr:last-child td{{border-bottom:none}}tbody tr:hover{{background:var(--hover)}}
.pill.sm{{font-size:10px}}
.size{{display:inline-block;min-width:26px;font-size:11px;color:var(--disabled);font-weight:600}}
.tag{{background:var(--hover);border-radius:999px;padding:2px 8px;font-size:11px;margin-left:6px}}
.tag.regime{{background:var(--info-bg);color:var(--info)}}
details.f{{background:var(--surface);border:1px solid var(--border);border-radius:12px;margin:10px 0}}
details.f[open]{{border-color:var(--purple)}}
details.f{{scroll-margin-top:80px}}
details.f summary{{cursor:pointer;padding:16px;display:flex;gap:12px;align-items:baseline;list-style:none}}
details.f summary::-webkit-details-marker{{display:none}}
details.f summary:hover{{background:var(--hover);border-radius:12px}}
.ttl{{flex:1;min-width:0;overflow-wrap:anywhere;font-weight:600;color:var(--ink)}}
.fb{{padding:4px 20px 20px;border-top:1px solid var(--border);font-size:14px;overflow-wrap:anywhere}}
.meta,.why{{color:var(--neutral);font-size:12.5px}}
ul.ev{{margin:4px 0;padding-left:18px}}ul.ev li{{margin:8px 0;font-size:13px}}
code{{background:var(--hover);padding:2px 5px;border-radius:4px;font-size:12px;overflow-wrap:anywhere;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0;position:sticky;top:0;background:var(--page);padding:12px 0;z-index:5;border-bottom:1px solid var(--border)}}
button{{font-family:var(--font);background:var(--surface);color:var(--ink);border:1px solid var(--border);border-radius:999px;padding:6px 12px;font-size:12px;cursor:pointer;font-weight:600}}
button:hover{{border-color:var(--purple);background:var(--selected)}}button.on{{background:var(--purple);color:white;border-color:var(--purple)}}
a:focus-visible,button:focus-visible,summary:focus-visible{{outline:3px solid var(--purple);outline-offset:3px}}
.note{{margin:16px 0;font-size:14px;overflow-wrap:anywhere}}
@media(max-width:760px){{.wrap{{padding:24px 16px 64px}}.brand{{margin-bottom:20px}}.statrow{{grid-template-columns:1fr}}.stat{{padding:16px}}.stat .n,.score{{font-size:38px}}.scroll{{padding:12px}}.scroll table{{min-width:720px}}details.f summary{{flex-wrap:wrap;padding:12px}}.ttl{{flex-basis:65%}}.fb{{padding:4px 14px 16px}}.controls{{position:static}}h2{{margin-top:36px}}}}
</style></head><body><div class="wrap">

<div class="brand">Zoppy · Engenharia</div>
<h1>Auditoria de Segurança<br>e Privacidade</h1>
<p class="sub">{esc(meta.get("date",""))} · escopo: {esc(meta.get("scope",""))} · método: {esc(meta.get("method",""))}</p>

<div class="hero">
  <div class="statrow">
    <div class="stat"><div class="n">{security_total}</div><div class="k">Segurança</div><div class="d">pontos de exposição</div></div>
    <div class="stat"><div class="n">{privacy_total}</div><div class="k">Privacidade</div><div class="d">LGPD / GDPR</div></div>
    <div class="stat total"><div class="score">{total} <span>pontos</span></div><div class="k">KPI combinado</div><div class="d">Menor é melhor</div></div>
  </div>
  {bar(counts, total)}
  <div class="severity-summary">{' · '.join(f'{LB[p]} {counts.get(p,0)}' for p in ORDER if counts.get(p))}</div>
  {f'<div class="note crit">{esc(gnote)}</div>' if gnote else ''}
</div>

{'<p class="sub"><a href="#plano-de-acao"><b>Ir para o plano de ação ↓</b></a></p>' if meta.get('actionPlan') else ''}
{executive_coverage(bundle, "html")}
{trend}
{snapshots(bundle, "html")}

<div class="note">KPI combinado = Catastrófica×16 + Crítica×8 + Alta×4 + Média×2 + Baixa×1
sobre achados em aberto. Menor é melhor. Segurança e Privacidade são exibidas separadamente antes
do total combinado.</div>


<h2>Por área</h2>
<div class="scroll"><table>
<tr><th>Área</th><th>Catastrófica</th><th>Crítica</th><th>Alta</th><th>Média</th><th>Baixa</th><th>Pontos</th></tr>
{''.join(sec_rows)}
</table></div>

{inv}
{gap_html}

<h2>Fila de remediação por ROI</h2>
<p class="sub" style="margin:0 0 8px">Pontos da severidade ÷ pontos de esforço
(XS=1, S=2, M=5, L=13, XL=34). Use esta fila para sequenciar o trabalho e a severidade para
comunicar o risco; as duas ordens respondem a perguntas diferentes.</p>
<div class="scroll"><table>
<tr><th>Severidade</th><th>Tamanho</th><th>Pontos da severidade</th><th>ROI</th><th>Achado</th></tr>{roi_rows}</table></div>

<h2>Todos os achados</h2>
<div class="controls">
  <button class="on" data-f="all">Todos ({len(allf)})</button>
  {''.join(f'<button data-f="{p}">{LB[p]} ({counts.get(p,0)})</button>' for p in ORDER if counts.get(p))}
  {''.join(f'<button data-f="k:{s["key"]}">{esc(s["label"])}</button>' for s in sections)}
  <button data-x="expand">Expandir tudo</button><button data-x="collapse">Recolher tudo</button>
</div>
{''.join(cards)}

{action_plan_html(meta.get('actionPlan'), ids)}

<p class="sub" style="margin-top:40px">Gerado em {datetime.date.today().isoformat()} ·
análise de código e enumeração read-only · nenhuma exploração ativa foi realizada.</p>
</div><script>
document.querySelectorAll('.controls button').forEach(b=>b.onclick=()=>{{
  const x=b.dataset.x;
  if(x){{document.querySelectorAll('details.f').forEach(d=>d.open=(x==='expand'));return}}
  document.querySelectorAll('.controls button[data-f]').forEach(o=>o.classList.remove('on'));
  b.classList.add('on');
  const f=b.dataset.f;
  document.querySelectorAll('details.f').forEach(d=>{{
    const show = f==='all' || (f.startsWith('k:') ? d.dataset.kind===f.slice(2) : d.dataset.pri===f);
    d.style.display = show?'':'none';
  }});
  document.querySelectorAll('h3.sech').forEach(h=>{{h.style.display = (f==='all'||f.startsWith('k:'))?'':'none'}});
}});
function openHash(){{
  const d=document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if(!d||!d.matches('details.f'))return;
  if(d.style.display==='none')document.querySelector('.controls button[data-f="all"]').click();
  d.open=true;d.scrollIntoView({{block:'start'}});
}}
window.addEventListener('hashchange',openHash);
document.addEventListener('click',e=>{{const a=e.target.closest('a[href^="#"]');if(a&&a.getAttribute('href')===location.hash)openHash();}});
openHash();
</script></body></html>'''
    open(out, 'w').write(doc)
    print(f'wrote {out} · {len(doc)} bytes · {len(allf)} findings · score {total} · grade {g}')


if __name__ == '__main__':
    main()
