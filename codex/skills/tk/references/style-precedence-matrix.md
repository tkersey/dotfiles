# TK Style Precedence Matrix

Use this when TK doctrine collides with a wrapper, worker lane, or repo-local contract.

## Decision order
1. Outer artifact contract
2. Explicit task envelope / scope fence
3. Stable boundary + invariants
4. Proof posture
5. Repo dialect
6. TK prose shape

If two layers disagree, satisfy the higher layer and keep the lower-layer discipline internal.

## What each layer owns

| Layer | Owns | Never override with |
| --- | --- | --- |
| Outer artifact contract | Exact output shape (`diff`, `NO_DIFF:`, JSON, patch-only worker output) | TK chat sections |
| Task envelope / scope fence | Write scope, risk tier, proof delegation, caller constraints | A "cleaner" wider refactor |
| Stable boundary + invariants | Seam choice, abstraction level, where the rule lives | Easier prose or file-local convenience |
| Proof posture | Executed signal, delegated proof, equivalence leash, characterization harness | Wishful claims or faux PASS |
| Repo dialect | Naming, error style, test harness, architecture vocabulary | Imported patterns from another repo |
| TK prose shape | Section order and wording in non-strict mode | Any higher-priority artifact contract |

## Common conflict resolutions

### Strict-output worker lane
- Situation: a strict-output author worker requires one fenced `diff` block or `NO_DIFF:`.
- Resolve: run TK internally, emit only the required artifact.
- Keep internal: Contract, Invariants, Creative Frame, Cut Rationale, and any wider portfolio analysis.

### Scope fence vs cross-module inevitability
- Situation: stable boundary spans two files/modules.
- Resolve: cross the module boundary only if both files are inside scope and the wider cut deletes drift/shotgun edits.
- Otherwise: add the smallest seam now and surface the blocked widening explicitly.

### Small patch vs highest provable tier
- Situation: a tiny file-local branch "works" but keeps the bug-class alive.
- Resolve: pick the higher tier when it remains reviewable, incremental, and provable.
- Heuristic: if the smaller cut duplicates validation or adds a new boolean/flag, it usually loses.

### Proof ownership mismatch
- Situation: wrapper/output contract delegates proof to orchestrator or another lane.
- Resolve: do not fake local proof; describe the proof hook or leave proof out if the outer contract forbids prose.

## Review questions
- Did the chosen seam remove a future branch/check instead of moving it?
- Did artifact constraints change only the output shape, not the code-shape decision?
- Did we widen scope only because the stable boundary demanded it?
- Is the proof claim exactly as strong as the executed or delegated signal?
