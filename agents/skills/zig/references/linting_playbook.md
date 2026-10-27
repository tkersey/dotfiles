# Zig formatting and repository-pinned lint

Use for formatting, syntax checks and the project's lint integration. Select the
check that answers the task. A formatting-only change does not automatically
require a build/test cycle; honor repository-required checks and investigate any
semantic uncertainty introduced by the diff.

## Built-in checks

For a focused edit, target the authorized files:

```bash
zig fmt --check path/to/file.zig
zig ast-check path/to/file.zig
```

Use `zig fmt` to apply canonical formatting and inspect its diff. Match the selected
compiler; its formatter can migrate syntax as well as layout. `zig ast-check`
accepts Zig source, not `build.zig.zon`, and does not replace full semantic analysis
or integration tests. Use project build/test checks when those are the question,
not simply because a formatter ran. Whole-tree checks and scans are appropriate
when the requested scope or project policy calls for them. Exclude generated,
vendor, cache and custom package locations where they are outside that scope.

## Steering `zig fmt`

The formatter is not configurable like a style engine, but source syntax can
communicate useful grouping. Preserve meaning rather than adding layout-only
noise.

A trailing comma where the grammar permits an optional final comma requests
expanded layout. Removing it permits collapsing when the construct fits; comments
and line length can still prevent a single line. Arrays can use a trailing comma
and an intentional first-row break to request columnar layout. Compose separately
shaped chunks with `++` where that improves readability. Emit trailing commas in
generated lists intended to stay one-item-per-line.

```zig
// Without a trailing comma, formatting can collapse this call.
f(1, 2,
    3);

// With a trailing comma, formatting expands the arguments.
f(1, 2,
    3,
);
```

For differently shaped array chunks:

```zig
try run(&(.{ "aws", "s3", "sync", path, url } ++ .{
    "--include",            "*.html",
    "--include",            "*.xml",
    "--metadata-directive", "REPLACE",
    "--cache-control",      "max-age=0",
}));
```

These are layout examples, not instructions to run the depicted command. Use real
line/doc comments for meaning rather than dummy anchors. Inspect whether the
selected formatter preserved the intended grouping:

```bash
zig fmt path/to/file.zig
git diff -- path/to/file.zig
zig fmt --check path/to/file.zig
```

Formatting acceptance proves neither program behavior nor every version-migration
contract. See [testing](testing_failure_discovery_playbook.md) when semantic
validation is needed.

## Repository lint integration

Use the existing pinned [zlinter](https://github.com/kurtwagner/zlinter) integration
when the repository has one. Inspect its compatible revision, build wiring and
supported arguments. Do not install the historical `0.16.x` branch into a 0.17
project or assume `master` is a compatible stable release. A compiler upgrade does
not authorize an unrelated dependency upgrade or a new lint framework.

Read the actual rule semantics, especially deprecated APIs, swallowed errors,
cleanup and exhaustive switching. Enabling every rule can create pedantry and
conflict with deliberate designs; select rules for the project's requirements.
An existing project may expose commands such as:

```bash
zig build lint
```

Pass warning limits, rule selectors or fix flags only when the pinned tool and
build step expose them. Preserve unrelated working-tree changes. For an authorized
fix, scope it to intended files and inspect the resulting diff; a dirty working
tree alone is not a blocker. Re-read overlapping changes rather than assuming a
clean tree or backup authorizes overwriting them.
