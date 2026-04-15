---
name: universalist
description: >
  Use when code smells point to a structural refactor that should ship:
  flag or state matrices, repeated boundary validation, shared-key agreement
  checks, branchy policy logic, or syntax mixed with execution. Default to one
  seam, one smallest honest construction, adapter-first staging, and one proof
  signal.
---

# Universalist

Use this skill when the highest leverage comes from changing the *shape of truth*
in a codebase, not from adding another ordinary feature branch.

This is an **inner lens** for choosing the right structural move. It is not a
generic implementation skill. Use it to decide and stage the structure, then let
the repo's normal implementation flow carry the change.

## Do not trigger for

- Routine feature work with no structural smell
- Pure performance tuning, infra, UI polish, or docs work
- Broad rewrites with no stable seam
- Cases where the domain rules are still too unstable to freeze into a stronger model

## Quick start: pick a track

### Track A — Diagnosis only
Use when the user wants analysis, design review, refactor advice, or a structural
reading of the current code.

Deliver:
- observed signal
- chosen construction
- why nearby alternatives are worse
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

### Track C — Staged migration
Use when the internal model should improve while API, JSON, DB row, or message
shapes stay stable for now.

Deliver:
- boundary decoder or adapter
- internal stronger model
- parity or differential tests
- migration notes
- clear cut line between legacy shape and internal shape

## Non-negotiables

- One signal, one seam, one smallest honest construction
- Prefer products, coproducts, refined types, pullbacks, exponentials, and free constructions before advanced machinery
- Keep wire and storage shapes stable behind adapters unless the user explicitly wants a breaking change
- Use the repo's current language, framework, and test stack before proposing new libraries
- Say what remains runtime-only in dynamic or weakly typed environments
- Stop after the first verified seam unless the user asked for a sweep

## Step 0 — Create or update `.universalist-plan.md`

This file is the progress record for the current run. Create it in the project
root for Track B or Track C. Use `scripts/init_universalist_plan.sh` if helpful.

Minimum fields:

```md
# Universalist Plan
## Track:
## Signal:
## Construction:
## Why this construction:
## Seam / files:
## Public boundaries touched:
## Wire/storage compatibility plan:
## Verification command(s):
## Runtime-only leftovers:
## Status: planned / editing / verified / staged
## Next seam:
```

If context compacts, read this file first and resume from its status line.

## Operator loop

1. **Inspect repo reality**
   - language and type features
   - framework conventions
   - serializer, ORM, and API boundaries
   - current test runner and proof tools

2. **Find candidate signals**
   Start from code smells and pressure, not category labels:
   - flag, enum string, boolean, or nullable field matrices
   - the same predicate enforced in several places
   - repeated shared-id or shared-version agreement checks
   - branchy policy logic that really wants supplied behavior
   - syntax mixed with execution, logging, or explanation

3. **Pick one seam**
   Choose the smallest stable seam where the stronger shape can land with low blast radius.
   Good first seams:
   - DTO -> domain conversion
   - controller or handler boundary
   - constructor or factory
   - one central service or evaluator
   - one join helper or aggregate constructor

4. **Choose the smallest honest construction**
   - independent fields -> product
   - exclusive states -> coproduct
   - repeated stable predicate -> refined type / equalizer
   - shared projection agreement -> pullback witness
   - configurable behavior -> exponential
   - syntax separate from execution -> free construction / initial algebra

5. **Plan the boundary**
   Decide whether the seam can change in place or whether it needs:
   - decoder
   - adapter
   - DTO / row mapping
   - persistence converter
   - legacy-to-new translation layer

6. **Encode idiomatically**
   Use the strongest encoding the repo can actually support:
   - native ADT
   - sealed hierarchy / enum with payload
   - interface + tag
   - checked constructor or wrapper
   - witness type
   - closure or strategy
   - AST + interpreters

7. **Verify with the fastest credible proof signal**
   Prefer:
   - compile or typecheck
   - targeted unit tests
   - exhaustive handling checks
   - constructor-only entry
   - decode / encode round-trip
   - mismatch rejection
   - parity or differential tests during migration

8. **Stop or name the next seam**
   Do not turn one structural insight into a repo-wide rewrite. Verify one seam,
   record it, and stop unless the user asked for a broader sweep.

9. **Update `.universalist-plan.md`**
   Record:
   - what changed
   - which boundary stayed stable
   - which proof passed
   - what still remains runtime-only
   - next seam, if any

## Practical decision guide

| Repo smell | Default construction | Nearby alternative to reject first | First seam | Proof signal |
| --- | --- | --- | --- | --- |
| `status`, booleans, and nullable fields describe one lifecycle | Coproduct | Product with optional fields | Decoder + core state type | exhaustive handling + invalid legacy fixture tests |
| Same input predicate repeated at controllers, services, serializers | Refined type / equalizer | Keep raw primitive plus helper validation | Parse / constructor boundary | accept valid, reject invalid, normalization idempotence |
| `customer.accountId != subscription.accountId` appears in several places | Pullback witness | Plain pair + scattered assertions | checked constructor | mismatch rejection + preserved projections |
| Large branch decides pricing, rendering, or policy | Exponential | Bigger state machine | function / strategy seam | fixture parity against old branch |
| Rule syntax mixed with execute / explain / log | Free construction | More conditionals inside existing class | AST + one interpreter | interpreter consistency + differential tests |
| Several fields always travel together and are consumed independently | Product | Coproduct | record / struct / object | constructor and projection consistency |

## Output contract

For any non-trivial response, produce these headings in order:

1. **Track**
2. **Signal**
3. **Construction**
4. **Why this instead of nearby alternatives**
5. **Seam / files**
6. **Boundary and compatibility plan**
7. **Before -> After**
8. **Verification**
9. **Runtime-only leftovers**
10. **Next seam** (optional)

For Track B or Track C, also update `.universalist-plan.md`.

## Guardrails

- Prefer plain engineering language over category jargon when both say the same thing
- Do not claim a universal construction without naming the constructor, eliminator, or factorization behavior it buys
- Do not recommend HKT-heavy or typeclass-heavy patterns where the language cannot carry them cleanly
- Do not propose new validation or property-test libraries without user approval
- Do not widen the seam just because the larger design looks elegant
- Call out persistence, serialization, and public API breakage explicitly
- Say when a validator is only runtime protection

## Hand-offs and companion skills

- Use **`invariant-ace`** when the main job is discovering or pinning down invariants before choosing structure
- Use **`accretive-implementer`** after the construction is chosen and the task becomes ordinary implementation
- Use **`repeatedly-apply-skill`** when sweeping the repo for multiple seams or doing a multi-pass campaign

## References

- `references/universalist-overview.md`
- `references/discovery-signals.md`
- `references/language-encoding-matrix.md`
- `references/framework-boundaries.md`
- `references/cost-model-and-false-positives.md`
- `references/structures-and-laws.md`
- `references/testing-playbook.md`
- `references/migration-playbooks.md`
- `references/case-studies.md`
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

## Templates

- `templates/universalist-plan.md`
- `templates/universalist-report.md`
