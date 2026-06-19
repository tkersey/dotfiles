# Controller

Canonical command:

```bash
python3 codex/skills/resolve/tools/review_compile.py --help
```

The controller stores local state under `.resolve-c3/`, manages the lab worktree, registers candidates, selects the lexicographic winner, emits MRPC, applies the exact patch, and gates commit/push.

The existing configured `$st` hooks delegate to the controller when C³ state is active.
