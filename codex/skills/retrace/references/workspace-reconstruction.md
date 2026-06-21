# Historical Workspace Reconstruction

## Modes

### exact

```text
historical HEAD
+ exact dirty patch/untracked content
+ required generated artifacts
+ required dependency/fork state
```

### head_only

Historical commit is exact; dirty/generated/dependency state is incomplete.

### transcript_only

No repository tools.

The fork reasons only from inherited conversation and capsule evidence.

### unavailable

Historical source cannot be reconstructed safely.

## Default

Prefer transcript-only for explanation and route replay unless code inspection is necessary.

This avoids accidental contamination from today's checkout.

## Exact reconstruction

Use a disposable checkout or linked worktree.

Requirements:

- path outside active delivery worktree;
- detached historical HEAD;
- captured patch applied with fingerprint verification;
- read-only fork permissions;
- no commit/push;
- cleanup receipt;
- no secret copying;
- generated/dependency uncertainty recorded.

## Current checkout prohibition

Do not expose the current checkout when:

```text
current HEAD differs
dirty state differs
generated artifacts differ
dependencies/forks differ
```

unless the lane is explicitly outcome/current-state-aware.

## Tool policy

Read-only means:

```text
file reads/search
git show/log/diff
build/test only when sandbox and workspace policy permit and no mutation occurs
```

Build tools may write caches/artifacts.

For strict inquiry, disable tools or use a disposable workspace with isolated caches.
