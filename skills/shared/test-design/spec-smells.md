# Spec smells that hide defects

## Assertions that cannot tell right from wrong

- `toBeDefined()`, `toBeTruthy()`, `length > 0` on a value the code computes: any non-empty output passes, including a duplicated list.
- Asserting only the main side effect when the method also returns a computed value, so the computed value is never checked.
- Counting the wrong proxy: number of queries when the cost is rows read.
- Nulling two inputs in the same test, so nobody knows which rule fired.

## Fixtures that pin the partition

- A factory that always fills the optional field, so the "missing" class is never exercised.
- The same literal in every test (the same phone, the same email in the database and in the input).
- `as unknown as T` building an object that cannot exist in production (for example, a user without the company it belongs to).

## Mocks that hide

- A third-party library stub with `jest.fn()`: it accepts a null id without complaint, while the real library would throw.
- A cache or queue mock that returns the object ready-made, skipping the `JSON.stringify/parse` the real one does.

## Oracle

- A test name that generalizes the belief ("does not register…", "is a stub outside production") and makes the wrong behavior look intended.
- A boundary test that asserts the rejection with no source: the test sat on the right boundary and protected the bug, because the expected value came from the code.
- Defective behavior exercised and dismissed as irrelevant by a comment in the test.
