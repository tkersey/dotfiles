# Counterexample admission evaluation

Offline tests and tuning inputs only. These are not a review lane, runtime
classifier, admission receipt, or part of ordinary Review Fold context.

## Local checks

```sh
node codex/skills/review-fold/tests/test-counterexample-admission.mjs
```

The test executes concrete candidate/probe snippets and checks their actual
observations. Six pairs hold the allegation constant while changing the decisive
program, authority, scope, or current-subject evidence. Additional cases cover
unknown premises and narrowing a partially valid allegation. Source-contract
checks cover the handoff from Actuating through Review Fold to corpus capture.
The existing Actuating composition test invokes this test as well.

The reference dispositions are evaluator expectations, not an implemented
adjudicator. Passing probes validate the fixtures and source consistency; they
establish neither model compliance nor improved precision. No CAS or Ledger is
executed here, and no test result grants review credit.

## Paired model evaluation

Export individual inputs and keep the answer key separate:

```sh
node codex/skills/review-fold/tests/test-counterexample-admission.mjs --list
node codex/skills/review-fold/tests/test-counterexample-admission.mjs --case case-01
node codex/skills/review-fold/tests/test-counterexample-admission.mjs --key
```

Give an evaluated run only the selected skill revision, exported case, and its
source evidence. Do not expose this test's source, key, pair identity, expected
observations, or the other variant. Inputs contain no preclassified validity
flag. Use fresh contexts and vary order while holding model and resources fixed
when comparing revisions. Compare the reasoning against the decisive source
fact, not only the disposition word. Source-level proof is allowed; reproduction
is not mandatory. The fixtures' exact source and supplied Goal are authoritative
within their synthetic scope, not claims about a live repository or review.

Measure false admission, retention of genuine violations, appropriate unresolved
outcomes, and relevant evidence cited separately. Do not reward rejecting or
blocking everything, preserving unsupported parts of a bundled finding, inventing
an oracle from the allegation, or accepting the reviewer's proposed repair.
Check all-valid batches without requiring a rejection and repeated reports
without treating reviewer agreement as independent witness evidence. Keep
material proof gaps distinct from runtime failures. The unknown case must not
be turned into a fabricated store implementation or a successful reproduction.

For retrospective sampling, include original proposed findings, not just the
accepted corpus. Judge current applicability on the original reviewed snapshot;
report false-finding-driven changes and unnecessary follow-up machinery as well
as missed genuine defects. A lower acceptance rate alone is not improvement.
Report actual model-run results separately from local fixture checks. Add no
new runtime store, quota, or campaign requirement to collect these measurements.
