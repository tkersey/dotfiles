# Durable repository custody

This reference and `../scripts/ledger_context.py` own Ledger's Codex integration
location policy. Consumers and `AGENTS.md` delegate here instead of copying it.
The native CLI takes explicit roots and has no Codex/Git default.

## Location and identity

For a previously unregistered repository, the default storage home is
`${CODEX_HOME:-$HOME/.codex}/ledger`; an explicit absolute `LEDGER_HOME` overrides
that default. The layout is:

```text
<storage-home>/repos/<random-stable-store-id>/
  .ledger-root.json
  .ledger/
    <definition-declared logical slots>
    .bindings/
    .definitions/
    .revisions/
    .transactions/
    ...native custody resources...
```

Resolve Git's absolute common directory from the caller-selected verified
workspace. Its untracked `ledger-store.json` holds a stable store ID and absolute
custody root; `ledger-store.lock` serializes first registration. The root's
`.ledger-root.json` independently carries `ledger-storage-root/v1` and the same
`store_id`. These metadata files are private local registration, not user source
records. Do not stage or transport them through a branch.

Linked worktrees share this registration. Worktree moves, branch changes, and
removal do not select new stores. Relocating the common directory preserves the
registration file. A clone starts unregistered: remotes, branch names, commit IDs,
and path hashes do not automatically join independent histories. Explicit clone
attachment/reconciliation is not implemented by this helper; never fake it by
copying a registration over divergent data.

An established registration wins over changed `CODEX_HOME`/`LEDGER_HOME`. Changing
an environment variable cannot silently fork or relocate its history. A missing
or mismatched registered root/marker/control directory fails closed, including
when `--initialize` is repeated. This detects root continuity failures; it is not
backup, cross-machine synchronization, or a replacement for native slot integrity.

The helper currently uses POSIX filesystem/advisory-lock APIs on macOS/Linux.
Grant only needed access to the selected custody tree and common Git metadata.
Do not broaden access to the entire home/configuration directory. Permission
failures are blockers, never permission to fall back to a worktree store.

## Normal resolution and authorized initialization

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --repo "<workspace-root>"
```

Read-only resolution never creates metadata or a store. Before an authorized
first capture, add `--initialize`. It checks every registered available worktree
for legacy control trees and retired source files. Legacy evidence or unavailable
worktree coverage blocks empty initialization. There is no per-turn rebind.

The result is `ledger-workspace-context/v1`. Preserve its `workspace_root`,
`git_common_dir`, stable `repository_id`, `store_id`, `store_root`, and native
selector array. The workspace supplies code/artifact provenance. The selector
supplies custody; they are not interchangeable. Use the same context for capture,
doctor, readback, recall, projections, and source-note admission.

A managed selector is:

```text
--store-root <context.store_root> --store-id <context.store_id>
```

The native engine checks the marker and control root before executing the
selected operation. Managed projection root failures exit 3, not a clear gate.
Do not mix selectors or retry with legacy `--repo` after failure.

## One-time cold adoption

This is explicit maintenance, not automatic recovery. First stop/upgrade all
writers that could still use legacy-local history. `--confirm-no-writers` is the
operator's quiescence assertion, not a lock that fences old executables.

Select the authoritative source worktree and supply every owning definition
needed to cover its static monolithic JSONL event stores:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" \
  --repo "<workspace-root>" --initialize \
  --adopt-from "<authoritative-source-worktree>" \
  --definition "<first-owner-definition>" \
  --definition "<second-owner-definition>" \
  --confirm-no-writers
```

The source must be in the same inspected worktree family. Native, definition-bound
doctor must report healthy bound custody with zero pending transactions. A known
unbound current-format source needs its separately authorized `bind-existing`
first; malformed/stale/unknown custody follows existing recovery rules. Adoption
does not bind, rebind, repair, reinterpret, or append records.

The helper checks coverage, rejects symlinks and unknown semantic files, and
compares sibling histories. Equal copies and complete-record byte prefixes of
the selected validated history are admissible. Additional or divergent history
blocks; there is no concatenation, timestamp winner, last-writer-wins merge, or
ID remapping. Preserve all lineages and reconcile through owners before retrying.
Document, segmented, and dynamic-slot layouts are outside this cold-adoption helper and
fail closed; do not flatten them to force admission.

Cold transport copies exact slot bytes and binding/definition/revision archives
into private staging, preserving original source trees. It does not transport
transaction journals, fencing counters, or reserved advisory lock files. Legacy
lease files require native recovery first. Native doctor checks staging and then
the final identity-checked destination before the registration is published.
Source/destination byte inventories must agree. A failed destination is not
registered; an interrupted final publication can leave an unregistered directory
for explicit inspection, never automatic selection.

After success, resolve from another worktree, run native doctor and a focused
source projection, then resume the original capture and read back its actual
returned ID. Do not claim that adoption retroactively captured a previously
missed learning. Do not delete old source lineages as part of adoption.

Switch all consumers together. Retained old branches may contain historical
tracked logs; they cease to be canonical inputs for managed consumers. Old
binaries explicitly using `--repo` are not technically fenced by the new marker.
Do not run them concurrently against old copies. Retirement of tracked copies
and publication of deliberate exports are separate authorized changes.

## Scope and provenance

Logical definition paths and old record IDs/fingerprints remain unchanged.
Existing provenance and immutable memory-source snapshots are not rewritten.
Resolve a definition-relative source reference through the registered context,
not through the checkout path recorded when the observation happened.

New supported records use `context.repository_id` for stable repository scope;
worktree/branch paths are provenance. Immutable artifact identity must cover the
actual relevant code/fixture/configuration state, including relevant dirty bytes.
Shared visibility does not imply shared applicability. Query-local differences
must not globally retire valid evidence for another active artifact.

The resolver's registration/transport tests do not replace native custody tests.
Run both before qualifying a release. Neither successful transport nor a healthy
doctor result selects a semantic history or authorizes a route.
