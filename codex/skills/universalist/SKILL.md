---
name: universalist
description: >
  Use when code smells point to a structural refactor that should ship: flag or state matrices,
  repeated boundary validation, shared-key agreement checks, branchy policy logic, syntax mixed
  with execution, or protocol state encoded as primitive bags. Default to one signal, one seam,
  one smallest honest construction, adapter-first staging, one proof signal, and an explicit
  reduction preflight so the new abstraction does not add more tax than it removes.
---

# Universalist

Use this skill when the highest leverage comes from changing the *shape of truth* in a codebase, not from adding another ordinary feature branch.

This is an inner lens for choosing and staging a structural move. It is not a generic implementation skill and it is not an abstraction maximizer. Use it to decide whether to climb into a stronger construction, then let the repo's normal implementation flow carry the change.

## Abstraction elevator

`universalist` climbs. `reduce` descends. They should share the same altitude map.

Before recommending a construction, classify the move:

- `climb`: a stronger shape removes repeated obligations or impossible states.
- `descend`: a lower-level primitive would preserve the same truth with less tax; hand off to `reduce`.
- `hold`: the current shape is justified by value, public obligation, protocol safety, or proof weakness.
- `split`: reduce an incidental wrapper while preserving or improving the essential invariant.

Read `references/abstraction-altitude.md` and `references/abstraction-move-packet.md` for shared vocabulary.

## Do not trigger for

- Routine feature work with no structural smell.
- Pure performance tuning, infra, UI polish, or docs work.
- Broad rewrites with no stable seam.
- Cases where the domain rules are still too unstable to freeze into a stronger model.
- Places where a lower-level primitive is plainly enough and no repeated obligation is being deleted.

## Quick start: pick a track

### Track A — Diagnosis only

Use when the user wants analysis, design review, refactor advice, or a structural reading of current code.

Deliver:

- observed signal
- current and proposed abstraction altitude
- chosen construction or `hold`/`ask_reduce`
- why nearby alternatives are worse
- reduction preflight
- first seam to attack
- proof signal
- compatibility notes

### Track B — One-seam refactor

Use when the user wants code changes, but the right move is narrow and reviewable.

Deliver:

- one seam only
- smallest honest construction
- adapter-first staging when a public boundary exists
- fastest credible proof signal
- explicit stop point after the first verified seam
- post-lift deletion/reduction opportunities

### Track C — Staged migration

Use when the internal model should improve while API, JSON, DB row, or message shapes stay stable for now.

Deliver:

- boundary decoder or adapter
- internal stronger model
- parity or differential tests
- migration notes
- clear cut line between legacy shape and internal shape
- handoff packet for follow-up seams

## Non-negotiables

- One signal, one seam, one smallest honest construction.
- Prefer products, coproducts, refined/equalizer types, pullback witnesses, exponentials, and free constructions before advanced machinery.
- Keep wire and storage shapes stable behind adapters unless the user explicitly wants a breaking change.
- Use the repo's current language, framework, and test stack before proposing new libraries.
- Say what remains runtime-only in dynamic or weakly typed environments.
- Run a reduction preflight before choosing a higher abstraction.
- Stop after the first verified seam unless the user asked for a sweep.

## Step 0 — Create or update `.universalist-plan.md`

Create this file in the project root for Track B or Track C. Use `scripts/init_universalist_plan.sh` if helpful.

Minimum fields:

```md
# Universalist Plan

## Track:
## Signal:
## Current altitude:
## Proposed altitude:
## Construction:
## Why this construction:
## Lower-level alternative rejected:
## Seam / files:
## Public boundaries touched:
## Wire/storage compatibility plan:
## Verification command(s):
## Runtime-only leftovers:
## Reduction preflight:
## Post-lift reduction opportunity:
## Status: planned / editing / verified / staged
## Next seam:
```

If context compacts, read this file first and resume from its status line.

## Operator loop

### 1. Inspect repo reality

Identify:

- language and type features
- framework conventions
- serializer, ORM, persistence, and API boundaries
- current test runner and proof tools
- build/codegen requirements
- existing public, wire, and storage shapes

### 2. Build an altitude map

Record the layers present at altitudes 0 through 5. Note which layers carry domain truth and which layers mostly impose ceremony, generated surface, hidden control flow, or toolchain tax.

### 3. Find candidate signals

Start from code smells and pressure, not category labels:

- flag, enum string, boolean, or nullable field matrices
- the same predicate enforced in several places
- repeated shared-id or shared-version agreement checks
- branchy policy logic that really wants supplied behavior
- syntax mixed with execution, logging, explanation, or persistence
- protocol state hidden in optional fields or lifecycle booleans

Use `scripts/detect_signals.py` for a heuristic first pass. Treat its output as scouting, not proof.

### 4. Run reduction preflight

Before choosing a construction, answer:

- What abstraction tax will this new structure add?
- What repeated obligation does it delete?
- Could a lower-level primitive solve this without a new model?
- Does the construction improve agent-editability or make edits more indirect?
- If scored with `reduce`'s `T/V/D` rubric, is this still worth doing?

If the lower primitive wins, hand off to `reduce`. If the invariant is essential but the wrapper is not, recommend a `split` move.

### 5. Pick one seam

Choose the smallest stable seam where the stronger shape can land with low blast radius.

Good first seams:

- DTO -> domain conversion
- controller or handler boundary
- constructor or factory
- one central service, reducer, or evaluator
- one join helper or aggregate constructor
- one state transition boundary

### 6. Choose the smallest honest construction

- Independent fields -> product.
- Exclusive states -> coproduct.
- Repeated stable predicate -> refined type / equalizer.
- Shared projection agreement -> pullback witness.
- Configurable behavior -> exponential.
- Syntax separate from execution -> free construction / initial algebra.
- Stateful allowed operations -> explicit transition table or reducer, often with a coproduct.

Do not claim a construction without naming the engineering behavior it buys: constructor, eliminator, checked projection agreement, behavior-as-data, or syntax/interpreter separation.

### 7. Plan the boundary

Decide whether the seam can change in place or whether it needs:

- decoder
- adapter
- DTO / row mapping
- persistence converter
- legacy-to-new translation layer
- compatibility wrapper for external callers

### 8. Encode idiomatically

Use the strongest encoding the repo can actually support:

- native ADT
- sealed hierarchy / enum with payload
- interface + tag
- checked constructor or wrapper
- witness type
- closure or strategy
- AST + interpreters
- explicit transition table or reducer

Avoid HKT-heavy, typeclass-heavy, macro-heavy, or reflection-heavy patterns where the language and repo cannot carry them cleanly.

### 9. Verify with the fastest credible proof signal

Prefer:

- compile or typecheck
- targeted unit tests
- exhaustive handling checks
- constructor-only entry
- decode / encode round-trip
- mismatch rejection
- parity or differential tests during migration
- transition-table coverage for protocols

### 10. Post-lift reduction hook

After the seam is verified, identify residue that the lift made redundant:

- duplicate validators/checks/adapters
- dead flags and null guards
- framework/plugin hooks that now only forward
- compatibility wrappers that should remain for public boundaries
- follow-up cut list for `reduce`

Do not continue into those cuts unless the user asked for a sweep. Name the next seam and stop.

## Practical decision guide

| Repo smell | Default construction | Nearby alternative to reject first | First seam | Proof signal |
|---|---|---|---|---|
| `status`, booleans, and nullable fields describe one lifecycle | Coproduct | Product with optional fields | Decoder + core state type | exhaustive handling + invalid legacy fixture tests |
| Same input predicate repeated at controllers, services, serializers | Refined type / equalizer | Raw primitive plus helper validation | Parse / constructor boundary | accept valid, reject invalid, normalization idempotence |
| `customer.accountId != subscription.accountId` appears in several places | Pullback witness | Plain pair + scattered assertions | checked aggregate constructor | mismatch rejection + preserved projections |
| Large branch decides pricing, rendering, or policy | Exponential | Bigger state machine | function / strategy seam | fixture parity against old branch |
| Rule syntax mixed with execute / explain / log | Free construction | More conditionals inside existing class | AST + one interpreter | interpreter consistency + differential tests |
| Several fields always travel together and are consumed independently | Product | Coproduct | record / struct / object | constructor and projection consistency |
| Allowed operations change by lifecycle phase | Coproduct + transition table | Boolean matrix or generic workflow engine | reducer or command handler | invalid transition rejection + valid transition fixtures |

## Do not universalize table

| Smell | Tempting construction | Prefer instead |
|---|---|---|
| One-off branch | Exponential / strategy | direct conditional or local function |
| One evaluator only and no need to explain/log/render syntax separately | Free construction | direct data + function |
| Predicate unstable or still being discovered | Refined type | local validation until the rule stabilizes |
| Pair checked once at one boundary | Pullback witness | one assertion near the join |
| UI state is simple and local | state machine | plain event handler or reducer |
| Framework layer is the real pain | new domain model first | `reduce` audit or split move |
| New construction adds more files than checks it removes | abstraction lift | stay lower and document the invariant locally |

## Output contract

For any non-trivial response, produce these headings in order:

1. **Track**
2. **Signal**
3. **Altitude delta**
   - Current altitude:
   - Proposed altitude:
   - Why climbing is cheaper than staying lower:
   - What lower-level alternative was rejected:
4. **Construction**
5. **Reduction preflight**
6. **Why this instead of nearby alternatives**
7. **Seam / files**
8. **Boundary and compatibility plan**
9. **Before -> After**
10. **Verification**
11. **Runtime-only leftovers**
12. **Post-lift reduction opportunity**
13. **Next seam** optional

For Track B or Track C, also update `.universalist-plan.md`.

## Guardrails

- Prefer plain engineering language over category jargon when both say the same thing.
- Do not recommend new validation, property-test, codegen, framework, or state-machine libraries without user approval.
- Do not widen the seam just because the larger design looks elegant.
- Call out persistence, serialization, and public API breakage explicitly.
- Say when a validator is only runtime protection.
- If evidence is incomplete, cap the recommendation at diagnosis or first seam.
- When `reduce` and `universalist` disagree, produce an Abstraction Move Packet and route through an adjudicator.

## Hand-offs and companion skills

- Use `reduce` when the proposed higher structure appears to add more tax than it removes.
- Use `invariant-ace` when the main job is discovering or pinning down invariants before choosing structure.
- Use `accretive-implementer` after the construction is chosen and the task becomes ordinary implementation.
- Use `repeatedly-apply-skill` when sweeping the repo for multiple seams or doing a multi-pass campaign.

## References

- `references/abstraction-altitude.md`
- `references/abstraction-move-packet.md`
- `references/reduction-preflight.md`
- `references/universalist-overview.md`
- `references/discovery-signals.md`
- `references/language-encoding-matrix.md`
- `references/framework-boundaries.md`
- `references/cost-model-and-false-positives.md`
- `references/structures-and-laws.md`
- `references/testing-playbook.md`
- `references/migration-playbooks.md`
- `references/case-studies.md`
- `references/eval-prompts.md`
- `references/examples-haskell.md`
- `references/examples-go.md`
- `references/examples-typescript.md`
- `references/examples-python.md`
- `references/examples-java-kotlin.md`
- `references/examples-rust-swift.md`
- `references/sources.md`

## Scripts

- `scripts/init_universalist_plan.sh`
- `scripts/detect_signals.py`
- `scripts/emit_scaffold.py`
- `scripts/emit_boundary_adapter.py`
- `scripts/emit_verification_plan.py`
- `scripts/emit_law_test_stub.sh`
- `scripts/validate_scaffold.py`

## Templates

- `templates/universalist-plan.md`
- `templates/universalist-report.md`
