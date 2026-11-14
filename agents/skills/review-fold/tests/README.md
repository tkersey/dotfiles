# Counterexample admission evaluation

Offline tests and tuning inputs only. These are not a review lane, runtime
classifier, admission receipt, or part of ordinary Review Fold context.

## Local checks

```sh
node agents/skills/review-fold/tests/test-counterexample-admission.mjs
```

The test executes concrete candidate/probe snippets and checks their actual
observations. Seven pairs hold the allegation constant while changing the decisive
program, authority, scope, or current-subject evidence. Additional cases cover
unknown premises, narrowing, failed expectations, oracle defects, setup failures,
incidental assertions, and passing retries after failures. Synthetic local probes
distinguish a wrong return model from omitted entry checks and reject-all; they
also separate ownership from drop permission. They are not historical replays. Source-contract
checks cover the handoff from Actuating through Review Fold to corpus capture.
The existing Actuating composition test invokes this test as well.

The native corpus check exercises the prescribed managed owner route:

```sh
LEDGER_BIN=/path/to/ledger JAQ_BIN=jaq \
  sh agents/skills/review-fold/tests/test-counterexample-corpus.sh
```

Use Ledger 1.8.0 or newer; `JAQ_BIN=jq` also works. The isolated fixture first
observes the missing-owner result, prepares empty custody without a quiescence
assertion, captures and projects a real record, and retries idempotently. A later
invocation from a new Git worktree selects the same managed owner and captures a
second witness without legacy preparation. After both checkouts are removed, the
fixture retrieves the original record unchanged by stable store ID and original
semantic repository scope. It does not exercise a model's decision to obtain that
context or admit a delayed witness.

The reference dispositions are evaluator expectations, not an implemented
adjudicator. Passing probes validate the fixtures and source consistency; they
establish neither model compliance nor improved precision. No CAS or Ledger is
executed here, and no test result grants review credit.

## Paired model evaluation

Export individual inputs and keep the answer key separate:

```sh
node agents/skills/review-fold/tests/test-counterexample-admission.mjs --list
node agents/skills/review-fold/tests/test-counterexample-admission.mjs --case case-01
node agents/skills/review-fold/tests/test-counterexample-admission.mjs --key
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

## Owner workflow evaluation

Evaluate full-fold context use separately from admission-reference reuse. In a
fresh isolated context with a prepared corpus, ask for a full Review Fold with
`corpus_write_authorized: false`, without suggesting a custody command. Check for
an actual basis projection or reuse of a supplied projection whose selector,
semantic scope, definition, and source state still apply. An unsupported statement
that history is incomplete is not an access attempt. A paired input requesting
only Counterexample admission must not grow into the full storage workflow.
Exercise an actual inaccessible owner separately: the result must retain its
failed operation or explicit access constraint, without inventing rows or capture
permission. Keep evaluator expectations out of the run's input.

For delayed capture, supply the original candidate, accepted Goal, witness,
provenance, and failed or uncertain original append outcome, followed by a current
candidate that excludes the witness. With enclosing capture authority, check that
the run re-establishes the original admission, preserves the original subject and
semantic scope, checks any known record before an uncertain retry, and retains
`already-excluded` current applicability. A paired case without the original
authority or decisive evidence must remain unresolved; an old report alone is not
admission. Native idempotence does not establish these semantic judgments.
