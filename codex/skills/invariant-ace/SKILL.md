---
name: invariant-ace
description: "Turn 'should never happen' into 'cannot happen' by defining owned inductive invariants and enforcing them at parse/construct/API/DB/lock/txn boundaries with a verification signal. Use when prompts mention invariants, impossible states, validation sprawl, cache/index drift, idempotency/versioning, retries/duplicates/out-of-order events, race/linearization bugs, loop correctness, or hardening another implementation workflow with invariant checks first."
---

# Invariant Ace

## Mission

Turn "should never happen" into "cannot happen" with minimal, high-leverage changes: pick owned, inductive invariants; enforce them at the strongest cheap boundary; prove via a concrete counterexample trace and a verification signal.

## Use When (Signals)

- Null/shape surprises, runtime validation sprawl, or input decoding scattered across the codebase.
- Redundant stored facts drift (cache/index/denormalized columns) or "fix-up" code runs often.
- Flags/states explode; impossible combinations appear; "unreachable" is reachable.
- Races, duplicate/out-of-order events, retries, partial failures, or "exactly once" assumptions.
- Idempotency keys, monotonic version/epoch checks, stale writes, or linearization questions are central.
- Loop/algorithm correctness depends on comments or intuition; tricky indexing/arithmetic/termination.
- "Should never happen" branches show up in logs or error trackers.

## Routing Priority

- If a task has invariant/protocol cues and also asks for broad implementation (`$tk`, `$work`), run this skill first to lock invariants, then execute edits.
- If you cannot name state owner + transitions, switch to clarification/discovery before implementation.

## Core Model (Fast Definitions)

- Invariant: predicate P(state) intended to hold for all reachable states in a scope.
- Inductive: true initially AND preserved by every allowed transition in that scope.
- Owner: the single module/type/transaction/lock/actor that controls all mutations needed to preserve P.
- Precondition/postcondition: caller obligation vs operation guarantee; do not mislabel these as invariants.
- Derived property: recomputable fact; avoid storing it as "must match" unless you centralize updates.
- Safety vs liveness: invariants are safety ("nothing bad"); keep progress ("eventually") separate.

## Immediate Scan

- State owner: where does the truth live (type/module/service/table)?
- State boundary: where does raw data enter (API/DB/file/queue)?
- Allowed transitions: list operations/events that mutate the state (including retries and concurrency).
- Failure today: one concrete trace (inputs + transitions + schedule) that reaches a bad state.
- Protection level: hope -> runtime -> construction-time -> type/compile-time -> persistence/protocol/atomicity.
- Pain tag(s): data | concurrency/protocol | algorithm/loop (often multiple).

## Protection Ladder

Choose the cheapest strong layer that makes the violation hard or impossible.

- Hope-based: comments, assumptions, "unreachable".
- Runtime: scattered guards/validators near use sites.
- Construction-time: parse/validate once at boundaries; core code only handles refined values.
- Type/compile-time: illegal states are unrepresentable (ADTs, typestates, opaque wrappers).
- Persistence: schema/constraints/transactions enforce invariants at rest.
- Concurrency boundary: locks/actors/CAS/txns define where invariants must hold (under lock, at commit, at linearization).

## Protocol (Counterexample-Driven)

1. Declare scope + owner.
   - Write "P holds when/where": always | after construction | under lock | at txn commit | after message apply.
   - If you cannot name an owner, the invariant will drift; pick a choke point first.

2. List transitions and try to break P.
   - For each transition (and retry/out-of-order variants), attempt a counterexample trace.
   - If P fails, decide: bug vs wrong scope vs missing state vs wrong owner.

3. Make P inductive (or downgrade it).
   - Weaken P, move it to pre/postconditions, or add auxiliary state (version/epoch/status/idempotency key) until it closes under transitions.

4. Run a coordination check (concurrency/distributed).
   - Ask: can two individually-valid concurrent transitions merge into a P-violating state?
   - If yes, you need coordination (lock/txn/consensus) OR you must redesign the invariant/operation (partition, escrow, monotone merges, idempotency).

5. Encode enforcement at the strongest cheap boundary.
   - Prefer: parser/decoder + smart constructors + narrow/opaque types + centralized mutation.
   - Avoid: N scattered validators, duplicated truths without a single writer, and "fix-up" routines on every read.

6. Add observability if full enforcement must be staged.
   - Add cheap tripwires (assert/log/metric) and quarantine paths (reject/dead-letter/compensate).
   - Record replayable context (transition name, IDs, versions), not raw secrets.

7. Verify with the right harness.
   - Data: fuzz/property tests on parsers/constructors.
   - State machines: stateful/model-based tests (sequences).
   - Concurrency: stress + schedule perturbation; assert at quiescent points.
   - Protocols: small model checking/simulation for drops/dupes/reorder.
   - Algorithms: invariant assertions in loops + differential tests vs reference.

## Compact Mode (Fast Path)

Use this when the task is small or time-boxed.

1. Counterexample: one concrete failing trace (<=5 transitions).
2. Invariants: 1-2 predicates with explicit owner + scope.
3. Enforcement Boundary: one chosen choke point (parse/construct/API/DB/lock/txn).
4. Verification: one signal tied to one predicate.

Escalate to full protocol if any of the above is ambiguous or non-inductive.

## Invariant Record (Use This Format)

- Predicate: P(state) (precise, checkable)
- Owner: module/type/service/table/lock/txn
- Holds: always | after construction | under lock | at commit | after apply
- Maintained by: transitions that must preserve P
- Enforced at: parse/construct/API/DB/lock/txn/protocol
- Counterexample to avoid: minimal trace that breaks it today
- Verification: property/stateful/stress/model/differential

## Patterns by Pain

### Data Modeling & Input Validity

- Boundary refinement: raw -> parsed -> validated; only validated enters core.
- Canonicalization: normalize early (case/whitespace/timezone/ID format) so equality and caching are stable.
- Explicit absence: model optionality explicitly; avoid "sometimes null" in the core. In proof or matcher code, an absent optional field is not a wildcard unless wildcard semantics are explicitly owned; required witness fields must be present and exact.
- Cross-field coupling: combine coupled fields into one value to prevent illegal combinations.
- Denormalization discipline: if you store derived facts, centralize writes or make them recomputed.
- Canonical-versus-alias fields: when a field is an alias, cache, summary, normalized spelling, or derived boolean for canonical data, validators must recompute it from the canonical source and reject mismatches. Tests should include forged alias fixtures that keep canonical fields valid while corrupting the alias.
- Descriptor versus occurrence multiplicity: decide whether a reference names a unique descriptor, a use site, or a counted occurrence before using set, multiset, or cardinality equality. Repeated uses of one descriptor may be valid even when duplicate descriptor definitions are invalid; encode and test those as different invariants.
- Policy-owned exceptions: if an invariant depends on an allowlist, capability, ACL, feature flag, or policy predicate, add legitimate exceptions through that policy owner. Do not add local "explicit input" shortcuts that bypass the policy predicate; tests should configure the policy, not weaken the checker. Partial, blocker, audit-only, and best-effort modes are not implicit exceptions to fail-closed switches; the same policy object must authorize the exception before those paths can accept an otherwise unsupported artifact.
- Layered negative fixtures: when a stronger outer boundary now rejects before an older inner invariant, decide deliberately. Configure the outer policy to reach the inner failure when that is the test's purpose; otherwise update the expected error to the stricter boundary and document why the earlier rejection is now correct.
- Validation/projection identity drift: if one phase accepts by an identity rule, every analysis, elaboration, selection, lowering, generation, certificate, or projection path must use the same rule or a named stricter refinement. Prefer one shared predicate/helper over parallel "close enough" lookups such as validate by intrinsic-aware identity but generate by shape-only matching, or apply different route-specific source-vs-target shape rules across phases.
- Site-aware matching: if identity includes a site index, yield site, operation occurrence, route position, or source-map entry, every matcher/resolver/certificate path must compare that occurrence field and name its coordinate space, such as source selector versus residual selector. Shape, type, protocol, or provider equality alone is not enough when two valid occurrences share the same descriptor.
- Identity versus witness: a matching hash, fingerprint, ref, descriptor, label, or global dependency proves sameness/availability only, not capability, support, or local route ownership. If validation depends on a mapping being usable, require an explicit witness/proof field that the downstream phase can consume, such as a selected plan edge or certificate-bound link artifact. Reused provider programs need witnesses bound to the selected provider offer or route occurrence, not only to the shared provider program ref. Require the witness the route semantics owns, not an unrelated stronger witness; an explicit shape-owned world-port witness should not be rejected merely because no host-intrinsic/static-plan witness exists, and host-intrinsic routes must prefer intrinsic-bound witnesses over generic shape witnesses.
- Route target evidence: if generation can select a route-specific target that differs from the original source, the validator must either replay that target from fields carried in the certificate/proof or require an explicit target-owned witness. Do not infer a morphism target, selected offer body, lowered shape, or residual route from the source shape when the artifact does not carry the mapping evidence. A non-null target-shaped witness is not enough unless it is compared against the target ref/fingerprint/protocol/site coordinate the route semantics actually selected.
- Generator/validator parity: every invariant required to generate a certificate, source map, proof, or artifact must also be enforced when validating an externally supplied one. When a stronger validator breaks generated/comptime self-checks, update the generator to emit the required witness fields or proof links instead of weakening validation. A generator self-check is not enough if imported/manual certificates can bypass the same predicate.
- Derived fixture parity: tests for generated certificates, plans, or shapes should use the same construction path as production for derived fields. Re-typed fixtures drift when fingerprints include usage summaries, normalized labels, target response refs, policy-derived fields, or computed shape metadata; use the generator/helper or assert every derived field intentionally.
- Policy authority checks: proving a referenced object exists is not proving the policy authorizes using it. Certificate validation must check both the reference relationship and the relevant policy predicate/capability. An allow flag, enum kind, or generic object tag is not a substitute for the policy-owned ref or capability; for example, host-intrinsic allowlisting must bind a host-intrinsic ref, not just any world-port-shaped object marked as intrinsic-capable.
- Phase-owned references: do not require an earlier phase to provide a reference, hash, dependency, or residual id that only a later phase can correctly construct. Bind it at the owning phase, include it in that phase's certificate/proof/dependency vector, and when relaxing the earlier requirement add a replacement proof condition that ties the late value to its legitimate source rather than accepting arbitrary later values. Certificate-bound compiled hashes and residual ids must be recomputed from the actual compiled/generated artifact, not trusted from caller overrides. Keep negative tests that prove explicitly wrong early references and forged late bindings are still rejected.
- Unsupported mapping fail-closed: unimplemented, unmodeled, or unsupported provider/mapping/lowering cases must fail before certificate, proof, source-map, or generated artifact construction. Preserve route-specific supported mappings; negative fixtures should use a genuinely unsupported mapping, not a valid mapping from another route such as an after-site resume mapping.
- Shortcut preservation: early returns, lowering shortcuts, shape-only world-port paths, and other bypasses must preserve the proof obligations of the selected route semantics before they skip the normal path. A simpler emitted disposition is not permission to skip morphism, adapter, provider, mapping, or dependency evidence that made the selected route valid.
- Blocked-state certificates: fail-closed partial artifacts may carry blockers, but their certificates must still self-verify by attesting the blocked state and reason. Count equality is not enough; each blocker ref must be tied to a legitimate blocked entry, blocker object, or owning proof source, and blocked source-map entries must not exceed blocker/unsupported counts. If an unsupported/blocked summary count claims to summarize source-map evidence, it must equal the actual emitted blocked entries rather than a looser total blocker count. Track source-shape map entries, blocked entries, unsupported blocked source shapes, and direct/root blockers as separate dimensions unless the artifact contract explicitly derives one from another. Missing `effect_shape_ref` is not by itself proof that an emitted source-map entry is not a source effect; classify by disposition first, then bind to the generator's owning fallback ref, such as the world-port ref, when the primary shape/effect ref is absent and no static-plan owner exists. Static-plan-owned morphism entries may instead bind through the target shape plus plan evidence. When a certificate has a nonempty source-effect surface and actual blocked source-map entries, blocker refs need blocked source-map evidence; root/report-only blockers or no-source-effect partials may bind through closure blocker refs and counts without inventing blocked entries. Preserve the blocked source subject in the entry's source ref and add a separate blocker-ref witness instead of overwriting source identity. Require stronger descriptor/ref equality only for fields the blocked entry actually owns, such as a static-plan ref when present. A blocker is proof state, not permission for certificate mismatch.
- Emitted-disposition accounting: summary counts, effect rows, source maps, and certificates must count the route disposition actually emitted after lowering or redirection, not the earlier selected-route class. A morphism or pipeline candidate lowered to a world port must not also inflate residualized, pipeline, or adapter totals unless the emitted artifact contains that disposition too.
- Fixture precondition alignment: when testing a downstream invariant, make the synthetic fixture satisfy all upstream shape, policy, provenance, residual-coverage, and ownership preconditions. If the fixture trips an earlier gate, it is proving the wrong boundary. Relax only the orthogonal coordinate needed to satisfy that earlier model rule, such as using an existing wildcard allowlist meaning for residual-site coverage, while keeping the target witness or ownership invariant strict.
- Competing-descriptor fixtures: when a test needs a decoy descriptor to prove selection logic, make the decoy legitimate under the verifier too. If supplied descriptors must be referenced, owned, or consumed, create a real source-map/report use for every descriptor instead of relying on unused extras.

### Concurrency & Protocol Correctness

- Lock/txn invariants: P holds under lock or at commit; define where the linearization point is.
- Monotonic metadata: versions/epochs/counters only increase; reject stale writes.
- Idempotency: retries and duplicates are safe (idempotency keys, dedupe tables, "apply once").
- Explicit state machines: enumerate states + allowed transitions; persist enough metadata to reject out-of-order events.
- Coordination decisions: if P depends on global uniqueness or non-negativity under concurrent debits, choose coordination or redesign (partition/escrow).

### Algorithms & Loop-Heavy Code

- Loop invariants: assert what is preserved each iteration (partitioned regions, sorted prefix, conservation laws).
- Variant/termination: name a decreasing measure; if you cannot, expect non-termination edges.
- Representation invariants: hide internal structure behind an API; add a rep-check for tests/debug.
- Differential testing: compare to a simple, slow reference implementation to catch corner cases.

## Before/After Sketches (Language-Agnostic)

### Boundary Refinement (Data)

```text
Before: functions accept RawInput and validate ad hoc
After:  parseRaw(...) -> ValidatedValue | Error
        core functions accept ValidatedValue only
```

### Idempotency + Versioning (Concurrency/Protocol)

```text
Before: handle(event) mutates state directly (retries duplicate side effects)
After:  if seen(event.id) return
        if event.version <= state.version return (or reject)
        apply(event) at a single atomic boundary (lock/txn/CAS)
```

### Loop Invariant (Algorithm)

```text
Before: comment says "array left side is partitioned"
After:  assert(invariant(state)) inside loop
        test: random arrays, shrink failing cases, compare to reference
```

## Verification

Pick at least one signal and tie it to a specific invariant predicate.

- Property/fuzz: parsers, constructors, normalization.
- Stateful/model-based: sequences over operations; check invariants after each step.
- Concurrency stress: N threads + jitter; assert invariants at quiescent points.
- Protocol simulation: reorder/duplicate/drop + crash/restart; assert safety invariants.
- Model checking (optional): small state + exhaustive exploration for protocols.
- Differential/reference: algorithm output equals reference for randomized inputs.
- Runtime tripwires: assertions/logging/metrics for staged rollout.

## Research Anchors (Mental Models, Not Requirements)

- Hoare/Floyd/Dijkstra: invariants as proof objects; weakest preconditions.
- ADT/rep invariants (Liskov-style): abstraction function + local reasoning.
- Abstract interpretation: over-approx reachable states; inferred invariants.
- Dynamic invariant mining (Daikon-style): candidate generation; falsify with counterexamples.
- Separation logic / framing: invariants tied to ownership; interference-aware reasoning.
- Rely-guarantee & linearizability: concurrency invariants under schedules.
- TLA+/Alloy mindset: protocols as transitions + invariants; counterexample traces.
- Coordination avoidance / CRDT laws: when invariants require coordination vs merge-safe design.

## Output Contract (Required Headings)

Use these exact headings in the final response for this skill:

1. Counterexample
2. Invariants
3. Owner and Scope
4. Enforcement Boundary
5. Seam (Before -> After)
6. Verification
7. Observability (optional)

## Deliverable Checklist

1. Counterexample: minimal breaking trace (include schedule/retry if relevant).
2. Invariants: 1-5 predicates with owner + scope ("holds when").
3. Enforcement Boundary: boundary/type/API/DB/lock/txn/protocol choice + why.
4. Seam (Before -> After): minimal structural change that makes violations hard.
5. Verification: property/stateful/stress/model/differential tied to at least one predicate.
6. Observability (optional): tripwires/quarantine/metrics if rollout must be staged.

## Cross-Coordination

- If broader failures emerge, lean on the Unsoundness checklist.
- If stronger invariants dent ergonomics, reference the Footgun guardrails.

## Measurement (seq)

Track adoption and compliance with `seq`:

```bash
seq skill-trend --root ~/.codex/sessions --skill invariant-ace --bucket week
seq skill-report --root ~/.codex/sessions --skill invariant-ace \
  --sections "Counterexample,Invariants,Owner and Scope,Enforcement Boundary,Seam (Before -> After),Verification,Observability (optional)" \
  --sample-missing 5
```
