import fs from 'fs';
import crypto from 'crypto';
import path from 'path';
import { execSync } from 'child_process';

const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname);
const SKILL_DIR = path.resolve(SCRIPT_DIR, '..');
const REPO_DIR = process.env.RX_REPO_DIR || process.cwd();
const GIT_DIR = process.env.RX_GIT_DIR || REPO_DIR;
const SOURCE_ROOT = process.env.RX_SOURCE_ROOT;
const MANIFEST = process.env.RX_MANIFEST || `${REPO_DIR}/docs/review-bundles/manifest-9756.json`;
const M = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
// gh api repos/<repo>/pulls/<N>/comments --paginate > /tmp/rx-comments.json
const COMMENTS = JSON.parse(fs.readFileSync(process.env.RX_COMMENTS || '/tmp/rx-comments.json', 'utf8'));
// git diff <base> <head> > /tmp/rx.diff   (or: gh pr diff <N>)
const DIFF = fs.readFileSync(process.env.RX_DIFF || '/tmp/rx.diff', 'utf8');
const OUT = process.argv[2] || `${REPO_DIR}/docs/review-bundles/pr-9756-prototype.html`;
const FONT_PATH = process.env.RX_FONT || `${SKILL_DIR}/assets/Inter-Regular.otf`;
if (!fs.existsSync(FONT_PATH)) throw new Error(`fonte Inter obrigatória não encontrada: ${FONT_PATH}`);
const FONT_DATA = fs.readFileSync(FONT_PATH).toString('base64');
const GENERATOR_VERSION = 'zoppy-rx-2';
const DIFF_SHA256 = crypto.createHash('sha256').update(DIFF).digest('hex');

const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const anchor = p => 'diff-' + crypto.createHash('sha256').update(p).digest('hex');

let PROOFS = {};
try {
  const registryPath = process.env.RX_PROOFS || `${REPO_DIR}/docs/review-bundles/proof-registry.json`;
  const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
  for (const proof of registry.proofs) PROOFS[proof.id] = proof;
} catch {}
let PROVENANCE = {};
try {
  PROVENANCE = JSON.parse(fs.readFileSync(process.env.RX_PROVENANCE || `${REPO_DIR}/docs/review-bundles/introduced-bug-provenance.json`, 'utf8')).findings || {};
} catch {}
function proofCards(ids = []) {
  return ids.map(id => {
    const proof = PROOFS[id];
    if (!proof) return `<div class="proof missing">prova <code>${esc(id)}</code> não encontrada no registry</div>`;
    return `<div class="proof"><span class="peyebrow">Evidência · <code>${esc(id)}</code></span>
<p><b>${esc(proof.claim)}</b></p><p>${esc(proof.result)}</p><p class="preading">${esc(proof.reading)}</p>
${proof.sql ? `<details><summary>SQL</summary><pre>${esc(proof.sql)}</pre></details>` : ''}</div>`;
  }).join('');
}

/* ---------- 1. parse unified diff ---------- */
function parseDiff(text) {
  const files = {};
  let cur = null, hunk = null;
  for (const raw of text.split('\n')) {
    if (raw.startsWith('diff --git ')) {
      const m = raw.match(/ b\/(.+)$/);
      cur = { path: m[1], hunks: [], add: 0, del: 0 };
      files[cur.path] = cur; hunk = null; continue;
    }
    if (!cur) continue;
    if (raw.startsWith('@@')) {
      const m = raw.match(/@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)/);
      hunk = { header: (m[5]||'').trim(), oldStart:+m[1], newStart:+m[3], lines: [] };
      cur.hunks.push(hunk); continue;
    }
    if (!hunk) continue;
    if (raw.startsWith('+++') || raw.startsWith('---')) continue;
    const t = raw[0];
    if (t === '+' || t === '-' || t === ' ' || raw === '') hunk.lines.push(raw === '' ? ' ' : raw);
    if (t === '+') cur.add++; if (t === '-') cur.del++;
  }
  // assign line numbers
  for (const f of Object.values(files))
    for (const h of f.hunks) {
      let o = h.oldStart, n = h.newStart;
      h.rows = h.lines.map(l => {
        const t = l[0];
        if (t === '+') return { t:'+', n: n++, txt: l.slice(1) };
        if (t === '-') return { t:'-', o: o++, txt: l.slice(1) };
        return { t:' ', o: o++, n: n++, txt: l.slice(1) };
      });
      h.newEnd = n - 1;
    }
  return files;
}
const FILES = parseDiff(DIFF);

/* ---------- 2. dependency graph over changed files ---------- */
const paths = Object.keys(FILES);
const out = new Map(paths.map(p => [p, []]));
function changedImports(src, importer) {
  const found = new Set();
  for (const match of src.matchAll(/from\s+['"]([^'"]+)['"]/g)) {
    const spec = match[1];
    const resolved = (spec.startsWith('.') ? path.posix.normalize(path.posix.join(path.posix.dirname(importer), spec)) : spec)
      .replace(/\.(?:js|ts)$/, '');
    for (const candidate of paths) {
      if (resolved === candidate.replace(/\.ts$/, '')) found.add(candidate);
    }
  }
  return [...found];
}
for (const f of paths) {
  let src;
  if (SOURCE_ROOT && fs.existsSync(`${SOURCE_ROOT}/${f}`)) src = fs.readFileSync(`${SOURCE_ROOT}/${f}`, 'utf8');
  else {
    try { src = execSync(`git -C ${GIT_DIR} show ${M.headSha}:${f}`, {encoding:'utf8',maxBuffer:1e8,stdio:['ignore','pipe','ignore']}); }
    catch { try { src = execSync(`git -C ${GIT_DIR} show ${M.baseSha}:${f}`, {encoding:'utf8',maxBuffer:1e8,stdio:['ignore','pipe','ignore']}); } catch { continue; } }
  }
  for (const g of changedImports(src, f)) if (f !== g) out.get(f).push(g);
}
const inDeg = new Map(paths.map(p => [p, 0]));
for (const [a, bs] of out) for (const b of bs) inDeg.set(b, inDeg.get(b) + 1);
const memo = new Map();
const depth = (p, seen = new Set()) => {
  if (memo.has(p)) return memo.get(p);
  if (seen.has(p)) return 0;
  seen.add(p);
  const d = out.get(p).length ? 1 + Math.max(...out.get(p).map(q => depth(q, new Set(seen)))) : 0;
  memo.set(p, d); return d;
};
const alpha = [...paths].sort();
const edgeCount = [...out.values()].reduce((a,b)=>a+b.length,0);
let edgeViolations = 0;
for (const [a, bs] of out) for (const b of bs) if (alpha.indexOf(a) < alpha.indexOf(b)) edgeViolations++;

/* ---------- 3. flatten manifest ---------- */
const stops = [];
for (const s of M.sessions) for (const st of s.stops) stops.push({ ...st, session: s });
const missing = paths.filter(p => !stops.some(s => s.path === p));
const extra = stops.filter(s => !FILES[s.path]).map(s => s.path);
let pairInversions = 0, pairs = 0;
for (let i = 0; i < stops.length; i++) for (let j = i + 1; j < stops.length; j++) {
  pairs++; if (alpha.indexOf(stops[i].path) > alpha.indexOf(stops[j].path)) pairInversions++;
}

/* ---------- 4. render ---------- */
const CANONICAL_PREP = /^🤖 \[prep\]\s*/;
const LEGACY_PREP = /^🤖 \[prep\s+\d+\/\d+\]\s*/;
const isPrep = c => CANONICAL_PREP.test(c.body || '') || LEGACY_PREP.test(c.body || '');
const prepComments = COMMENTS.filter(isPrep);
const nonPrepComments = COMMENTS.filter(c => !isPrep(c));
const commentsFor = p => prepComments.filter(c => c.path === p);
const reviewCommentsFor = p => nonPrepComments.filter(c => c.path === p);
function hunkComments(p, h) {
  return commentsFor(p).filter(c => {
    if (c.subject_type === 'file' || c.line == null) return false;
    return c.line >= h.newStart && c.line <= h.newEnd;
  });
}
function fileLevelComments(p, hunks) {
  return commentsFor(p).filter(c =>
    c.subject_type === 'file' || c.line == null ||
    !hunks.some(h => c.line >= h.newStart && c.line <= h.newEnd));
}
function reviewLevelComments(p) {
  return reviewCommentsFor(p);
}
const stripPrep = body => String(body || '').replace(CANONICAL_PREP, '').replace(LEGACY_PREP, '');
const md = s => esc(s)
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  .replace(/\b(MUDANÇA|ALTERNATIVA|EQUIVALÊNCIA|POR QUE|O QUE FORÇOU|POR QUE FOI POSSÍVEL|NÃO|CHANGE|WHY)\b:/g,
           '<b class="kw">$1:</b>');

const NOISE = [
  /^\s*import\s/, /^\s*}\s*from\s/, /^\s*[A-Za-z][\w]*,?$/,
  /^\s*(private|public|protected)\s+(readonly\s+)?\w+:\s*[\w<>[\]]+,?$/,
  /^\s*\)?\s*\{?$/, /^\s*$/,
];
const VIEWED = new Set(M.viewed || []);
const EXPLICIT_COVERAGE = M.coverage || [];
function groupedCoverage(p, h) {
  return EXPLICIT_COVERAGE.filter(item => item.path === p && (item.fullFile || (Number(item.start) <= h.newEnd && Number(item.end) >= h.newStart)) && prepComments.some(comment => String(comment.id) === String(item.commentId) && comment.path === p));
}
function classify(h, cs, p) {
  if (cs.length) return 'told';
  if (groupedCoverage(p, h).length) return 'grouped';
  const changed = h.rows.filter(r => r.t !== ' ');
  if (!changed.length) return 'told';
  if (VIEWED.has(p)) return 'viewed';
  return changed.every(r => NOISE.some(re => re.test(r.txt))) ? 'noise' : 'quiet';
}
function renderHunk(p, h, idx) {
  const cs = hunkComments(p, h);
  const rows = h.rows.map(r => {
    const cls = r.t === '+' ? 'a' : r.t === '-' ? 'd' : 'c';
    const ln = r.t === '-' ? r.o : r.n;
    const commented = cs.some(c => c.line === r.n);
    return `<tr class="${cls}${commented?' hit':''}"><td class="ln">${ln||''}</td><td class="sg">${r.t==='+'?'+':r.t==='-'?'−':''}</td><td class="tx">${esc(r.txt)||'&nbsp;'}</td></tr>`;
  }).join('');
  const why = cs.map(c => `<blockquote class="prep"><b>Contexto da mudança${LEGACY_PREP.test(c.body || '') ? ' · formato legado' : ''}</b> <span class="at">@${esc(c.user.login)} · L${c.line}</span><p>${md(stripPrep(c.body))}</p></blockquote>`).join('');
  const grouped = groupedCoverage(p, h).map(item => `<div class="prep grouped"><b>Cobertura geral declarada · comentário ${esc(item.commentId)}</b><p>${md(item.reason)}</p></div>`).join('');
  const nchg = h.rows.filter(r=>r.t!==' ').length;
  const kind = classify(h, cs, p);
  const plural = nchg === 1 ? 'linha' : 'linhas';
  const deleted = h.newEnd < h.newStart;
  const position = deleted ? '' : `R${h.newStart}`;
  const meta = deleted ? `arquivo deletado · −${nchg} ${plural}` : `L${h.newStart}–${h.newEnd} · ${nchg} ${plural}`;
  const ghlink = `<a class="gh" href="https://github.com/${M.repo}/pull/${M.pr}/files#${anchor(p)}${position}" target="_blank" rel="noopener">comentar no GitHub ↗</a>`;
  if (kind === 'noise' || kind === 'viewed') {
    const summary = kind === 'viewed' ? 'arquivo trivial já marcado Viewed no GitHub' : 'ruído: imports / injeção de dependência';
    return `<div class="hunk noise">
  <details><summary class="nsum">${summary} <span class="hmeta">${meta}</span></summary>
  <div class="dtbl"><table>${rows}</table></div></details>
</div>`;
  }
  const label = kind === 'told' ? 'diff' : kind === 'grouped' ? 'diff coberto pela nota geral declarada' : 'SEM NOTA DE PREPARAÇÃO NESTE TRECHO';
  const flag = kind !== 'told' && kind !== 'grouped' ? ' gap' : '';
  return `<div class="hunk ${kind}${flag}">
  <div class="hh"><span class="scope">${esc(h.header) || '—'}</span><span class="hmeta">${meta}</span>
  ${ghlink}</div>
  ${why}
  ${grouped}
  <details${kind==='told'?' open':''}><summary>${label}</summary><div class="dtbl"><table>${rows}</table></div></details>
</div>`;
}

let gapHunks = [];
for (const p of paths) {
  const f = FILES[p];
  for (const h of f.hunks) if (classify(h, hunkComments(p,h), p) === 'quiet') gapHunks.push(p + ':L' + h.newStart);
}
let n = 0;
const sessionHtml = M.sessions.map(s => {
  const stopsHtml = s.stops.map(st => {
    n++;
    const f = FILES[st.path];
    if (!f) return `<section class="stop bad"><h3>${n}. ${esc(st.path)}</h3><p>ARQUIVO NÃO ESTÁ NO DIFF</p></section>`;
    const d = depth(st.path), callers = inDeg.get(st.path);
    const fl = fileLevelComments(st.path, f.hunks);
    const reviewContext = reviewLevelComments(st.path);
    const base = st.path.split('/').pop();
    const dir = st.path.slice(0, -base.length);
    return `<section class="stop" id="stop-${n}" data-stop="${n}">
  <header>
    <div class="srow">
      <button class="tick" data-tick="${n}" aria-label="marcar parada ${n} como lida"><span>${n}</span></button>
      <div>
        <h3><span class="dir">${esc(dir)}</span><span class="base">${esc(base)}</span></h3>
        <p class="badges">
          <span class="badge dep${d===0?' zero':''}">profundidade ${d}</span>
          <span class="badge">${callers} dependente${callers===1?'':'s'} nesta PR</span>
          <span class="badge">+${f.add} −${f.del}</span>
          <span class="badge alpha">GitHub mostraria em ${alpha.indexOf(st.path)+1}º</span>
        </p>
      </div>
    </div>
    <p class="orderwhy"><b>por que agora:</b> ${md(st.why)}</p>
  </header>
  ${proofCards(st.proofs)}
  ${fl.map(c=>`<blockquote class="prep file"><b>Contexto geral do arquivo${LEGACY_PREP.test(c.body || '') ? ' · formato legado' : ''}</b> <span class="at">@${esc(c.user.login)}</span><p>${md(stripPrep(c.body))}</p></blockquote>`).join('')}
  ${reviewContext.length ? `<details class="review-context"><summary>Discussão de revisão (${reviewContext.length})</summary>${reviewContext.map(c=>`<blockquote><b>${esc(c.user?.login || 'autor desconhecido')}</b><p>${md(c.body || '')}</p></blockquote>`).join('')}</details>` : ''}
  ${f.hunks.map((h,i)=>renderHunk(st.path,h,i)).join('')}
</section>`;
  }).join('');
  return `<div class="session" id="${s.id}">
  <div class="shead">
    <p class="eyebrow">Sessão · ~${s.minutes} min</p>
    <h2>${esc(s.title)}</h2>
    <p class="goal">${esc(s.goal)}</p>
  </div>
  ${stopsHtml}
  <div class="checkpoint">
    <p class="eyebrow">Checkpoint — o que você agora acredita</p>
    <ul>${s.beliefs.map((b,i)=>`<li><label><input type="checkbox" data-belief="${s.id}-${i}"> ${md(b)}</label></li>`).join('')}</ul>
    <p class="cpnote">Se alguma linha acima não é verdade pra você, a parada correspondente não foi lida — volte antes de seguir. Discordar é um comentário no GitHub, não um checkbox desmarcado.</p>
  </div>
</div>`;
}).join('');

/* rail */
let rn = 0;
const rail = M.sessions.map(s => `<div class="rs"><p class="rst">${esc(s.title)} <small>${s.minutes}′</small></p><ol>${
  s.stops.map(st => { rn++; return `<li><a href="#stop-${rn}" data-rail="${rn}"><span class="rnum">${rn}</span> ${esc(st.path.split('/').pop())}</a></li>`; }).join('')
}</ol></div>`).join('');

/* depth map */
const byDepth = {};
for (const p of paths) (byDepth[depth(p)] ??= []).push(p);
const depthCols = Object.keys(byDepth).sort().map(d => `<div class="dcol"><p class="dlab">${d==='0'?'definições':'nível '+d}</p>${
  byDepth[d].sort().map(p=>`<span class="dnode${/\.spec\.ts$/.test(p)?' spec':''}">${esc(p.split('/').pop())}</span>`).join('')
}</div>`).join('<span class="darrow">→</span>');

const integrity = `
<ul class="integrity">
<li><b>${paths.length}</b> arquivos no diff · <b>${stops.length}</b> paradas no manifesto · <b>${missing.length}</b> não cobertos${missing.length?': '+missing.map(esc).join(', '):''}</li>
<li><b>${prepComments.filter(c=>CANONICAL_PREP.test(c.body || '')).length}</b> comentários canônicos <code>🤖 [prep]</code> · <b>${prepComments.filter(c=>LEGACY_PREP.test(c.body || '')).length}</b> no formato ordinal legado · <b>${nonPrepComments.length}</b> comentários de revisão separados</li>
<li>Linhas: lógica <b>${M.loc.logicAdd-M.loc.logicDel}</b> de saldo (+${M.loc.logicAdd} / −${M.loc.logicDel}) · testes <b>${M.loc.specAdd-M.loc.specDel}</b> de saldo (+${M.loc.specAdd} / −${M.loc.specDel})</li>
<li><b>${edgeViolations}/${edgeCount}</b> (${Math.round(100*edgeViolations/(edgeCount||1))}%) das arestas de import reais aparecem <i>caller primeiro</i> na ordem alfabética do GitHub</li>
<li><b>${pairInversions}/${pairs}</b> (${Math.round(100*pairInversions/(pairs||1))}%) dos pares de arquivos estão na ordem relativa errada no GitHub</li>
<li>Trechos com lógica e <b>zero</b> nota de preparação ancorada no próprio trecho: <b>${gapHunks.length}</b>${gapHunks.length?' — '+gapHunks.map(esc).join(', '):''}</li>
<li>achados relacionados: <b>${(M.findings || []).filter(f => f.classification === 'introduced_bug').length}</b> bug(s) introduzido(s) aberto(s) · <b>${(M.findings || []).filter(f => f.classification === 'fixed_introduced_bug').length}</b> bug(s) introduzido(s) corrigido(s) · <b>${(M.findings || []).filter(f => f.classification === 'inherited_debt').length}</b> dívida(s) herdada(s) · <b>${(M.findings || []).filter(f => f.classification === 'speculative').length}</b> hipótese(s)</li>
${extra.length?`<li class="err">manifesto aponta arquivos fora do diff: ${extra.map(esc).join(', ')}</li>`:''}
</ul>`;

const findingLabels = {
  introduced_bug: 'FALHA INTRODUZIDA — aberta',
  fixed_introduced_bug: 'FALHA INTRODUZIDA — corrigida nesta PR',
  inherited_debt: 'DÍVIDA NÃO ELIMINADA — herdada',
  speculative: 'HIPÓTESE — não confirmada',
  rollout_constraint: 'RESTRIÇÃO DE ROLLOUT — confirmada',
  assessment: 'AVALIAÇÃO — nenhum bug introduzido confirmado'
};
const findings = M.findings || [];
const VALID_FINDING_CLASSES = new Set(['introduced_bug', 'fixed_introduced_bug', 'inherited_debt', 'speculative', 'rollout_constraint', 'assessment']);
const introducedClasses = new Set(['introduced_bug', 'fixed_introduced_bug']);
const resolvedProvenance = finding => {
  const p = finding.provenance || PROVENANCE[finding.provenanceRef || finding.id];
  return p?.ref ? PROVENANCE[p.ref] : p;
};
const completeProvenance = finding => {
  const p = resolvedProvenance(finding);
  if (!p?.baseline?.sha || !p?.baseline?.path || !p?.baseline?.reading) return false;
  if (!p?.introduced?.sha || !p?.introduced?.path || !p?.introduced?.pr || !p?.introduced?.reading) return false;
  if (!p?.failure?.evidence || !p?.failure?.reading) return false;
  if (finding.classification === 'fixed_introduced_bug' && (!p?.corrected?.sha || !p?.corrected?.path || !p?.corrected?.pr || !p?.corrected?.reading)) return false;
  return true;
};
function provenanceHtml(finding) {
  const p = resolvedProvenance(finding);
  if (!p) return '';
  const stage = (label, value) => value ? `<div class="pstage"><span>${label}</span><b>${esc(value.reading || '')}</b><small>${esc(value.pr ? `PR #${value.pr} · ` : '')}${esc(value.sha || '')}${value.path ? ` · ${esc(value.path)}` : ''}${value.lines ? ` · ${esc(value.lines)}` : ''}</small></div>` : '';
  return `<div class="provenance" aria-label="Proveniência da falha">
    ${stage('Base segura', p.baseline)}<i>→</i>${stage('Introdução', p.introduced)}<i>→</i>${stage('Falha demonstrada', p.failure)}${p.corrected ? `<i>→</i>${stage('Correção', p.corrected)}` : ''}
  </div>`;
}
const findingsHtml = findings.length ? `<section class="findings">
  <p class="eyebrow">Classificação dos achados relacionados</p>
  ${findings.map(finding => `<div class="finding ${esc(finding.classification)}">
    <b>${findingLabels[finding.classification] || esc(finding.classification)} · ${esc(finding.id)}</b>
    <p>${md(finding.summary)}</p>
    ${provenanceHtml(finding)}
  </div>`).join('')}
</section>` : '';

const html = `<!doctype html>
<html lang="pt-BR" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review guiada — PR #${M.pr}</title>
<style>
@font-face{font-family:'Inter';font-style:normal;font-weight:400;font-display:swap;src:url(data:font/otf;base64,${FONT_DATA}) format('opentype')}
:root{color-scheme:light;--paper:#F6F7FB;--ink:#2A3545;--heading:#002E73;--muted:#727C8C;--disabled:#A8AFBA;
--line:#DDE2E8;--line-strong:#C9D0D9;--accent:#7B3DFF;--accent-hover:#4400D3;--accent-soft:#F1ECFF;
--accent-selected:#EFF1FE;--drift:#CF7F20;--drift-soft:#FFF3E3;--bug:#B91414;--bug-soft:#FCE8E8;
--success:#2DB081;--success-soft:#E3F6F0;--info:#1652ED;--info-soft:#E5EDFF;--card:#FFFFFF;--code:#F2F5F9;
--add:#E3F6F0;--addln:#0C9564;--del:#FCE8E8;--delln:#B91414;--shadow:0 3px 10px rgba(198,193,211,.22);
--gradient:linear-gradient(90deg,#00CDB9 0%,#7B3DFF 68%,#A575FF 100%);}
:root[data-theme=dark]{color-scheme:dark;--paper:#151A22;--ink:#E4E8EE;--heading:#C6D7FF;--muted:#98A2B3;--disabled:#5F6C7E;
--line:#2C3542;--line-strong:#3A4553;--accent:#A575FF;--accent-hover:#C0A0FF;--accent-soft:#2C2342;
--accent-selected:#242B3E;--drift:#E0A15A;--drift-soft:#33271A;--bug:#E4736B;--bug-soft:#361F1F;
--success:#4FC79C;--success-soft:#16302A;--info:#6B8DFF;--info-soft:#1C2740;--card:#1C232E;--code:#232B37;
--add:#16302A;--addln:#4FC79C;--del:#361F1F;--delln:#E4736B;--shadow:0 3px 14px rgba(0,0,0,.28);}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:400 16px/1.5 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
code{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.85em;background:var(--code);padding:.1em .35em;border-radius:4px}
h1,h2,h3{line-height:1.25;letter-spacing:-.012em;text-wrap:balance;color:var(--heading)}
a{color:var(--accent);text-decoration:none}a:hover{color:var(--accent-hover);text-decoration:underline}
button,a{outline-offset:3px}button:focus-visible,a:focus-visible{outline:3px solid color-mix(in srgb,var(--accent) 34%,transparent)}
.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:.7rem;font-weight:700;color:var(--accent);margin:0 0 .5rem}
.kw{color:var(--drift);font-weight:700}
.wrap{display:grid;grid-template-columns:304px minmax(0,1fr);min-height:100vh;min-width:0}
main,.content,.session,.stop,.rs,.srow>div{min-width:0}
/* rail */
aside{position:sticky;top:0;height:100vh;overflow:hidden;background:var(--card);border-right:1px solid var(--line);display:flex;flex-direction:column;font-size:.82rem}
.sidebrand{height:64px;border-bottom:1px solid var(--line);padding:0 20px;display:flex;align-items:center;gap:12px;flex:none}
.zlogo{width:28px;height:28px;border-radius:50%;background:conic-gradient(from 30deg,#7B3DFF,#00CDB9,#7B3DFF);position:relative;box-shadow:0 0 0 5px var(--accent-soft)}
.zlogo::after{content:"";position:absolute;inset:7px;background:var(--card);border-radius:50%}
.sidebrand b{display:block;color:var(--heading);font-size:.9rem;line-height:1.2}.sidebrand small{display:block;color:var(--muted);font-size:.69rem;margin-top:2px}
aside .prog{margin:16px 16px 12px;background:var(--accent-selected);border:1px solid color-mix(in srgb,var(--accent) 18%,var(--line));border-radius:12px;padding:14px 16px;flex:none}
aside .prog b{font-size:1.35rem;font-variant-numeric:tabular-nums;display:block;color:var(--heading)}
aside .prog span{color:var(--muted);font-size:.75rem}
.bar{height:6px;background:color-mix(in srgb,var(--accent) 10%,var(--card));border-radius:100px;overflow:hidden;margin-top:10px}
.bar i{display:block;height:100%;background:var(--gradient);width:0;transition:width .2s}
.railscroll{overflow-y:auto;padding:4px 12px 24px;scrollbar-width:thin;flex:1}
.rs{margin:10px 0 18px}
.rst{font-weight:700;font-size:.78rem;margin:0 8px 6px;color:var(--heading);overflow-wrap:anywhere}
.rst small{color:var(--muted);font-weight:500}
aside ol{list-style:none;margin:0;padding:0}
aside li a{display:flex;gap:8px;align-items:center;color:var(--muted);text-decoration:none;padding:7px 8px;border-radius:8px;
font-size:.73rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
aside li a:hover{background:var(--code);color:var(--ink);text-decoration:none}
aside li a.done{opacity:.45;text-decoration:line-through}
aside li a.active{background:var(--accent-soft);color:var(--accent);font-weight:700;box-shadow:inset 3px 0 0 var(--accent)}
.rnum{color:var(--accent);font-weight:700;font-variant-numeric:tabular-nums;min-width:24px;text-align:center;flex:none;background:var(--accent-soft);border-radius:100px;padding:2px 4px}
.sidefoot{border-top:1px solid var(--line);padding:12px 16px 16px;flex:none}
/* head */
.topbar{height:64px;background:var(--card);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 28px;position:sticky;top:0;z-index:20}
.crumb{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:.8rem}.crumb b{color:var(--heading)}
.productdot{width:8px;height:8px;background:var(--accent);border-radius:50%;box-shadow:0 0 0 4px var(--accent-soft)}
.topactions{display:flex;align-items:center;gap:8px}.iconbtn{width:40px;height:40px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);cursor:pointer;font-size:1rem}
.iconbtn:hover{border-color:var(--accent);background:var(--accent-soft)}
.primaryaction{min-height:40px;display:inline-flex;align-items:center;padding:0 16px;background:var(--accent);color:#fff;border-radius:8px;font-weight:700;font-size:.8rem}
.primaryaction:hover{background:var(--accent-hover);color:#fff;text-decoration:none}
.content{width:100%;max-width:1240px;margin:0 auto;padding:32px 40px 96px}
header.top{position:relative;background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:32px;overflow:hidden}
header.top::before{content:"";position:absolute;inset:0 0 auto;height:4px;background:var(--gradient)}
header.top h1{font-size:2rem;font-weight:700;line-height:1.25;margin:.2rem 0 .75rem;max-width:30ch}
header.top .thesis{max-width:72ch;color:var(--ink);font-size:1rem;margin-bottom:1.1rem}
header.top .sub{color:var(--muted);font-size:.85rem;overflow-wrap:anywhere}
.claim{border-left:3px solid var(--info);background:var(--info-soft);padding:14px 18px;border-radius:0 12px 12px 0;margin:16px 0;max-width:82ch;font-size:.9rem}
.prepstate{border-left:3px solid var(--drift);background:var(--drift-soft);padding:14px 18px;border-radius:0 12px 12px 0;margin:16px 0;max-width:84ch;font-size:.9rem}.prepstate.ok{border-color:var(--success);background:var(--success-soft)}.prepstate p{margin:4px 0}.prepstate strong{color:var(--ink)}
.dmap{border:1px solid var(--line);border-radius:12px;background:var(--paper);padding:16px;margin:20px 0 0;display:flex;gap:8px;align-items:stretch;overflow-x:auto}
.dcol{flex:0 0 auto;display:flex;flex-direction:column;gap:.3rem;min-width:170px}
.dlab{margin:0 0 .2rem;font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700}
.dnode{font-family:ui-monospace,Menlo,monospace;font-size:.7rem;background:var(--accent-soft);color:var(--accent);
padding:.22rem .45rem;border-radius:5px;white-space:nowrap}
.dnode.spec{background:var(--code);color:var(--muted)}
.darrow{align-self:center;color:var(--muted);flex:none}
/* sessions */
.session{margin:32px 0 0;scroll-margin-top:80px}
.shead{display:grid;grid-template-columns:auto 1fr;column-gap:12px;align-items:center;margin-bottom:16px}
.shead::before{content:"";width:4px;height:42px;border-radius:100px;background:var(--accent)}
.shead>*{grid-column:2}.shead h2{font-size:1.35rem;font-weight:700;margin:0 0 4px}
.goal{color:var(--muted);font-size:.9rem;max-width:70ch;margin:0}
.stop{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);padding:20px 24px;margin:16px 0;scroll-margin-top:80px;transition:border-color .15s,box-shadow .15s}
.stop:hover{border-color:var(--line-strong);box-shadow:0 8px 24px rgba(198,193,211,.24)}
.srow{display:flex;gap:.85rem;align-items:flex-start}
.tick{flex:none;width:36px;height:36px;border-radius:100px;border:1.5px solid var(--line);background:var(--paper);
color:var(--muted);font:700 .8rem/1 Inter,system-ui;cursor:pointer;font-variant-numeric:tabular-nums;display:grid;place-items:center}
.tick:hover{border-color:var(--accent);color:var(--accent)}
.stop.done .tick{background:var(--accent);border-color:var(--accent);color:#fff}
.stop.done .tick span{display:none}
.stop.done .tick::after{content:"✓";font-size:.95rem}
.stop.done{opacity:.62}
.stop.done:hover{opacity:1}
.stop h3{font-size:1rem;font-weight:650;margin:.15rem 0 .35rem;font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere;color:var(--ink)}
.dir{color:var(--muted);font-weight:400;font-size:.8rem}
.base{font-size:.92rem}
.badges{margin:0;display:flex;flex-wrap:wrap;gap:.35rem}
.badge{font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;padding:.15em .5em;border-radius:99px;
background:var(--code);color:var(--muted)}
.badge.dep.zero{background:var(--success-soft);color:var(--success)}
.badge.alpha{background:var(--drift-soft);color:var(--drift)}
.orderwhy{font-size:.88rem;color:var(--ink);margin:.75rem 0 0;max-width:76ch;border-left:2px solid var(--accent);padding-left:.75rem}
.orderwhy b{color:var(--accent);text-transform:uppercase;font-size:.68rem;letter-spacing:.07em}
.proof{border-left:3px solid var(--success);background:var(--success-soft);border-radius:0 12px 12px 0;padding:14px 18px;margin:.9rem 0}.proof p{margin:.25rem 0;font-size:.87rem;max-width:80ch}.proof .peyebrow{font-size:.68rem;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:6px}.proof .preading{color:var(--success);font-weight:650}.proof pre{overflow-x:auto;background:var(--code);padding:8px 12px;border-radius:8px;font-size:.72rem;white-space:pre-wrap}.proof.missing{border-color:var(--bug);background:var(--bug-soft)}
.prep{margin:.9rem 0 .3rem;padding:12px 16px;background:var(--accent-soft);border:none;border-radius:8px;font-size:.87rem}
.prep>b{font-size:.66rem;letter-spacing:.08em;color:var(--accent);text-transform:uppercase}
.prep .at{font-size:.68rem;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
.prep p{margin:.35rem 0 0;max-width:82ch}
.hunk{margin:1rem 0 0;border-top:1px dashed var(--line);padding-top:.75rem}
.hunk.quiet{opacity:.78}.hunk.quiet:hover{opacity:1}
.hunk.noise{border-top:none;padding-top:.3rem;margin-top:.3rem}
.hunk.gap>.hh{color:var(--drift)}
.hunk.gap summary{color:var(--drift)}
.hunk.gap summary::before{color:var(--drift)}
.nsum{color:var(--muted);text-transform:none;letter-spacing:0;font-weight:500;font-size:.72rem;font-style:italic}
.nsum .hmeta{font-style:normal;margin-left:.4rem}
.kbd{font-size:.72rem;color:var(--muted);margin:.9rem 0 0;line-height:1.8}
.kbd kbd{font:600 .7rem/1 ui-monospace,Menlo,monospace;background:var(--code);border:1px solid var(--line);
border-bottom-width:2px;border-radius:4px;padding:.25em .45em;color:var(--ink)}
.hh{display:flex;flex-wrap:wrap;gap:.6rem;align-items:baseline;font-size:.74rem}
.scope{font-family:ui-monospace,Menlo,monospace;color:var(--ink);font-weight:600}
.hmeta{color:var(--muted);font-variant-numeric:tabular-nums}
.gh{margin-left:auto;color:var(--accent);text-decoration:none;font-weight:650}.gh:hover{text-decoration:underline}
details{margin:.5rem 0 0}
summary{cursor:pointer;font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;font-weight:700;list-style:none}
summary::before{content:"›";display:inline-block;color:var(--accent);font-size:1rem;transition:transform .15s;margin-right:.3rem}
details[open] summary::before{transform:rotate(90deg)}
.dtbl{overflow-x:auto;border:1px solid var(--line);border-radius:8px;margin-top:.45rem;background:var(--paper)}
.dtbl table{border-collapse:collapse;width:100%;font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.76rem;line-height:1.5}
.dtbl td{padding:0 .45rem;white-space:pre;vertical-align:top}
.dtbl .ln{width:1%;text-align:right;color:var(--muted);user-select:none;font-size:.7rem;background:var(--code)}
.dtbl .sg{width:1%;user-select:none;font-weight:700}
.dtbl .tx{width:98%}
tr.a{background:var(--add)}tr.a .sg,tr.a .ln{color:var(--addln)}
tr.d{background:var(--del)}tr.d .sg,tr.d .ln{color:var(--delln)}
tr.hit .tx{box-shadow:inset 3px 0 0 var(--drift)}
.findings{margin:1.5rem 0}.finding{border-left:3px solid var(--muted);background:var(--code);border-radius:0 10px 10px 0;padding:.75rem 1rem;margin:.6rem 0;font-size:.86rem}
.finding p{margin:.35rem 0 0}.finding.introduced_bug{border-left-color:var(--bug);background:var(--bug-soft)}
.finding.fixed_introduced_bug{border-left-color:var(--success);background:var(--success-soft)}
.finding.inherited_debt{border-left-color:var(--drift);background:var(--drift-soft)}
.finding.rollout_constraint{border-left-color:var(--accent);background:var(--accent-soft)}
.finding.assessment{border-left-color:var(--success);background:var(--success-soft)}
.provenance{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr);gap:.55rem;align-items:stretch;margin:.8rem 0 .15rem}.provenance>i{align-self:center;color:var(--muted);font-style:normal}.pstage{border:1px solid var(--line);border-radius:8px;background:var(--card);padding:.65rem .75rem;min-width:0}.pstage span{display:block;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-size:.62rem;font-weight:700}.pstage b{display:block;font-size:.76rem;margin:.28rem 0;color:var(--ink)}.pstage small{display:block;color:var(--muted);font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere}
.review-context{border-left:3px solid var(--info);background:var(--info-soft);padding:.6rem .85rem;border-radius:0 8px 8px 0}.review-context blockquote{margin:.55rem 0;padding:.55rem .7rem;background:var(--card);border:1px solid var(--line);border-radius:6px}.review-context p{margin:.25rem 0 0}
.checkpoint{border:1px solid color-mix(in srgb,var(--accent) 30%,var(--line));border-radius:12px;background:var(--accent-selected);padding:16px 20px;margin:20px 0 0}
.checkpoint ul{list-style:none;margin:.4rem 0 .6rem;padding:0;display:flex;flex-direction:column;gap:.45rem}
.checkpoint label{display:flex;gap:.6rem;align-items:flex-start;font-size:.9rem;cursor:pointer;max-width:76ch}
.checkpoint input{margin-top:.35rem;accent-color:var(--accent);flex:none}
.cpnote{font-size:.78rem;color:var(--muted);margin:0;max-width:74ch}
.integrity{font-size:.83rem;color:var(--muted);list-style:none;padding:0;max-width:80ch}
.integrity li{padding:.3rem 0;border-top:1px solid var(--line)}
.integrity b{color:var(--ink);font-variant-numeric:tabular-nums}
.integrity .err{color:var(--bug)}
footer{margin-top:48px;border-top:1px solid var(--line);padding:24px 0;font-size:.85rem;color:var(--muted);max-width:90ch}
.bignum{display:flex;gap:.6rem;flex-wrap:wrap;margin:1.25rem 0}
.bn{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:145px;flex:1}
.bn b{display:block;font-size:1.5rem;font-weight:700;font-variant-numeric:tabular-nums;color:var(--heading)}
.bn span{font-size:.75rem;color:var(--muted);display:block;line-height:1.35}
@media (max-width:960px){.wrap{grid-template-columns:1fr}aside{position:static;height:auto;max-height:46vh;border-right:0;border-bottom:1px solid var(--line)}.sidebrand{display:none}.railscroll{max-height:30vh}.topbar{position:static}.content{padding:24px 20px 72px}.provenance{grid-template-columns:1fr}.provenance>i{transform:rotate(90deg);justify-self:center}}
@media (max-width:640px){.content{padding:16px 12px 64px}.topbar{padding:0 14px}.crumb span:not(.productdot){display:none}.primaryaction{padding:0 12px}header.top{padding:24px 18px}header.top h1{font-size:1.55rem}.stop{padding:16px 14px}.srow{gap:10px}.dir{display:none}}
@media print{aside,.topbar{display:none}.wrap{display:block}.content{max-width:none;padding:0}.stop{box-shadow:none;break-inside:avoid}details:not([open])>*:not(summary){display:block}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body>
<div class="wrap">
<aside>
  <div class="sidebrand"><span class="zlogo" aria-hidden="true"></span><div><b>Revisão Zoppy</b><small>Épico de WhatsApp</small></div></div>
  <div class="prog"><b id="pc">0/${stops.length}</b><span>paradas lidas · ~${M.sessions.reduce((a,s)=>a+s.minutes,0)} min no total</span><div class="bar"><i id="pb"></i></div></div>
  <div class="railscroll">${rail}</div>
  <div class="sidefoot"><p class="kbd"><kbd>j</kbd>/<kbd>k</kbd> navegar · <kbd>x</kbd> marcar lida<br>progresso salvo neste navegador</p>
  <p style="font-size:.7rem;color:var(--muted);margin:.75rem 0 0"><a href="../wpp-review-experience.html">← Todas as revisões</a></p></div>
</aside>
<main>
<div class="topbar"><div class="crumb"><span class="productdot" aria-hidden="true"></span><b>WhatsApp epic</b><span>/</span><span>PR #${M.pr}</span></div>
  <div class="topactions"><button class="iconbtn" id="theme" type="button" aria-label="alternar tema" title="Alternar tema">◐</button>
  <a class="primaryaction" href="https://github.com/${M.repo}/pull/${M.pr}" target="_blank" rel="noopener">Abrir PR ↗</a></div></div>
<div class="content">
<header class="top">
  <p class="eyebrow">${esc(M.eyebrow || 'Guia de revisão')}</p>
  <h1>PR #${M.pr} — ${esc(M.title)}</h1>
  <p class="thesis">${esc(M.thesis)}</p>
  <p class="sub"><a href="https://github.com/${M.repo}/pull/${M.pr}" target="_blank" rel="noopener" style="color:var(--accent)">github.com/${M.repo}/pull/${M.pr}</a> · ${paths.length} arquivos · head <code>${M.headSha}</code> · base <code>${M.baseRef}</code></p>
  <p class="sub">docs do épico: ${(M.docsLinks || []).map(d => `<a href="${esc(d.href)}">${esc(d.label)}</a>`).join(' · ')}</p>
  <div class="prepstate ${M.prep?.complete ? 'ok' : ''}"><p><strong>Estado da preparação:</strong> ${esc(M.prep?.summary || 'não informado')}</p>${M.prep?.gap ? `<p><strong>Lacuna registrada:</strong> ${esc(M.prep.gap)}</p>` : ''}${M.prep?.retry ? `<p><strong>Nova tentativa:</strong> ${esc(M.prep.retry)}</p>` : ''}</div>
  <div class="claim">${md(M.claim || 'A ordem editorial segue definições → operações → callers → specs; a lista alfabética do GitHub não preserva essa dependência.')}</div>
  ${M.prepWarning ? `<div class="claim"><b>COBERTURA DE PREP INCOMPLETA:</b> ${md(M.prepWarning)}</div>` : ''}
  ${findingsHtml}
  <div class="bignum">
    <div class="bn"><b>${M.loc.logicAdd-M.loc.logicDel>=0?'+':''}${M.loc.logicAdd-M.loc.logicDel}</b><span>saldo de linhas de lógica (+${M.loc.logicAdd} / −${M.loc.logicDel})</span></div>
    <div class="bn"><b>${M.loc.specAdd-M.loc.specDel>=0?'+':''}${M.loc.specAdd-M.loc.specDel}</b><span>saldo de linhas de testes (+${M.loc.specAdd} / −${M.loc.specDel})</span></div>
    <div class="bn"><b>${prepComments.length}</b><span>notas de contexto no trecho correspondente</span></div>
    <div class="bn"><b>${M.sessions.length}</b><span>sessões guiadas em vez de ${paths.length} arquivos soltos</span></div>
  </div>
  <div class="dmap">${depthCols}</div>
</header>
${sessionHtml}
<footer>
  <p class="eyebrow">Integridade do guia</p>
  ${integrity}
  <p>Gerado a partir do diff da PR, dos comentários exportados e de um manifesto explícito de ordenação. A ordem das paradas é editorial; a profundidade e os dependentes cobrem somente imports diretos resolvidos entre arquivos alterados.</p>
  <p><b>Atualidade:</b> este guia corresponde ao commit completo <code>${M.headSha}</code>. Um novo push invalida números de linha e âncoras; gere outro arquivo.</p>
</footer>
</div></main></div>
<script>
const themeButton=document.getElementById('theme');
const savedTheme=localStorage.getItem('rx-theme')||'light';
document.documentElement.dataset.theme=savedTheme;
themeButton.setAttribute('aria-pressed',String(savedTheme==='dark'));
themeButton.addEventListener('click',()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;localStorage.setItem('rx-theme',next);themeButton.setAttribute('aria-pressed',String(next==='dark'));});
const K='rx-${String(M.repo).replace(/[^a-zA-Z0-9]+/g,'-')}-pr${M.pr}-${M.headSha}';
const S=JSON.parse(localStorage.getItem(K)||'{}');
const save=()=>localStorage.setItem(K,JSON.stringify(S));
const total=${stops.length};
function paint(){
  let n=0;
  document.querySelectorAll('.stop[data-stop]').forEach(el=>{
    const i=el.dataset.stop, done=!!S['s'+i];
    el.classList.toggle('done',done);
    const r=document.querySelector('[data-rail="'+i+'"]'); if(r) r.classList.toggle('done',done);
    if(done)n++;
  });
  document.getElementById('pc').textContent=n+'/'+total;
  document.getElementById('pb').style.width=(100*n/total)+'%';
}
document.querySelectorAll('.tick').forEach(b=>b.addEventListener('click',()=>{
  const i=b.dataset.tick; S['s'+i]=!S['s'+i]; save(); paint();
}));
document.querySelectorAll('input[data-belief]').forEach(c=>{
  c.checked=!!S['b'+c.dataset.belief];
  c.addEventListener('change',()=>{S['b'+c.dataset.belief]=c.checked;save();});
});
paint();
const io=new IntersectionObserver(es=>{es.forEach(e=>{
  if(e.isIntersecting){
    document.querySelectorAll('[data-rail]').forEach(a=>a.classList.remove('active'));
    const r=document.querySelector('[data-rail="'+e.target.dataset.stop+'"]');
    if(r){r.classList.add('active');r.scrollIntoView({block:'nearest'});}
  }})},{rootMargin:'-20% 0px -70% 0px'});
document.querySelectorAll('.stop[data-stop]').forEach(s=>io.observe(s));
document.addEventListener('keydown',e=>{
  if(e.target.matches('input,textarea'))return;
  if(e.key==='j'||e.key==='k'){
    const ss=[...document.querySelectorAll('.stop[data-stop]')];
    const cur=ss.findIndex(s=>s.getBoundingClientRect().top>-40);
    const t=ss[Math.max(0,Math.min(ss.length-1,e.key==='j'?cur+1:cur-1))];
    if(t)t.scrollIntoView({behavior:'smooth',block:'start'});
  }
  if(e.key==='x'){
    const ss=[...document.querySelectorAll('.stop[data-stop]')];
    const c=ss.find(s=>{const r=s.getBoundingClientRect();return r.top<200&&r.bottom>200;});
    if(c){S['s'+c.dataset.stop]=!S['s'+c.dataset.stop];save();paint();}
  }
});
</script></body></html>`;

fs.mkdirSync(OUT.replace(/\/[^/]+$/, ''), { recursive: true });
fs.writeFileSync(OUT, html);
const duplicatePaths = stops.map(s => s.path).filter((p, i, all) => all.indexOf(p) !== i);
const missingProofs = stops.flatMap(s => s.proofs || []).filter(id => !PROOFS[id]);
const invalidFindingClasses = findings.filter(f => !VALID_FINDING_CLASSES.has(f.classification)).map(f => `${f.id}:${f.classification}`);
const incompleteProvenance = findings.filter(f => introducedClasses.has(f.classification) && !completeProvenance(f)).map(f => f.id);
const integrityErrors = [];
if (M.schemaVersion === 2) {
  if (M.designVersion !== GENERATOR_VERSION) integrityErrors.push(`designVersion esperado ${GENERATOR_VERSION}`);
  if (M.diffSha256 !== DIFF_SHA256) integrityErrors.push('diffSha256 não corresponde ao diff de entrada');
  if (missing.length) integrityErrors.push(`${missing.length} arquivo(s) do diff sem parada`);
  if (extra.length) integrityErrors.push(`${extra.length} parada(s) fora do diff`);
  if (duplicatePaths.length) integrityErrors.push(`${duplicatePaths.length} caminho(s) duplicado(s)`);
  if (gapHunks.length) integrityErrors.push(`${gapHunks.length} trecho(s) de lógica sem preparação ancorada`);
  if (missingProofs.length) integrityErrors.push(`${missingProofs.length} prova(s) ausente(s)`);
  if (invalidFindingClasses.length) integrityErrors.push(`${invalidFindingClasses.length} classe(s) de achado inválida(s)`);
  if (incompleteProvenance.length) integrityErrors.push(`${incompleteProvenance.length} falha(s) introduzida(s) sem proveniência completa`);
}
const htmlSha256 = crypto.createHash('sha256').update(html).digest('hex');
const sidecar = {
  schemaVersion: 2,
  generatorVersion: GENERATOR_VERSION,
  designVersion: M.designVersion || 'legado',
  repository: M.repo,
  pr: M.pr,
  baseSha: M.baseSha,
  headSha: M.headSha,
  hashes: {
    manifest: crypto.createHash('sha256').update(fs.readFileSync(MANIFEST)).digest('hex'),
    diff: DIFF_SHA256,
    comments: crypto.createHash('sha256').update(JSON.stringify(COMMENTS)).digest('hex'),
    font: crypto.createHash('sha256').update(fs.readFileSync(FONT_PATH)).digest('hex'),
    html: htmlSha256
  },
  coverage: {
    changedPaths: paths.length,
    stops: stops.length,
    missingPaths: missing,
    extraPaths: extra,
    duplicatePaths,
    meaningfulUncoveredHunks: gapHunks
  },
  comments: {
    canonicalPrep: prepComments.filter(c => CANONICAL_PREP.test(c.body || '')).length,
    legacyPrep: prepComments.filter(c => LEGACY_PREP.test(c.body || '')).length,
    reviewContext: nonPrepComments.length
  },
  dependencyModel: {
    scope: 'imports diretos resolvidos entre arquivos alterados',
    resolvedEdges: edgeCount,
    alphabeticalCallerFirstEdges: edgeViolations
  },
  findings: {
    total: findings.length,
    invalidClasses: invalidFindingClasses,
    incompleteIntroducedBugProvenance: incompleteProvenance
  },
  externalAssetRequests: 0,
  result: integrityErrors.length ? 'failed' : 'passed',
  errors: integrityErrors
};
const sidecarPath = OUT.replace(/\.html$/, '.integrity.json');
fs.writeFileSync(sidecarPath, JSON.stringify(sidecar, null, 2) + '\n');
console.log('wrote', OUT, (html.length/1024).toFixed(0)+'KB');
console.log('wrote', sidecarPath);
console.log('uncovered files:', missing.length ? missing : 'none');
console.log('manifest paths not in diff:', extra.length ? extra : 'none');
console.log('edge violations', edgeViolations+'/'+edgeCount, 'pair inversions', pairInversions+'/'+pairs);
if (integrityErrors.length) {
  console.error('falhas de integridade:', integrityErrors);
  process.exitCode = 2;
}
