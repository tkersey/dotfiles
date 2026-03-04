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
3. Phase 2: prove-selected worktree lanes
   - fixer selects one candidate; prover applies it in an isolated worktree and runs proof (bounded retry)
   - optional full-mesh apply: locksmith/applier before prover when reservation-gated apply is required
4. Phase 3: scope gating + adaptive quorum
   - treat write_scope as exclusive lock roots; serialize overlapping scopes
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
