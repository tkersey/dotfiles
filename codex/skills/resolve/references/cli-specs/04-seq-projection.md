# Seq Projection

`seq review-compiler-audit` exposes the local session/controller evidence used
by the resolve closure gate.

## Summary Projection

`seq review-compiler-audit --mode summary --format json` exposes flat counts for
candidate sessions, true resolve sessions, tuple/terminal closure, material run
coverage, RAC/mutation/closure gate coverage, violation counters, semantic
surface movement, orphan constructs, unmapped proof actions, and
wound-specific tests.

## Run Projection

`seq review-compiler-audit --mode runs --format jsonl` emits one row per
candidate or material run. Rows include session/run identity, repository,
protocol, C3 lifecycle booleans, closure booleans, compression state, batch and
kernel progress, semantic surface delta, AC rebase state, RAC totals, mutation
and closure gate status, orphan/unmapped/wound counters, and class-mapping
status.

## Contamination Policy

Current audit prompts, generated reports, quoted examples, and skill-body schema
examples are excluded from positive workflow evidence. Projection limitations
remain separate from controller failures.
