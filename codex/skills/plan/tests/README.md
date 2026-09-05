# Plan regression checks

Run from the repository root:

```bash
uv run codex/skills/plan/tests/test_plan.py
```

The graph tests exercise source-byte fidelity, acyclic prerequisites, foreign-seam
factor use, global factor identity, and the adaptive example's common final proof.
They are artifact checks, not a replacement for native Ledger or evidence that a
model followed the skill. Native admission tests run the installed Ledger bootstrap,
check the imported export definition, and exercise missing owner, source, boundary,
lock, rollback, retirement, and repository-affecting-probe cases. An unavailable
Ledger is reported as skipped, never as validated. Run those tests before accepting
changes to the passive definition.

For a fresh-session behavioral check, use the local, adaptive, and revision examples
in `assets/` as illustrative source contracts against a matching disposable repository.
Give the implementation session only one complete block and that repository, not the
original prompt, another example, or synthesis history. Check whether it invents a
material requirement, needs missing context, takes both alternative routes, credits
an unselected branch's proof, or cannot establish the stated done-state. The revision
must preserve identity but must not need revision 1 to execute revision 2.

These are manual replay cases, not claimed completed model evaluations. Keep model
results separate from deterministic artifact-test results; no new evaluation store
or runtime score is required.
