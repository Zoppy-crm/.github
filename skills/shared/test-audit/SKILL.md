---
name: test-audit
description: Use when reviewing whether an existing spec actually verifies the code it covers — a PR that touches .spec.ts files, a file that just had a bug fixed despite having tests, "esse teste pega o bug?", "revisa esse teste", "o que falta nesse spec", "lacunas do teste", coverage green and a defect escaped anyway.
---

# Test audit

## Principle

Coverage says the line ran, not that a test would fail if the output were wrong. This skill asks a single question: **assuming the code has a defect the spec does not catch, what is it?**

Measured on real bugs that escaped existing specs, this question, asked directly and with a concrete input, pointed at the defect in about 1 case out of 3. A longer procedure (a class catalog, a full table) did not raise that number. That is why the skill is short: ask the question well.

## How to do it

Read the source file, the spec, and the factories or seed helpers the spec uses. Then list **exactly 5 gaps**, from most to least likely. Each one with:

- **A concrete input or state** the spec does not exercise or does not verify. A value, not a category: `fullName = '   '`, not "test strings".
- **What the code does** with that input, from reading the code, and whether it looks wrong.
- **Why the spec does not catch it:** it does not exercise it; it exercises it, but the assertion cannot tell right from wrong; or the spec asserts something that may be wrong.

## Where it usually is

- A fixture that uses a single value across every test for a field the code reads.
- A weak assertion on a computed value: `toBeDefined`, `length > 0`, `toHaveBeenCalled` with no arguments.
- A test that asserts a rejection, a block, a stub, or "does not do": check whether another source (the caller, the card, the other system) agrees with that expected value.
- A mock that accepts any argument, or that skips the serialization the real thing does.

## What it does not catch

A rule nobody wrote down, a contract with another system, concurrency, and state that changes between runs rarely show up from reading only the file and the spec. If the feature's card exists, read it first: that is where the right expected value comes from.

Write the gaps in the dev's language.
