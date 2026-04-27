# Zig cache hygiene and disk-pressure playbook

Use this playbook when a user reports disk pressure, runaway caches, stale build outputs, `No space left on device`, CI cache bloat, or confusion about `.zig-cache`, `zig-out`, `zig-pkg`, local cache, or global cache locations.

## Operating principle

Do not blindly delete paths. First classify the path, estimate the reclaimable size, protect dependency edits, then validate a rebuild.

Zig cache work is operational systems work. The goal is to reclaim space while preserving intentional artifacts, local dependency edits, forks, and reproducibility.

## Cache and output taxonomy

| Path/class | Default action | What it is | Main risk |
| --- | --- | --- | --- |
| `.zig-cache` | Safe delete | Project-local build cache; rebuildable. | Forces recompilation. |
| `zig-cache` | Safe delete when present | Legacy or custom local cache name. | Forces recompilation. |
| `zig-out` | Optional delete | Build install prefix/output selected by `zig build -p/--prefix`; may contain binaries, libraries, generated assets, packages, docs, or PDBs. | Deletes outputs the user may still need. |
| `zig-pkg` | Guarded delete | Zig 0.16 project-local fetched dependency tree next to `build.zig`. | May contain edited dependencies, local clones, or intentional vendoring. |
| global Zig cache | Guarded drain | Shared compiler/package cache discovered by `zig env` or overridden by `--global-cache-dir`. | Forces rebuilds/refetches and can affect many projects. |
| custom `--cache-dir` | Guarded drain | User-selected local cache path. | May be shared by CI/jobs if configured poorly. |
| custom `--global-cache-dir` | Guarded drain | User-selected global cache path. | May be shared across repos, users, or CI jobs. |

## Protocol

1. **Inventory before deletion.**
   - Record `zig version`.
   - Capture `zig env` when available, especially `global_cache_dir`.
   - Measure `.zig-cache`, `zig-cache`, `zig-out`, `zig-pkg`, and global cache size.
   - Search for nested Zig projects before recursive deletion.

2. **Classify candidates.**
   - `.zig-cache` and `zig-cache`: local build cache; safe to delete.
   - `zig-out`: generated output/install prefix; delete only if those outputs are not needed.
   - `zig-pkg`: dependency working tree; delete only after checking local edits/forks/vendor policy.
   - Global cache: shared cache; drain by explicit path and preferably by age/size policy.

3. **Default to dry-run.**
   - Show exact paths and sizes first.
   - Require an explicit `--yes` flag or user confirmation before destructive deletion.
   - Never delete paths outside the discovered project/cache roots.

4. **Protect dependency edits.**
   - Before deleting `zig-pkg`, detect nested git repositories.
   - If any nested repo has uncommitted changes, report `CACHE_MODIFIED_DEPENDENCY_UNTOUCHED` and leave `zig-pkg` intact.
   - Do not treat paths supplied to `zig build --fork` as cache.
   - If the repository intentionally vendors `zig-pkg`, require explicit confirmation and repository-specific policy.

5. **Drain in safe order.**
   - First: `.zig-cache` / `zig-cache`.
   - Second: `zig-out`, only when generated outputs are disposable.
   - Third: global Zig cache entries, preferably by age.
   - Last: `zig-pkg`, only when dependency edits/forks are protected.

6. **Validate after draining.**
   - If dependency state was touched, run `zig build --fetch=needed` or `zig build --fetch=all`.
   - Run `zig build --summary all` or the repository’s normal build lane.
   - Report `CACHE_REBUILD_VERIFIED` or `CACHE_REBUILD_UNVERIFIED`.

7. **Prevent recurrence.**
   - Use `--cache-dir` and `--global-cache-dir` to route caches to a larger or ephemeral disk.
   - In CI, include Zig version, OS/architecture, target triple, `build.zig`, `build.zig.zon`, and dependency/fork state in cache keys.
   - Apply TTLs to shared CI caches.

## Result labels

Use these labels in reports:

- `CACHE_AUDITED`
- `CACHE_DRY_RUN_ONLY`
- `CACHE_LOCAL_DRAINED`
- `CACHE_OUTPUT_DRAINED`
- `CACHE_GLOBAL_DRAINED`
- `CACHE_ZIG_PKG_DRAINED`
- `CACHE_ZIG_PKG_SKIPPED`
- `CACHE_MODIFIED_DEPENDENCY_UNTOUCHED`
- `CACHE_ACTIVE_BUILD_REFUSED`
- `CACHE_REBUILD_VERIFIED`
- `CACHE_REBUILD_UNVERIFIED`
- `CACHE_PATH_UNDISCOVERED`

## Fast local triage

From the project root:

```bash
du -sh .zig-cache zig-cache zig-out zig-pkg 2>/dev/null
```

Safe local cache cleanup:

```bash
rm -rf .zig-cache zig-cache
```

Optional generated-output cleanup:

```bash
rm -rf zig-out
```

Guarded `zig-pkg` inspection:

```bash
du -sh zig-pkg 2>/dev/null
find zig-pkg -type d -name .git -print 2>/dev/null
```

If `zig-pkg` contains nested git repositories, inspect them before deletion:

```bash
find zig-pkg -type d -name .git -print0 2>/dev/null |
while IFS= read -r -d '' gitdir; do
  repo="${gitdir%/.git}"
  echo "== $repo =="
  git -C "$repo" status --short || true
done
```

## Cache relocation

Use this when disk pressure recurs or when a small project volume should not receive build-cache writes:

```bash
zig build \
  --cache-dir "$PWD/.zig-cache" \
  --global-cache-dir "$HOME/.cache/zig"
```

For a scratch disk:

```bash
zig build \
  --cache-dir "/mnt/fast-scratch/$USER/project-zig-cache" \
  --global-cache-dir "/mnt/fast-scratch/$USER/global-zig-cache"
```

Do not share a mutable local cache directory across concurrent jobs unless the workflow has been tested for that access pattern. Prefer one local cache per job and a shared global cache with a conservative key/TTL policy.

## CI disk-pressure policy

- Use an ephemeral project-local `--cache-dir` per job when disk pressure is frequent.
- Cache the global cache only when the cache key includes Zig version, host OS/architecture, target triple, `build.zig`, `build.zig.zon`, and dependency/fork state.
- Do not persist `.zig-cache` indefinitely across branches without a TTL.
- Do not cache `zig-pkg` if the job mutates dependencies.
- Drain `.zig-cache` first, then `zig-out`, then old global-cache entries, and only then guarded `zig-pkg`.
- After dependency cache drain, run `zig build --fetch=needed` or `zig build --fetch=all`.

## Review checklist

- Did the report show sizes before deletion?
- Did the command avoid `.git`, `node_modules`, and unrelated build systems?
- Were nested Zig projects accounted for?
- Were custom `--cache-dir` and `--global-cache-dir` settings considered?
- Was `zig-pkg` protected from deleting local modifications?
- Was `zig-out` treated as output, not cache?
- Was a post-drain rebuild/fetch probe run?
- Was recurrence addressed through cache routing, TTL, or CI cache keys?
