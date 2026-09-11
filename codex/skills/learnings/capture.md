# Write Workflow

## Write Workflow

1. Verify the git root:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Fail closed when either retired Learnings path exists without the canonical
   store. Do not create a parallel store or read the retired path:

   ```bash
   if [ ! -f .ledger/learnings/events.jsonl ] &&
      { [ -e .ledger/learnings/learnings.jsonl ] || [ -e .learnings.jsonl ]; }; then
     printf '%s\n' 'blocked: retired Learnings store requires explicit owner-authorized recovery' >&2
     exit 1
   fi
   ```

3. Run the definition-bound doctor:

   ```bash
   ledger doctor \
     --definition "$learnings_definition" \
     --repo "<repo-root>" \
     --format json
   ```

   Append only when the store is `current` or absent. For an unbound
   current-format store, run the explicit `bind-existing` operation once after
   full validation. For `StoreBindingRevisionMismatch` or
   `StoreBindingRecordCountMismatch` after authoritative external transport,
   run `rebind-existing`; it must validate the complete current store, replace
   only stale Ledger binding metadata, and leave event bytes unchanged. Stop on
   every invalid row; do not skip or reinterpret it.
4. Gather exact evidence and changed paths.
5. Distill objective, inflection, proof, and transferable rule.
6. Author `learning.json` as one `submission.record` packet, then append from
   the verified repo root:

   ```bash
   ledger transact \
     --definition "$learnings_definition" \
     --operation capture \
     --repo "<repo-root>" \
     --input submission=learning.json \
     --format json
   ```

7. Retain the appended learning ID, rerun definition-bound doctor, and use a
   focused `record` or `recall` projection to verify readability.
8. Before any Codex-made commit, inspect the current learning through the
   `record` projection. Do not read the store directly.
9. Retain exactly one canonical learning proof line in working evidence. Include
   source-memory proof in the final user-facing reply only when it changed
   repo-visible state, needs user action, explains a blocker/error, or the user
   explicitly asks.

Use the [disposition invariant](SKILL.md#disposition-invariant) as the internal proof line.
