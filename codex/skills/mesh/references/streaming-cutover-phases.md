# Streaming Cutover Phases (Direct Replacement)

This rollout replaces wave-barrier orchestration with streaming execution and does not keep a fallback mode.

## Completion Definition

A unit is complete only when both are true:

- fixer decision is accepted with quorum satisfied
- proof_status is pass (after at most one retry)

## Phases

1. Phase 0: baseline instrumentation
   - capture units/hour, proof fail rate, reject rate, scope conflict requeue rate
2. Phase 1: patch-only author lanes + output-contract v2
   - coder/reducer lanes emit candidates with scope/risk metadata
3. Phase 2: prove-all worktree lanes
   - locksmith/applier/prover run for all candidates
4. Phase 3: reservation + adaptive quorum
   - mutating phases require write_scope lease
   - low/med/high quorum target = 1/2/3
5. Phase 4: CAS multi-instance scaling
   - scale only when remaining budget and saturation gates allow it
6. Phase 5: persistence and resume
   - event log + checkpoints recover in-flight orchestration

## Acceptance Gate

Done for rollout requires a full-batch soak that demonstrates:

- positive units/hour delta versus baseline
- no closure regressions (accepted + proof-pass for every completed unit)
- no uncontrolled overlap in mutating write scopes
