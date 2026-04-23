# Review grading rubrics

## Complexity Delta

Use this grid when assessing complexity pressure.

### Overall delta
- `reduces`: the current state removes incidental complexity or collapses risky surface area
- `neutral`: complexity is roughly unchanged or increases only in essential, justified ways
- `increases`: incidental complexity grows in a way that adds fragility, burden, or misuse risk
- `indeterminate`: there is not enough evidence to judge the delta confidently

### Complexity vectors
Assess only the vectors that matter:
- `control-flow`: branching, fallback trees, special cases
- `state`: mutable state, hidden caches, lifecycle burden
- `coupling`: tighter dependency entanglement or hidden reliance
- `config-surface`: more knobs, flags, or environment requirements
- `API-surface`: broader caller obligations or public behavior area
- `operational-surface`: rollout, observability, migration, or runbook burden
- `cognitive-load`: how hard the artifact is to reason about or safely modify

### Essential vs incidental
- `essential`: required by the problem or domain constraints
- `incidental`: created by the implementation shape rather than by the problem itself

## Invariant Ledger

### Tiers
- `critical`: breakage would compromise correctness, safety, security, data integrity, or system validity
- `major`: breakage would cause notable regressions or user-visible instability
- `supporting`: useful stabilizers whose failure matters but is not system-defining

### Status
- `preserved`: current evidence supports the invariant still holding
- `strained`: the invariant may still hold but the patch makes it easier to violate or harder to verify
- `broken`: the invariant no longer holds or is directly contradicted by evidence
- `unknown`: the invariant might matter, but the current evidence is insufficient to classify it safely

### Confidence
- `proven`: directly supported by strong evidence such as code, tests, or logs
- `plausible`: supported, but not decisively
- `speculative`: a meaningful concern, but under-evidenced

### Blast radius
- `local`: limited to one function, file, or narrow path
- `module`: affects a subsystem or package
- `cross-cutting`: affects callers, storage, deployment, or multiple subsystems

## Foot-Gun Register

A foot-gun is behavior that is easy to use incorrectly, easy to misread, or likely to fail silently.

### Ease of misuse
- `low`: misuse requires unusual behavior or violating obvious expectations
- `medium`: misuse is realistic in normal maintenance or integration
- `high`: misuse is likely during ordinary usage, extension, or incident response

### Detectability
- `obvious`: misuse fails loudly or is likely to be noticed quickly
- `subtle`: misuse can slip through review or partial testing
- `silent`: misuse can persist without immediate visible failure

### Common foot-gun classes
- unsafe defaults
- misleading names or contracts
- hidden ordering requirements
- partial-failure traps
- retry or idempotency traps
- reentrancy or concurrency hazards
- silent fallback behavior
- hidden global state
- fragile rollout or migration assumptions
