# Architecture Reconciliation

Actuating reconstructs the incumbent from the exact current Git tree. It does
not load a stored architecture and recompiles a target only when current
evidence makes the incumbent contestable.

## Incumbent model

Inspect repository-native evidence for:

```text
boundaries and sanctioned inputs
owner set and authority
authoritative representation
states, events, transitions, effects, ordering, and custody
observations and public contracts
compatibility, migration, retry, cancellation, and recovery
proof mechanisms
primary enforcement, derived guards, bypasses, and residue
```

Use code, types, schemas, tests, public interfaces, and ordinary architecture
documentation. Historical analyses are hypotheses unless current-tree evidence
still supports them.

## Bug-driven input

A bug is a counterexample to a required law, not a patch instruction.

Review Fold supplies an observational class with provenance, applicability,
law, current owner sites, and a bounded family hypothesis. Actuating derives an
ordinary counterexample theory:

```text
Theta_0 = (Omega_0, Alpha_0, L_0, Phi_0, A_0, O_0, C_0, Q_0)
```

`Omega` is a semantic observation domain independent of one candidate's
representation; `Alpha` the interpretation family for witnesses, incumbent,
and candidates; `L` the law; `Phi` the invalidity predicate; `A` sanctioned
admission semantics; `O` the owner model; `C` a frontier/cut hypothesis; and `Q`
the weakest supporting claim strength. Include validity horizon, family-theory
falsifier, and interpretation-adequacy argument and falsifier.

Review Fold does not select the final theory, interpretation, frontier, cut, or
repair.

## Interpretation adequacy

For candidate `K`, sanctioned concrete behavior `B_K`, and interpretation
`alpha_K : B_K -> Omega`, require at an explicit strength:

```text
Totality
  alpha_K is defined for every sanctioned behavior

Violation reflection
  Bad_L(b) -> Phi(alpha_K(b))

Invalidity precision
  Phi(alpha_K(b)) -> Bad_L(b)

Required-observation preservation
  alpha_K identifies behaviors only when they agree under L and every
  Goal-required observation
```

The interpretation is therefore a lawful quotient of concrete behavior. It may
remove accidental representation but cannot erase violation or required
observable meaning.

A theory or candidate is not architecture-comparable merely because an
interpretation function has been named. State the totality, reflection,
precision, observation-preservation, evidence strength, lost distinctions, and
falsifier.

## Theory synthesis and adjudication

Invoke one bounded `$metanoetic` challenge before finalization when `Theta_0` is
detection-shaped, enumerative, representation-bound, contradicted by a same-law
witness, owner/topology-captive, one of several materially different plausible
explanations, or based on a domain/interpretation that collapses law-distinct
behavior.

The challenger may revise the semantic domain, interpretation, law,
state-versus-trace formulation, predicate, admission semantics, owner,
frontier/cut, claim strength, or falsifier.

Then **OPERATE ARCHITECTONICALLY**. Compare the ordinary and challenger theories
by witness coverage, law provenance, representation independence,
interpretation adequacy, causal and conceptual compression, canonical ownership,
lawful construction/elimination/composition, admission coverage,
valid-observation preservation, falsifiers, and proof surface.

Return:

```text
retain | replace | combine | split | unresolved
```

Select the smallest lawful quotient and coherent organizing theory, not the most
abstract wording or the coarsest domain.

## Architecture closure

For selected theory:

```text
Theta = (Omega, Alpha, L, Phi, A, O, C, Q)
```

`I(H)` is closed under the bug only when its incumbent interpretation
`alpha_I(H)` is total and adequate and:

```text
for every behavior b sanctioned by A:
  Bad_L(b) <-> Phi(alpha_I(H)(b))
  and not Phi(alpha_I(H)(b))
```

at strength `Q`. Its existing authority and frontier/cut must preserve that
concrete exclusion without adding another independent guard, owner,
representation, state dimension, transition law, effect,
compatibility/recovery mode, or escape path.

It is not closed when the correction requires:

- a different semantic domain, interpretation, or governing law;
- recovery of a correctness-bearing distinction erased by the current domain;
- new state, transition, ordering, effect, authority, custody, or admission;
- new representation, interpreter, handler, observation, compatibility, retry,
  cancellation, timeout, or recovery semantics;
- structural removal of a bypass, competing owner, or obsolete representation;
- another downstream check while the invalid family remains admitted;
- a multi-frontier cut absent from the incumbent; or
- a live witness or candidate that falsifies the selected theory or its
  interpretation adequacy.

When closed, repair realization. Otherwise recompile before mutation.

## Reconsideration evidence

Reopen only from witnessed evidence:

```text
source change
sanctioned-path law falsification
semantic novelty or causal recurrence
predicate-defined hotspot
absent, distributed, contested, or unknown ownership
incomplete frontier/cut coverage
law-erasing or partial interpretation
live dominated residue
smaller correctness-non-dominated candidate
incoherent incumbent model
selected counterexample theory or adequacy claim falsified by a witness/candidate
```

Diff size, file proximity, elapsed time, bug/test/retry count, reviewer
preference, and abstract vocabulary do not establish reconsideration.

## Candidate compilation

1. Freeze the incumbent-independent premise basis with `$first-principles`.
2. Derive `Theta_0` and `Alpha_0` from Review Fold evidence and the incumbent.
3. Run one bounded `$metanoetic` challenge when its trigger is live.
4. **OPERATE ARCHITECTONICALLY** to adjudicate the theory and lawful quotient.
5. Finalize one theory, interpretation contract, frontier/cut, falsifiers, and
   claim strength.
6. Ask `$universalist` for repository-native candidates. Require each candidate
   to interpret every sanctioned behavior into the selected `Omega`, establish
   totality, violation reflection, invalidity precision, and required-observation
   preservation, and cover the same Goal, family, admission semantics,
   compatibility, effects, and resource constraints.
7. Permit one bounded co-refinement if a candidate exposes a materially simpler,
   more representation-independent, more law-reflecting, or more causally
   adequate theory. Return once to architectonic adjudication; do not rerun
   Metanoetic on the unchanged decision surface.
8. Ask `$reduce` to challenge unearned factors, witness-enumerating predicates,
   law-erasing quotients, compensating guards, and detection movement.
9. Establish the correctness Pareto frontier from explicit relation evidence.
   Exclude candidates with partial, unknown, or law-erasing interpretations.
10. Among correctness-equivalent candidates, select the least costly effective
    realization; preserve material incomparability.
11. State the selected theory, interpretation-adequacy argument, architecture
    delta, falsifiers, evidence strength, and proof before mutation.

Compare candidates by:

```text
required laws and observations
total law-reflecting interpretation into selected Omega
correctness-bearing distinctions retained
invalid concrete behavior excluded
sanctioned admission and frontier/cut coverage
semantic ownership and derived guards
representations, escape paths, compatibility, and migration
retirements and residual proof burden
proof strength, resources, and operational cost
```

A candidate cannot win by omitting an orthogonal obligation, merely moving
detection, or abstracting away evidence of invalidity.

## One bounded co-refinement

Universalist may return a candidate theory or interpretation delta:

```text
accidental incumbent coordinate
proposed semantic domain or law
witness and candidate interpretations
adequacy argument and falsifier
predicted sibling counterexamples
```

Actuating may return once to architectonic adjudication, then retain, revise,
split, or block. A candidate may expose a better theory; it may not silently
redefine the family or erase the violation it claims to eliminate.

## Architecture Working Set

For active implementation retain:

```text
Bound head / Goal / incumbent / falsified laws
Witness provenance / applicability / observational class
Theta_0 / Theta_1 / architectonic disposition
Selected Omega / Alpha / law / Phi / A / falsifiers / Q
Interpretation totality / reflection / precision / observation preservation
Correctness-bearing distinctions retained / distinctions intentionally quotiented
Owner set / frontier or cut / escape paths / classified scar tissue
Selected target / candidate owner / candidate interpretation
Co-refinement used: yes | no
Preserve / introduce / retire
Disposition: eliminated | contained | obstructed | unresolved
Invalid region eliminated / admission coverage / residual / proof
Reconsider when
```

The Working Set is ephemeral and grants no authority. Refresh it when the head,
Goal, applicability, selected theory, interpretation adequacy, owner set,
frontier/cut, or target changes. After implementation, the Git tree is the
realized construction.

## Architectural memory

Persist architecture where maintainers naturally encounter it: code and types,
executable tests, schemas and API contracts, an accepted specification, a PR
explanation, or a genuine long-lived ADR. Do not create an Actuating-private
source of truth. If the decision cannot be recovered from the repository,
improve repository legibility.
