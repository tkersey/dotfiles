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

Interpretation family Alpha
  witness, incumbent, and candidate maps into Omega

Comparison universe U_K
  concrete behaviors considered at candidate K's admission surfaces

Sanctioned behavior B_K subset U_K
  concrete behaviors K actually admits

Counterexample theory Theta
  (Omega, Alpha, L, Phi, A, O, C, Q): semantic domain, interpretations, law,
  invalidity predicate, sanctioned admission semantics, owner model,
  frontier/cut, and claim strength

Invalid family
  F = { omega in Omega | Phi(omega) }

Family-theory falsifier
  evidence that would refute Theta

Safety-adequacy falsifier
  evidence that an interpretation is partial or fails to reflect a concrete
  violation

Goal-adequacy falsifier
  evidence that a required valid behavior or observation was lost

Diagnostic-exactness counterexample
  a safe behavior conservatively classified as abstractly unsafe
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
Theta_0 = (Omega_0, Alpha_0, L_0, Phi_0, A_0, O_0, C_0, Q_0)
```

State:

```text
Semantic observation domain Omega_0:
Interpretation family Alpha_0:
Comparison universe U_0 / sanctioned behavior B_0:
Governing law L_0 and provenance:
Witness interpretation into Omega_0:
Predicate or generator Phi_0:
Sanctioned admission semantics A_0:
Current owner model O_0:
Frontier/cut hypothesis C_0:
Validity horizon and claim strength Q_0:
Safety-adequacy argument and falsifier:
Goal-adequacy argument and falsifier:
Diagnostic-exactness status and counterexample:
Family-theory falsifier:
```

`Omega` must expose the Goal's required observations without assuming that the
incumbent fields, classes, services, or storage layout are the correct
coordinates. Representation independence is necessary but not sufficient: a
coarse domain can underapproximate danger or erase required meaning.

A theory requires challenge when it is:

- **detection-shaped** — expressed mainly in the failure site;
- **enumerative** — a disjunction of observed examples without a governing law;
- **representation-bound** — meaningful only in accidental incumbent concepts;
- **violation-erasing** — a concrete law violation maps outside `Phi`;
- **Goal-erasing** — a required valid behavior or observation disappears;
- **escaping** — a same-law applicable witness lies outside `Phi`;
- **owner/topology-captive** — it assumes the current owner or one frontier;
- **merely adequate** — a materially different coherent explanation remains live.

A false positive alone does not activate a safety reframe. It downgrades
diagnostic exactness and matters when it excludes accepted valid behavior or
creates material proof, usability, or operational cost.

## Safety adequacy, Goal adequacy, and diagnostic exactness

For candidate architecture `K`, let:

```text
U_K
  concrete behaviors considered at K's sanctioned admission surfaces within the
  declared validity horizon

B_K subset U_K
  concrete behaviors actually sanctioned or admitted by K

alpha_K : U_K -> Omega
  K's interpretation into the selected semantic observation domain

Bad_L(u)
  concrete behavior u violates governing law L
```

### Totality

```text
for every u in U_K:
  alpha_K(u) is defined
```

A behavior in the declared comparison horizon cannot disappear merely because
the semantic model has no coordinate for it.

### Violation reflection

```text
for every u in U_K:
  Bad_L(u) -> Phi(alpha_K(u))
```

Every concrete violation remains visibly unsafe after abstraction. This is the
soundness direction required to infer concrete exclusion from abstract
exclusion.

### Abstract exclusion

```text
for every b in B_K:
  not Phi(alpha_K(b))
```

The candidate sanctions no behavior that its sound abstraction marks unsafe.
Together with violation reflection, this implies that no `b in B_K` violates
`L`.

### Required-valid preservation

```text
for every Goal-required valid behavior v in U_K:
  v is in B_K
```

Safety cannot be established vacuously by rejecting everything the Goal
requires.

### Required-observation preservation

Every Goal-required observation must remain available with its accepted meaning.
`Alpha` may quotient representational distinctions only when that quotient does
not erase required observable behavior.

### Diagnostic exactness

```text
for every u in U_K:
  Phi(alpha_K(u)) -> Bad_L(u)
```

This converse is useful but not a safety premise. Classify it as:

```text
exact
conservative-overapproximation
bounded
sampled
unknown
```

A conservative overapproximation may classify optional safe behavior as unsafe.
It remains correct by construction when totality, violation reflection, abstract
exclusion, and Goal adequacy hold. Record the optional behavior excluded and use
that cost in candidate comparison.

State:

```text
Interpretation totality:
Violation-reflection evidence:
Abstract-exclusion evidence:
Required valid behavior preserved:
Required observations preserved:
Correctness-bearing distinctions retained:
Distinctions intentionally quotiented:
Optional safe behavior excluded:
Safety-adequacy strength and falsifier:
Goal-adequacy strength and falsifier:
Diagnostic-exactness status, strength, and counterexample:
```

Evidence strength is one of:

```text
proved | exhaustive-finite | bounded | property-tested |
sampled | hypothesized | unknown
```

The selected theory's safety claim strength `Q` cannot exceed the weakest of
its family, totality, violation-reflection, Goal-adequacy, admission-coverage,
and abstract-exclusion evidence. Diagnostic exactness has its own strength and
does not cap the safety claim.

The governing rule is:

> Abstraction may overapproximate danger. It may not underapproximate danger,
> erase required behavior, or call conservative rejection residual incorrectness.

## Metanoetic challenge

When theory, safety, or Goal pressure is live, invoke `$metanoetic` exactly once
on the unchanged theory decision surface. Bind the Goal, witnesses, `Theta_0`,
required observations, claim strengths, and material falsifiers.

The challenger may revise any coordinate:

```text
Theta_1 = (Omega_1, Alpha_1, L_1, Phi_1, A_1, O_1, C_1, Q_1)
```

It may discover a missing semantic object, replace a state predicate with a
trace or authority law, split one family, combine several manifestations,
relocate ownership, or replace an unsound observation domain with a sound one.
Metanoetic generates; it does not select.

Skip this pass when an already-canonical owner and representation clearly
exclude the family, the interpretation is already sound and Goal-adequate, and
one implementation merely violates that mechanism. Conservative diagnostic
exactness alone is not a reason to invoke Metanoetic.

## OPERATE ARCHITECTONICALLY

Actuating adjudicates `Theta_0`, a live `Theta_1`, and any material split or
combination. Compare:

```text
witness coverage and law provenance
representation independence of Omega
interpretation totality and violation reflection
abstract exclusion and required-valid preservation
required-observation preservation
diagnostic exactness and optional valid behavior excluded
causal compression and sibling-counterexample prediction
canonical ownership and derived enforcement
lawful construction, elimination, and composition
sanctioned admission and escape-path coverage
falsifier quality, proof strength, and reconstitution cost
```

Return one theory disposition:

```text
retain | replace | combine | split | unresolved
```

Architectonic adjudication seeks the **least discriminating sound abstraction**:
the semantic domain that removes accidental distinctions while reflecting every
violation and preserving every required observation. It does not retain
complexity merely to classify optional safe behavior exactly.

## Predicate-defined family

After adjudication, finalize:

```text
Omega / Alpha / L / witness interpretation
U / B / D within Omega / Phi / F = { omega in D | Phi(omega) }
A / owner model / frontier or cut
safety-adequacy and Goal-adequacy laws and falsifiers
diagnostic-exactness status and counterexample
validity horizon / claim strength / family-theory falsifier
```

Fixing every observed example does not prove exclusion of `Phi`. A predicate
without a credible semantic domain, total violation-reflecting interpretation,
Goal-adequacy argument, admission model, or falsifier remains `hypothesized` or
`unknown`.

## Observational classes and frontier partition

Review Fold may group currently applicable witnesses when evidence supports the
same law, compatible discrepancy/applicability, and a plausible causal
relation. It returns a family hypothesis, not a final theory or frontier.

Actuating:

1. adjudicates the counterexample theory and interpretation;
2. partitions the observational class if distinct theories or frontiers emerge;
3. selects one frontier if it covers every sanctioned admission path;
4. otherwise selects a minimal admission cut;
5. returns unresolved when safety, Goal adequacy, coverage, or authority is
   unknown.

## One bounded co-refinement

Theory and architecture are co-discovered. A live Universalist candidate may
expose a materially simpler, more representation-independent, more sound, or
more causally adequate theory.

Permit one back-edge before target selection:

```text
selected theory
-> repository-native candidate
-> explicit candidate theory or interpretation delta
-> one return to architectonic adjudication
-> revise or retain theory
-> compare candidates
```

Do not rerun Metanoetic on the unchanged decision surface. A candidate delta
must identify the accidental coordinate, proposed semantic domain/law,
witness and candidate interpretations, safety and Goal arguments, diagnostic-
exactness status, predicted sibling counterexamples, and falsifiers. It may
expose a better theory; it may not silently redefine the family, erase
invalidity, or discard Goal-required behavior.

## Theory, safety, Goal, and exactness counterevidence

Material theory or safety refuters include:

```text
same-law current witness outside Phi
sanctioned path omitted from A
sanctioned behavior without an interpretation
concrete L-violation mapped outside Phi
candidate behavior not interpretable into Omega
selected owner lacks authority for L
simpler live theory with equal or stronger proof
```

Goal-adequacy refuters include:

```text
Goal-required valid behavior excluded from B
Goal-required observation erased or changed by Alpha
accepted compatibility, effect, or resource behavior lost
```

Diagnostic-exactness counterevidence is:

```text
Phi-member that does not violate L
```

It downgrades exactness to a conservative or weaker status. It does not by itself
reopen or block safety elimination.

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
- a total violation-reflecting interpretation;
- preservation of every Goal-required valid behavior and observation; and
- no live sanctioned escape path requiring a new mechanism.

Diagnostic exactness may be conservative. Reopen only when its false positives
remove accepted behavior or create a material dominated burden.

Reopen when a sanctioned-path witness shows constructible forbidden state,
illegal transition/composition, absent/distributed/contested authority,
bypassable enforcement, a missing semantic law, compensating guard accretion,
prior pointwise fixes retaining the route, or a theory/candidate interpretation
that underapproximates danger or erases required meaning.

One witness is sufficient when it falsifies an attributed universal law over a
sanctioned path. Unsupported test hooks or corrupted fixtures are not sanctioned
counterexamples unless the architecture claims to admit them.

## Bounded excavation

1. Preserve provenance and classify applicability.
2. Name the law and detection surface.
3. Inspect owner sites and sanctioned admission paths.
4. Derive `Theta_0`, safety/Goal arguments, exactness status, and falsifiers.
5. Challenge and adjudicate only when evidence activates the route.
6. Walk to owner-capable frontiers and classify scar tissue.
7. Inspect targeted history only when current evidence suggests recurrence.
8. Stop when closure, a hotspot, an admission cut, or material uncertainty is
   established.

Do not perform repository-wide archaeology by default.

## Closure and disposition

For selected `Theta = (Omega, Alpha, L, Phi, A, O, C, Q)` and candidate `K`,
elimination requires:

```text
for every u in U_K:
  alpha_K(u) is defined
  Bad_L(u) -> Phi(alpha_K(u))

for every b in B_K:
  not Phi(alpha_K(b))

every Goal-required valid behavior is in B_K
every Goal-required observation is preserved
```

Together these imply:

```text
for every b in B_K:
  not Bad_L(b)
```

at strength `Q`. Diagnostic exactness is not used in this proof.

Use one disposition:

```text
eliminated
  concrete L-violations are excluded from sanctioned behavior at Q

contained
  current risk is bounded, but concrete invalidity, reflection/path coverage, or
  an external residual remains admitted or only partially characterized

obstructed
  required exclusion or a sound Goal-adequate interpretation is unavailable

unresolved
  theory, safety/Goal adequacy, ownership, coverage, or proof is unknown
```

Conservative rejection of optional safe behavior is not containment.
Containment is not correct by construction.

## Correctness dominance

For candidate `K`:

```text
Invalid(K)      concrete L-violations still admitted, reflected through Alpha
Escape(K)       unchecked sanctioned or bypass paths
Owners(K)       independent semantic authorities for the law
Residual(K)     runtime checks and proof obligations not discharged
Restriction(K)  safe optional behavior conservatively excluded
```

First compare safety, Goal adequacy, ownership, path coverage, and residual proof
burden. A candidate with unknown, partial, or violation-erasing interpretation,
or one that loses required valid behavior, cannot enter the correctness Pareto
frontier as an equal alternative.

Among safety- and Goal-equivalent candidates, compare `Restriction(K)`,
diagnostic exactness, conceptual compression, proof burden, migration, and
operational cost. A more exact abstraction does not dominate merely by retaining
extra distinctions with no accepted dividend.

State relation evidence as:

```text
proof | exhaustive-finite | bounded | property-tested |
sampled | inferred | unknown
```

Preserve incomparability when correctness and cost trade off materially. Never
use a scalar architecture score.

## Universalist projection

For every live candidate require:

```text
Selected counterexample theory / candidate theory or interpretation delta
Candidate semantic owner / enforcement locus or admission cut
Comparison universe U / sanctioned behavior B
Witness and candidate interpretation into Omega
Interpretation totality
Violation-reflection evidence
Abstract-exclusion evidence
Required valid behaviors preserved
Required observations preserved
Correctness-bearing distinctions preserved
Distinctions intentionally quotiented
Optional safe behavior excluded
Safety/Goal strength and falsifiers
Diagnostic-exactness status, strength, and counterexample
Family predicate / domain / sanctioned admission relation
Claim strength and comparison evidence
Invalid family excluded / unchecked paths retired
Primary enforcement / derived guards preserved
Valid observations preserved / residual invalidity and owner
Disposition / falsifier / transition / retirement
```

Universalist nominates. Actuating adjudicates any theory or interpretation delta
and selects.

## Proof and compression

```text
one witness -> focused regression
several same-law witnesses -> observational class and ordinary theory
live alternative -> Metanoetic challenge and architectonic adjudication
stable family -> property/model/exhaustive/schema/fuzz proof
architecture correction -> owner/cut concrete exclusion and escape proof
```

A correct-by-construction claim proves, at an explicit strength:

```text
current-witness rejection
witness and candidate interpretation into the selected Omega
interpretation totality
violation reflection
abstract exclusion from sanctioned behavior
required-valid and required-observation preservation
the selected theory and safety/Goal claims survive their falsifiers
Phi excluded from sanctioned admission over the declared domain
valid observations, effects, compatibility, and resources preserved
frontier/cut covers every sanctioned path and bypass
residual constraints are explicit, owned, observable, and falsifiable
diagnostic exactness is classified separately
```

## Working analysis

```text
Witness provenance / applicability / law / detection surface
Observational class / Theta_0 / Theta_1 / architectonic disposition
Omega / Alpha / U / B / Phi / A / theory falsifier / claim strength
Interpretation totality / reflection / abstract exclusion
Required valid behavior / required observations preserved
Diagnostic exactness / optional safe behavior excluded
Safety/Goal strength and falsifiers
Correctness-bearing distinctions retained / distinctions intentionally quotiented
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
- Do not finalize a detection-shaped, enumerative, representation-bound,
  violation-erasing, or Goal-erasing theory while a material challenger remains
  live.
- Do not rerun Metanoetic on one unchanged decision surface.
- Do not use architectonic vocabulary without adjudicating the organizing law,
  semantic domain, sound abstraction, ownership, construction, composition, and
  falsifier.
- Do not let a candidate silently redefine the family or interpretation it
  claims to realize.
- Do not treat representation independence as safety adequacy.
- Do not allow `Alpha` to underapproximate danger or erase Goal-required behavior
  or observations.
- Do not require diagnostic exactness for elimination.
- Do not treat conservative rejection of optional safe behavior as residual
  incorrectness.
- Do not conflate detection with admission or containment with elimination.
- Do not claim elimination without a selected theory, total violation-reflecting
  interpretation, abstract exclusion, Goal adequacy, admission relation, claim
  strength, falsifiers, and path coverage.
