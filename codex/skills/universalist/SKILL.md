---
name: universalist
description: >
  Use when code smells point to a structural refactor that should ship: flag or state matrices, repeated boundary validation, shared-key agreement checks, branchy policy logic, syntax mixed with execution, duplicated projections, generated artifacts losing provenance, callbacks crossing architecture boundaries, public contracts determining internals, or any need for canonical boundary artifacts. Default to one signal, one seam, one smallest honest construction, adapter-first staging, one explicit boundary artifact, and one proof signal.
---

# Universalist

Use this skill when the highest leverage comes from changing the **shape of truth** in a codebase, not from adding another ordinary feature branch.

This is an **inner lens** for choosing the right structural move. It is not a generic implementation skill. Use it to decide and stage the structure, then let the repo's normal implementation flow carry the change.

The enriched slogan is:

> Universal architecture is the practice of designing software around canonical boundary artifacts: **free syntax, coherent observations, transported semantics, lifted implementations, explicit IRs, and law tests.**

## Do not trigger for

- Routine feature work with no structural smell.
- Pure performance tuning, infra, UI polish, or docs work.
- Broad rewrites with no stable seam.
- Cases where the domain rules are still too unstable to freeze into a stronger model.
- Category-theory exposition that does not change a concrete seam, construction, or proof signal.

## Quick start: pick a track

### Track A — Diagnosis only

Use when the user wants analysis, design review, refactor advice, or a structural reading of the current code.

Deliver:

- observed signal;
- chosen construction;
- why nearby alternatives are worse;
- first seam to attack;
- proof signal;
- compatibility notes;
- whether this is ordinary universalist structure or universal-architecture territory.

### Track B — One-seam refactor

Use when the user wants code changes, but the right move is narrow and reviewable.

Deliver:

- one seam only;
- smallest honest construction;
- canonical boundary artifact if needed;
- adapter-first staging when a public boundary exists;
- fastest credible proof signal;
- explicit stop point after the first verified seam.

### Track C — Staged migration

Use when the internal model should improve while API, JSON, DB row, or message shapes stay stable for now.

Deliver:

- boundary decoder or adapter;
- internal stronger model;
- parity or differential tests;
- migration notes;
- clear cut line between legacy shape and internal shape;
- `.universalist-plan.md` update.

### Track D — Universal architecture boundary

Use when the smell is no longer just “choose a better type” but “choose the canonical artifact at a boundary.”

Deliver:

- worlds involved;
- boundary map, projection, embedding, interpreter, or forgetful API;
- known side and unknown artifact;
- canonical boundary artifact;
- one executable law test;
- one falsifier showing when the framing is overkill.

Use Track D for:

- duplicated projections or query/view sprawl;
- generated artifacts losing provenance;
- public contract determining internal implementation obligations;
- plugin, workflow, effect, rule-engine, or DSL boundaries;
- callback/closure/handler behavior that should become explicit IR;
- old semantics transported to a new target surface;
- compatibility facades where several old observations must agree.

## Non-negotiables

- One signal, one seam, one smallest honest construction.
- Prefer products, coproducts, refined types, pullbacks, exponentials, and free constructions before advanced machinery.
- Escalate to universal architecture only when the boundary artifact changes code shape or tests.
- Keep wire and storage shapes stable behind adapters unless the user explicitly wants a breaking change.
- Use the repo's current language, framework, and test stack before proposing new libraries.
- Say what remains runtime-only in dynamic or weakly typed environments.
- Stop after the first verified seam unless the user asked for a sweep.

## Step 0 — Create or update `.universalist-plan.md`

This file is the progress record for the current run.

Create it in the project root for Track B, Track C, or Track D. Use `scripts/init_universalist_plan.sh` if helpful.

Minimum fields:

```md
# Universalist Plan

## Track:
## Signal:
## Construction:
## Canonical boundary artifact:
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
   - language and type features;
   - framework conventions;
   - serializer, ORM, and API boundaries;
   - current test runner and proof tools.

2. **Find candidate signals**

   Start from code smells and pressure, not category labels:

   - flag, enum string, boolean, or nullable field matrices;
   - same predicate enforced in several places;
   - repeated shared-id or shared-version agreement checks;
   - branchy policy logic that really wants supplied behavior;
   - syntax mixed with execution, logging, or explanation;
   - duplicated projections or selectors;
   - generated artifacts with no provenance;
   - public contract/tests implying missing internal obligations;
   - callbacks/handlers crossing boundaries without explicit IR.

3. **Pick one seam**

   Choose the smallest stable seam where the stronger shape can land with low blast radius.

   Good first seams:

   - DTO -> domain conversion;
   - controller or handler boundary;
   - constructor or factory;
   - one central service or evaluator;
   - one join helper or aggregate constructor;
   - one projection/query/read-model boundary;
   - one plugin or rule-family adapter;
   - one public contract case.

4. **Choose the smallest honest construction**

   Default ladder:

   - independent fields -> product;
   - exclusive states -> coproduct;
   - repeated stable predicate -> refined type / equalizer;
   - shared projection agreement -> pullback witness;
   - configurable behavior -> exponential;
   - syntax separate from execution -> free construction / initial algebra.

5. **Escalate to canonical boundary artifacts only when needed**

   Use this matrix when the ordinary construction ladder is not enough:

   | Smell | Canonical boundary artifact | Universal reading | First proof signal |
   | --- | --- | --- | --- |
   | Many consumers interpret the same commands differently | Free syntax / explicit AST | Free object / initial algebra | interpreters agree on fixtures |
   | New target surface must preserve old source behavior | Transported semantics | Left Kan / generated path | identity or embedding path preserves behavior |
   | New internals must satisfy old views | Coherent observations | Right Kan / Yoneda | overlapping observations commute |
   | New model must be viewed through old API | Restriction adapter | Precomposition / `Delta` | old golden tests pass through adapter |
   | Public behavior is known before internals | Lifted implementation | Kan lift / realization | `project(realize(case)) == required(case)` |
   | Public policy implies internal checks | Residual obligations | Right-lift / weakest obligation | missing obligation fails projection |
   | Generated payloads lose provenance | Generation path vocabulary | Coyoneda | lowering equals direct interpretation |
   | Query/projection sprawl | Observation vocabulary | Yoneda | representation change preserves observations |
   | Callbacks/closures cross architecture boundaries | Explicit first-order IR | Defunctionalization | `apply(encodedCase, x) == oldCallback(x)` |

6. **Plan the boundary**

   Decide whether the seam can change in place or needs:

   - decoder;
   - adapter;
   - DTO / row mapping;
   - persistence converter;
   - legacy-to-new translation layer;
   - observation vocabulary;
   - generation path;
   - explicit IR plus interpreter;
   - projection from implementation to public behavior.

7. **Encode idiomatically**

   Use the strongest encoding the repo can actually support:

   - native ADT;
   - sealed hierarchy / enum with payload;
   - interface + tag;
   - checked constructor or wrapper;
   - witness type;
   - closure or strategy;
   - AST + interpreters;
   - observation enum + `runObservation`;
   - generated payload + path + `lowerGenerated`;
   - realizer/obligation + `project`/`satisfy`.

8. **Verify with the fastest credible proof signal**

   Prefer:

   - compile or typecheck;
   - targeted unit tests;
   - exhaustive handling checks;
   - constructor-only entry;
   - decode / encode round-trip;
   - mismatch rejection;
   - parity or differential tests during migration;
   - observation coherence;
   - projection/lift realization test;
   - defunctionalized interpreter equivalence.

9. **Stop or name the next seam**

   Do not turn one structural insight into a repo-wide rewrite. Verify one seam, record it, and stop unless the user asked for a broader sweep.

10. **Update `.universalist-plan.md`**

   Record:

   - what changed;
   - which boundary stayed stable;
   - which proof passed;
   - what still remains runtime-only;
   - next seam, if any.

## Practical decision guide

| Repo smell | Default construction | Nearby alternative to reject first | First seam | Proof signal |
| --- | --- | --- | --- | --- |
| `status`, booleans, and nullable fields describe one lifecycle | Coproduct | Product with optional fields | Decoder + core state type | exhaustive handling + invalid legacy fixture tests |
| Same input predicate repeated at controllers, services, serializers | Refined type / equalizer | Raw primitive plus helper validation | Parse / constructor boundary | accept valid, reject invalid, normalization idempotence |
| `customer.accountId != subscription.accountId` appears repeatedly | Pullback witness | Plain pair + scattered assertions | checked constructor | mismatch rejection + preserved projections |
| Large branch decides pricing, rendering, or policy | Exponential | Bigger state machine | function / strategy seam | fixture parity against old branch |
| Rule syntax mixed with execute / explain / log | Free construction | More conditionals inside existing class | AST + one interpreter | interpreter consistency + differential tests |
| Several fields always travel together and are consumed independently | Product | Coproduct | record / struct / object | constructor and projection consistency |
| Several old views must agree on new internals | Coherent observations | Independent adapters | read-model/projection boundary | overlapping observation coherence |
| Generated artifacts lose provenance | Generation path vocabulary | anonymous callbacks | generation/lowering boundary | lowering equals direct interpretation |
| Public contract determines implementation | Lifted implementation | ad hoc service design | one contract case | projection matches required behavior |
| Callbacks carry architecture behavior | Explicit IR | hidden closure registry | plugin/handler seam | apply/interpreter equivalence |

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

For Track D, also include:

- **Canonical boundary artifact**
- **Law / proof signal**
- **Falsifier**

For Track B, Track C, or Track D, also update `.universalist-plan.md`.

## Guardrails

- Prefer plain engineering language over category jargon when both say the same thing.
- Do not claim a universal construction without naming the constructor, eliminator, or factorization behavior it buys.
- Do not recommend HKT-heavy or typeclass-heavy patterns where the language cannot carry them cleanly.
- Do not propose new validation or property-test libraries without user approval.
- Do not widen the seam just because the larger design looks elegant.
- Call out persistence, serialization, and public API breakage explicitly.
- Say when a validator is only runtime protection.
- Do not use Kan/Yoneda/Coyoneda vocabulary unless it produces a concrete artifact and law test.
- Defunctionalize only when higher-order behavior crosses a meaningful boundary.

## Hand-offs and companion skills

- Use **`kan`** when the chosen boundary artifact needs detailed Kan extension/lift, Yoneda/Coyoneda, codensity, or defunctionalization mechanics.
- Use **`invariant-ace`** when the main job is discovering or pinning down invariants before choosing structure.
- Use **`accretive-implementer`** after the construction is chosen and the task becomes ordinary implementation.
- Use **`repeatedly-apply-skill`** when sweeping the repo for multiple seams or doing a multi-pass campaign.

## References

Existing references:

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

Universal architecture additions:

- `references/universal-architecture-ecosystem.md`
- `references/canonical-boundary-artifacts.md`
- `references/kan-boundaries-for-universalist.md`
- `references/yoneda-coyoneda-defunctionalization.md`
- `references/universal-architecture-law-tests.md`

## Scripts

Existing scripts:

- `scripts/init_universalist_plan.sh`
- `scripts/detect_signals.py`
- `scripts/emit_scaffold.py`
- `scripts/emit_boundary_adapter.py`
- `scripts/emit_verification_plan.py`
- `scripts/emit_law_test_stub.sh`

Universal architecture additions:

- `scripts/emit_universal_artifact_matrix.sh`
- `scripts/emit_canonical_artifact_plan.sh`
- `scripts/emit_universal_architecture_prompt.sh`
- `scripts/check_universalist.sh`

## Templates

Existing:

- `templates/universalist-plan.md`
- `templates/universalist-report.md`

Additions:

- `templates/universal-architecture-report.md`
