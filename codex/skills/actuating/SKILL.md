---
name: actuating
description: "Plan-to-PR execution controller for material work. Compile intent into canonical `$st` graph state, require a current CLI-emitted GCR-v1, compile one AFR-v1 frontier/route record for each non-trivial aperture, realize only that selected route through `$fixed-point-driver`, record obligation-level proof, recompile the graph, and ship with explicit PR mode. Use for `$actuating`, plan-to-PR, implement this plan and open a PR, or `$st` -> fixed point -> proof -> `$ship`. Never degrade a failed material graph into prose-driven mutation."
metadata:
  version: "2.0.0"
  activation_cost: high
  default_depth: standard
---

# Actuating

## Mission

```text
plan
-> canonical $st graph
-> current GCR-v1
-> AFR-v1
-> selected-route realization
-> focused proof + $st completion
-> new GCR
-> wave/final proof
-> explicit PR mode
-> $ship
```

Invariant:

```text
No material delivery mutation without a current executable GCR and a valid
AFR bound to that GCR, artifact state, and selected task set.
```

## Authority

```text
$st                  durable graph, proof/status, GCR, projection
$actuating           frontier/route, cadence, plan-to-PR and ship decision
$fixed-point-driver  bounded realization of an already selected route
language skills      language hazards and proof lanes
read-only specialists frontier/proof/wave evidence
$ship                PR creation/update/promotion
$land                separate explicit merge workflow
```

## Modes

### Material graph

Use for material plans, cross-file work, meaningful dependency/proof graphs, or work expected to survive compaction.

Require:

```text
canonical .step/st-plan.jsonl
implementation-ready graph
current executable GCR-v1
valid AFR-v1
```

### Graph repair

Enter when graph compile/currentness/projection fails or blocking unwaived debt exists.

Only read/search, graph/intake/debt repair, and proof/frontier analysis are allowed.

No delivery mutation, task completion, or ship.

### Simple ledger

Only for clearly bounded work with no material graph.

Report:

```text
Graph not compiled; proceeding in ledger mode.
```

A material plan never silently degrades to ledger mode.

## 1. Pin ASR-v2

Maintain `actuation_state / ASR-v2` with run/plan/objective, artifact state, target PR intent, contract versions, graph/GCR, AFR set, proof, surface, and ship state.

After compaction, reread a skill only when its recorded version/fingerprint changed or current evidence requires it.

## 2. Compile the plan

```bash
st intake scaffold --source <plan.md> --out .step/st-intake.md
# Fill/edit semantic intake.
st intake check --input .step/st-intake.md \
  --gate implementation-ready --format json
st intake normalize --input .step/st-intake.md \
  --out .step/st-intake.normalized.md
st intake apply --file .step/st-plan.jsonl \
  --input .step/st-intake.normalized.md \
  --gate implementation-ready
st compile aperture --file .step/st-plan.jsonl --limit 7
```

`st intake plan` is only a deprecated scaffold alias.

Use only `.step/st-plan.jsonl`; never create a sidecar durable plan to route around debt.

## 3. Enforce GCR-v1

Material execution requires a CLI-emitted GCR proving:

```text
current durable seq/fingerprints
implementation-ready gate
execution_allowed = yes
no blocking unwaived debt
dependency-ready selected tasks
proof obligations
current native projection
```

When this fails:

```text
graph-repair mode
no delivery mutation
```

See [st-control-gate.md](references/st-control-gate.md).

## 4. Project once

Publish only exact `plan_sync.codex.plan` from the current GCR.

- preserve `[st-id]`;
- never project graph envelope;
- never hand-author the frontier;
- one `update_plan` publication per GCR sequence/fingerprint;
- another requires explicit projection-drift repair.

Block:

```text
failed/stale graph
-> repeated update_plan
-> prose frontier
-> material mutation
```

## 5. Compile AFR-v1

Create:

```text
.step/actuation/<run-id>/<slice-id>.afr.json
```

AFR references `$st`; it does not own task status.

It binds artifact/GCR/tasks, owner/invariant, counterexample quotient, selected/rejected routes, mutation boundary, surface budget, proof DAG, next frontier, and SDR-v1 decision projection.

Group raw combinations only when accepted observations, owner, route, and proof law match.

```bash
python3 codex/skills/actuating/tools/afr_gate.py <afr.json>
```

See [actuation-frontier-record.md](references/actuation-frontier-record.md) and [counterexample-quotient.md](references/counterexample-quotient.md).

## 6. Use specialists conditionally

Root is the sole writer.

```text
actuation_frontier_mapper  unclear/recurring state space or owner
actuation_proof_mapper     unclear proof cut/currentness
actuation_wave_skeptic     material completed wave or surface growth
```

Use them at frontier/wave boundaries, not after every patch.

See [frontier-specialists.md](references/frontier-specialists.md).

## 7. Select before realization

Routes:

```text
no_change
validate_only
reuse_existing_owner
delete_or_collapse
canonicalize
representation_change
bounded_new_surface
blocked
```

Before mutation record alternatives, selected/rejected routes, owner, permitted scope, forbidden actions/non-goals, surface budget, proof obligations, route-flip condition, and expected outcome.

If selection is unresolved, do not call `$fixed-point-driver`.

## 8. Hand off ARH-v1

For non-trivial mutation emit `actuation_realization_handoff / ARH-v1` containing:

```text
run/slice/GCR/AFR/task identity
artifact state
selected route and owner
scope and forbidden actions
surface budget
selected class/invariant
proof obligations
```

`$fixed-point-driver` realizes this route and may use `$accretive-implementer` for narrow writing.

It may not change class, route, owner, scope, or semantics.

See [fixed-point-execution-loop.md](references/fixed-point-execution-loop.md).

## 9. Consume FPSR-v1

```bash
python3 codex/skills/fixed-point-driver/tools/fpsr_gate.py <result.json>
```

Results:

```text
valid
return_to_frontier
blocked
invalid
```

`return_to_frontier` stops mutation, updates the quotient/evidence and `$st` scope/obligations when needed, then requires a new AFR/ARH.

Never append an adjacent patch under the stale route.

## 10. Tier proof

```text
slice  focused proof for selected class/invariant
wave   affected aggregate proof after coherent aperture/subset
ship   one complete current-head closure suite
```

Run full proof earlier only when repository policy or the dependency cut requires it.

Track proof as missing/running/pass/fail/stale with explicit invalidators.

See [validation-cadence.md](references/validation-cadence.md).

## 11. Record and recompile

After valid realization/focused proof:

```bash
st proof plan --file .step/st-plan.jsonl --scope aperture --format json
st proof record --file .step/st-plan.jsonl \
  --id <st-id> --obligation <proof-id> --action <proof-action-id> \
  --command "<command>" --evidence-ref <proof-log> \
  --artifact-ref "git:<sha-or-working-tree-fingerprint>"
st complete --file .step/st-plan.jsonl --id <st-id>
st compile aperture --file .step/st-plan.jsonl --limit 7
st assert-projection --file .step/st-plan.jsonl
```

If the installed proof parser is narrower, keep `$st` truthful with the smallest accepted command and report the parser gap. Do not create sidecar task status.

## 12. Resume after compaction

Resume from ASR-v2, latest GCR, active AFR, current proof receipts, and Git state:

```bash
python3 codex/skills/actuating/tools/actuation_resume.py \
  --state <asr.json> --frontier <afr.json>
```

Invalidate resume when artifact state, GCR/tasks, proof currentness, or contract fingerprints changed.

Do not reconstruct the frontier from prose or repeated skill reads.

## 13. Learn at inflections

Use `$learnings` for validation transitions, strategy pivots, hidden footguns, repeated acceleration patterns, and delivery boundaries—not every turn.

## 14. Ship gate

Require:

```text
no unhandled in-scope tasks
current GCR/projection
all AFRs terminal
no unresolved return-to-frontier observation
focused/wave proof accounted for
full closure proof current
PR publication in scope
explicit PR mode
```

```yaml
pr_mode_decision:
  mode: ready | draft | update-existing | promote-draft | blocked
  reason:
  draft_allowed_reason:
```

Default:

```text
complete graph + terminal AFRs + current full proof -> ready
```

No `$ship` without explicit mode. `$ship` does not merge.

See [shipping-gate.md](references/shipping-gate.md) and [pr-mode-decision.md](references/pr-mode-decision.md).

## 15. Validate final state

```bash
python3 codex/skills/actuating/tools/asr_gate.py <state.json> --mode ship
```

ASR-v2 binds graph/GCR/projection, AFR/FPSR set, task counts, decision receipts, proof currentness, surface delta, ship mode, and blockers.

## Output

End with:

```text
Actuation Bottom Line:
- target state:
- GCR / graph mode:
- active or final AFR:
- tasks complete / blocked / deferred / open:
- selected route / owner:
- focused / wave / closure proof:
- surface delta:
- PR mode:
- PR:
- blocker / next frontier:
```

## Hard rules

- No material mutation without current executable GCR-v1.
- No material mutation with blocking unwaived graph debt.
- No material graph-failure fallback to prose/ledger execution.
- No non-trivial mutation without valid AFR-v1.
- `update_plan` is a GCR projection, never the state machine.
- `$actuating` selects; `$fixed-point-driver` realizes.
- New observations return to frontier.
- Root is the sole writer.
- Full proof is wave/ship cadence, not default per patch.
- No ship without current graph, terminal frontier, current proof, and explicit PR mode.
- Do not merge or land.
