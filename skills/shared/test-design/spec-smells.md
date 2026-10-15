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
- A list that already comes sorted, so removing the `sort` of the code changes nothing. Feed it out of order when the code picks the first, the oldest or the biggest.
- Pagination tested with a single page, so the loop that fetches the next ones never runs and stopping at page 1 passes.
- A filter fed only items that pass it. Every condition of the filter needs one item that fails exactly that condition, or removing it passes.

## Paths never taken

- A `catch` that logs and goes on, with no test where the call inside it fails. Emptying the block passes.
- A fallback (`?? []`, `?.`, default value) with no test where the value is missing. Sometimes it is dead defense, sometimes it is the provider answering without the field; the test decides which.

## Setup heavier than the code

- Pure logic (mapper, util, builder, payload, an adapter over an HTTP gateway) tested through the framework container and a database. It does not hide a defect, but it costs seconds per file instead of milliseconds, and it makes mutation testing unaffordable: every mutant pays the setup again.
- The whole repository or domain layer imported to test one class. Import what the class uses.

## Mocks that hide

- A third-party library stub with `jest.fn()`: it accepts a null id without complaint, while the real library would throw.
- A cache or queue mock that returns the object ready-made, skipping the `JSON.stringify/parse` the real one does.

## Oracle

- A test name that generalizes the belief ("does not register…", "is a stub outside production") and makes the wrong behavior look intended.
- A boundary test that asserts the rejection with no source: the test sat on the right boundary and protected the bug, because the expected value came from the code.
- Defective behavior exercised and dismissed as irrelevant by a comment in the test.
