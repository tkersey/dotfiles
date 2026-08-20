# Live Closure

Closure is a current judgment over owner facts, not stored workflow state.

Let:

```text
G = current accepted Goal
H = exact clean Git head and tree
V = exact validation results bound to H
R = exact CAS review receipts bound to H and the current review context
P = current Ship/provider publication evidence
F = current applicable Review Fold
A = current architecture reconciliation judgment
S = selected counterexample theory, interpretation, topology, and correctness delta
```

Then:

```text
Close(G, H, V, R, P, F, A, S)
  -> continue | ready-to-ship | complete | blocked
```

## Bug-driven closure

For selected theory:

```text
Theta = (Omega, Alpha, L, Phi, A_s, O, C, Q)
```

and selected candidate `K`, let `B_K` be its sanctioned concrete behaviors and
`alpha_K : B_K -> Omega` its interpretation.

An `eliminated` claim requires, at strength `Q`:

```text
Totality
  for every b in B_K, alpha_K(b) is defined

Violation reflection
  Bad_L(b) -> Phi(alpha_K(b))

Invalidity precision
  Phi(alpha_K(b)) -> Bad_L(b)

Required-observation preservation
  alpha_K collapses only distinctions irrelevant to L and every Goal-required
  observation

Abstract exclusion
  for every b in B_K, not Phi(alpha_K(b))
```

Therefore:

```text
for every b in B_K:
  not Bad_L(b)
```

This is the concrete correctness consequence. Without interpretation adequacy,
abstract exclusion is not evidence that the architecture excludes concrete
incorrectness.

Use one disposition:

```text
eliminated
  concrete L-violations are excluded through an adequate interpretation at Q

contained
  current risk is bounded, but the family, interpretation, or external residual
  remains admitted or only partially characterized

obstructed
  required exclusion or adequate interpretation is evidenced as unavailable

unresolved
  theory, interpretation, ownership, coverage, or proof is unknown
```

Containment is not correct by construction. It may satisfy only a Goal that
explicitly accepts the residual, owner, observation, and failure behavior.

The selected theory must include semantic domain, interpretation family, law
and provenance, witness interpretation, predicate, sanctioned admission
semantics, validity horizon, owner model, frontier/cut, claim strength,
family-theory falsifier, and interpretation-adequacy falsifier.

When a Metanoetic challenger was required, closure needs a resolved architectonic
disposition. When a candidate exposed a material theory or interpretation delta,
closure needs the one bounded co-refinement adjudicated. A candidate may not
silently redefine the family or erase the violation it claims to eliminate.

The theory or interpretation remains open when evidence establishes any
falsifier, including:

```text
same-law witness outside Phi
Phi-member not violating L
sanctioned path omitted from A_s
required valid observation classified as invalid
sanctioned behavior without an interpretation
concrete L-violation mapped outside Phi
two L-distinct behaviors mapped to one Omega observation
Goal-required observation erased by Alpha
candidate behavior not interpretable into Omega
selected owner lacks authority for L
simpler live theory with equal or stronger proof
```

## Local implementation

`$actuating implement` is locally complete only when:

- the Goal permits mutation and its local outcome is met;
- the current tree realizes the selected target and retirements;
- required validation passes on the exact head;
- every applicable witness is rejected through sanctioned paths and interpreted
  into the selected `Omega`;
- the selected theory and interpretation survive their falsifiers;
- candidate comparisons use adequate interpretations into the same `Omega`;
- every `eliminated` family has semantic-domain, interpretation-totality,
  violation-reflection, invalidity-precision, observation-preservation, law,
  predicate, admission, validity-horizon, claim-strength, frontier/cut, and
  escape-path proof;
- every `contained` residual is authorized, owned, observable, tested, and not
  described as eliminated;
- primary and derived enforcement remain coherent;
- no requested local operation or blocker remains.

Publication and closure-grade review are required only when the Goal says so.

## Final closeout

Final `complete` additionally requires:

- required Ship/provider state matches the exact head;
- review context binds the exact Goal, base, head, Review Contract, and optional
  pre-review Ship observation;
- all auxiliaries have terminal semantic verdicts;
- five consecutive distinct standard attempts are clean on the unchanged head;
- every finding is classified and no applicable accepted finding remains;
- no hotspot remains answered only by compensating detection or a law-erasing
  semantic quotient;
- no detection-shaped, enumerative, representation-bound, or interpretation-
  inadequate theory remains unchallenged while a material alternative is live;
- every required architectonic adjudication and co-refinement is complete;
- historical witness provenance and current applicability remain distinct;
- no later evidence invalidates Goal, theory, interpretation, architecture,
  realization, validation, publication, or review.

A non-publicly complete implementation is `ready-to-ship`.

## Blockers

Return `blocked` for:

- missing source or repository authority;
- unresolved semantic domain, interpretation, law, predicate, admission
  semantics, owner, frontier/cut, theory falsifier, or claim strength;
- unknown or failed interpretation totality, violation reflection, invalidity
  precision, or required-observation preservation for an elimination claim;
- a required Metanoetic challenge not performed;
- unresolved architectonic adjudication;
- a live candidate theory or interpretation delta not co-refined;
- unsupported recurrence, independence, dominance, adequacy, or elimination
  claims;
- validation, realization, retirement, publication, or review failure;
- an unauthorized containment residual;
- stale or unresolvable CAS evidence.

## Invalidation

No event is needed:

```text
Goal changed -> recompile
head changed -> rerun applicability, validation, and review
new bug/finding -> Review Fold, theory synthesis, hotspot analysis, closure reopen
theory or adequacy falsifier established -> architectonic adjudication reopens
candidate exposes theory/interpretation delta -> bounded co-refinement reopens
owner/admission changed -> recompile
publication/review context changed -> prior evidence no longer matches
```

Actuating reports the live verdict and current premises. It does not materialize
a closure receipt.
