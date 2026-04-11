---
name: complexity-mitigator
description: Mitigate incidental complexity in existing code when control flow is tangled, nesting is deep, names are hard to parse, or reasoning requires cross-file hops. Use when a review stalls on readability, you need an analysis-first refactor plan before edits, or you want essential-vs-incidental verdicts, dominant-risk triage, ranked simplification steps, one visibility artifact, and a TRACE assessment. Do not use for greenfield requirements discovery, architecture selection, or delivery planning.
---

# Complexity Mitigator

## Intent
Reduce incidental complexity (understanding cost) while preserving essential domain meaning.

## Core Mindset
- Keep essential complexity; vaporize the incidental.
- There is no silver bullet refactor; identify the dominant source of understanding cost before prescribing moves.
- Optimize for reader comprehension first, then for extraction.
- Minimal incision, maximal precision: change only what reduces cognitive load.
- Prefer boring, local clarity over cleverness.
- Sometimes the smallest viable cut is not a refactor. It may be:
  - a learning artifact that clarifies behavior, or
  - deletion/delegation to an existing facility.
- Grow changes in safe cuts; do not prescribe a grand rewrite.
- Recommend one preferred default unless tradeoffs are genuinely close.
- Reduce "understanding cost": fewer branches to hold in mind, fewer places to jump, fewer states to simulate.

## Epistemic Status (Heuristics, Not Laws)
- The playbook below is a set of defaults, not guarantees.
- There is no general proof that any single move always reduces complexity; validate locally.
- When you break a default (e.g., extract before flatten), state the reason and what it unlocks.
- When specification risk dominates, do not pretend syntax cleanup solves it; recommend the smallest learning step first.

## Definitions (Essential vs Incidental vs Specification Risk)
- Essential complexity: domain rules, invariants, boundaries, required state transitions, and irreducible external conformity/change pressure (simplifying it changes correct behavior or meaning).
- Incidental (accidental) complexity: complexity introduced by implementation choices (simplifying it preserves behavior and clarifies intent).
- Specification risk: uncertainty about required behavior, contracts, or edge-case policy. It often looks like messy code, but the real problem is that the boundary is not settled.

- Quick test (imperfect): if a reader must mentally execute the code to infer intent or allowed states, incidental complexity may be hiding the essential. Exception: some algorithms, protocol handlers, and concurrency require real simulation.

## Brooks Lens (No Silver Bullet)
- Do not assume one move (`extract`, `rename`, `state machine`, `types`) will dissolve the whole problem.
- Ask five questions before recommending a cut:
  - Complexity: is the code hard because the real state space is large and interlocked?
  - Conformity: is the code hard because it must match awkward external APIs, schemas, laws, or legacy behavior?
  - Changeability: is the code hard because the surrounding requirements or extension pressure are genuinely moving?
  - Invisibility: is the code hard because intent is split across overlapping views (control flow, data flow, ownership, lifecycle, dependency)?
  - Specification risk: is the code awkward because behavior, contracts, or edge-case policy are not yet fully known?
- Prefer recommendations that expose these constraints over recommendations that merely rearrange syntax.

## Engage When
- A review stalls because readers can't follow the flow.
- You need an explanation of what the code is doing (analysis-first) before changing anything.
- You see deep nesting (>3 levels is a good heuristic), long if/else chains, or duplicated branching.
- Progress requires cross-file hops or simulating shared/mutable state.
- The real question may be whether the complexity is in the code, the requirements, or the boundaries the code must conform to.

## Guardrails
- No file edits, no commits.
- No running commands unless explicitly requested.
- If expected behavior is unclear or product-sensitive, do not prescribe refactor first. Identify the missing contract and recommend a learning artifact.
- If you suspect crash/corruption risk, say the problem is no longer complexity-only and hand off to a dedicated remediation workflow.
- If the user wants greenfield requirements discovery, architecture choice, or delivery sequencing, use a planning skill instead.

## Quick Scan (Cognitive Heat Read)
- Measure (rough, not academic):
  - Max nesting depth
  - Branch count (`if`/`else`/`switch`/ternary)
  - Boolean soup count (booleans/flags that gate behavior, especially combined)
  - Cross-file hops (distinct definitions you must open to understand)
  - State to simulate (mutable vars, implicit globals, order dependencies)
  - External conformity burden (legacy behavior, API/schema/policy obligations)
  - Change pressure (how much of the branching exists to preserve extension points or evolving cases)
  - Views to reconcile (control/data/lifecycle/ownership spread across multiple representations)
  - Specification risk (unclear behavior, disputed edge cases, implicit contracts, policy drift)
- Call out hotspots in one line each:
  - `path:line - [metrics] - why it is hard`
- Tag each hotspot:
  - `essential` (domain)
  - `incidental` (implementation)
  - `mixed` (domain hidden by noise)
  - `spec-risk` (behavior unclear at the boundary)
- Treat metrics as proxies; do not optimize for the number if it harms locality or domain clarity.

## Workflow
1. Choose the slice: entrypoint, inputs, outputs, state.
2. Heat read: name hotspots and what makes them hard.
3. Trace behavior (if meaning is unclear): happy path + key failure paths; call out mutations/IO.
4. Dominant risk: classify the main source of difficulty:
   - `complexity`
   - `conformity`
   - `changeability`
   - `invisibility`
   - `specification risk`
5. Boundary check:
   - If `conformity`, `changeability`, or `specification risk` dominates, do not recommend refactoring first.
   - Recommend the smallest learning artifact first:
     - example matrix
     - contract tests
     - fixture set
     - state table
     - tiny spike
6. Delete-or-delegate check:
   - Ask whether homegrown incidental logic should be removed in favor of an existing repo/platform/framework capability.
   - Delegate only when semantics match and maintenance burden drops.
   - Keep essential policy visible; do not hide domain rules behind an opaque wrapper.
7. Verdict: separate essential domain logic, external conformity/change burden, specification risk, and incidental implementation noise.
8. Simplify in order (default local refactor path): flatten -> rename -> extract.
   - Do not extract until flatten/rename reveals stable shapes.
9. Options: rank by effort vs impact and state the smallest viable cut.
10. Visibility artifact:
   - If invisibility is dominant, output exactly one compact artifact:
     - state model
     - boundary contract table
     - ownership map
     - domain glossary
11. Sketch: show the improved structure (types + flow), not the full implementation.
12. TRACE: cite which letters are satisfied and which are currently violated.

## Standard Playbook

### 0) Delete-and-Delegate
- Prefer existing repo modules, platform features, framework affordances, or mature libraries over homegrown incidental logic when semantics match.
- Use this when a custom abstraction exists mainly to compensate for tooling gaps that no longer exist.
- If delegation is partial, isolate the seam and localize compatibility code.
- Do not delegate away essential domain policy that future readers need to see.

### 1) Flatten
- Lead with guard clauses and early returns; keep the happy path linear.
- Split nested conditionals into separate paths (small helpers or separate functions per path); keep helpers close to avoid extra cross-file hops.
- Make temporal coupling explicit (state machine / explicit step enum) when ordering materially affects correctness.
- Do not flatten away required protocol steps, compatibility branches, or lifecycle edges; if they are essential, make them explicit instead.

### 2) Rename
- Replace vague verbs (`process`, `handle`, `do`) with domain actions; align nouns with domain entities.
- Fix boolean naming (prefer positive, avoid double negatives); eliminate boolean-flag arguments when possible.
- Move meaning into data: enums / tagged unions / option objects over multiple booleans (when it reduces branching or invalid states).

### 3) Extract (Rule of Three)
- Split mixed responsibilities (parse vs validate vs decide vs effect).
- Convert repeated branching into data-driven dispatch (tables, handler maps, pattern matching).
- Extract only stable, repeatable concepts; Rule of Three is a heuristic (exceptions exist).
- Sequence larger mitigations as growth, not rewrite:
  1. pin behavior,
  2. linearize flow,
  3. extract stable shapes.

## Learning Artifacts (when not refactor first)
- Example matrix: inputs, context, expected output, edge-case notes.
- Contract tests: pin observed/required behavior at the seam before structural changes.
- Fixture set: representative cases that reveal the real policy surface.
- State table: legal states, transitions, and forbidden combinations.
- Tiny spike: a minimal experiment to answer one uncertainty, then discard or replace.

## Option Ranking Rubric
- Effort:
  - tiny (learning artifact, rename, guard clause, comment-to-assertion)
  - small (split function, local enum, contract tests)
  - medium (introduce table/handler map, isolate adapter, explicit state model)
  - large (module boundary, protocol adapter, state machine, wider delegation)
- Impact:
  - reduces branching
  - reduces cross-file hops
  - reduces state to simulate
  - localizes external conformity
  - clarifies invariants
  - converts ambiguity into an explicit contract
- Pick one recommended default unless tradeoffs are genuinely close.

## What Counts as Evidence (Local, Not Global)
- Prefer local, checkable evidence over universal claims.
- Use before/after indicators where possible:
  - nesting/branching/flags/hops/state-to-simulate (from the heat read)
  - which external constraints remain essential versus which ones became localized
  - which invariant becomes explicit (type/constructor/assertion/test)
  - whether the recommendation clarified a missing contract instead of merely rearranging syntax
  - what tradeoff you accepted (e.g., more functions in exchange for linear flow)

## Output Format

**0) Slice**
- Entrypoint: ...
- Inputs/outputs/state: ...

**1) Heat Read (hotspots)**
- `path:line` - ...

**1.5) Behavior Trace (optional)**
- Happy path: ...
- Failure paths: ...
- Mutations/IO: ...

**2) Essential vs Incidental**
- Essential: ...
- Conformity/change pressure: ...
- Specification risk: ...
- Incidental: ...

**2.5) Dominant Risk**
- `complexity | conformity | changeability | invisibility | specification risk`
- Why: ...

**3) Recommendation Path**
- `learning artifact first` | `delete/delegate first` | `local refactor first`
- Reason: ...

**3.5) Learning Artifact (if needed)**
- Type: ...
- Question it resolves: ...
- What not to refactor until it is known: ...

**4) Options (ranked by effort vs impact)**
1. Preferred default: ...
2. ...
3. ...

**5) Visibility Artifact (only if invisibility dominates)**
```text
// exactly one compact artifact
```

**6) Sketch**
```text
// minimal illustrative snippet
```

**7) TRACE**
- Satisfied: ... (letters the recommended structure improves)
- Violated: ... (letters the current code is failing)

## Why TRACE Is Part of Complexity Mitigation
- In this skill, treat "complexity" primarily as understanding cost (not performance or operational complexity).
- TRACE is the lens that prevents fake simplifications and makes tradeoffs explicit:
  - T (Type): can remove invalid states from consideration; over-modeling can also add noise.
  - R (Readability): reduces naming/structure friction that feels like complexity.
  - A (Atomic): separates decide vs do; mixed responsibilities often create incidental complexity.
  - C (Cognitive): directly targets nesting/branching/state simulation.
  - E (Essential): checks that you are deleting implementation noise, not deleting domain meaning.
- Using TRACE makes the mitigation outcome checkable: which understanding costs went down, and what got traded off?

## TRACE Quick Reference
- T (Type): invalid states are unrepresentable; constraints live in types/constructors (keep the type model minimal).
- R (Readability): intent is obvious from names and locality.
- A (Atomic): one responsibility per unit; decisions separate from effects (avoid scattering logic across too many tiny units).
- C (Cognitive): low nesting/branching; minimal state simulation.
- E (Essential): code expresses only the domain-required complexity.

## Invariant Guidance
Use when missing invariants block simplification.
- Ask for or infer: state transitions, allowed/forbidden states, ownership/immutability, error handling boundaries.
- Identify the smallest invariant that unlocks flattening (e.g., `state X implies Y`).
- If invariants are unknown, recommend adding assertions, contract tests, or making them explicit in types.

## Footgun Checklist
Use when confusing APIs or naming cause misuse.
- Hidden side effects or stateful globals
- Non-obvious preconditions or order dependencies
- Boolean parameters with inverted meaning
- Silent defaults or magic values
- Similar names for different concepts
- Error handling that is inconsistent or implicit

## Escalation
- If repeated algebraic shapes or composable pipelines appear, consider switching to the Universalist skill and framing a minimal algebra + laws.
- If the user wants implementation, stop at the analysis artifact and hand off to implementation rather than extending this skill past its boundary.
- If the problem is primarily greenfield requirements, architecture selection, build-vs-buy, or delivery planning, use a planning/architecture skill instead.
