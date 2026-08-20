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
falsifier, safety-adequacy argument and falsifier, Goal-adequacy evidence, and
diagnostic-exactness status.

Review Fold does not select the final theory, interpretation, frontier, cut, or
repair.

## Sound interpretation and diagnostic exactness

For candidate `K`, let:

```text
U_K
  concrete behaviors considered at K's sanctioned admission surfaces within the
  declared validity horizon

B_K subset U_K
  behaviors K actually sanctions or admits

alpha_K : U_K -> Omega
  K's interpretation into the selected semantic observation domain
```

The elimination proof requires:

```text
Totality
  alpha_K is defined for every u in U_K

Violation reflection
  Bad_L(u) -> Phi(alpha_K(u))

Abstract exclusion
  b in B_K -> not Phi(alpha_K(b))

Required-valid preservation
  every Goal-required valid behavior in the horizon belongs to B_K

Required-observation preservation
  every Goal-required observation remains available with accepted meaning
```

Totality and violation reflection make `Alpha` a sound abstraction of danger.
Abstract exclusion then proves that no sanctioned concrete behavior violates
`L`. Required-valid and required-observation preservation prevent the vacuous
architecture that rejects everything.

Diagnostic exactness is separate:

```text
Phi(alpha_K(u)) -> Bad_L(u)
```

Classify it as:

```text
exact | conservative-overapproximation | bounded | sampled | unknown
```

A conservative abstraction may reject safe optional behavior. That affects
permissiveness and candidate quality, not safety, provided every Goal-required
valid behavior and observation remains preserved.

A theory or candidate is not architecture-comparable merely because an
interpretation function has been named. State totality, reflection, abstract
exclusion, Goal preservation, diagnostic exactness, evidence strength, lost or
intentionally excluded behavior, and falsifiers.

## Theory synthesis and adjudication

Invoke one bounded `$metanoetic` challenge before finalization when `Theta_0` is
detection-shaped, enumerative, representation-bound, contradicted by a same-law
witness, owner/topology-captive, one of several materially different plausible
explanations, or based on a domain/interpretation that underapproximates danger
or erases a Goal-required observation.

The challenger may revise the semantic domain, interpretation, law,
state-versus-trace formulation, predicate, admission semantics, owner,
frontier/cut, claim strength, or falsifier.

Then **OPERATE ARCHITECTONICALLY**. Compare the ordinary and challenger theories
by witness coverage, law provenance, representation independence, safety
adequacy, Goal adequacy, diagnostic exactness, causal and conceptual compression,
canonical ownership, lawful construction/elimination/composition, admission
coverage, falsifiers, and proof surface.

Return:

```text
retain | replace | combine | split | unresolved
```

Select the least discriminating sound abstraction that reflects every violation
and preserves every required observation. Do not retain distinctions merely to
achieve diagnostic exactness when they provide no Goal-level or proof dividend.

## Architecture closure

For selected theory:

```text
Theta = (Omega, Alpha, L, Phi, A, O, C, Q)
```

`I(H)` is closed under the bug only when its incumbent interpretation is total
and violation-reflecting, every Goal-required valid behavior and observation is
preserved, and:

```text
for every behavior b sanctioned by A in I(H):
  not Phi(alpha_I(H)(b))
```

at strength `Q`. Violation reflection and abstract exclusion imply that no
sanctioned concrete behavior violates `L`. Diagnostic exactness is recorded but
is not a premise of this safety conclusion.

The existing authority and frontier/cut must preserve that concrete exclusion
without adding another independent guard, owner, representation, state
dimension, transition law, effect, compatibility/recovery mode, or escape path.

It is not closed when the correction requires:

- a different semantic domain, interpretation, or governing law;
- recovery of a violation-bearing or Goal-required distinction erased by the
  current domain;
- new state, transition, ordering, effect, authority, custody, or admission;
- new representation, interpreter, handler, observation, compatibility, retry,
  cancellation, timeout, or recovery semantics;
- structural removal of a bypass, competing owner, or obsolete representation;
- another downstream check while the invalid family remains admitted;
- a multi-frontier cut absent from the incumbent; or
- a live witness or candidate that falsifies the selected theory, safety
  adequacy, or Goal adequacy.

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
partial or violation-erasing interpretation
required-valid or required-observation loss
live dominated residue
smaller correctness-non-dominated candidate
incoherent incumbent model
selected counterexample theory or safety claim falsified by a witness/candidate
```

A false-positive abstract classification downgrades diagnostic exactness but does
not alone reopen a sound, Goal-adequate architecture.

Diff size, file proximity, elapsed time, bug/test/retry count, reviewer
preference, and abstract vocabulary do not establish reconsideration.

## Candidate compilation

1. Freeze the incumbent-independent premise basis with `$first-principles`.
2. Derive `Theta_0` and `Alpha_0` from Review Fold evidence and the incumbent.
3. Run one bounded `$metanoetic` challenge when its trigger is live.
4. **OPERATE ARCHITECTONICALLY** to adjudicate the theory and sound abstraction.
5. Finalize one theory, interpretation contract, frontier/cut, falsifiers,
   diagnostic-exactness status, and claim strength.
6. Ask `$universalist` for repository-native candidates. Require each candidate
   to interpret its declared comparison universe into the selected `Omega`,
   establish totality and violation reflection, exclude `Phi` from sanctioned
   behavior, preserve every Goal-required valid behavior and observation, and
   classify diagnostic exactness. Require the same Goal, family, admission
   semantics, compatibility, effects, and resource constraints.
7. Permit one bounded co-refinement if a candidate exposes a materially simpler,
   more representation-independent, more sound, or more causally adequate
   theory. Return once to architectonic adjudication; do not rerun Metanoetic on
   the unchanged decision surface.
8. Ask `$reduce` to challenge unearned factors, witness-enumerating predicates,
   violation-erasing abstractions, unnecessary precision, compensating guards,
   and detection movement.
9. Establish the correctness Pareto frontier from explicit relation evidence.
   Exclude candidates with partial, unknown, or violation-erasing interpretations
   or with failed Goal adequacy. Do not exclude a sound candidate solely because
   diagnostic exactness is conservative or unknown.
10. Among safety- and Goal-equivalent candidates, compare accepted valid-behavior
    coverage, diagnostic exactness, conceptual compression, proof burden, and
    realization cost; select the least costly effective realization and preserve
    material incomparability.
11. State the selected theory, safety-adequacy and Goal-adequacy arguments,
    diagnostic-exactness status, architecture delta, falsifiers, evidence
    strength, and proof before mutation.

Compare candidates by:

```text
required laws and observations
total violation-reflecting interpretation into selected Omega
abstract exclusion of Phi from sanctioned behavior
Goal-required valid behaviors retained
correctness-bearing distinctions retained
optional safe behavior conservatively excluded
sanctioned admission and frontier/cut coverage
semantic ownership and derived guards
representations, escape paths, compatibility, and migration
retirements and residual proof burden
diagnostic exactness, proof strength, resources, and operational cost
```

A candidate cannot win by omitting an orthogonal obligation, merely moving
detection, abstracting away evidence of invalidity, or rejecting required valid
behavior.

## One bounded co-refinement

Universalist may return a candidate theory or interpretation delta:

```text
accidental incumbent coordinate
proposed semantic domain or law
witness and candidate interpretations
safety-adequacy and Goal-adequacy arguments
diagnostic-exactness status and counterexample
predicted sibling counterexamples
falsifiers
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
Comparison universe U / sanctioned behavior B
Interpretation totality / violation reflection / abstract exclusion
Required-valid behavior / required observations preserved
Diagnostic exactness / optional safe behavior excluded
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
Goal, applicability, selected theory, safety adequacy, Goal adequacy, owner set,
frontier/cut, or target changes. After implementation, the Git tree is the
realized construction.

## Architectural memory

Persist architecture where maintainers naturally encounter it: code and types,
executable tests, schemas and API contracts, an accepted specification, a PR
explanation, or a genuine long-lived ADR. Do not create an Actuating-private
source of truth. If the decision cannot be recovered from the repository,
improve repository legibility.
