#!/usr/bin/env python3
"""Assemble a Zoppy deck: shell + slides -> one self-contained HTML file.

  python3 build_deck.py --title "..." --slides slides.html --out deck.html

slides.html holds only <section class="slide">...</section> blocks. This script
supplies the shell: tokens, embedded font, slide counters, nav dots, key/click/swipe
handlers. Slide counters are numbered here, never by hand.

Importable helper: barchart(rows, ymax, ...) -> SVG string.
"""
import argparse, base64, pathlib, re, sys

FONT = pathlib.Path(__file__).resolve().parents[1] / 'assets' / 'Inter-Regular.otf'

CSS = """
:root{
  --purple:#7B3DFF; --purple-hover:#4400D3; --blue:#002E73;
  --ink:#2A3545; --neutral:#727C8C; --disabled:#A8AFBA;
  --border:#DDE2E8; --border-strong:#C9D0D9;
  --page:#F9F9FA; --surface:#FDFDFD; --selected:#EFF1FE; --hover:#F2F5F9;
  --info:#1652ED; --info-bg:#E5EDFF; --warn:#CF7F20; --warn-bg:#FFF3E3;
  --crit:#B91414; --crit-bg:#FCE8E8; --ok:#2DB081; --ok-bg:#E3F6F0;
  --grad:linear-gradient(135deg,#00FFE6 14.56%,#7B3DFF 85.73%);
  --font:'InterEmbedded',Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;width:100%;overflow:hidden}
body{font-family:var(--font);background:var(--page);color:var(--ink);font-size:16px;
     line-height:1.5;-webkit-font-smoothing:antialiased}
.deck{position:fixed;inset:0}
.slide{position:absolute;inset:0;display:flex;flex-direction:column;
       padding:clamp(24px,3.4vh,44px) clamp(24px,4vw,72px);
       opacity:0;visibility:hidden;transition:opacity .28s ease;overflow:hidden}
.slide.on{opacity:1;visibility:visible}
.inner{width:100%;max-width:1240px;margin:0 auto;flex:1;display:flex;flex-direction:column;
       justify-content:center;gap:clamp(12px,2vh,26px);min-height:0}
.topbar{display:flex;align-items:center;justify-content:space-between;flex:0 0 auto;
        margin-bottom:clamp(8px,1.6vh,20px)}
.brand{display:flex;align-items:center;gap:10px;font-size:13px;letter-spacing:.06em;
       text-transform:uppercase;color:var(--neutral);font-weight:600}
.brand::before{content:'';width:26px;height:4px;border-radius:2px;background:var(--grad)}
.counter{font-size:13px;color:var(--disabled);font-variant-numeric:tabular-nums}
h1{font-size:clamp(30px,4.4vw,52px);line-height:1.12;font-weight:700;color:var(--blue);letter-spacing:-.02em}
h2{font-size:clamp(21px,2.5vw,32px);line-height:1.2;font-weight:700;color:var(--blue);letter-spacing:-.01em}
.eyebrow{font-size:clamp(11px,1.05vw,13px);letter-spacing:.12em;text-transform:uppercase;
         color:var(--purple);font-weight:600}
.lede{font-size:clamp(14px,1.28vw,18px);line-height:1.55;color:var(--ink);max-width:76ch}
.sub{font-size:clamp(12px,1.05vw,14px);line-height:1.5;color:var(--neutral);max-width:82ch}
strong,b{font-weight:600}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(10px,1.3vw,18px)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;
      padding:clamp(14px,1.6vw,22px);min-width:0}
.card h3{font-size:clamp(13px,1.15vw,16px);font-weight:600;color:var(--blue);margin-bottom:6px}
.card p{font-size:clamp(11.5px,1vw,14px);line-height:1.5;color:var(--neutral)}
.statrow{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(10px,1.4vw,20px)}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:14px;
      padding:clamp(14px,1.8vw,24px);text-align:center}
.stat .n{font-size:clamp(34px,5vw,62px);line-height:1;font-weight:700;letter-spacing:-.03em;
         font-variant-numeric:tabular-nums}
.stat .k{font-size:clamp(10.5px,.95vw,13px);letter-spacing:.09em;text-transform:uppercase;
         color:var(--neutral);font-weight:600;margin-top:10px}
.stat .d{font-size:clamp(11px,.95vw,13px);color:var(--disabled);margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:clamp(11.5px,1.05vw,15px)}
th{text-align:left;font-weight:600;color:var(--neutral);font-size:clamp(10px,.9vw,12px);
   letter-spacing:.07em;text-transform:uppercase;padding:0 10px 8px;border-bottom:1px solid var(--border-strong)}
td{padding:clamp(6px,.85vh,11px) 10px;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:none}
.num{text-align:right}
tfoot td{font-weight:600;color:var(--blue);border-top:2px solid var(--border-strong);border-bottom:none}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:clamp(10px,.9vw,12.5px);
      font-weight:600;white-space:nowrap}
.p-cat{background:var(--crit);color:#fff}
.p-cri{background:var(--crit-bg);color:var(--crit)}
.p-alt{background:var(--warn-bg);color:var(--warn)}
.p-med{background:var(--info-bg);color:var(--info)}
.p-bai{background:var(--hover);color:var(--neutral)}
.p-ok{background:var(--ok-bg);color:var(--ok)}
.note{border-left:3px solid var(--purple);background:var(--selected);
      padding:clamp(10px,1.3vh,16px) clamp(12px,1.4vw,18px);border-radius:0 10px 10px 0;
      font-size:clamp(11.5px,1vw,14px);line-height:1.55;color:var(--ink)}
.note.warn{border-left-color:var(--warn);background:var(--warn-bg)}
.note.ok{border-left-color:var(--ok);background:var(--ok-bg)}
.note.crit{border-left-color:var(--crit);background:var(--crit-bg)}
.chartwrap{background:var(--surface);border:1px solid var(--border);border-radius:14px;
           padding:clamp(10px,1.4vw,20px);min-height:0;display:flex}
svg.chart{width:100%;height:auto;max-height:52vh;display:block}
.findings{display:flex;flex-direction:column;gap:clamp(7px,.95vh,12px)}
.f{display:grid;grid-template-columns:auto 1fr auto;gap:clamp(10px,1.2vw,16px);align-items:center;
   background:var(--surface);border:1px solid var(--border);border-radius:12px;
   padding:clamp(8px,1.05vh,14px) clamp(11px,1.2vw,16px)}
.f .t{font-size:clamp(12px,1.08vw,15.5px);font-weight:600;color:var(--ink);line-height:1.35}
.f .w{font-size:clamp(10.5px,.92vw,13px);color:var(--neutral);line-height:1.4;margin-top:2px}
.f .sz{font-size:clamp(10px,.88vw,12px);color:var(--disabled);font-weight:600;white-space:nowrap}
.links{display:grid;grid-template-columns:1fr 1fr;gap:clamp(10px,1.4vw,18px)}
a.rep{display:block;background:var(--surface);border:1px solid var(--border);border-radius:14px;
      padding:clamp(14px,1.8vw,24px);text-decoration:none;transition:border-color .15s,background .15s}
a.rep:hover{border-color:var(--purple);background:var(--selected)}
a.rep .rt{font-size:clamp(14px,1.25vw,18px);font-weight:600;color:var(--purple)}
a.rep .rd{font-size:clamp(11px,.98vw,13.5px);color:var(--neutral);margin-top:6px;line-height:1.45}
.nav{position:fixed;left:0;right:0;bottom:clamp(12px,2vh,22px);display:flex;align-items:center;
     justify-content:center;gap:9px;z-index:10}
.dot{width:8px;height:8px;border-radius:50%;background:var(--border-strong);border:none;
     cursor:pointer;padding:0;transition:all .18s}
.dot.on{background:var(--purple);width:22px;border-radius:4px}
.hint{position:fixed;right:clamp(16px,2vw,28px);bottom:clamp(12px,2vh,22px);font-size:11px;
      color:var(--disabled);z-index:10}
@media (max-width:900px){
  .cards,.statrow,.links{grid-template-columns:1fr}
  .cards .card:nth-child(n+3){display:none}
}
@media (max-width:760px){
  .slide{overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;justify-content:flex-start;
         padding:16px 16px 64px;touch-action:pan-y;overscroll-behavior:contain}
  .slide.on{position:relative;height:100%;width:100%}
  .tablewrap,.scrollx{touch-action:pan-x pan-y}
  .inner{flex:0 0 auto;justify-content:flex-start;gap:14px;max-width:100%}
  .topbar{margin-bottom:10px}
  h1{font-size:30px}
  h2{font-size:21px}
  .lede{font-size:15px}
  .sub{font-size:13px}
  .eyebrow{font-size:12px}
  .cards,.statrow,.links,.f{grid-template-columns:1fr}
  .cards .card:nth-child(n+3){display:block}
  .cards,.statrow,.links{gap:10px}
  .card{padding:14px}
  .card h3{font-size:14px}
  .card p{font-size:13px}
  .stat{padding:14px}
  .stat .n{font-size:34px}
  .stat .k,.stat .d{font-size:12px}
  .tablewrap,.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;min-width:0}
  .tablewrap table{min-width:640px;font-size:13px}
  th{font-size:12px}
  td{padding:8px 10px}
  .pill{font-size:12px}
  .note{font-size:13px;padding:10px 12px}
  .chartwrap{max-width:100%;min-width:0;padding:10px}
  svg.chart{max-height:none}
  .scrollx>svg{min-width:720px}
  .findings{gap:8px}
  .f{gap:6px;padding:10px 12px}
  .f .pill{justify-self:start}
  .f .t{font-size:14px}
  .f .w{font-size:12.5px}
  .f .sz{font-size:12px;white-space:normal}
  a.rep{padding:14px}
  a.rep .rt{font-size:15px}
  a.rep .rd{font-size:12.5px}
  .nav{gap:6px;bottom:12px}
  .hint{display:none}
}
"""

JS = """
(function(){
  var slides=[].slice.call(document.querySelectorAll('.slide'));
  var nav=document.getElementById('nav');var i=0;
  slides.forEach(function(_,n){var b=document.createElement('button');
    b.className='dot'+(n===0?' on':'');b.setAttribute('aria-label','Slide '+(n+1));
    b.onclick=function(){go(n)};nav.appendChild(b);});
  var dots=[].slice.call(nav.children);
  function go(n){if(n<0||n>=slides.length)return;
    slides[i].classList.remove('on');dots[i].classList.remove('on');
    i=n;slides[i].classList.add('on');dots[i].classList.add('on');
    if(location.hash!=='#'+(i+1))history.replaceState(null,'','#'+(i+1));}
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' '){e.preventDefault();go(i+1)}
    else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(i-1)}
    else if(e.key==='Home'){go(0)}else if(e.key==='End'){go(slides.length-1)}});
  document.addEventListener('click',function(e){
    if(e.target.closest('a')||e.target.closest('.nav'))return;
    go(i+(e.clientX<window.innerWidth*0.28?-1:1));});
  var x0=null,y0=null,sw=null,sx=0;
  document.addEventListener('touchstart',function(e){var t=e.touches[0];x0=t.clientX;y0=t.clientY;
    sw=e.target.closest?e.target.closest('.tablewrap,.scrollx'):null;sx=sw?sw.scrollLeft:0;},{passive:true});
  document.addEventListener('touchend',function(e){if(x0===null)return;
    var t=e.changedTouches[0];var dx=t.clientX-x0,dy=t.clientY-y0;
    var scrolled=sw&&sw.scrollLeft!==sx;x0=null;y0=null;sw=null;
    if(scrolled)return;
    if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5)go(i+(dx<0?1:-1));},{passive:true});
  var h=parseInt((location.hash||'').slice(1),10);
  if(h>=1&&h<=slides.length)go(h-1);})();
"""


def barchart(rows, ymax, ticks, avg=None, avg_label='', pct=False, colour='#7B3DFF'):
    """rows = [(top_label, sub_label, value, is_partial)]. Returns an <svg> string."""
    X0, X1, Y0, Y1 = 62, 880, 32, 268
    slot = (X1 - X0) / len(rows)
    bw = slot * 0.60
    y = lambda v: Y1 - v * ((Y1 - Y0) / ymax)
    out = []
    for t in ticks:
        out.append(f'<line x1="{X0}" y1="{y(t):.1f}" x2="{X1}" y2="{y(t):.1f}" stroke="#DDE2E8"/>')
        out.append(f'<text x="{X0-10}" y="{y(t)+4:.1f}" text-anchor="end" font-size="11" '
                   f'fill="#A8AFBA">{t}{"%" if pct else ""}</text>')
    for i, (top, sub, v, part) in enumerate(rows):
        x = X0 + i * slot + (slot - bw) / 2
        c = '#C9D0D9' if part else colour
        lc = '#A8AFBA' if part else colour
        if pct:
            out.append(f'<rect x="{x:.1f}" y="{Y0}" width="{bw:.1f}" height="{Y1-Y0}" rx="4" fill="#F2F5F9"/>')
        out.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{Y1-y(v):.1f}" rx="4" fill="{c}"/>')
        lab = f'{v:.0f}%' if pct else f'{v:g}'
        out.append(f'<text x="{x+bw/2:.1f}" y="{y(v)-7:.1f}" text-anchor="middle" font-size="12.5" '
                   f'font-weight="700" fill="{lc}">{lab}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{Y1+18:.1f}" text-anchor="middle" font-size="10.5" '
                   f'font-weight="600" fill="#727C8C">{top}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{Y1+32:.1f}" text-anchor="middle" font-size="9.5" '
                   f'fill="#A8AFBA">{sub}</text>')
    if avg is not None:
        out.append(f'<line x1="{X0}" y1="{y(avg):.1f}" x2="{X1}" y2="{y(avg):.1f}" stroke="#2DB081" '
                   f'stroke-width="1.5" stroke-dasharray="6 4"/>')
        out.append(f'<text x="{X1}" y="{y(avg)-7:.1f}" text-anchor="end" font-size="11.5" '
                   f'font-weight="600" fill="#2DB081">{avg_label}</text>')
    return f'<svg class="chart" viewBox="0 0 900 315" role="img">{"".join(out)}</svg>'


def wrap_tables(html):
    """Wrap every bare <table> in <div class="tablewrap"> so it can scroll sideways on phones."""
    def repl(m):
        start = m.start()
        before = html[max(0, start - 40):start].rstrip()
        if before.endswith('<div class="tablewrap">'):
            return m.group(0)
        return f'<div class="tablewrap">{m.group(0)}</div>'
    return re.sub(r'<table\b.*?</table>', repl, html, flags=re.S)


def build(title, slides_html, out):
    if not FONT.exists():
        sys.exit(f'font asset missing: {FONT}')
    b64 = base64.b64encode(FONT.read_bytes()).decode()
    n = len(re.findall(r'<section class="slide', slides_html))
    if n == 0:
        sys.exit('no <section class="slide"> blocks found')
    # number the counters: every {{COUNTER}} becomes NN / TT in document order
    seq = iter(range(1, n + 1))
    slides_html = re.sub(r'\{\{COUNTER\}\}', lambda m: f'{next(seq):02d} / {n:02d}', slides_html)
    slides_html = wrap_tables(slides_html)
    doc = (f'<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
           f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           f'<title>{title}</title>\n<style>\n'
           f"@font-face{{font-family:'InterEmbedded';src:url(data:font/otf;base64,{b64}) "
           f"format('opentype');font-weight:400;font-style:normal;font-display:block}}\n"
           f'{CSS}</style>\n</head>\n<body>\n<div class="deck" id="deck">\n{slides_html}\n</div>\n'
           f'<div class="nav" id="nav"></div>\n<div class="hint">← → · espaço</div>\n'
           f'<script>{JS}</script>\n</body>\n</html>\n')
    pathlib.Path(out).write_text(doc)
    print(f'wrote {out} · {len(doc)} bytes · {n} slides')
    return n


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True)
    ap.add_argument('--slides', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    build(a.title, pathlib.Path(a.slides).read_text(), a.out)
