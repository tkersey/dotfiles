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

## macOS with an existing elan installation

Install an exact toolchain alongside existing ones. For example, to install the 4.34.0 release:

```bash
elan toolchain install leanprover/lean4:v4.34.0
lean +leanprover/lean4:v4.34.0 --version
lake +leanprover/lean4:v4.34.0 --version
```

These explicit `+toolchain` invocations verify the installed tools without changing a project's pin. Only when the user wants to change the global fallback:

```bash
elan default leanprover/lean4:v4.34.0
```

A project pin or applicable override can still select another version. Diagnose selection in the target directory rather than reinstalling:

```bash
elan show
elan override list
lean --version
lake --version
```

Also check `ELAN_TOOLCHAIN` and that the selected `lean`/`lake` executables are elan proxies when selection is surprising. Do not unset overrides or change defaults without intent. Updating elan itself (`elan self update`, when supported by its installation method) is distinct from installing Lean.

A project upgrade is separate: change `lean-toolchain` only when authorized, select compatible dependency revisions, review manifest changes, and run the project's checks. For mathlib, inspect the `lean-toolchain` at the chosen revision; its development branch may be ahead of the desired stable Lean release. Do not blindly run `lake update` or delete the lock state to force an upgrade.

Source: [elan toolchain management](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Managing-Toolchains-with-Elan/). The exact version above is an installation example, not the skill's default for all projects.

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

## Structured lint diagnostics (Lean 4.34.0)

When the pinned Lake supports it, use this for machine-readable diagnostics:

```bash
lake lint --code-quality
```

It implies `--builtin-lint` and `--builtin-only`: it does not replace custom lint drivers. Read the JSON entries, not just the exit code. Text-linter results aggregate warning counts by module and linter; environment-linter results identify flagged declarations. Inspect each entry's `name`, `source`, and `value.scalar.value`. Treat nonzero counts as findings, not a clean result.

This mode succeeds even when it reports violations. A command/build failure is still a failure, and missing or malformed output is not evidence of a clean run. Retain the repository's ordinary lint/build gates and report which modules and linters were actually checked. On older toolchains, use the repository's existing diagnostics rather than upgrading just for JSON output.

Sources: [Lake code-quality mode](https://github.com/leanprover/lean4/pull/14622) and [the reviewed release notes](https://github.com/leanprover/reference-manual/blob/6624868291800878b94b5e58ad57bf642880ec39/Manual/Releases/v4_34_0.lean).

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
