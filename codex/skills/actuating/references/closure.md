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
S = current counterexample topology and correctness delta when bug-driven
```

Then:

```text
Close(G, H, V, R, P, F, A, S)
  -> continue | ready-to-ship | complete | blocked
```

## Bug-driven closure vocabulary

Use one current disposition for each selected family:

```text
eliminated
  the predicate-defined family is excluded from the sanctioned admission
  relation over the declared domain at the stated claim strength

contained
  the current witness or risk is bounded, but the family or an external residual
  remains admitted

obstructed
  current evidence establishes that the required exclusion is unavailable or
  inadmissible under accepted constraints

unresolved
  family, applicability, ownership, frontier/cut coverage, or proof strength is
  unknown
```

`contained` is not correct by construction. It may satisfy a deliberately
bounded Goal only when current authority explicitly accepts the residual,
owner, observation, and failure behavior.

## Local implementation

`$actuating implement` is locally complete only when:

- the accepted Goal permits mutation and its local terminal outcome is met;
- the current tree realizes the selected target architecture;
- every required retirement is absent or deliberately successor-mapped;
- every required validation command passes on the exact current head;
- every accepted currently applicable witness is rejected through sanctioned
  paths;
- every `eliminated` family has a declared predicate, domain, sanctioned
  admission relation, claim strength, and proof covering the selected frontier
  or admission cut;
- every `contained` residual is explicitly accepted by the Goal, owned,
  observable, tested, and not described as eliminated;
- every material escape path selected for retirement is absent;
- required primary and derived enforcement sites remain coherent;
- no requested local operation remains open;
- no applicable current blocker remains.

It requires neither publication nor closure-grade review unless the accepted
Goal explicitly requires them.

## Final closeout

Final `complete` additionally requires:

- the exact current head is publicly represented by Ship when publication is
  required;
- the current review context binds the exact Goal, base, head, Review Contract,
  and optional pre-review Ship observation;
- all four auxiliary requests have current terminal semantic verdicts;
- five consecutive distinct standard attempts are clean for the exact unchanged
  head;
- every finding has been classified by `$review-fold`;
- no applicable accepted finding remains unresolved;
- no hotspot remains answered only by another compensating downstream guard
  when an admissible owner- or cut-level exclusion was selected;
- historical witnesses retain their original provenance and have current
  applicability judgments;
- no material later evidence invalidates the Goal, architecture, realization,
  validation, publication, or review result.

A current implementation satisfying every non-public predicate but not yet
published is `ready-to-ship`.

## Blockers

Return `blocked` for:

- missing source authority;
- unknown or conflicting current repository identity;
- architecture underdetermination requiring external choice;
- missing witness provenance or current applicability material to the decision;
- an unresolved family predicate, domain, sanctioned admission relation, owner
  status, frontier, or admission cut;
- family, recurrence, or witness-independence claims unsupported by current
  owner evidence;
- unsupported correctness-dominance or family-elimination claims;
- applicable evidence that cannot be classified safely;
- validation failure;
- incomplete family exclusion, escape-path retirement, realization, or
  retirement;
- a containment residual not explicitly accepted by current authority;
- publication mismatch;
- missing or stale review evidence;
- exhausted request-local review recovery;
- any claimed review count that cannot be resolved to exact CAS receipts.

## Invalidation

No invalidation event is needed:

```text
Goal changed -> recompile
head changed -> rerun head-bound applicability, validation, and review
review context changed -> prior request bindings do not match
publication changed -> provider readback does not match
new bug or finding arrived -> Review Fold, semantic-hotspot analysis,
                              and architecture closure reopen
family predicate, owner set, or admission relation changed -> recompile
```

Actuating reports the live verdict and its current premises in the user-facing
closeout. It does not materialize a closure receipt.
