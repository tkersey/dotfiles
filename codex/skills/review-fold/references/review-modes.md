# Review Loop Modes

The review loop is a reducer, not a patch queue.

## Workflow defaults

`$actuating review ...` defaults to `review-closeout`.

Explicit review mode names carry the mutation rule:

```text
triage -> classify findings and stop without implementation
remediation-plan -> produce resolution inputs and stop without implementation
review-closeout -> hand refactor-kernel findings to resolution, then prove closure
```

`review-closeout` still preserves no-code dispositions. A review with ten
findings may close as:

```text
2 rejected
2 proof-only
1 follow-up
1 ask-human
4 folded under one refactor-kernel
```

It must not become ten local patches.

## Finding dispositions

| Disposition | Meaning | Code? |
|---|---|---|
| `reject` | False, duplicate, out-of-scope, or incompatible with the accepted goal. | No |
| `proof-only` | The right answer is evidence, not code. | No by default |
| `ask-human` | The review introduces a product/API/compatibility decision. | No |
| `follow-up` | Valid but outside the intended change. | No in current PR |
| `blocked` | Closure or direct implementation is blocked by unclear state, unresolved refactor-kernel pressure, or unknown quarantine. | No |

## Kernel status

| Status | Meaning | Resolution implication |
|---|---|---|
| `none` | No in-scope code liability remains. | No code |
| `refactor-kernel` | Material pressure needs one owner-boundary kernel account. | May become one owner-level work node |
| `unknown` | The fold cannot prove whether a material kernel is required. | Inspect, ask, block, branch-race, or reclassify before mutation |

## Reabstraction tests

Choose `kernel_fold.status: refactor-kernel` when at least two are true:

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
- a refactor-kernel with `boundary_proof: proven`;
- a human-owned decision;
- a blocker because the kernel status is unknown.

It is not always the smallest diff.
