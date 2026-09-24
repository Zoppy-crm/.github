#!/usr/bin/env python3
"""Render the Zoppy security audit report to a single self-contained HTML file.

Reads a combined JSON bundle and emits HTML with no external assets (works offline,
survives being emailed around). Usage: gen_html.py <bundle.json> <out.html>
"""
import json, sys, html, datetime

W = {'CATASTROFICO': 100, 'P0': 30, 'P1': 8, 'P2': 2}
E = {'XS': 1, 'S': 2, 'M': 5, 'L': 13, 'XL': 34}
LB = {'CATASTROFICO': 'CATASTRÓFICO', 'P0': 'P0', 'P1': 'P1', 'P2': 'P2'}
ORDER = ['CATASTROFICO', 'P0', 'P1', 'P2']
COLOR = {'CATASTROFICO': '#b3123b', 'P0': '#d9480f', 'P1': '#b8860b', 'P2': '#3b6ea5'}


def grade(score, counts):
    if counts.get('CATASTROFICO'):
        return 'F', 'Any open CATASTRÓFICO caps the grade at F.'
    band = ('A+', 0) if score == 0 else \
           ('A', 15) if score <= 15 else \
           ('B', 40) if score <= 40 else \
           ('C', 80) if score <= 80 else \
           ('D', 150) if score <= 150 else ('F', 10**9)
    g = band[0]
    if counts.get('P0') and g in ('A+', 'A', 'B'):
        return 'C', 'Any open P0 caps the grade at C.'
    return g, ''


def esc(s):
    return html.escape(str(s if s is not None else ''))


def bar(counts, total):
    segs = []
    for p in ORDER:
        n = counts.get(p, 0)
        if not n:
            continue
        pts = n * W[p]
        pct = pts / total * 100 if total else 0
        segs.append(f'<div class="seg" style="width:{pct:.2f}%;background:{COLOR[p]}" '
                    f'title="{LB[p]}: {n} findings, {pts} pts"></div>')
    return '<div class="bar">' + ''.join(segs) + '</div>'


def finding_card(i, f, kind):
    pr = f.get('priority', 'P2')
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
<details class="f" data-pri="{pr}" data-kind="{kind}" data-size="{esc(f.get('size',''))}">
  <summary>
    <span class="pill" style="background:{COLOR[pr]}">{LB[pr]}</span>
    <span class="size">{esc(f.get('size',''))}</span>
    <span class="ttl">{i}. {esc(f.get('title',''))}</span>
  </summary>
  <div class="fb">
    <p class="meta">{esc(f.get('owasp') or f.get('owaspCategory') or f.get('category') or '')}
       · status: {esc(f.get('status',''))} · confidence: {esc(f.get('confidence',''))} {extra}</p>
    <p><b>Attack path / impact.</b> {esc(body)}</p>
    <p><b>Evidence.</b></p><ul class="ev">{''.join(rows)}</ul>
    <p><b>Fix.</b> {esc(f.get('recommendedFix',''))}</p>
    {f'<p class="why"><b>Why {esc(f.get("size",""))}.</b> {esc(why)}</p>' if why else ''}
  </div>
</details>'''


def main():
    bundle = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    sections = bundle['sections']          # [{key,label,findings:[...]}]
    meta = bundle.get('meta', {})

    allf = [(s['key'], f) for s in sections for f in s['findings']]
    counts = {}
    for _, f in allf:
        p = f.get('priority', 'P2')
        counts[p] = counts.get(p, 0) + 1
    total = sum(counts.get(p, 0) * W[p] for p in ORDER)
    g, gnote = grade(total, counts)

    # per-section subtotals
    sec_rows = []
    for s in sections:
        c = {}
        for f in s['findings']:
            c[f.get('priority', 'P2')] = c.get(f.get('priority', 'P2'), 0) + 1
        sub = sum(c.get(p, 0) * W[p] for p in ORDER)
        cells = ''.join(f'<td>{c.get(p,0) or "—"}</td>' for p in ORDER)
        sec_rows.append(f'<tr><td class="l">{esc(s["label"])}</td>{cells}<td><b>{sub}</b></td></tr>')

    # ROI queue
    roi = sorted(allf, key=lambda kf: -(W[kf[1].get('priority', 'P2')] / E.get(kf[1].get('size', 'M'), 5)))
    roi_rows = ''.join(
        f'<tr><td><span class="pill sm" style="background:{COLOR[f.get("priority","P2")]}">{LB[f.get("priority","P2")]}</span></td>'
        f'<td>{esc(f.get("size",""))}</td><td>{W[f.get("priority","P2")]/E.get(f.get("size","M"),5):.1f}</td>'
        f'<td>{esc(f.get("title",""))}</td></tr>'
        for k, f in roi[:30])

    trend = bundle.get('trend_html', '')
    inv = bundle.get('inventory_html', '')

    cards = []
    n = 0
    for s in sections:
        cards.append(f'<h3 class="sech">{esc(s["label"])} <span class="cnt">{len(s["findings"])}</span></h3>')
        for f in sorted(s['findings'], key=lambda x: -W[x.get('priority', 'P2')]):
            n += 1
            cards.append(finding_card(n, f, s['key']))

    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Zoppy Security &amp; Privacy Audit — {esc(meta.get("date",""))}</title>
<style>
*{{box-sizing:border-box}}
:root{{--bg:#fbfbfa;--fg:#1a1a18;--mut:#6b6b66;--line:#e3e3df;--card:#fff;--accent:#b3123b}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16161a;--fg:#e8e8e4;--mut:#9a9a94;--line:#2c2c33;--card:#1d1d22}}}}
html[data-theme=dark]{{--bg:#16161a;--fg:#e8e8e4;--mut:#9a9a94;--line:#2c2c33;--card:#1d1d22}}
html[data-theme=light]{{--bg:#fbfbfa;--fg:#1a1a18;--mut:#6b6b66;--line:#e3e3df;--card:#fff}}
body{{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:32px 20px 80px}}
h1{{font-size:26px;margin:0 0 4px;letter-spacing:-.02em}}
h2{{font-size:19px;margin:38px 0 12px;letter-spacing:-.01em}}
h3.sech{{font-size:15px;margin:26px 0 8px;color:var(--mut);text-transform:uppercase;letter-spacing:.07em}}
.cnt{{background:var(--line);border-radius:9px;padding:1px 7px;font-size:12px}}
.sub{{color:var(--mut);margin:0 0 22px;font-size:13.5px}}
.hero{{display:flex;gap:22px;align-items:center;background:var(--card);border:1px solid var(--line);
border-radius:12px;padding:20px 22px;margin:18px 0}}
.grade{{font-size:60px;font-weight:700;line-height:1;color:var(--accent);min-width:78px;text-align:center}}
.score{{font-size:31px;font-weight:650}}
.bar{{display:flex;height:11px;border-radius:6px;overflow:hidden;margin:12px 0 4px;background:var(--line)}}
.seg{{height:100%}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:10px 0}}
th,td{{text-align:right;padding:6px 9px;border-bottom:1px solid var(--line)}}
th:first-child,td.l,td:last-child{{text-align:left}}
th{{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
.pill{{color:#fff;border-radius:5px;padding:2px 7px;font-size:11px;font-weight:650;white-space:nowrap}}
.pill.sm{{font-size:10px}}
.size{{display:inline-block;min-width:26px;font-size:11px;color:var(--mut);font-weight:650}}
.tag{{background:var(--line);border-radius:5px;padding:1px 6px;font-size:11px;margin-left:6px}}
.tag.regime{{background:#3b6ea5;color:#fff}}
details.f{{background:var(--card);border:1px solid var(--line);border-radius:9px;margin:6px 0}}
details.f summary{{cursor:pointer;padding:10px 13px;display:flex;gap:10px;align-items:baseline;list-style:none}}
details.f summary::-webkit-details-marker{{display:none}}
.ttl{{flex:1}}
.fb{{padding:2px 15px 14px;border-top:1px solid var(--line);font-size:14px}}
.meta{{color:var(--mut);font-size:12.5px}}
.why{{color:var(--mut);font-size:13px}}
ul.ev{{margin:4px 0;padding-left:18px}}
ul.ev li{{margin:3px 0;font-size:13px}}
code{{background:var(--line);padding:1px 5px;border-radius:4px;font-size:12.5px;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
.controls{{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0;position:sticky;top:0;
background:var(--bg);padding:9px 0;z-index:5;border-bottom:1px solid var(--line)}}
button{{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:7px;
padding:5px 11px;font-size:12.5px;cursor:pointer;font-weight:550}}
button.on{{background:var(--fg);color:var(--bg);border-color:var(--fg)}}
.note{{background:var(--card);border-left:3px solid var(--accent);padding:11px 15px;
border-radius:0 8px 8px 0;margin:14px 0;font-size:14px}}
.scroll{{overflow-x:auto}}
</style></head><body><div class="wrap">

<h1>Zoppy — Security &amp; Privacy Audit</h1>
<p class="sub">{esc(meta.get("date",""))} · scope: {esc(meta.get("scope",""))} · method: {esc(meta.get("method",""))}</p>

<div class="hero">
  <div><div class="grade">{g}</div></div>
  <div style="flex:1">
    <div class="score">{total} <span style="font-size:14px;color:var(--mut);font-weight:400">exposure points</span></div>
    {bar(counts, total)}
    <div style="font-size:12.5px;color:var(--mut)">
      {' · '.join(f'{LB[p]} {counts.get(p,0)}' for p in ORDER if counts.get(p))}
    </div>
    {f'<div style="font-size:12.5px;color:var(--accent);margin-top:6px">{esc(gnote)}</div>' if gnote else ''}
  </div>
</div>

<div class="note">Exposure = Σ(CATASTRÓFICO×100, P0×30, P1×8, P2×2) over open findings. Lower is better.
Weights are order-of-magnitude apart so low-severity volume can never offset one critical.
Grade caps: any open CATASTRÓFICO forces F; any open P0 caps at C.</div>

<h2>By area</h2>
<div class="scroll"><table>
<tr><th>Area</th><th>CATASTRÓFICO</th><th>P0</th><th>P1</th><th>P2</th><th>Points</th></tr>
{''.join(sec_rows)}
</table></div>

{trend}
{inv}

<h2>Remediation queue by ROI</h2>
<p class="sub" style="margin:0 0 8px">Priority weight ÷ effort points (XS=1, S=2, M=5, L=13, XL=34).
Use this to sequence work; use priority to report it. The two orders disagree, and that is the point.</p>
<div class="scroll"><table>
<tr><th>Priority</th><th>Size</th><th>ROI</th><th>Finding</th></tr>{roi_rows}</table></div>

<h2>All findings</h2>
<div class="controls">
  <button class="on" data-f="all">All ({len(allf)})</button>
  {''.join(f'<button data-f="{p}">{LB[p]} ({counts.get(p,0)})</button>' for p in ORDER if counts.get(p))}
  {''.join(f'<button data-f="k:{s["key"]}">{esc(s["label"])}</button>' for s in sections)}
  <button data-x="expand">Expand all</button><button data-x="collapse">Collapse all</button>
</div>
{''.join(cards)}

<p class="sub" style="margin-top:40px">Generated {datetime.date.today().isoformat()} ·
code analysis and read-only cloud enumeration only · no live exploitation was performed.</p>
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
</script></body></html>'''
    open(out, 'w').write(doc)
    print(f'wrote {out} · {len(doc)} bytes · {len(allf)} findings · score {total} · grade {g}')


if __name__ == '__main__':
    main()
