# Write Workflow

## Write Workflow

1. Resolve the intended personal store through [store guidance](store.md),
   including `$ledger`'s first-use owner preparation. Reuse its returned selector.
2. Gather exact evidence, immutable artifact identity where relevant, and changed
   paths. Use stable `repository_id` in `context.repo`, retaining actual branch
   provenance separately (`not-applicable` for non-Git evidence). Use stable,
   sorted project-relative paths, not temporary checkout paths. Distinguish
   observed results from explanations and transferable claims.
3. Distill objective, inflection, proof, and a bounded rule using the
   [claim discipline](#bounded-claims) below.
4. Inspect a relevant prior record when deciding whether this is a duplicate or
   correction. Same wording with different applicability can be a distinct rule;
   another timestamp, branch name, or repeated proof run is not novelty.
5. Author `learning.json` as one `submission.record` packet, then append:

   ```bash
   ledger transact \
     --definition "$learnings_definition" \
     --operation capture \
     --store-root "<context.store_root>" --store-id "<context.store_id>" \
     --input submission=learning.json \
     --format json
   ```

6. Retain the native transaction outcome and returned learning ID. Native
   compare-and-append owns validation, binding, and concurrent-write safety; do
   not surround a successful transaction with repeated doctor or precommit
   readback. Use a focused `record` projection for an uncertain result, a changed
   consumer, or requested proof. Native failure remains a failure; do not
   change selectors or reinterpret invalid rows to make an append pass.
7. Retain the canonical learning outcome in working evidence. Include
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
manufacture paraphrases to count reuses, or bypass idempotency to add another
passing run to an unchanged claim. New capture fingerprints cover status,
normalized learning text, application, stable project identity, and scoped paths.
Capture time, branch, session/source metadata, and evidence bytes do not create
novelty. A substantive correction belongs in a bounded claim/application with
`supersedes_id`, preserving its evidence. Historical IDs and fingerprints remain
unchanged; compare old records by their full claim and scope, not hash equality.
A failed learning does not automatically warrant an operational exclusion:
Negative Ledger must satisfy its own activation and capture gates.
