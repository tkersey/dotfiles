# Historical Workspace and Replay Lineage

Workspace reconstruction and conversation lineage are separate.

## Workspace modes

### exact

Historical HEAD, dirty state, generated artifacts, and dependencies are verified.

### head_only

Historical commit is known; dirty/generated/dependency state is incomplete.

### transcript_only

No repository tools. The replay reasons only from the verified retained transcript and explicit capsule evidence.

### unavailable

No safe historical environment is available.

## Lineage modes

### thread_fork

May use exact, head-only, or transcript-only workspace according to DCP evidence.

### rollout_transcript

Must use transcript-only workspace.

CAS verifies the rollout and retained-anchor digests, starts a fresh inquiry thread, and supplies bounded historical transcript context.

Do not describe rollout transcript lineage as a live historical thread fork.

## Current checkout prohibition

Never expose today's checkout as historical context when HEAD, dirty state, generated artifacts, or dependencies differ.

## Exact reconstruction

Use a disposable checkout/worktree, read-only fork policy, exact patch verification, isolated caches, and cleanup receipts.

## Tool policy

Transcript-only:

```text
no repository tools
no network
```

Exact/head-only:

```text
read/search/git-show tools only unless the explicit experiment requires safe proof
```

Build tools may mutate caches and generated output, so use disposable state or disable them.
