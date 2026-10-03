# Zig cache hygiene and disk pressure

Inventory before deletion. Cache cleanup is operational work: preserve user data,
dependency edits/forks, intended outputs, and reproducibility. A familiar basename
or a successful `zig env` does not by itself prove arbitrary contents disposable.

| Class | Treatment |
| --- | --- |
| `.zig-cache`, legacy `zig-cache` | Normally rebuildable local cache; inspect identity, tracked files and nested repositories. |
| `zig-out` | Generated install prefix/output; opt in only when those outputs are disposable. |
| `zig-pkg` | Dependency working state, not automatically disposable. Never deleted by this helper. |
| Global cache | Shared infrastructure; discover with `zig env`, verify supported object-store layout, and preserve packages. |
| Custom paths | Require explicit identity and repository/CI policy; no arbitrary-path deletion override. |

## Guarded helper

Resolve `zig_skill_root` to the loaded skill's directory. The existing shell
entrypoint delegates to the standard-library Python implementation through `uv`.

```bash
bash "$zig_skill_root/scripts/zig_cache_drain.sh" --root .
bash "$zig_skill_root/scripts/zig_cache_drain.sh" --root . --yes
bash "$zig_skill_root/scripts/zig_cache_drain.sh" --root . --include-zig-out
bash "$zig_skill_root/scripts/zig_cache_drain.sh" --root . --include-global --older-than 7
```

Default is dry-run. `--yes` authorizes the requested disposable cache cleanup,
not unrelated deletion. One project root is inspected at a time; nested projects
are not recursively swept by basename. Inventory and select them independently.
The whole candidate selection is validated before any deletion.

### Custom package paths in 0.17

`ZIG_LOCAL_PKG_DIR` and `zig build/fetch --pkg-path` can move dependency sources
inside an otherwise cache-looking directory. The helper protects the conventional
`zig-pkg` path, the current environment override and explicit `--pkg-path` values,
including canonical symlink destinations and ancestor/descendant overlaps:

```bash
bash "$zig_skill_root/scripts/zig_cache_drain.sh" --root . --pkg-path custom-packages
```

Repeat `--pkg-path` for additional locations that must survive. Relative values
are interpreted against `--root`. Past command-line overrides are not discoverable
from the current environment: inspect the build/CI invocation and pass them in.
When package locations are unknown, do not authorize deletion. This flag protects
sources; it never expands the set of deletion candidates. An overlap refuses the
whole initial selection with `CACHE_PACKAGE_PATH_UNTOUCHED`; it is rechecked before
individual deletions. Existing concurrent-writer limitations still apply.

`--global-path` only asserts the path reported by `zig env`; it cannot select an
arbitrary directory. Global object-store directories `o`, `h`, `z`, `b`, and `tmp`
are supported; package storage `p` is preserved. Unknown layouts fail closed and
need inspection. Missing paths, aliases overlapping protected roots, overlapping
candidates, tracked contents, nested `.git` directories or worktree `.git` files,
and symlink candidates are refused. Clean Git metadata would not establish that
a dependency is safe to destroy: local commits and extracted edits also matter.

`--include-zig-pkg` is retired and refuses the entire operation before deletion.
Dependency cleanup needs a repository-specific preservation/recovery decision,
not an inferred "clean" status or a blanket confirmation flag.

`--older-than` considers descendants, not just parent directory mtime. Reported
bytes are file-content estimates, not promised disk reclamation. Destructive use
requires a working `pgrep` check and symlink-resistant platform deletion. Stop
builds and other writers first: process checks and preflight are defensive checks,
not a lock against a concurrently starting writer. Do not run against hostile or
concurrently mutated cache directories.

## Outcomes

A successful deletion emits `CACHE_LOCAL_DRAINED`, `CACHE_OUTPUT_DRAINED`, or
`CACHE_GLOBAL_DRAINED` for that path, then exits zero. Dry-run emits
`CACHE_DRY_RUN_ONLY`; an empty selection emits `CACHE_NO_CHANGES`. Recent contents
are skipped explicitly. A refusal, unavailable identity/process check, or deletion
error exits nonzero and never claims the failed path was drained. Earlier
successful deletions remain reported if a later operation fails.

Inspect stdout and stderr. Do not infer success from a requested flag. The helper
does not assert a successful rebuild. Use the repository's normal build command
when rebuilding is in scope, and distinguish `CACHE_REBUILD_VERIFIED` from
`CACHE_REBUILD_UNVERIFIED`.

## Relocation and CI

For recurring pressure, route caches deliberately rather than repeatedly deleting:

```bash
zig build --cache-dir "$PWD/.zig-cache" --global-cache-dir "$HOME/.cache/zig"
```

Use per-job local caches and conservative shared-cache keys/TTLs. Include the Zig
version, host/target, relevant build inputs, and dependency/fork state. Preserve
mutable dependency working trees. See [CI cache policy](cache_ci_policy.md).
Diagnose the actual failing resource before changing cache routing for a sandbox
permission error; see [evidence context](evidence_context_playbook.md).
