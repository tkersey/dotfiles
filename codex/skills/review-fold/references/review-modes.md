# Review Loop Modes

The review loop is a reducer, not a patch queue.

## Workflow defaults

`$actuating review ...` defaults to `review-closeout`.

Explicit review mode names carry the mutation rule:

```text
triage -> classify findings and stop without implementation
remediation-plan -> produce the fix plan and stop without implementation
review-closeout -> fix accepted liabilities and prove closure
```

`review-closeout` still preserves no-code dispositions. A review with ten findings may close as:

```text
2 rejected
2 proof-only
1 follow-up
1 ask-human
3 fixed by one refactor-kernel
1 minimal local fix
```

It must not become ten local patches.

## Finding dispositions

| Disposition | Meaning | Code? |
|---|---|---|
| `reject` | False, duplicate, out-of-scope, or incompatible with the accepted goal. | No |
| `proof-only` | The right answer is evidence, not code. | No by default |
| `minimal-fix` | One valid liability has one owner-correct repair. | Yes |
| `refactor-kernel` | Several findings share one missing abstraction, owner, or invariant. | Yes, one kernel |
| `ask-human` | The review introduces a product/API/compatibility decision. | No |
| `follow-up` | Valid but outside the intended change. | No in current PR |

## Reabstraction tests

Choose `refactor-kernel` when at least two are true:

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
- a one-line owner fix;
- a small adapter;
- a deliberate reabstraction.

It is not always the smallest diff.
