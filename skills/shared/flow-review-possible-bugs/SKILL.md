---
name: flow-review-possible-bugs
description: Review the current PR diff for possible bugs, logic errors, edge cases, and risky patterns. Use when the user asks to "review bugs", "find bugs in the PR", "checar bugs", "revisar bugs", or wants a bug-focused analysis of current changes.
---

# Review Possible Bugs

Analyzes the current PR diff looking for bugs, logic errors, edge cases, and risky patterns.

## Workflow

### Step 1: Collect the current PR diff

Identify the current PR and get the full diff:

```bash
gh pr view --json number,title,baseRefName
git diff origin/<base-branch>...HEAD
```

If no PR is open, use the diff of the current branch against the base:

```bash
git log --oneline origin/main..HEAD
git diff origin/main...HEAD
```

### Step 2: Analyze the diff by bug category

Walk through the full diff actively looking for:

**Logic errors**
- Inverted conditionals (`!` in the wrong place, `&&` vs `||`)
- Incorrect comparisons (`==` vs `===`, `>` vs `>=`)
- Off-by-one errors in loops, slices, pagination
- Wrong order of operations

**Missing or incorrect error handling**
- `await` without `try/catch` on operations that can fail
- Silenced errors with empty `catch(() => {})`
- API return values not checked before use
- Unhandled promises (floating promises)

**State and side effect problems**
- Direct mutation of state/props instead of copying
- Race conditions in concurrent async operations
- Missing dependencies in `useEffect` / dependency arrays
- Stale data used after an async operation

**Unchecked null/undefined**
- Property access without null-check (`obj.prop` where `obj` may be null)
- Destructuring without default values
- Empty array not checked before `.map`, `.find`, `.reduce`

**Security issues**
- User data inserted into queries without sanitization
- Hardcoded secrets or tokens
- Input values used in shell commands or SQL without validation

**Type / coercion problems**
- Comparing different types without explicit conversion
- `parseInt` without radix
- Accidental string + number concatenation

**Ignored edge cases**
- Empty strings treated as valid
- Empty lists not handled
- Zero values interpreted as falsy when they shouldn't be

### Step 3: Build the report

For each bug found, record:

```
**[SEVERITY] File:line — Category**
Description of the problem.
Problematic code snippet.
Suggested fix.
```

Severity levels:
- `CRITICAL` — can cause crash, data loss, or silent failure in production
- `HIGH` — incorrect behavior in common cases
- `MEDIUM` — edge case likely to appear in real usage
- `LOW` — potential issue but low impact

### Step 4: Final summary

At the end of the report, present:

```
## Summary

- Bugs found: X (Y critical, Z high, W medium, V low)
- Affected files: <list>
- Recommendation: [Block merge / Review before merge / Can merge with caution]
```

## Rules

- **Focus only on the diff** — do not report issues in code not changed by the PR
- **Report only real bugs** — do not suggest style, performance, or architecture improvements
- **Include the exact snippet** of the problematic code to make it easy to locate
- **Explain the concrete risk** — "can cause X" instead of "this is a problem"
- **Do not open PRs or make commits** — report only

## Output

Return the report directly in the chat, without creating files, in English.
