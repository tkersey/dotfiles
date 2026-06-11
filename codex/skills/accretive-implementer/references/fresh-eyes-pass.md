# Implementation Fresh-Eyes Pass

Before final output on any non-trivial code change, reread the new code, modified code, and directly relevant unchanged neighbors as if another agent wrote the patch.

Pass objective:

> Carefully read over all new code and all existing code modified in this run with fresh eyes, looking for obvious bugs, errors, broken assumptions, missing imports, stale callsites, partial-state leaks, invariant breaks, overbroad edits, under-tested behavior, confusing seams, surface creep, additive scaffolding, duplicate owners, or embarrassing blunders. Fix anything material before reporting completion.

Then run one independent second blunder pass:

> Check everything again with fresh eyes, looking for mistakes, oversights, omissions, misconceptions, scope creep, missed verification, bugs introduced by the fixes, and any added surface that does not earn itself.

Rules:

- If the pass changes code, rerun the narrowest credible verification that covers the changed behavior.
- If the pass finds no material delta, report `fresh_eyes_delta: none`.
- Do not use the pass to broaden scope; it may fix only material defects in the chosen cut or evidence/reporting gaps that would mislead closure.
