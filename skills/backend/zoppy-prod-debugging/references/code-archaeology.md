# Code archaeology — naming the culprit with git

```bash
git fetch origin   # ALWAYS — stale local master has produced a wrong narrative
git log origin/master --first-parent --format='%h | committed:%ci | %s' --since=<window>
git log origin/master -S '<HotSymbol>'                 # did the deploy touch this path?
git log origin/master --diff-filter=A -- '*<thing>*'   # is it brand new?
git diff <merge>^1 <merge> --name-status               # merge-parent archaeology
git show '<merge>^1:<path>'                            # read the old file
git grep -n "<pattern>" <merge>^1 -- 'src/*.ts'        # enumerate call sites AS THEY WERE
```

Committer date (`%ci`) = when it landed; landing ≠ deployed — the deploy merge PR
timestamps are the real event. For dependency bumps: exact version from
`package-lock.json`, then `git diff <oldTag> <newTag> -- src` in the library repo
(fetch it first; local clones go stale). Ruling *out* (hot symbol unchanged →
backlog, not regression) is as valuable as ruling in.

**Attribution honesty**: a tokenized-SQL → code attribution can silently hit a
sibling call-site. A shape mismatch (`IN (...)` vs single id) disqualifies the
match — don't rationalize it. When your own output lists a second candidate
(another queue, another helper), address it before concluding.

Index existence: prefer live `information_schema.STATISTICS` via the SQL proxy
(`zoppy-debug-with-grafana`, datasource recipes); repo migrations are a
drift-prone proxy.
