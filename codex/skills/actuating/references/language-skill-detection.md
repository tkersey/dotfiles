# Language Skill Detection

Activate language-specific skills when project surface, files, commands, or errors make them relevant.

## Zig

Use `$zig` for:

- `.zig`, `build.zig`, `build.zig.zon`
- `zig build`, `zig test`, `zig fmt`, `zig ast-check`
- comptime, allocator, FFI, packed/extern, pointer, safety, cache, or migration hazards

## Lean

Use `$lean` for:

- `.lean`, `lake`, mathlib, theorem/proof repair, termination, formalization

## Python

Use repo Python tooling standards for:

- `pyproject.toml`, `uv`, `pytest`, `ruff`, `mypy`, packaging, script/test work

## Other languages

Use any visible repo skill that clearly owns the toolchain or proof lane. Language skills inform commands and hazards; `$actuating` still owns the end-to-end plan-to-PR lifecycle.
