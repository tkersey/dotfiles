# Merge-policy discrimination cases

This is evaluator material. Do not give this file, `merge_policy_cases.py`, its
answer key, probe output, or sibling subjects to a reviewer. The exported subjects
contain neutral requirements, base/candidate files, and source evidence. They
contain no family names, expected findings, disposition labels, or assigned mode.

The same subject should receive separate fresh reviews under `pragmatic` and
`pedantic`. Hold source, admission instructions, and runtime settings constant;
change only the bound merge policy. Run each reviewer with no authoring history,
other reviewer result, or expected answer. A mode pair is useful evidence about
that subject, not a general efficacy comparison or a native campaign.

## Export and qualify the subjects

From the repository root, with new export destinations:

```bash
uv run --no-project python -B agents/skills/elenctic/tests/merge_policy_cases.py export \
  --subjects /tmp/elenctic-policy-subjects --key /tmp/elenctic-policy-evaluator/key.json
uv run --no-project python -B agents/skills/elenctic/tests/merge_policy_cases.py check \
  --subjects /tmp/elenctic-policy-subjects --key /tmp/elenctic-policy-evaluator/key.json
```

`--seed INTEGER` makes the shuffled opaque IDs reproducible. The manifest binds
IDs to source digests; the evaluator key must be outside the export. `check`
compiles the Python fixture sources and runs only the supplied probes against
digest-matched synthetic candidates. It compares factual observations, including
known wrong or bounded outcomes. It does not grade a model, prove all source
contracts, or count a skipped required check as passed.

Give a fresh reviewer one opaque subject directory, the frozen shared admission
and merge-policy instructions, and exactly one mode. Include the same applicable
engineering-standard text in both modes; change only the mode binding. Use a
neutral assignment:

> Review the change in the supplied subject under merge policy `<MODE>`. Read
> SUBJECT.md and the complete base/candidate artifacts. Apply the supplied
> admission and merge-policy contracts to current evidence. Return supported
> findings and their dispositions, the decisive evidence and strongest
> countercase, coverage limits, and your final merge judgment. Do not edit files.

For a worker-integration check, supply the entire frozen worker semantic contract
and auxiliary concerns. Do not invent native assignment IDs or claim a prepared
history seed. Label an isolated check honestly. The complete native workflow still
requires its separate campaign/runtime qualification.

## Expected discrimination

All observations must be independently assessed from source. These expectations
are hypotheses for adjudication, not authority to reject an unexpected valid
finding. A correct final verdict with a fabricated mechanism is not a successful
review; a risk relabeled as an unknown has lost relevant truth.

| Case | Pragmatic | Pedantic | Decisive evidence |
|---|---|---|---|
| Extra test coupling | Block | Block | An allowed inline implementation preserves the API behavior and independent behavioral checks but fails the new helper-call assertion. Adequate existing coverage makes deleting the added test sufficient. |
| Contractual delivery count | Approve | Approve | The protocol requires one external delivery with the supplied arguments. The interaction assertion tolerates internal delegation and rejects duplicate delivery. |
| Internal completion carrier | Approve with concern | Block under the additional construction standard | All present producers preserve the law; the new trusted carrier separately maintains one three-field relationship across them and admits forbidden combinations through ordinary construction. Do not invent an external caller or incident. |
| Ordinary subtotal | Block | Block | The loop omits the final price for an ordinary supported list. |
| Revocation during export | Block | Block | The accepted event hook can revoke permission before the second read; the candidate still releases that document. |
| Mandatory codec verification | Block | Block | The candidate's required check is known to have been skipped. The missing mandatory result is not a demonstrated encoding defect. |
| Supported value boundary | Approve | Approve | Malformed constructor input is rejected, the ordinary mutation is prohibited, and the new operation preserves the checked fact. Unsafe state-forging does not establish a supported bypass. |
| Bounded preview observation | Approve with risk | Approve with risk | A combining sequence is visibly severed at the truncation boundary; exact open/export behavior remains intact. The limited consequence is known, not uncertain. |
| Optional durability question | Approve | Approve | Atomic replacement meets current visibility requirements. Device power-loss behavior for an unaccepted future offline mode remains unknown without preventing the current decision. |

The test cases distinguish noncontractual helper coupling from verification of a
required external effect. The helper assertion's permitted-refactor failure is a
test-quality violation in both modes; adequate existing behavioral coverage permits
removal without replacement. The delivery assertion has independent protocol
authority and should remain. Neither mock syntax nor call-count syntax decides
test quality, and neither case establishes a production failure in the candidate.

For the completion-carrier case, the pedantic assessment must still establish the
actual engineering standard's materiality, proportionality, and applicability.
Neither a weaker type name nor the evaluator's desired architecture proves that
claim. Reject a source-supported countercase on its merits only; do not force a
verdict to satisfy this table. A concern/risk boundary disagreement is less
important than retaining the supported observation and the correct merge consequence.

For every case check that pragmatic blockers remain a subset of pedantic blockers,
fixed external obligations remain binding, and the reviewer does not turn optional
improvements into mandatory drafts or risk-acceptance rituals. An unresolved
optional question must not become `INCOMPLETE` merely by surviving discussion.

## Preserve the actual evaluation

Retain each first raw report, delivered instructions, mode, source digest, and
declared runtime settings before adjudicating it. The existing `review_cases.py
record` command can capture these unchanged bytes using the compatible subject
manifest; record the assigned mode and exact instruction hashes in `--context`.
`--arm current-full` applies only when that complete instruction bundle was
actually supplied. An admission-only exercise should preserve its raw report and
context directly and be labeled as such, not promoted to a full-worker result.

Do not retry an unchanged subject until it produces the desired answer. Preserve
misses, incomplete runs, unexpected valid findings, and disagreements. Revise a
fixture only when independent source evidence establishes a flaw, then treat the
revised bytes as a new subject. The published bank becomes calibration material
after its key has been seen; confirm promising behavior on unseen causal structures
before claiming that the mode improves real reviews.

These assets add no production review pass, model judge, score, corpus, or new
merge gate. Fixture probes and model evaluation are separate evidence.
