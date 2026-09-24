# Deterministic Zoppy HTML reports

Use this contract for every substantive coworker-facing Zoppy report produced by this skill. Markdown may be retained as internal source. The delivered artifact is HTML.

## Fixed visual input

Do not ask for a page, login, screenshot, or visual reference. The identity is fixed here:

- font: Inter from `../assets/Inter-Regular.otf`;
- primary purple: `#7b3dff`;
- dark purple: `#4400d3`;
- heading blue: `#002e73`;
- body text: `#2a3545`;
- muted text: `#727c8c`;
- border: `#dde2e8`;
- page: `#f9f9fa`;
- surface: `#fdfdfd`;
- selected/accent surface: `#eff1fe`;
- informational surface: `#e5edff`;
- warning surface: `#fff3e3`;
- critical surface: `#fce8e8`;
- success surface: `#e3f6f0`.

Use the diagonal cyan-to-purple accent only as a small brand rule. Do not use it as a page background or large decorative area.

## Document structure

Every report contains, in this order:

1. title, scope, exact revision or evidence horizon, and generated timestamp;
2. bounded conclusion;
3. completed, incomplete, blocked, and deferred deliverables;
4. evidence tables;
5. introduced bugs, inherited debt, and unproved concerns in distinct sections;
6. exact unrun checks and stale measurements;
7. links to PRs and companion HTML artifacts.

Use short paragraphs and tables. Avoid dashboards, marketing heroes, decorative status pills, gradients behind content, and monospace body text.

## Language

Use one language per artifact. For PT-BR, write controlled technical Portuguese: active voice, one claim per sentence, consistent terms, and no literal translations of English idioms. Preserve code identifiers and established team terms only when they improve precision.

## Validation

Normal report generation requires deterministic checks only:

- the font asset exists and is embedded or packaged with the HTML;
- the expected sections and revision pins exist;
- every local link resolves inside the package;
- the HTML makes no unplanned external asset request;
- tables can scroll on narrow screens;
- no finding appears in more than one classification.

Do not perform visual discovery or repeated aesthetic inspection. Use one representative browser regression only after changing this contract, its font, or the shared report template.
