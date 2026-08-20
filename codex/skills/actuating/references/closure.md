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

and selected candidate `K`, let:

```text
U_K
  concrete behaviors considered at K's sanctioned admission surfaces within the
  declared validity horizon

B_K subset U_K
  behaviors K actually sanctions or admits

alpha_K : U_K -> Omega
  K's semantic interpretation
```

An `eliminated` claim requires, at strength `Q`:

```text
Totality
  for every u in U_K, alpha_K(u) is defined

Violation reflection
  Bad_L(u) -> Phi(alpha_K(u))

Abstract exclusion
  for every b in B_K, not Phi(alpha_K(b))

Required-valid preservation
  every Goal-required valid behavior in the declared horizon remains in B_K

Required-observation preservation
  every Goal-required observation remains available with its accepted meaning
```

Therefore:

```text
for every b in B_K:
  not Bad_L(b)
```

This is the concrete safety consequence. It does not require the abstraction to
classify every safe behavior precisely.

Track diagnostic exactness separately:

```text
Phi(alpha_K(u)) -> Bad_L(u)
```

with one status:

```text
exact | conservative-overapproximation | bounded | sampled | unknown
```

Diagnostic exactness determines whether `Phi` has false positives over `U_K`.
It affects permissiveness, explanation, and candidate comparison. Its absence
does not weaken the elimination proof when totality, violation reflection,
abstract exclusion, and Goal adequacy hold.

Use one disposition:

```text
eliminated
  concrete L-violations are excluded from sanctioned behavior at Q

contained
  current risk is bounded, but concrete invalidity, path/reflection coverage, or
  an external residual remains admitted or only partially characterized

obstructed
  required exclusion or a sound Goal-adequate interpretation is evidenced as
  unavailable

unresolved
  theory, safety interpretation, Goal adequacy, ownership, coverage, or proof is
  unknown
```

Conservative rejection of optional safe behavior is not residual incorrectness.
Containment is not correct by construction and may satisfy only a Goal that
explicitly accepts the residual, owner, observation, and failure behavior.

The selected theory must include semantic domain, interpretation family, law
and provenance, witness interpretation, predicate, sanctioned admission
semantics, validity horizon, owner model, frontier/cut, claim strength,
family-theory falsifier, safety-adequacy falsifier, Goal-adequacy evidence, and
diagnostic-exactness status.

When a Metanoetic challenger was required, closure needs a resolved architectonic
disposition. When a candidate exposed a material theory or interpretation delta,
closure needs the one bounded co-refinement adjudicated. A candidate may not
silently redefine the family or erase the violation it claims to eliminate.

The theory or safety interpretation remains open when evidence establishes any
material falsifier, including:

```text
same-law witness outside Phi
sanctioned path omitted from A_s
sanctioned behavior without an interpretation
concrete L-violation mapped outside Phi
Goal-required valid behavior excluded
Goal-required observation erased by Alpha
candidate behavior not interpretable into Omega
selected owner lacks authority for L
simpler live theory with equal or stronger proof
```

A `Phi` member that does not violate `L` falsifies diagnostic exactness. It
downgrades exactness to a conservative or weaker status; by itself it does not
falsify safety elimination.

## Local implementation

`$actuating implement` is locally complete only when:

- the Goal permits mutation and its local outcome is met;
- the current tree realizes the selected target and retirements;
- required validation passes on the exact head;
- every applicable witness is rejected through sanctioned paths and interpreted
  into the selected `Omega`;
- the selected theory and safety interpretation survive their falsifiers;
- candidate comparisons use total, violation-reflecting interpretations into the
  same `Omega`;
- every `eliminated` family has semantic-domain, interpretation-totality,
  violation-reflection, abstract-exclusion, required-valid-preservation,
  observation-preservation, law, predicate, admission, validity-horizon,
  claim-strength, frontier/cut, and escape-path proof;
- diagnostic exactness is classified without being mistaken for safety;
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
  semantic abstraction;
- no detection-shaped, enumerative, representation-bound, or safety-inadequate
  theory remains unchallenged while a material alternative is live;
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
- unknown or failed interpretation totality or violation reflection;
- unknown or failed required-valid-behavior or required-observation preservation;
- a required Metanoetic challenge not performed;
- unresolved architectonic adjudication;
- a live candidate theory or interpretation delta not co-refined;
- unsupported recurrence, independence, dominance, safety adequacy, Goal
  adequacy, or elimination claims;
- validation, realization, retirement, publication, or review failure;
- an unauthorized containment residual;
- stale or unresolvable CAS evidence.

Unknown or conservative diagnostic exactness is not itself a blocker when the
safety and Goal obligations above are established.

## Invalidation

No event is needed:

```text
Goal changed -> recompile
head changed -> rerun applicability, validation, and review
new bug/finding -> Review Fold, theory synthesis, hotspot analysis, closure reopen
theory or safety-adequacy falsifier established -> architectonic adjudication reopens
candidate exposes theory/interpretation delta -> bounded co-refinement reopens
owner/admission changed -> recompile
publication/review context changed -> prior evidence no longer matches
```

Actuating reports the live verdict and current premises. It does not materialize
a closure receipt.
