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
4. Gather exact evidence, artifact identity, and changed paths. Distinguish the
   observed result from its proposed explanation and transferable claim.
5. Distill objective, inflection, proof, and a bounded rule using the
   [claim discipline](#bounded-claims) below.
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

## Bounded claims

Use the existing record fields; do not add a parallel schema or evidence store:

- `learning`: the conditional claim and the observation it preserves. State an
  inferred mechanism as an inference, not an observed fact.
- `application`: prerequisites, the current artifact facts to inspect, and when
  not to apply the rule. An untested boundary is not a proved failure.
- `evidence`: inspectable source/artifact references, the actual check and result,
  any executed boundary challenge, and material uncertainty or untested scope.
  Keep proposed checks distinct from executed evidence.

For example, a faster parse benchmark supports reuse for the tested immutable
configuration, not "cache all configuration." The application must address
semantic inputs in the cache key and mutation/invalidation before wider reuse.
Keep the supporting case when narrowing a rule after a counterexample.

Capture a useful scoped observation without demanding an adversarial run for
every row. Before elevating it into wider technical guidance, apply
[memory admission](memory-admission.md#technical-generalization). Action labels
such as `codify_now` express intended use, not evidential confidence.

## Refinement instead of accumulation

If new evidence changes the claim or its application boundary, append the
corrected bounded learning with `supersedes_id` when it replaces an earlier row;
use `related_ids` for relevant non-replacement relationships. Preserve useful
supporting evidence and the reason for revision. Leave unrelated rules alone.
When admitted guidance changes, follow the existing
[supersession or withdrawal](memory-admission.md#supersession-and-withdrawal)
workflow; never edit old events or compiled memory.

No change is a valid outcome. Do not append a warning beside a rule that needs
correction, manufacture paraphrases to count successful reuses, or bypass
idempotency just to add evidence to an unchanged claim. The current fingerprint
uses status and learning text, not the evidence array; this workflow adds no
evidence-enrichment operation. A failed learning does not automatically warrant
an operational exclusion: Negative Ledger must satisfy its own activation and
capture gates.
