# Setup and workflow

## Treat the repo as the source of truth

Always inspect these files first:

- `lean-toolchain`
- `lakefile.lean` or `lakefile.toml`
- the target `.lean` file's imports
- any project README or local instructions

Do not assume examples copied from the newest docs or release notes will work unchanged. Adapt to the toolchain pinned by the repo.

## Project classification

Identify which case you are in:

- **plain Lean project**: mostly standard library imports, little or no mathlib
- **mathlib project**: imports `Mathlib` or has mathlib in Lake dependencies
- **executable**: has `def main : IO Unit`
- **library / theorem development**: mostly definitions and theorems, no runtime entrypoint
- **mixed project**: pure core plus an executable wrapper

This classification changes the commands you should run and the tactics or lemmas you should expect to have available.

## Canonical commands

Prefer project-aware commands through Lake.

- Build the whole workspace:
  ```bash
  lake build
  ```

- Check a single file inside the project's environment:
  ```bash
  lake env lean path/to/File.lean
  ```

- Run a small Lean script or standalone executable file inside the project's environment:
  ```bash
  lake env lean --run path/to/File.lean
  ```

- Inspect the environment that Lake would use:
  ```bash
  lake env
  ```

For a single-file toy example outside a project, this is the simplest execution form:

```bash
lean --run Hello.lean
```

## New project patterns

Use these when the task is to bootstrap a project rather than edit an existing one:

- Plain Lean project:
  ```bash
  lake new MyProj
  ```

- mathlib-oriented project with stricter defaults:
  ```bash
  lake new MyProj math
  ```
  or
  ```bash
  lake init MyProj math
  ```

When the task is to create a verified program from scratch, start with a plain pure core unless the user clearly needs mathlib.

## mathlib dependency and cache workflow

For mathlib-heavy repos, the common fast path after cloning is:

```bash
lake exe cache get
```

Use it when:

- the project already depends on mathlib
- compiled `.olean` dependencies are missing
- local builds are trying to recompile far too much
- imports fail after a fresh checkout

If the dependency state looks stale:

```bash
lake clean
```

If necessary, remove `.lake/` and then refresh dependencies again.

## Frequent failure modes and responses

### 1. Raw `lean` works differently from project builds

Cause: you are outside the Lake environment.

Response: switch to `lake env lean ...` or `lake build`.

### 2. `unknown package 'Mathlib'` or missing import errors

Cause: wrong working directory, dependency not fetched, or stale `.lake/`.

Response:

- confirm you are in the project root
- inspect `lakefile`
- run `lake update` if appropriate for the repo
- run `lake exe cache get` for mathlib projects
- rebuild with `lake build`

### 3. Feature mismatch with docs

Cause: docs or examples assume a newer Lean version than the project pins.

Response:

- read `lean-toolchain`
- downgrade the syntax or tactic choice to the current toolchain
- avoid “forcing” the repo to the newest release unless the user asked for an upgrade

### 4. Names or notation not found

Cause: missing import, missing namespace qualification, missing `open scoped`, or notation section not in scope.

Response:

- inspect imports
- qualify the declaration name
- check local `namespace ... end`
- search nearby files for how the same notation is opened

### 5. File compiles conceptually but the theorem fails

Cause: wrong statement shape, missing generalization, or using the wrong induction principle.

Response:

- move the exact failing goal into a local `example`
- generalize variables explicitly if recursion changes them
- switch from plain `induction` to `fun_induction` when proving a theorem about a recursive function

## Editing discipline

When changing existing Lean code:

- make the smallest change that fixes the issue
- preserve local naming conventions
- add imports only when justified
- prefer a helper lemma over a massive one-shot tactic block
- if you introduce a new abstraction for proof convenience, justify why it is better than a local lemma

## Final environment checks

Before handing the result back:

- run the project-aware command that actually checks the changed file or target
- confirm there are no leftover scratch `example`s unless they are intentionally helpful
- confirm the final code would make sense to someone reading the surrounding file
