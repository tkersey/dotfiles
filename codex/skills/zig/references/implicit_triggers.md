# Zig activation and reference selection

Use `$zig` when the requested work requires Zig-specific expertise, explicitly
or implicitly. A Zig repository alone does not activate a language audit for an
unrelated prose, Git, or operational task.

Direct examples include implementing or reviewing `.zig` code, migrating a Zig
API, diagnosing `zig build`, choosing a comptime representation, or profiling a
Zig executable. `std.Io`, `std.process.Init`, `@typeInfo`, `anytype`, generated
types, error unions, allocators, C ABI, atomics, and cache/toolchain flags can help
identify relevant expertise when they occur in the actual task.

Generic words such as `proof`, `manifest`, `report`, `commit`, `rollback`,
`performance`, and `recursion` do not activate the skill on their own. A mention
of Tiger Style does not establish either Zig context or a style violation.

Once active, consult the root reference map selectively. Use ownership guidance
for an escaping borrow, transition guidance for a fallible state change, verifier
guidance for hostile input, and evidence guidance when a validation assumption
may have changed. Construction and routine edits are first-class uses; they do
not need to fit a failure family.

No implicit activation requires ZSR-v1, a specialist, a resource sketch, a
family contract packet, or a second final report. Structured artifacts are for
explicit requests or actual consumers. Compose with other skills only when their
own triggers apply; the receiving workflow owns execution and closure.
