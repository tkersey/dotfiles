# Zig cache CI policy

Use this reference when configuring CI caches, investigating CI disk pressure, or deciding what to persist between jobs.

## Default stance

Prefer short-lived local caches and carefully keyed global caches. CI cache correctness matters more than maximizing hit rate.

## Recommended cache key inputs

Include at least:

- Zig version.
- Host OS and architecture.
- Target triple or target matrix name.
- `build.zig` hash.
- `build.zig.zon` hash.
- Dependency/fork mode, including whether `zig build --fork` is used.
- Relevant C toolchain/sysroot/libc identifiers when C/C++ integration is involved.

## Recommended layout

```bash
zig build \
  --cache-dir "$RUNNER_TEMP/zig-local-cache" \
  --global-cache-dir "$RUNNER_TOOL_CACHE/zig-global-cache" \
  --summary all
```

Guidelines:

- Local cache: one job, one workspace, disposable.
- Global cache: share only with conservative keys and TTL.
- `zig-out`: usually an artifact, not a CI cache. Upload it only when the job needs produced binaries/libs/docs.
- `zig-pkg`: do not cache if dependencies are edited, patched, or replaced during the job. If cached, key it on `build.zig.zon` plus Zig version and branch/fork policy.

## Drain order under CI disk pressure

1. `.zig-cache` / configured local cache.
2. `zig-out` if outputs have already been uploaded or are no longer needed.
3. Old global-cache entries.
4. `zig-pkg`, guarded by policy and only if dependency state can be refetched.

After draining dependencies or global cache:

```bash
zig build --fetch=needed
zig build --summary all
```

## Anti-patterns

- Sharing the same mutable local cache across concurrent CI jobs.
- Persisting `.zig-cache` forever across all branches.
- Caching `zig-pkg` while also mutating packages during the job.
- Treating `zig-out` as a safe cache when it contains release artifacts.
- Deleting global cache as a hidden build step without logging reclaimed size and rebuild/fetch validation.
