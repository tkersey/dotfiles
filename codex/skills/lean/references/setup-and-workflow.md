# Setup and workflow

Use the repository's Lean setup instead of guessing.

## Files to inspect first

- `lean-toolchain`
- `lakefile.lean` or `lakefile.toml`
- `lake-manifest.json`
- target `.lean` file imports
- nearby files in the same namespace
- existing CI commands, if present

The pinned toolchain and dependency lock are authoritative.

## Common commands

Build the project:

```bash
lake build
```

Check one module by name:

```bash
lake build +Module.Name
```

Check one file inside the Lake environment:

```bash
lake env lean path/to/File.lean
```

Run a Lean file that has `main`:

```bash
lake env lean --run path/to/File.lean
```

Inspect the Lake environment:

```bash
lake env
```

For a single-file toy example outside a Lake project:

```bash
lean --run Hello.lean
```

For mathlib-heavy projects after clone or cache loss:

```bash
lake exe cache get
```

## Do not casually update dependencies

Use `lake update` only when changing dependency resolution is intended. For proof repair, local correctness work, or CI fixes, prefer preserving the existing lock state.

## Import strategy

Prefer local imports already used nearby. When adding imports:

1. Add the smallest import that exposes the needed declarations.
2. Recheck the file.
3. Avoid importing all of Mathlib unless the project already does so or the file is exploratory.

## Error workflow

When Lean reports an error:

1. Read the first real error, not the cascade.
2. Check namespace/import/module-name mismatches.
3. Check that the theorem or tactic exists under the pinned dependency version.
4. Move complex failures into a tiny local `example` when helpful.
5. Fix the theorem statement only if the original statement is false or mismatched with the implementation/spec.

## Output discipline

After changes, report:

- command run;
- result;
- files changed;
- theorem names proved;
- placeholder status;
- proof boundary for verification tasks;
- trust/axiom notes for high-assurance tasks.
