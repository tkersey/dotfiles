# Zig 0.16 explicit I/O and effect-injection playbook

Use this playbook when code touches `std.Io`, `std.process.Init`, process args/env, filesystem paths, randomness, time, logging, networking, task cancellation, or tests that need deterministic effects.

## Expert objective

In Zig 0.16, I/O and other sources of nondeterminism should be explicit capabilities. For each effectful API, state:

1. which effects it needs;
2. which parameters/context provide those effects;
3. how the effect is faked or constrained in tests;
4. whether operations may block or be canceled;
5. whether args/env/current path are captured once or queried repeatedly.

## Capability table

| Effect | Preferred API shape |
| --- | --- |
| Allocation | `allocator: std.mem.Allocator` or context field. |
| I/O | `io: std.Io` or context field. |
| Environment | parsed config or `*const std.process.Environ.Map`. |
| Args | parsed options, not global args lookup in library code. |
| Filesystem | explicit dir/path/preopen/capability. |
| Time | injectable clock/time source when tests need determinism. |
| Randomness | injectable RNG or entropy source. |
| Logging | explicit logger/writer or well-scoped `std.log` use. |
| Cancellation | task/group lifetime and cancellation ownership documented. |

## `main` design

Application `main` is the integration boundary. It should usually:

- accept `std.process.Init` when it needs allocator, I/O, args, env, arena, or preopens;
- parse args/env into a config struct;
- construct top-level allocator and I/O capabilities;
- pass capabilities into application logic;
- keep library code free of hidden process globals.

Library functions should not reach into process args/env. Accept the already-parsed value or an explicit environment map.

## Context object pattern

```zig
const AppContext = struct {
    allocator: std.mem.Allocator,
    io: std.Io,
    config: Config,
};

pub fn run(ctx: AppContext) !void {
    // Effectful operations are visible through ctx.
}
```

Use a context when many functions share the same effect set. Keep it small enough that ownership and lifetime remain clear.

## Testing effects

Use test-specific capabilities when available:

- `std.testing.allocator` for allocation;
- `std.testing.io` for I/O;
- in-memory buffers for writers/readers;
- fixed config objects instead of env lookups;
- deterministic RNG seeds;
- bounded timeouts for async/concurrent tests.

Do not let tests silently depend on the developer machine's cwd, env, locale, network, or time unless the test is explicitly an integration test.

## Blocking and cancellation

When an API may block:

- accept `std.Io` explicitly;
- state whether callers can cancel the work;
- tie spawned tasks to a group/lifetime;
- close files/resources on cancellation;
- avoid borrowed data escaping into tasks after caller scope exits.

For one-off migration work, constructing a local `Io.Threaded` may unblock progress, but prefer passing `Io` through the API as a design improvement.

## Args/env/current path migration

Zig 0.16 moved process args/env toward `std.process.Init` and explicit maps. Review code that calls global args/env/current-directory helpers and migrate to:

- parsed config from `main`;
- `init.environ_map` or explicit `Environ.Map`;
- `std.process.currentPath*` with `io` where required;
- pure path functions that receive cwd/env inputs.

## Review checklist

- Effectful library APIs accept explicit capabilities or context.
- `main` is the boundary that captures args/env/preopens.
- Tests use fake/constrained capabilities.
- Blocking and cancellation behavior is documented.
- Async tasks do not borrow data past its lifetime.
- Local `Io.Threaded` workarounds are not left in core library APIs.
- Environment and current-path queries are not hidden inside business logic.
