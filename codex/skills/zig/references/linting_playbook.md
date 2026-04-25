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

`zig ast-check` catches simple compile errors, but it is not a full semantic build. Follow with `zig build` and `zig build test`.

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
