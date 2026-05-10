# Zig Linting Playbook

## Built-in checks

```bash
zig fmt --check .
find . -name '*.zig' \
  -not -path './zig-pkg/*' \
  -not -path './.zig-cache/*' \
  -not -path './zig-out/*' \
  -print0 | xargs -0 zig ast-check
```

Use `zig fmt` for canonical formatting and review the diff. Use `zig ast-check` only for `.zig` files; do not point it at `build.zig.zon`.

`zig fmt` has no style configuration, but it is still steerable through syntax-level layout cues. Before formatting, make the desired grouping explicit in the source; after formatting, review the diff to verify the formatter preserved the intended structure.

`zig ast-check` catches simple compile errors, but it is not a full semantic build. Follow with `zig build` and `zig build test`.

## Steering `zig fmt`

Use formatter steering when the desired layout communicates review or maintenance intent.

Durable controls:

- A trailing comma on a comma-separated construct, where Zig accepts an optional final comma, requests expanded multi-line layout after `zig fmt`.
- Removing the optional trailing comma permits `zig fmt` to collapse the construct when it fits. It does not guarantee one line if the content is too long or comments anchor the layout.
- For arrays and array literals, a trailing comma plus the first intentional line break can request columnar layout. `zig fmt` uses the first row width as the column shape and aligns later rows.
- Array concatenation with `++` can compose differently shaped chunks, such as a compact command prefix followed by aligned option/value rows.
- Line comments, doc comments, and block comments are layout anchors. Use real comments for meaning, not dummy comments just to pin a shape.
- Generated Zig should emit trailing commas for lists that should remain one-item-per-line as items are added, removed, or reordered.

### Trailing commas select compact vs expanded layout

```zig
// No trailing comma: `zig fmt` can collapse to one line.
f(1, 2,
    3);

// zig fmt:
f(1, 2, 3);

// Trailing comma: `zig fmt` expands one item per line.
f(1, 2,
    3,
);

// zig fmt:
f(
    1,
    2,
    3,
);
```

Use this to communicate whether the call is conceptually compact or whether each argument deserves its own row.

### Arrays can be shaped as columns

For arrays and array literals, a trailing comma plus the first intentional line break can request columnar layout. `zig fmt` uses the first row width as the column shape and aligns later rows.

```zig
const ids = .{ 1, 2, 3,
    4, 5, 6, 7, 8, 9, 10, 11,
};
```

For arrays whose prefix and suffix have different structure, compose chunks with `++` so each chunk gets an appropriate layout:

```zig
try run(&(.{ "aws", "s3", "sync", path, url } ++ .{
    "--include",            "*.html",
    "--include",            "*.xml",
    "--metadata-directive", "REPLACE",
    "--cache-control",      "max-age=0",
}));
```

Review protocol:

```bash
zig fmt path/to/file.zig
git diff -- path/to/file.zig
zig fmt --check .
```

When a diff is formatting-only, identify the actual steering token, usually a trailing-comma add/remove, an intentional first-row array break, `++` chunking, or a real comment. Do not claim `zig fmt` proves semantics; follow with the repo's build/test lanes.

## `zlinter` for Zig 0.16.x

Install:

```bash
zig fetch --save git+https://github.com/kurtwagner/zlinter#0.16.x
```

Use `#master` only for 0.17.x-dev or when intentionally tracking unstable upstream.

Build step:

```zig
const zlinter = @import("zlinter");

const lint_step = b.step("lint", "Lint Zig source code.");
lint_step.dependOn(step: {
    var builder = zlinter.builder(b, .{});
    builder.addPaths(.{
        .include = &.{ b.path("src/"), b.path("build.zig") },
        .exclude = &.{ b.path("zig-pkg/"), b.path(".zig-cache/"), b.path("zig-out/") },
    });
    builder.addRule(.{ .builtin = .no_deprecated }, .{});
    builder.addRule(.{ .builtin = .no_unused }, .{});
    builder.addRule(.{ .builtin = .no_swallow_error }, .{});
    builder.addRule(.{ .builtin = .require_errdefer_dealloc }, .{});
    builder.addRule(.{ .builtin = .require_exhaustive_enum_switch }, .{});
    break :step builder.build();
});
```

Avoid enabling every built-in rule permanently without review. Upstream documents all-rules mode as useful for testing/exploration and warns that many rules are pedantic.

## Commands

```bash
zig build lint
zig build lint -- --max-warnings 0
zig build lint -- --rule no_unused --rule no_deprecated
zig build lint -- --rule no_unused --fix
```

Before `--fix`, require a clean working tree or a backup. Review the diff afterwards.
