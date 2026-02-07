# Patch Theory (Practical)

This reference exists to prevent a common category error:

- A git patch file is a context-sensitive *procedure* over a base.
- A join-semilattice merge is a base-free *data merge* (commutative, associative, idempotent).

If you treat git patches like semilattice elements, you will over-promise on merge properties.

## Three meanings of "patch"

1) Patch as diff (procedure)
- Unified diff / `git diff` output.
- Applies to a base via fuzzy context matching.
- Not generally commutative/associative/idempotent.

2) Patch as identified change (fact)
- An immutable, uniquely identified event ("this block was introduced", "this edge was deleted").
- Naturally mergeable by set union (join-semilattice).

3) Patch as patchset identity
- A stable identifier for "the same logical change" enables deduplication.
- In git, `git patch-id --stable` approximates this for text diffs.

## Join-semilattice: what it buys you (and when)

A join-semilattice is a set `L` with `a ⊔ b` that is:

- commutative: `a ⊔ b = b ⊔ a`
- associative: `(a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)`
- idempotent: `a ⊔ a = a`

For version control, the clean semilattice often lives at the *knowledge layer*:

- Version = dependency-closed set of patch IDs
- Merge = dependency-closed union

The hard part is *interpretation*: mapping the merged set of changes back into a single working tree without ambiguity.

## Pijul's approach (why it is "patch-based" in a deeper sense)

Pijul's theory models a repository as a graph of text blocks:

- Vertices are blocks (initially described as lines), uniquely identified by the change that introduced them (hash + position/interval).
- Edges encode ordering ("comes before") plus liveness (alive/dead/etc) and carry the change-id that introduced that edge.
- There are two primitive actions:
  - add vertices and alive edges
  - map an existing edge label to another label (deletions/status changes)

Key consequences:

- Append-only: deletions are new facts (tombstones), not removal.
- Dependencies become structural (context and referenced edges).
- Independent changes commute (order-independent application), so patch transport can be out-of-order.
- Conflicts become first-class graph shapes (incomparable vertices, cycles, zombies) rather than "merge failed".

This is closer to the semilattice/CRDT ideal: facts accumulate; merge is deterministic; conflicts are explicit data.

## xit's approach (why it is "patch-aware" without being patch-distributed)

xit takes a hybrid stance:

- Network/history: snapshots/commits (Git-like).
- Local merge: compute per-commit text patches and use them for merge/cherry-pick.

Claimed advantages over diff3-style three-way merge:

- Cherry-pick then merge: patch identity makes duplicates skippable.
- Adjacent-line conflicts: less likely because patching can be more precise than diff3.
- "Bad merges": fewer context-misplacement risks.

Design tradeoff:

- Since patches are local (not exchanged), xit avoids locking all clients into one patch calculus.
- It does not need full Pijul-style order-independent patch semantics.

## Practical rules for git patch files (what this skill optimizes for)

1) Keep patches tiny and coherent
- Small changes reduce context fragility and conflict surface.
- Avoid drive-by formatting and unrelated refactors.

2) Be explicit about the base
- A patch is meaningful relative to a base (usually `HEAD`).
- When sharing externally, include the base commit hash in your message.

3) Validate the patch
- Quick: `git apply --check --reverse` on your current working tree verifies "this patch corresponds to what I have".
- Strong: check on a clean `HEAD` in a temporary worktree.

4) Choose the right patch format
- `git apply` style: `git diff --cached --binary ... > file.patch`
- `git am` style: `git format-patch` (needs commits; carries metadata)

5) Treat secrets as a hard stop
- Patch files are portable; they leak whatever is in the diff.
