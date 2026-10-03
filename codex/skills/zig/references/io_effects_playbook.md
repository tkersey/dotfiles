# Zig explicit I/O and effect injection

Use for `std.Io`, process initialization, filesystem, environment/arguments,
networking, time, randomness, logging or cancellation. Make consequential effects
and their lifetime visible at the boundary where they are used. Select the shape
that fits the API; a small function does not need an effects report or context
framework.

Zig 0.17 retains the explicit-capability style introduced in 0.16. Check exact
signatures and initialization fields in the selected compiler's stdlib and the
repository, rather than copying a historical process/global-I/O recipe. Use the
[release migration map](zig_0_17_migration.md) for version-sensitive changes.

## Capability shapes

| Effect | Useful interface |
| --- | --- |
| Allocation | Caller-provided `std.mem.Allocator` with an explicit cleanup owner. |
| I/O | `std.Io` parameter or a context that carries the needed capability. |
| Arguments/environment | Parsed options/config, or an explicit environment map when lookup itself is needed. |
| Filesystem | Explicit directory, path or preopen contract appropriate to the operation. |
| Time | Clock/deadline input or injectable source when determinism matters. |
| Randomness | Explicit seeded RNG or entropy capability according to the security contract. |
| Logging | Writer/logger or scoped `std.log` with understood configuration. |
| Cancellation | A task/group owner and a completion/cleanup contract. |

Application `main` is usually the integration boundary: use `std.process.Init`
when appropriate, interpret arguments/environment once where consistent with the
application semantics, and pass required inputs to library logic. Preserve deliberate
live configuration semantics rather than freezing values solely to follow a recipe.
An explicit environment parameter can be appropriate; repeated hidden process-global
lookups should not determine unrelated library behavior.

Use a small context when several functions genuinely share capabilities. Prefer
ordinary parameters when clearer. A context does not extend borrowed lifetimes,
and passing an I/O object does not itself establish a security sandbox or prove
that every transitive effect is constrained.

## Resource ownership and task lifetime

Understand which operations may block or be canceled, who owns files/sockets,
and which effects may have occurred before failure. A locally constructed
`Io.Threaded` backend can be legitimate at an application or test boundary; do not
silently instantiate one in a library merely to avoid accepting the caller's I/O
capability. Its lifetime must cover all users and outstanding work.

Tie spawned work to a clear owner. Follow the actual group API to cancel/await or
otherwise establish completion on success and failure before destroying borrowed
inputs or shared resources. A cancellation request alone need not establish
completion. Cleanup does not undo partial output or irreversible side effects;
preserve the advertised failure guarantee and retry/idempotency behavior.
See [concurrency](atomics_concurrency_playbook.md), [ownership](memory_ownership_playbook.md)
and [state transitions](atomic_transition_playbook.md).

## Deterministic tests

Choose substitutes that exercise the contract: `std.testing.allocator`, the
selected toolchain's test I/O facility, fixed readers/writers, explicit config,
seeded non-security RNGs, controlled clocks and bounded waits where useful.
Test I/O is not automatically in-memory or hermetic. Keep external filesystem,
network, environment, locale and time dependencies explicit in integration tests.
Do not replace required cryptographic entropy with a deterministic production RNG.

Exercise meaningful acquisition, operation, partial-progress and cancellation
failures, not only allocation failure. Check that borrowed storage remains live
until tasks complete and that cleanup occurs exactly once. Preserve intentional
integration coverage; do not add mocks or a universal effect framework merely to
make every operation use the same testing technique.
