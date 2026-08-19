# Semantic Hotspots

Normative only for bug-driven reconciliation where an accepted bug, failing
test, incident, migration failure, compatibility failure, or review finding may
expose a boundary defect.

## Disclosure contract

**Load when:** a witnessed incorrect state or trace touches construction,
transition, composition, ownership, representation, interpretation, or
observation; or current code shows repeated defenses for one law.

**Do not load when:** the defect is wholly internal to one already-correct owner
and the incumbent already excludes the complete invalid family.

**Return:** one bounded counterexample topology and, when architecture selection
reopens, one correctness delta. Create no durable artifact.

## Semantic objects

A bug is one witness to incorrectness. It is not the complete family and not a
patch instruction.

```text
Witness provenance
  exact version/build/schema/environment/input/state/trace observed

Current applicability
  whether the law and causal route remain live at the current Goal and head

Violated law
  attributed Goal, public contract, type invariant, protocol, test law, derived
  law, or explicit hypothesis falsified by the witness

Detection surface
  where incorrectness became visible

Observational class
  Review Fold's same-law grouping before frontier partition

Family predicate or generator
  Phi over domain D; invalid family F = { x in D | Phi(x) }

Sanctioned admission relation
  supported constructors, transitions, deserializers, handlers, interpreters,
  or other paths through which F can enter

Admission frontier
  one minimal seam with enough information and authority to prevent admission

Admission cut
  a minimal set of incomparable owner-capable seams covering every sanctioned
  admission path

Current owner set / status
  canonical | distributed | absent | contested | unknown

Escape path
  a sanctioned or bypass route that evades intended enforcement

Semantic scar tissue
  existing enforcement or compensation around the same law
```

A semantic hotspot is the ephemeral conjunction:

```text
law x predicate-defined family x owner set x frontier/cut x escape paths x witnesses
```

It is not a file, churn score, bug count, review count, or persistent record.

## Provenance and applicability

Never rewrite a historical witness as though it occurred at the current head.
Record:

```text
Witness subject:
Applicability subject:
Applicability status: still-present | transformed-applicable |
  already-excluded | not-comparable | unknown
Applicability basis:
```

Only `still-present` and `transformed-applicable` witnesses create current
architectural pressure. `already-excluded` is historical explanation.
`not-comparable` and `unknown` cannot establish current recurrence or coverage.

## Predicate-defined families

Before claiming family exclusion, state:

```text
Domain D:
Predicate or generator Phi:
Sanctioned admission relation A:
Validity horizon:
Claim strength:
```

Claim strength is exactly one of:

```text
proved
exhaustive-finite
bounded
property-tested
sampled
hypothesized
unknown
```

Match the claim to the evidence. Fixing every observed example does not prove
`Phi` excluded from `A` over `D`.

## Observational classes and frontier partition

Review Fold may group currently applicable witnesses when evidence supports the
same law, compatible discrepancy/applicability, and a plausible causal relation.
It reports current owner sites and a family hypothesis, but no admission
frontier.

Actuating then:

1. identifies candidate owner-capable frontiers;
2. partitions one observational class when witnesses cross materially different
   frontiers;
3. selects one frontier if it covers every sanctioned admission path;
4. otherwise selects a minimal admission cut;
5. returns unresolved when path coverage or authority is unknown.

This avoids requiring a frontier to establish the class that Actuating uses to
derive the frontier.

## Owner sets and guard roles

Owner dilution may be the defect. Record current owner sites, owner status,
candidate semantic owner, primary enforcement, and derived enforcement.

Classify scar tissue:

```text
primary enforcement
  semantic authority for the law

derived boundary guard
  defense in depth or trust-boundary enforcement derived from that authority

compensating guard
  downstream detection/repair caused by permissive admission

compatibility adapter
  temporary or externally required transition behavior

observability guard
  monitoring/audit without admission authority

redundant semantic owner
  independently authored implementation of the same law
```

Distributed/redundant ownership and compensating guards are architectural
pressure. Legitimate derived guards are not residue merely because primary
enforcement exists elsewhere.

## Realization or architecture defect

Preserve the architecture when it already has:

- one canonical semantic authority;
- an adequate representation and state space;
- complete sanctioned-path coverage through one frontier or explicit cut;
- a mechanism capable of excluding `Phi` over `D` at the stated strength; and
- no live sanctioned escape path needing a new mechanism.

Reopen architecture when a sanctioned-path witness shows constructible forbidden
state, illegal transition/composition, absent/distributed/contested authority,
bypassable enforcement, a missing semantic state/law, compensating guard
accretion, or prior pointwise fixes retaining the same admission route.

One witness is sufficient when it falsifies an attributed universal claim over
a sanctioned path. Test hooks, corrupted fixtures, unsupported paths, and
externally invalid values do not falsify sanctioned construction soundness
unless the architecture claims to admit them.

## Bounded excavation

1. Preserve witness provenance and classify current applicability.
2. Name the law, provenance, and detection surface.
3. Inspect current owner sites and sanctioned admission paths.
4. Walk upstream and across ingress paths to candidate owner-capable frontiers.
5. Inspect code, types, schemas, tests, public constructors, transition APIs,
   interpreters, handlers, and ordinary documentation at those seams.
6. Classify scar tissue rather than counting checks.
7. Inspect targeted Git, issue, PR, CAS, or incident history only when current
   evidence suggests recurrence or displaced ownership.
8. Stop when closure, a hotspot, an admission cut, or material uncertainty is
   established.

Do not perform repository-wide archaeology by default. Missing history means
recurrence is unknown, not absent.

## Witness independence

Independent witnesses differ materially in input partition, state/transition,
call or admission path, producer/consumer, external incident, generator, or
temporal trace. Duplicate reports, copied tests, repeated prose, and several
failures from one root execution are not independent evidence.

One file may contain unrelated classes; several files may expose one class.

## Closure and disposition

Let `I(H)` be the incumbent, `F = {x in D | Phi(x)}`, `A` the sanctioned
admission relation, and `C` the frontier or cut.

The incumbent is closed only when its semantic authority and `C` can exclude
`F` from `A` over `D` at the stated strength without another independent
compensating guard, semantic owner, representation, state dimension, transition
law, effect, compatibility/recovery mode, or escape path.

Use one disposition:

```text
eliminated
  F is excluded from A over D at the stated claim strength

contained
  current risk is bounded, but F or an external residual remains admitted

obstructed
  evidence establishes that required exclusion is unavailable or inadmissible

unresolved
  family, applicability, ownership, coverage, or proof is unknown
```

Containment may satisfy an explicitly bounded Goal but is not correct by
construction and does not eliminate the hotspot.

## Correctness dominance

For candidate `A`:

```text
Invalid(A)   predicate-defined invalid states/traces still admitted
Escape(A)    unchecked sanctioned or bypass paths
Owners(A)    independent semantic authorities for the law
Residual(A)  runtime checks and proof obligations not discharged
```

State how each comparison was established:

```text
proof | exhaustive-finite | bounded | property-tested | sampled | inferred | unknown
```

Candidate `A` correctness-dominates `B` only when it preserves required valid
observations, compatibility, effects, and resources; has subset invalidity and
escape paths at compatible strength; has no more semantic authorities or
residual burden; introduces no materially worse operational/migration/resource
burden; and is strictly better on at least one relation.

Selection is two-stage:

1. establish the correctness Pareto frontier;
2. among correctness-equivalent candidates choose the least costly effective
   realization;
3. preserve incomparability when correctness and cost trade off materially.

Never use a scalar architecture score.

## Universalist projection

For each bug-driven candidate require:

```text
Current owner set and status:
Candidate semantic owner:
Enforcement locus or admission cut:
Family predicate / domain / sanctioned admission relation:
Claim strength and comparison evidence:
Invalid family excluded:
Unchecked paths retired:
Primary enforcement / derived guards preserved:
Valid observations preserved:
Residual invalidity and owner:
Disposition supported:
Falsifier / transition / retirement:
```

Universalist nominates. Actuating compares and selects.

## Reduce challenge

Ask Reduce to classify every implicated check before ablation. A candidate is
presumptively dominated when it preserves the same invalid region and only
moves/adds compensating detection. Do not remove primary enforcement, derived
trust-boundary guards, compatibility adapters, or observability guards as though
they were compensating residue.

## Proof and compression

As evidence accumulates:

```text
one witness -> focused regression
several same-law witnesses -> observational class and family hypothesis
stable predicate-defined family -> property/model/exhaustive/schema/fuzz proof
architectural correction -> owner- or cut-level family exclusion and escape proof
```

A correct-by-construction claim proves at an explicit strength:

```text
current-witness rejection
Phi excluded from sanctioned admission over the declared domain
valid behavior/compatibility/effects/resources preserved
frontier or cut covers every sanctioned path
escape paths cannot evade enforcement
all valid represented cases remain handled
residual constraints are explicit, owned, observable, and falsifiable
```

Use the strongest honest repository-supported mechanism: refinement or
implication proof, opaque constructors, tagged unions, exhaustive matching,
schema constraints, compile-fail tests, property/model tests, fuzzing,
interpreter agreement, transactional checks, or targeted surface searches.

## Working analysis

```text
Witness provenance / current applicability / law and provenance
Detection surface / observational class
Family predicate / domain / admission relation / claim strength
Current owner set/status / candidate owner
Admission frontier or cut / escape paths / classified scar tissue
Disposition / invalid region eliminated / admission coverage
Paths retired / derived guards preserved / valid observations preserved
Residual invalidity/owner / evidence strength
```

This remains ephemeral. Git, tests, owner evidence, and ordinary documentation
retain durable truth.

## Discriminators

```text
Existing canonical mechanism, one implementation deviates
  -> preserve architecture; repair realization

Public representation admits forbidden combinations
  -> reopen; exclude Phi at construction/representation

One law independently implemented across services
  -> distributed owner set; select authority and possibly an admission cut

Incident at old build B0, analysis at H1
  -> preserve B0 provenance; classify H1 applicability

Several incomparable ingress paths admit one family
  -> minimal admission cut, not an invented single frontier

External provider remains capable of invalid output
  -> earliest local containment; explicit residual; no elimination claim

Two bugs in one file violate different laws
  -> split; no hotspot
```

## Hard exclusions

- No bug Ledger, hotspot registry/database, score, threshold, receipt family,
  predecessor chain, or durable Actuating state.
- Do not define a family as only observed examples.
- Do not rewrite historical provenance as current-head provenance.
- Do not require one current owner when owner dilution may be the defect.
- Do not invent one frontier when a minimal admission cut is required.
- Do not use file proximity, churn, retries, elapsed time, or vocabulary as
  hotspot evidence.
- Do not conflate detection with admission.
- Do not call guard multiplication or containment correct by construction.
- Do not claim elimination without domain, admission relation, claim strength,
  and path coverage.
