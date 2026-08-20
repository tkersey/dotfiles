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

Counterexample theory Theta
  (Omega, Alpha, L, Phi, A, O, C, Q): semantic domain, interpretations, law,
  invalidity predicate, sanctioned admission semantics, owner model,
  frontier/cut, and claim strength

Invalid family
  F = { omega in Omega | Phi(omega) }

Family-theory falsifier
  evidence that would refute Theta

Interpretation-adequacy falsifier
  evidence that an interpretation erases, invents, or fails to cover a
  correctness-bearing distinction
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
Governing law L_0 and provenance:
Witness interpretation into Omega_0:
Predicate or generator Phi_0:
Sanctioned admission semantics A_0:
Current owner model O_0:
Frontier/cut hypothesis C_0:
Validity horizon and claim strength Q_0:
Interpretation-adequacy argument and falsifier:
Family-theory falsifier:
```

`Omega` must expose the Goal's required observations without assuming that the
incumbent fields, classes, services, or storage layout are the correct
coordinates. Representation independence is necessary but not sufficient: a
coarse domain can erase the distinction that makes a concrete behavior wrong.

A theory requires challenge when it is:

- **detection-shaped** — expressed mainly in the failure site;
- **enumerative** — a disjunction of observed examples without a governing law;
- **representation-bound** — meaningful only in accidental incumbent concepts;
- **law-erasing** — its interpretation identifies behaviors that differ under
  the governing law or a required observation;
- **escaping** — a same-law applicable witness lies outside `Phi`;
- **owner/topology-captive** — it assumes the current owner or one frontier;
- **merely adequate** — a materially different coherent explanation remains live.

## Interpretation adequacy

For candidate architecture `K`, let:

```text
B_K
  concrete behaviors sanctioned by K within the declared validity horizon

alpha_K : B_K -> Omega
  K's interpretation into the selected semantic observation domain

Bad_L(b)
  concrete behavior b violates governing law L
```

An interpretation is adequate only when the evidence supports all four laws at
an explicit strength.

### Totality

```text
for every b in B_K:
  alpha_K(b) is defined
```

A sanctioned behavior cannot disappear merely because the comparison model has
no coordinate for it.

### Violation reflection

```text
for every b in B_K:
  Bad_L(b) -> Phi(alpha_K(b))
```

Every concrete violation remains visibly invalid after abstraction. This is the
minimum law needed to infer concrete exclusion from abstract exclusion.

### Invalidity precision

```text
for every b in B_K:
  Phi(alpha_K(b)) -> Bad_L(b)
```

The invalidity predicate must not classify required valid behavior as invalid.
When exact precision cannot be established, the residual must be explicit and
cannot support an unqualified correct-by-construction claim.

### Required-observation preservation

For sanctioned behaviors `b1` and `b2`:

```text
alpha_K(b1) == alpha_K(b2)
->
  (Bad_L(b1) <-> Bad_L(b2))
  and every Goal-required observation agrees
```

Equivalently, the kernel of `alpha_K` must be contained within equivalence under
`L` and the Goal's required observations. The interpretation may quotient
accidental representation; it may not quotient violation or observable meaning.

State:

```text
Interpretation totality:
Violation-reflection evidence:
Invalidity-precision evidence:
Required observations preserved:
Correctness-bearing distinctions retained:
Distinctions intentionally quotiented:
Adequacy strength:
Adequacy falsifier:
```

The adequacy strength is one of:

```text
proved | exhaustive-finite | bounded | property-tested |
sampled | hypothesized | unknown
```

The selected theory's overall strength `Q` cannot exceed the weakest of its
family, interpretation-adequacy, admission-coverage, and exclusion evidence.

The governing rule is:

> Abstraction may forget representation; it may not forget violation.

## Metanoetic challenge

When theory or interpretation pressure is live, invoke `$metanoetic` exactly
once on the unchanged theory decision surface. Bind the Goal, witnesses,
`Theta_0`, required observations, claim strengths, and both falsifiers.

The challenger may revise any coordinate:

```text
Theta_1 = (Omega_1, Alpha_1, L_1, Phi_1, A_1, O_1, C_1, Q_1)
```

It may discover a missing semantic object, replace a state predicate with a
trace or authority law, split one family, combine several manifestations,
relocate ownership, or replace a coarse observation domain with a law-reflecting
one. Metanoetic generates; it does not select.

Skip this pass when an already-canonical owner and representation clearly
exclude the family, the interpretation is already law-reflecting, and one
implementation merely violates that mechanism.

## OPERATE ARCHITECTONICALLY

Actuating adjudicates `Theta_0`, a live `Theta_1`, and any material split or
combination. Compare:

```text
witness coverage and law provenance
representation independence of Omega
interpretation totality and law reflection
invalidity precision and required-observation preservation
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

Architectonic adjudication seeks the **smallest lawful quotient**: the semantic
domain that removes accidental distinctions while retaining every distinction
needed to state and decide `L` and every required observation. It does not select
the most abstract vocabulary or the smallest state space at any cost.

## Predicate-defined family

After adjudication, finalize:

```text
Omega / Alpha / L / witness interpretation
D within Omega / Phi / F = { omega in D | Phi(omega) }
A / owner model / frontier or cut
interpretation-adequacy laws and falsifier
validity horizon / claim strength / family-theory falsifier
```

Fixing every observed example does not prove exclusion of `Phi`. A predicate
without a credible semantic domain, total law-reflecting interpretation,
admission model, or falsifier remains `hypothesized` or `unknown`.

## Observational classes and frontier partition

Review Fold may group currently applicable witnesses when evidence supports the
same law, compatible discrepancy/applicability, and a plausible causal
relation. It returns a family hypothesis, not a final theory or frontier.

Actuating:

1. adjudicates the counterexample theory and interpretation;
2. partitions the observational class if distinct theories or frontiers emerge;
3. selects one frontier if it covers every sanctioned admission path;
4. otherwise selects a minimal admission cut;
5. returns unresolved when interpretation, coverage, or authority is unknown.

## One bounded co-refinement

Theory and architecture are co-discovered. A live Universalist candidate may
expose a materially simpler, more representation-independent, more
law-reflecting, or more causally adequate theory.

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
witness and candidate interpretations, adequacy argument, predicted sibling
counterexamples, and falsifier. It may expose a better theory; it may not
silently redefine the family it claims to eliminate or erase invalidity through
its interpretation.

## Theory and interpretation falsifiers

Include every applicable refuter:

```text
same-law current witness outside Phi
Phi-member that does not violate L
sanctioned path omitted from A
valid observation classified as invalid
sanctioned behavior without an interpretation
concrete L-violation mapped outside Phi
two behaviors with different L-status mapped to one Omega observation
Goal-required observation erased by Alpha
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
- a total, law-reflecting, precise interpretation preserving required
  observations; and
- no live sanctioned escape path requiring a new mechanism.

Reopen when a sanctioned-path witness shows constructible forbidden state,
illegal transition/composition, absent/distributed/contested authority,
bypassable enforcement, a missing semantic law, compensating guard accretion,
prior pointwise fixes retaining the route, or a theory/candidate interpretation
that hides a law-bearing distinction.

One witness is sufficient when it falsifies an attributed universal law over a
sanctioned path. Unsupported test hooks or corrupted fixtures are not sanctioned
counterexamples unless the architecture claims to admit them.

## Bounded excavation

1. Preserve provenance and classify applicability.
2. Name the law and detection surface.
3. Inspect owner sites and sanctioned admission paths.
4. Derive `Theta_0`, interpretation-adequacy argument, and falsifiers.
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
for every behavior b sanctioned by A in K:
  alpha_K(b) is defined
  Bad_L(b) <-> Phi(alpha_K(b))
  not Phi(alpha_K(b))
```

Together these imply:

```text
for every behavior b sanctioned by A in K:
  not Bad_L(b)
```

at strength `Q`. The candidate must also preserve every Goal-required valid
observation and close every sanctioned or bypass path in `C`.

Use one disposition:

```text
eliminated
  concrete L-violations are excluded through an adequate interpretation at Q

contained
  current risk is bounded, but the family, interpretation, or external residual
  remains admitted or only one direction of adequacy is established

obstructed
  required exclusion or adequate interpretation is evidenced as unavailable

unresolved
  theory, interpretation, ownership, coverage, or proof is unknown
```

Containment is not correct by construction.

## Correctness dominance

For candidate `K`:

```text
Invalid(K)   concrete L-violations still admitted, reflected through Alpha
Escape(K)    unchecked sanctioned or bypass paths
Owners(K)    independent semantic authorities for the law
Residual(K)  runtime checks and proof obligations not discharged
```

Compare candidates through adequate interpretations into the same selected
`Omega`. A candidate with unknown, partial, or law-erasing interpretation cannot
enter the correctness Pareto frontier as an equal correctness alternative.
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
Selected counterexample theory / candidate theory or interpretation delta
Candidate semantic owner / enforcement locus or admission cut
Witness and candidate interpretation into Omega
Interpretation totality
Violation-reflection evidence
Invalidity-precision evidence
Correctness-bearing distinctions preserved
Distinctions intentionally quotiented
Required observations preserved
Adequacy strength and falsifier
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
violation reflection and invalidity precision
required-observation preservation
the selected theory and interpretation survive their falsifiers
Phi excluded from sanctioned admission over the declared domain
valid observations, effects, compatibility, and resources preserved
frontier/cut covers every sanctioned path and bypass
residual constraints are explicit, owned, observable, and falsifiable
```

## Working analysis

```text
Witness provenance / applicability / law / detection surface
Observational class / Theta_0 / Theta_1 / architectonic disposition
Omega / Alpha / Phi / A / theory falsifier / claim strength
Interpretation totality / reflection / precision / observation preservation
Correctness-bearing distinctions retained / distinctions intentionally quotiented
Interpretation-adequacy strength and falsifier
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
- Do not finalize a detection-shaped, enumerative, representation-bound, or
  law-erasing theory while a material challenger remains live.
- Do not rerun Metanoetic on one unchanged decision surface.
- Do not use architectonic vocabulary without adjudicating the organizing law,
  semantic domain, lawful quotient, ownership, construction, composition, and
  falsifier.
- Do not let a candidate silently redefine the family or interpretation it
  claims to realize.
- Do not treat representation independence as interpretation adequacy.
- Do not allow `Alpha` to collapse behaviors that differ under `L` or a
  Goal-required observation.
- Do not conflate detection with admission or containment with elimination.
- Do not claim elimination without a selected theory, total law-reflecting
  interpretation, admission relation, claim strength, falsifiers, and path
  coverage.
