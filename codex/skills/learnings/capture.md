# Write Workflow

## Write Workflow

1. Verify the Git workspace with `git rev-parse --show-toplevel`. This identifies
   code/evidence provenance, not the canonical storage address.
2. Resolve its managed custody through `$ledger`. Only an authorized first
   capture may request initialization. The Ledger owner handles legacy inventory,
   cold adoption, and exact binding/recovery; do not create a parallel checkout
   store or repeat initial binding in each worktree.
3. Run the definition-bound doctor against that same context:

   ```bash
   ledger doctor \
     --definition "$learnings_definition" \
     --store-root "<context.store_root>" --store-id "<context.store_id>" \
     --format json
   ```

   Append only when the selected source is current or legitimately absent in
   the established custody root. Root/marker failures, invalid rows, binding
   failures, and unknown replacements block capture. Do not skip/reinterpret rows
   or change selectors to make the check pass.
4. Gather exact evidence, immutable artifact identity, and changed paths from
   the workspace. Use the resolved stable `repository_id` in `context.repo` for
   new rows, retaining branch/path provenance separately. Distinguish observed
   results from proposed explanations and transferable claims.
5. Distill objective, inflection, proof, and a bounded rule using the
   [claim discipline](#bounded-claims) below.
6. Author `learning.json` as one `submission.record` packet, then append:

   ```bash
   ledger transact \
     --definition "$learnings_definition" \
     --operation capture \
     --store-root "<context.store_root>" --store-id "<context.store_id>" \
     --input submission=learning.json \
     --format json
   ```

7. Retain the appended learning ID, rerun doctor, and use a focused `record` or
   `recall` projection in the same context to verify readability.
8. Before any Codex-made commit, inspect the current learning through `record`.
   Do not read the store directly or stage canonical private history as source.
9. Retain exactly one canonical learning proof line in working evidence. Include
   source-memory proof in the final reply only when it changed repo-visible
   state, needs action, explains a blocker/error, or the user explicitly asks.

Use the [disposition invariant](SKILL.md#disposition-invariant) as the internal proof line.

## Bounded claims

Use existing record fields; do not add a parallel schema or evidence store:

- `learning`: the conditional claim and the observation it preserves. State an
  inferred mechanism as an inference, not an observed fact.
- `application`: prerequisites, current artifact facts to inspect, and when not
  to apply the rule. An untested boundary is not a proved failure.
- `evidence`: inspectable source/artifact references, the actual check/result,
  executed boundary challenges, and material uncertainty or untested scope.
  Keep proposed checks distinct from executed evidence.

A faster parse benchmark supports reuse for the tested immutable configuration,
not "cache all configuration." Application must address semantic inputs in the
cache key and mutation/invalidation before wider reuse. Keep the supporting case
when narrowing a rule after a counterexample.

Capture a useful scoped observation without demanding an adversarial run for
every row. Before wider technical guidance, apply
[memory admission](memory-admission.md#technical-generalization). Action labels
such as `codify_now` express intended use, not evidential confidence.

## Refinement instead of accumulation

If evidence changes a claim or application boundary, append the corrected bounded
learning with `supersedes_id` when replacing an earlier row; use `related_ids`
for relevant non-replacements. Preserve supporting evidence and revision reasons.
Leave unrelated rules alone. Admitted guidance changes follow
[supersession or withdrawal](memory-admission.md#supersession-and-withdrawal);
never edit old events or compiled memory.

No change is valid. Do not append a warning beside a rule needing correction,
manufacture paraphrases to count reuses, or bypass idempotency to add evidence to
an unchanged claim. The fingerprint uses status and learning text, not evidence;
sharing custody does not change that identity law or add evidence enrichment.
A failed learning does not automatically warrant an operational exclusion:
Negative Ledger must satisfy its own activation and capture gates.
