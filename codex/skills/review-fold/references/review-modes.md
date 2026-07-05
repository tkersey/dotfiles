# Review Loop Modes

The review loop is a reducer, not a patch queue.

## Workflow defaults

`$actuating review ...` defaults to `review-closeout`.

Explicit review mode names carry the mutation rule:

```text
triage -> classify findings and stop without implementation
remediation-plan -> produce resolution inputs and stop without implementation
review-closeout -> hand accepted liabilities to resolution, then prove closure
```

`review-closeout` still preserves no-code dispositions. A review with ten
findings may close as:

```text
2 rejected
2 proof-only
1 follow-up
1 ask-human
3 accepted under one structural kernel
1 accepted under a proven point kernel
```

It must not become ten local patches.

## Finding dispositions

| Disposition | Meaning | Code? |
|---|---|---|
| `reject` | False, duplicate, out-of-scope, or incompatible with the accepted goal. | No |
| `proof-only` | The right answer is evidence, not code. | No by default |
| `accepted-liability` | A valid in-scope liability may be considered by the resolution fold. | Advisory only |
| `ask-human` | The review introduces a product/API/compatibility decision. | No |
| `follow-up` | Valid but outside the intended change. | No in current PR |
| `blocked` | Validity, scope, source, current artifact, or kernel status is unclear. | No |

## Kernel status

| Status | Meaning | Resolution implication |
|---|---|---|
| `none` | No in-scope code liability remains. | No code |
| `point` | One owner boundary is enough and `point_safety: proven`. | May become one bounded work node |
| `structural` | Same-family pressure needs one normal-form owner correction. | Must not split by comment |
| `unknown` | The fold cannot prove point versus structural. | Inspect, ask, or block before mutation |

## Reabstraction tests

Choose `kernel_fold.status: structural` when at least two are true:

- multiple comments mention the same state, transition, or boundary;
- fixes would add similar guards/helpers in multiple files;
- a test per comment would be wound-specific;
- the change would broaden tolerance for invalid internal state;
- a canonical owner can prevent the class once;
- proof becomes simpler after the abstraction.

## Minimal but right

The minimal correct response may be:

- a short proof note;
- a no-code rejection;
- a proven point kernel;
- a structural kernel;
- a human-owned decision;
- a blocker because the kernel status is unknown.

It is not always the smallest diff.
