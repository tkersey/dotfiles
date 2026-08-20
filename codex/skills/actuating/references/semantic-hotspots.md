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

**Return:** one bounded counterexample theory and topology and, when architecture
selection reopens, one correctness delta. Create no durable artifact.

## Semantic objects

A bug is one witness, not the family and not a patch instruction.

```text
Witness provenance
  exact version/build/schema/environment/input/state/trace observed

Current applicability
  whether the law and causal route remain live at the current Goal and head

Detection surface
  where incorrectness became visible

Observational class
  Review Fold's same-law grouping before theory adjudication

Semantic observation domain Omega
  representation-independent observations used to compare theories and candidates

Counterexample theory Theta
  (Omega, L, Phi, A, O, C, Q): domain, law, invalidity predicate, sanctioned
  admission semantics, owner model, frontier/cut, and claim strength

Invalid family
  F = { omega in Omega | Phi(omega) }

Witness / candidate interpretation
  how concrete evidence and candidate behavior denote observations in Omega

Family-theory falsifier
  evidence that would refute Theta
```

A semantic hotspot is the ephemeral conjunction:

```text
law x predicate-defined family x owner set x frontier/cut x escape paths x witnesses
```

It is not a file, churn score, bug count, review count, or persistent record.

## Provenance and applicability

Never rewrite a historical witness as though it occurred at the current head.
Record its original subject separately from current applicability:

```text
still-present | transformed-applicable | already-excluded |
not-comparable | unknown
```

Only `still-present` and `transformed-applicable` create current architectural
pressure. Unknown history means unknown recurrence, not absence.

## Ordinary counterexample theory

Review Fold supplies exact witnesses, law attribution, owner sites, and a
bounded family hypothesis. Actuating derives the smallest ordinary theory:

```text
Theta_0 = (Omega_0, L_0, Phi_0, A_0, O_0, C_0, Q_0)
```

State:

```text
Semantic observation domain Omega_0:
Governing law L_0 and provenance:
Witness interpretation into Omega_0:
Predicate or generator Phi_0:
Sanctioned admission semantics A_0:
Current owner model O_0:
Frontier/cut hypothesis C_0:
Validity horizon and claim strength Q_0:
Family-theory falsifier:
```

`Omega` must expose the Goal's required observations without assuming that the
incumbent fields, classes, services, or storage layout are the correct
coordinates.

A theory requires challenge when it is:

- **detection-shaped** — expressed mainly in the failure site;
- **enumerative** — a disjunction of observed examples without a governing law;
- **representation-bound** — meaningful only in accidental incumbent concepts;
- **escaping** — a same-law applicable witness lies outside `Phi`;
- **owner/topology-captive** — it assumes the current owner or one frontier;
- **merely adequate** — a materially different coherent explanation remains live.

## Metanoetic challenge

When that pressure is live, invoke `$metanoetic` exactly once on the unchanged
theory decision surface. Bind the Goal, witnesses, `Theta_0`, required
observations, claim strength, and falsifier.

The challenger may revise any coordinate:

```text
Theta_1 = (Omega_1, L_1, Phi_1, A_1, O_1, C_1, Q_1)
```

It may discover a missing semantic object, replace a state predicate with a
trace or authority law, split one family, combine several manifestations, or
relocate ownership. Metanoetic generates; it does not select.

Skip this pass when an already-canonical owner and representation clearly
exclude the family and one implementation merely violates that mechanism.

## OPERATE ARCHITECTONICALLY

Actuating adjudicates `Theta_0`, a live `Theta_1`, and any material split or
combination. Compare:

```text
witness coverage and law provenance
representation independence of Omega
causal compression and sibling-counterexample prediction
canonical ownership and derived enforcement
lawful construction, elimination, and composition
sanctioned admission and escape-path coverage
valid-observation preservation
falsifier quality, proof strength, and reconstitution cost
```

Return one theory disposition:

```text
retain | replace | combine | split | unresolved
```

Architectonic adjudication selects the smallest coherent organizing law,
domain, ownership, and composition—not the most abstract vocabulary.

## Predicate-defined family

After adjudication, finalize:

```text
Omega / L / witness interpretation
D within Omega / Phi / F = { omega in D | Phi(omega) }
A / owner model / frontier or cut
validity horizon / claim strength / theory falsifier
```

Claim strength is exactly one of:

```text
proved | exhaustive-finite | bounded | property-tested |
sampled | hypothesized | unknown
```

Fixing every observed example does not prove exclusion of `Phi`. A predicate
without a credible semantic domain, interpretation, admission model, or
falsifier remains `hypothesized` or `unknown`.

## Observational classes and frontier partition

Review Fold may group currently applicable witnesses when evidence supports the
same law, compatible discrepancy/applicability, and a plausible causal
relation. It returns a family hypothesis, not a final theory or frontier.

Actuating:

1. adjudicates the counterexample theory;
2. partitions the observational class if distinct theories or frontiers emerge;
3. selects one frontier if it covers every sanctioned admission path;
4. otherwise selects a minimal admission cut;
5. returns unresolved when interpretation, coverage, or authority is unknown.

## One bounded co-refinement

Theory and architecture are co-discovered. A live Universalist candidate may
expose a materially simpler, more representation-independent, or more causally
adequate theory.

Permit one back-edge before target selection:

```text
selected theory
-> repository-native candidate
-> explicit candidate theory delta
-> one return to architectonic adjudication
-> revise or retain theory
-> compare candidates
```

Do not rerun Metanoetic on the unchanged decision surface. A candidate theory
delta must identify the accidental coordinate, proposed semantic domain/law,
witness and candidate interpretations, predicted sibling counterexamples, and
falsifier. It may expose a better theory; it may not silently redefine the
family it claims to eliminate.

## Family-theory falsifier

Include every applicable refuter:

```text
same-law current witness outside Phi
Phi-member that does not violate L
sanctioned path omitted from A
valid observation classified as invalid
candidate behavior not interpretable into Omega
selected owner lacks authority for L
simpler live theory with equal or stronger explanatory and proof power
```

When one is established, reopen theory adjudication even after implementation
has begun.

## Owner sets and guard roles

Owner status is:

```text
canonical | distributed | absent | contested | unknown
```

Classify enforcement before ablation:

```text
primary enforcement
  semantic authority for the law

derived boundary guard
  legitimate defense in depth or trust-boundary enforcement

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
pressure. Derived guards are not residue merely because primary enforcement
exists elsewhere.

## Realization or architecture defect

Preserve the architecture only when it already has:

- canonical semantic authority;
- an adequate representation and state space;
- complete sanctioned-path coverage through one frontier or explicit cut;
- a mechanism capable of excluding `Phi` at the stated strength;
- behavior interpretable through the selected semantic domain; and
- no live sanctioned escape path requiring a new mechanism.

Reopen when a sanctioned-path witness shows constructible forbidden state,
illegal transition/composition, absent/distributed/contested authority,
bypassable enforcement, a missing semantic law, compensating guard accretion,
prior pointwise fixes retaining the route, or a candidate falsifying the theory.

One witness is sufficient when it falsifies an attributed universal law over a
sanctioned path. Unsupported test hooks or corrupted fixtures are not sanctioned
counterexamples unless the architecture claims to admit them.

## Bounded excavation

1. Preserve provenance and classify applicability.
2. Name the law and detection surface.
3. Inspect owner sites and sanctioned admission paths.
4. Derive `Theta_0` and its falsifier.
5. Challenge and adjudicate only when evidence activates the route.
6. Walk to owner-capable frontiers and classify scar tissue.
7. Inspect targeted history only when current evidence suggests recurrence.
8. Stop when closure, a hotspot, an admission cut, or material uncertainty is
   established.

Do not perform repository-wide archaeology by default.

## Closure and disposition

For selected `Theta = (Omega, L, Phi, A, O, C, Q)`, the incumbent is closed only
when:

```text
for every behavior b sanctioned by A:
  not Phi(interpret_I(H)(b))
```

at strength `Q`, without another independent compensating guard, semantic
owner, representation, state dimension, transition law, effect,
compatibility/recovery mode, or escape path.

Use one disposition:

```text
eliminated  family excluded at the stated strength
contained   risk bounded but family or external residual remains admitted
obstructed  required exclusion is evidenced as unavailable or inadmissible
unresolved  theory, interpretation, ownership, coverage, or proof is unknown
```

Containment is not correct by construction.

## Correctness dominance

For candidate `K`:

```text
Invalid(K)   predicate-defined invalid observations still admitted
Escape(K)    unchecked sanctioned or bypass paths
Owners(K)    independent semantic authorities for the law
Residual(K)  runtime checks and proof obligations not discharged
```

Compare candidates through interpretations into the same selected `Omega`.
State relation evidence as:

```text
proof | exhaustive-finite | bounded | property-tested |
sampled | inferred | unknown
```

Establish the correctness Pareto frontier before minimizing cost. Preserve
incomparability when correctness and cost trade off materially. Never use a
scalar architecture score.

## Universalist projection

For every live candidate require:

```text
Selected counterexample theory / candidate theory delta
Candidate semantic owner / enforcement locus or admission cut
Witness and candidate interpretation into Omega
Family predicate / domain / sanctioned admission relation
Claim strength and comparison evidence
Invalid family excluded / unchecked paths retired
Primary enforcement / derived guards preserved
Valid observations preserved / residual invalidity and owner
Disposition / falsifier / transition / retirement
```

Universalist nominates. Actuating adjudicates any theory delta and selects.

## Proof and compression

```text
one witness -> focused regression
several same-law witnesses -> observational class and ordinary theory
live alternative -> Metanoetic challenge and architectonic adjudication
stable family -> property/model/exhaustive/schema/fuzz proof
architecture correction -> owner/cut family exclusion and escape proof
```

A correct-by-construction claim proves, at an explicit strength:

```text
current-witness rejection
witness and candidate interpretation into the selected Omega
the selected theory survives its falsifier
Phi excluded from sanctioned admission over the declared domain
valid observations, effects, compatibility, and resources preserved
frontier/cut covers every sanctioned path and bypass
residual constraints are explicit, owned, observable, and falsifiable
```

## Working analysis

```text
Witness provenance / applicability / law / detection surface
Observational class / Theta_0 / Theta_1 / architectonic disposition
Omega / witness interpretation / Phi / A / theory falsifier / claim strength
Owner set / frontier or cut / escape paths / classified scar tissue
Candidate interpretation / co-refinement used
Disposition / invalid region eliminated / residual / proof
```

This remains ephemeral. Git, tests, owner evidence, and ordinary documentation
retain durable truth.

## Hard exclusions

- No bug Ledger, hotspot registry/database, score, threshold, receipt family,
  predecessor chain, or durable Actuating state.
- Do not define a family as only observed examples.
- Do not finalize a detection-shaped, enumerative, or representation-bound
  theory while a material challenger remains live.
- Do not rerun Metanoetic on one unchanged decision surface.
- Do not use architectonic vocabulary without adjudicating the organizing law,
  semantic domain, ownership, construction, composition, and falsifier.
- Do not let a candidate silently redefine the family it claims to eliminate.
- Do not conflate detection with admission or containment with elimination.
- Do not claim elimination without a selected theory, interpretation, admission
  relation, claim strength, falsifier, and path coverage.
