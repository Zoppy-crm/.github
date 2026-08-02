# Deterministic Zoppy design contract

This file is the approved visual reference for every generated review guide. It was extracted once from Zoppy's `ui-components/projects/visual-identity` assets and the established application shell. Do not require a live or authenticated product page on each run.

## Identity

- Product font: `Inter`.
- Shipped asset: `../assets/Inter-Regular.otf`, embedded as a base64 `@font-face` data URL in every HTML guide.
- Body: Inter 400, 16px/24px.
- Highlight: Inter 600, 16px/24px; the browser may synthesize 600 from the embedded face.
- Heading scale: 20/32, 24/32, and 32/48; weight 700.
- Code only: system monospace.

The generator must fail if the bundled font is absent. A CSS declaration naming Inter without the embedded font is not compliance.

## Canonical tokens

These values are fixed inputs, not suggestions:

| Role | Value |
|---|---|
| primary purple | `#7B3DFF` |
| primary hover | `#4400D3` |
| heading blue | `#002E73` |
| ink | `#2A3545` |
| neutral | `#727C8C` |
| disabled | `#A8AFBA` |
| border | `#DDE2E8` |
| strong border | `#C9D0D9` |
| page | `#F9F9FA` |
| surface | `#FDFDFD` |
| selected | `#EFF1FE` |
| hover | `#F2F5F9` |
| info | `#1652ED` / `#E5EDFF` |
| warning | `#CF7F20` / `#FFF3E3` |
| critical | `#B91414` / `#FCE8E8` |
| success | `#2DB081` / `#E3F6F0` |
| decorative gradient | `linear-gradient(135deg, #00FFE6 14.56%, #7B3DFF 85.73%)` |

The gradient is a narrow brand accent, never a dominant hero background.

## Shell

- Desktop: 304px left navigation, 64px top bar, centered content up to 1240px.
- Mobile at 960px: one column; navigation becomes a bounded top section.
- Cards: white/surface background, 1px border, 12–16px radius, restrained shadow.
- Spacing: 8px base; common gaps 8, 12, 16, 24, 32, 40.
- Primary action: solid purple, white label, 40px minimum height.
- Reading progress: private browser state, never GitHub verdict state.
- Light is the deterministic initial theme. Dark mode is optional and must use the same hierarchy.

## Information hierarchy

1. Revision and PR identity.
2. Thesis and behavior boundary.
3. Introduced bugs, fixed introduced bugs, inherited debt, and speculation in separate treatments.
4. Provenance timeline for corrective findings.
5. Logic/spec LOC split.
6. Dependency/session map.
7. Ordered stops with raw diff and attributed rationale.
8. Falsifiable checkpoints.
9. Machine-readable integrity summary.

Author rationale, independent evidence, reviewer feedback, bot feedback, and inference must have distinct labels and colors. Never relabel an arbitrary review comment as author rationale.

## Repeated checks

Every generated artifact must pass static structural checks. Browser screenshots are required only after a generator, token, layout, font, or theme-code change. A normal PR regeneration does not trigger new visual discovery or four-viewport inspection.
