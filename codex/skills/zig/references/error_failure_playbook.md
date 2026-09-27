# Zig errors, failure paths, and ownership

Use for fallible APIs, error unions, `try`/`catch`, `errdefer`, boundary mapping,
state mutation, publication, or cleanup. Identify the API's error categories,
ownership and advertised [failure guarantee](atomic_transition_playbook.md).

| Category | Examples | Handling |
| --- | --- | --- |
| Domain/protocol | Invalid header, version, or state | Precise error; caller can discriminate. |
| Resource | OOM, no space, capacity, depth/work budget | Propagate; inject representative failures. |
| Environment | File, permission, network | Preserve diagnostics; add context at the integration boundary. |
| Programmer bug | Impossible internal state | Assert/unreachable only with a real invariant. |
| Foreign/system | errno or status | Translate once at a boundary, including unknown statuses. |

Prefer named or inferred error sets within libraries. Widen to `anyerror` only at
a genuine integration/polymorphic boundary, not to hide an unclear contract.
Do not convert ordinary domain/resource failures into panics or use vague errors
to conceal a bug.

```zig
const ParseError = error{ Empty, InvalidChar, Overflow };
```

## Propagation and cleanup

At a consequential fallible call, decide whether propagation is correct, whether
translation belongs here, which resources have been acquired, and which state is
already observable. `catch` must not discard useful evidence. A runtime budget
that can be exhausted is not a justification for `catch unreachable`.

Use `errdefer` for failure cleanup and disarm it only after a valid ownership
transfer. Freeing memory does not restore counters, indexes, journals or events.
Conversely, an API advertising partial progress does not require fictional
transactional rollback. The transition playbook owns that distinction.

For a strong guarantee, prepare fallible work before commit or supply complete,
non-failing rollback. For irreversible effects, expose commit/recovery status and
retry/idempotency semantics. Do not return an ordinary "nothing happened" error
when state has committed but publication failed.

## Boundary mapping

Keep raw status/errno -> boundary-specific errors -> core domain behavior in one
place. Preserve the detail needed to diagnose environment failures. Do not identify
all `PermissionDenied` results as cache failures; consult the actual diagnostic.

## Tests and reporting

Exercise success, relevant domain/resource errors, partial acquisition cleanup,
and ownership transfer exactly once. `std.testing.checkAllAllocationFailures`
helps with allocation failures but does not cover I/O, callback, publication, or
other non-allocation failures. Add targeted fail points where consequential.

For strong guarantees, compare the full advertised pre-state with post-state.
For other guarantees, test valid continued use, reported partial progress or
recovery according to the contract. Tests should establish behavior, not merely
freeze incidental configuration booleans or mirror the implementation.

Report meaningful error-set changes, boundary translations, cleanup/commit
behavior, executed checks, and unresolved risk in the receiving workflow's format.
Use [evidence context](evidence_context_playbook.md) for reuse and unavailable lanes.
