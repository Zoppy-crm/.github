---
name: zoppy-deck
description: Build a Zoppy deck — full-viewport, self-contained HTML slides delivered as a local file. Use when the user asks for a deck, presentation or slides, and whenever another skill must render its results as one.
---

# Zoppy deck

A deck is a **local HTML file** that fills the viewport, never scrolls, and carries its own font and
styles so it survives being emailed. You author only the slides; `scripts/build_deck.py` supplies the
**shell** — tokens, embedded Inter, slide counters, nav dots, keyboard/click/swipe handling.

Never hand-write the shell. Never publish a deck as a claude.ai artifact.

`<zoppy-deck>` below is this skill's directory.

## Steps

### 1. Settle the spine before writing any HTML

Write the slide titles as a list first, in order. A deck earns each slide or drops it.

The spine always ends on a **gaps slide** — what this deck's numbers do not say. For a measurement
deck that means excluded population, unmeasurable cases, and the definition choices that would move
the number. Zoppy decks state their gaps; a deck that only flatters is not finished.

**Done when:** every slide has a one-line claim, and the last one is the gaps slide.

### 2. Author the slides fragment

One file holding only `<section class="slide">` blocks, first one carrying `on`:

```html
<section class="slide on">
  <div class="topbar"><div class="brand">Zoppy · Engenharia</div><div class="counter">{{COUNTER}}</div></div>
  <div class="inner">
    <div class="eyebrow">Kicker</div>
    <h2>The claim of this slide</h2>
    ...
  </div>
</section>
```

Write `{{COUNTER}}` literally — the builder numbers it. Hand-numbering drifts the moment a slide
moves.

**Done when:** the fragment parses as balanced HTML and every slide carries `{{COUNTER}}`.

Before building a PT-BR deck, apply the `ptbr-natural` skill to every slide, including headings, labels, and caveats. Complete this copy review before the layout and delivery checks.

### 3. Build

```bash
python3 <zoppy-deck>/scripts/build_deck.py \
  --title "Título" --slides slides.html --out docs/<area>/<nome>.html
```

### 4. Verify, then hand over the URI

Strip the base64 font before grepping — it produces false positives on almost any short pattern.

```bash
python3 - <<'PY'
t=open('OUT.html').read(); i=t.index('base64,'); j=t.index(')',i); b=t[:i]+'[FONT]'+t[j:]
print('slides   ',b.count('<section class="slide'))
print('sections ',b.count('<section'),'/',b.count('</section>'))
print('svg      ',b.count('<svg'),'/',b.count('</svg>'))
print('external ',b.count('http://')+b.count('https://'))
PY
```

**Done when:** section and svg tags balance, external references are zero, and every number shown on
a slide has been recomputed — sums match their parts, percentages match their fractions.

Hand over copyable local file URIs to the decks.

## Reference — slide anatomy

| Element | Class | Use |
| --- | --- | --- |
| Headline figures | `.statrow` > `.stat` with `.n` `.k` `.d` | Exactly three. More than three stops reading as a headline. |
| Three-way explanation | `.cards` > `.card` with `h3`+`p` | Collapses to one column under 900px, and cards 3+ hide — put nothing load-bearing in the third. |
| Data | `<table>` with `.num` on figures, `<tfoot>` for totals | Totals belong in `tfoot`, never as a body row. |
| Callout | `.note`, `.note.ok`, `.note.warn`, `.note.crit` | One per slide reads as emphasis; three read as noise. |
| Ranked list | `.findings` > `.f` with `.t` `.w` `.sz` | Severity/label pill, claim, aside. |
| Chart | `.chartwrap` wrapping `svg.chart` | Capped at 52vh so the note below it stays visible. |

Tokens are CSS variables: `--purple` `--blue` `--ink` `--neutral` `--disabled` `--border` `--surface`
`--ok` `--warn` `--crit` `--info`. Use the variable, never the hex.

## Reference — charts

`build_deck.py` exports `barchart(rows, ymax, ticks, avg=, avg_label=, pct=, colour=)` where
`rows = [(top_label, sub_label, value, is_partial)]`. Import it rather than hand-rolling axes:

```python
sys.path.insert(0, str(Path('<zoppy-deck>') / 'scripts'))
from build_deck import barchart, build
```

`is_partial=True` greys a bar. Use it for any bucket the window cuts short — an unmarked partial
period reads as a collapse.

The viewBox is `0 0 900 315` and scales; never set a pixel width.

## Reference — language

PT-BR when coworkers open the deck, which is the normal case. Reply to the user in English
regardless of the deck's language.

Plain sentences over jargon. A number on a slide is a claim: it needs the definition that produced it
somewhere in the same deck, close enough that a reader can check it.
