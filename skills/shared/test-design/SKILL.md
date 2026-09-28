---
name: test-design
description: Use when writing, adding or changing tests or spec files during development — a feature, a bugfix, "escreve o teste", "cria o spec", "adiciona teste pra isso", "cobre com teste", "write tests for", "add tests", "test this service", "TDD", "red-green", ".spec.ts", "test coverage" — and before opening a PR that changes tested behavior.
---

# Test design

## Principle

A test exists to **try to break the code**, not to confirm what it already does. So the expected value of every test comes from the **rule**: the card, the acceptance criteria, the contract of the caller. Never from reading the implementation.

If the rule does not say how the system should behave in a situation, that is not a detail to fill in with whatever the code does today. It is a **question for the dev**, and it comes before the test.

**The two rules with no exceptions:**
1. Do not write an expected value you only know because you read the code.
2. Do not change an expected value to make the test pass. A test that fails against the code is a finding, not a test error.

## Procedure

### 1. Read the rule before the code

Look, in this order, at: the "Exemplos" table in the card's acceptance criteria; the rest of the card or the refinement; the feature's OKF concept; the caller's contract (another service, the workflow node, the screen). Write down what each source says. Only then read the implementation.

### 2. List the classes of each input

For everything the function receives or reads (parameters, payload fields including the optional ones, session, prior state in the database, how many times it runs, environment), list the equivalence classes and the boundaries. Use [input-catalog.md](input-catalog.md). For every numeric or date boundary: the exact value, one below, one above. For a helper, normalizer or mapper, add the `property-tests` skill.

### 3. Decide the expected value of each class: ask what matters, declare the rest

For each row, the expected value and its source. When no source answers, the row is a **question** or an **assumption**. A dev answers a few questions carefully and ignores a long list, so separate them:

A **question** is a row where the current behavior of the code is **suspicious**:
1. the code contradicts another source (the caller, the other system, the concept, the method name);
2. the code handles a class **silently**: discards it, uses a default, treats empty or `0` as missing, swallows an error;
3. there is a boundary (number, date, quantity) with no rule saying which side it falls on;
4. the rule applies to one variant (payment method, provider, role, status) and nobody knows whether it applies to the others.

**At most 5 questions per file**, in the order above. Each one says what the code does, why it is suspicious, and which test depends on the answer. Write the questions in the dev's language:

> **E4 — cupom de R$1.** O código recusa (`amount <= 1`). O nó de cupom do workflow aceita R$1. Qual é o certo? Se for "aceita", o teste E4 vai falhar contra o código atual.

An **assumption** is everything else: a row with no rule where the code does something reasonable. Do not ask. Write the test with the current behavior, mark its source as `suposição`, and list all of them in a single block for the dev to correct if they want:

> Vou assumir, salvo correção: E9 lista vazia devolve `[]`; E11 telefone sem DDI é aceito; E14 …

**Never ask** about test mechanics (mock or not, which helper, adding a dependency): decide from the project conventions. Nor about internal details no caller can see.

The answer to each question becomes the source of that row (`dev, <date>`).

### 4. Write and run the tests

One `it()` per row covered by a unit test, with the ID at the start of the name: `it('E4 cupom de R$1 é válido')`. Each test builds the fixture **with the row's value** and asserts **the exact expected value**. Avoid the smells in [spec-smells.md](spec-smells.md).

**Setup and mechanics come from the repo, not from this skill.** Read the test conventions the repo documents: the file its `CLAUDE.md` points to (in zoppy-api, `rules/testing.md`) or the "Testing" section of the `CLAUDE.md` itself. That file also lists the repo's own history of escaped bugs; add those classes to the catalog when the code under test is in that area. If the repo documents nothing, follow the patterns of the existing specs next to the file.

Run only the file's spec. When a test fails:

> **E4 falhou.** Esperado (dev, 26/09): cupom de R$1 válido. O código recusa em `create-provider-coupon.helper.ts:88`. É bug no código, ou a regra é outra?

**Stop and show it to the dev.** Do not change the expected value or the code without their decision.

## Output in the PR

The PR is written in Portuguese. Keep these headings and the counted line **verbatim**:

```markdown
## Entradas testadas
| ID | Entrada | Esperado | De onde veio | Coberto por |
|----|---------|----------|--------------|-------------|

## Perguntas feitas
- E4: cupom de R$1 → válido (dev, 26/09)

## Suposições
- E9, E11, E14 (comportamento atual; corrija se estiver errado)

## Achados
Bugs pegos na criação dos testes: 1
- E7: <o que era esperado × o que o código fazia> → bug, corrigido neste PR
- E9: <o que era esperado × o que o código fazia> → regra era outra, teste ajustado (não conta)
```

"Coberto por" is `unit`, `QA` (becomes a QA case through `return-solution`) or `não coberto: <reason>`.

**The line "Bugs pegos na criação dos testes: N" is mandatory**, with that exact text, even when N is 0. It is counted automatically across PRs, and a PR with 0 still counts, as part of the denominator. A bug counts as caught when a test failed against the code, the dev confirmed it was a bug, and the code was fixed. It does not count when the dev decided the rule was different and the test was adjusted; that finding stays listed, marked "não conta".

## Bugfix

Row E1 is the input that broke, and its test **fails before the fix**. Run it before fixing and confirm. Then go through the neighboring classes of the same dimension, because bugs tend to have siblings.

## Signs you are making the test pass

| Thought | What to do |
|---|---|
| "The code does X, so the expected value is X" | Where does X come from besides the code? If nowhere, ask |
| "The card doesn't mention it, but it's obvious" | If the code handles it silently or contradicts someone, ask. Otherwise, declare it as an assumption |
| "I'll ask about everything I don't know" | Up to 5 questions, the suspicious ones. The rest becomes declared assumptions |
| "The test failed, I'll adjust the expected value" | It is a finding. Show it to the dev |
| "This edge case is unlikely" | Ask whether it is impossible. Unlikely happens in production |
| "I'll test only the happy path and the bug" | Go through every catalog dimension the code reads |
| "I'll use the factory default, it works" | The row's value is the point of the test |
