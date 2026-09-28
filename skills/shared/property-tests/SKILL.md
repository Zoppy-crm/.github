---
name: property-tests
description: Use when writing or changing tests for a helper, normalizer, formatter, parser, mapper, price or date calculation, cache/serialization round-trip, or any operation that must be idempotent — "normaliza telefone", "formata", "converte", "mapeia o payload", "roda duas vezes", "teste de propriedade", "fast-check", "property-based".
---

# Property-based tests

## Principle

An example test checks the inputs someone remembered to write. A property test generates hundreds of inputs and checks a rule that holds for **all** of them. It catches exactly what escapes at Zoppy: a whitespace-only string, `NaN`, swapped case, `undefined` turning into `"undefined"`, a second run duplicating data, a value that comes back different from the cache.

It does not replace example tests. It complements them where the function has a general rule.

## When to use

- **Yes:** helper, normalizer, formatter, parser, payload mapper, price, date or coupon calculation, serialization, an operation that runs again (sync, backfill, assignment).
- **No:** orchestration whose result only makes sense with a hand-built scenario. There, use example tests with the `test-design` skill.

## The properties

Pick the ones that hold for the function. Each one is an `it()`.

| Property | Form | Catches |
|---|---|---|
| **Does not crash** | any input of the accepted type, including `null` and `undefined` if the type allows them, throws no unexpected error | TypeError on an empty list, a null id |
| **Valid output** | the output always meets the contract: never `"undefined"`/`"null"`, never `NaN`, price ≥ 0, phone digits only | `String(undefined)`, sentinel `0` |
| **Idempotence** | `f(f(x))` equals `f(x)` | normalization applied twice |
| **Round-trip** | `read(write(x))` equals `x` | a date coming back from the cache as a string |
| **Equivalence** | `f(x)` equals `f(variant(x))` when they should be equal: case, leading/trailing spaces, mask | an email with different case |
| **Repeating does not duplicate** | running the operation twice leaves the same state as once | feature assignment duplicating |

## Generators

Default generators rarely produce the values that break things. Always mix in:

```typescript
import fc from 'fast-check';

const riskyText = fc.oneof(
    fc.string(),
    fc.constantFrom('', ' ', '   ', '\t', '\n'),
    fc.string().map((s) => `  ${s}  `),
    fc.mixedCase(fc.string())
);
const riskyNumber = fc.oneof(fc.double(), fc.constantFrom(0, 1, -1, NaN, Infinity, -Infinity));
const optional = <T>(arb: fc.Arbitrary<T>) => fc.option(arb, { nil: undefined });
```

## Example

```typescript
it('normalizePhone é idempotente e nunca devolve texto que não seja dígito', () => {
    fc.assert(
        fc.property(optional(riskyText), (input) => {
            const once = normalizePhone(input);
            expect(normalizePhone(once)).toEqual(once);
            expect(once === null || /^\d*$/.test(once)).toBe(true);
        })
    );
});
```

With a database (sync, backfill), use `fc.asyncProperty` with `{ numRuns: 20 }` and clean the database on every run.

## When a property fails

fast-check shrinks the input to the smallest counterexample. Turn that counterexample into a **fixed example test** with the literal value. It documents the case and keeps running even if the generator changes. If the function was fixed because of it, it is a new row in the PR's "Entradas testadas" table.

## Setup

`fast-check` is not in any Zoppy repo yet. Adding it as a devDependency changes `package.json` and the lock file: **confirm with the dev first**, and follow the repo's lock-file rule (in some repos `npm i` prunes packages; check the lock diff). Without it, write the same properties as loops over hand-built lists of risky values.
