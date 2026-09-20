# Review-credit admission replays

These offline cases exercise the owner decision described in
[Review-credit admission](../references/review-contract.md#review-credit-admission):
receipt -> adjudication -> accounting -> user/PR summary. They are synthetic
subjects, not new CAS receipts, stored workflow state, or another review lane.

## Run the fixture and grader checks

```sh
node codex/skills/actuating/tests/test-review-credit.mjs
```

The existing `test-reconciler-contract.sh` runner includes this command. It executes
a missing-generated-fixture failure, the same check after fixture recovery, and a
zero-exit skipped-test observation. It checks evidence-only CLI export, evaluator
key isolation, rejection of incorrect structured responses, and malformed input.
It does not execute Actuating or prove that an agent follows the changed guidance.
The grader is test-only; it is not a runtime coverage classifier or credit gate.

## Evaluate the actual owner behavior

```sh
node codex/skills/actuating/tests/test-review-credit.mjs --list
node codex/skills/actuating/tests/test-review-credit.mjs --case credit-01
# Supply only this case output to an isolated owner-adjudication run.
# Save the actual JSON response outside the repository, then:
node codex/skills/actuating/tests/test-review-credit.mjs --grade credit-01 /tmp/credit-response.json
# Evaluator only; never include this output or the test implementation in the run:
node codex/skills/actuating/tests/test-review-credit.mjs --key
```

`--case` includes the current closeout guidance, static review contract, closure
guidance, synthetic evidence, and evaluation response fields. It omits the expected
decision and evaluator rationale. The response fields are for measurement only;
production retains the existing per-request handoff and concise owner basis.

`--grade` checks structured decisions, accounting, completion, and preservation of
the original execution outcome. A match is not a semantic pass: independently
inspect the rationale, evidence equivalence, and both public summaries. In
particular, a scoped credited review may be complete while its original execution
remains blocked. Reject prose that claims the blocked command passed or that a
parent-run test was an independent reviewer confirmation. Do not use keyword
matching or a confidence threshold to decide adequacy.

| Cases | Discriminator |
|---|---|
| 01 / 02 / 11 | Unassessed blocker versus an explicitly adequate static scope, whether optional execution failed or was omitted. |
| 03 / 04 / 14 | Supported evidence reuse versus unspecified ReleaseSafe flags or a stale subject. |
| 05 / 06 / 15 | Actual missing-fixture observation: parent recovery alone versus completed reviewer reasoning versus a genuinely optional check. |
| 07 / 09 | Exact digest without accessible premises; historical receipt without required adequacy evidence. |
| 08 | Exit zero while the required test was skipped. |
| 10 | Held fifth standard preserves earlier valid credit but cannot advance the count or complete review. |
| 12 / 13 | Material findings and missing pre-review proof still invoke existing invalidation rules. |

For a matched comparison, run the same case with baseline and changed workflow
bytes under the same model/settings, without leaking the key. Preserve actual
responses and report disagreements; matching labels alone do not establish efficacy.
Also perform a small disposable real review with an intentionally unavailable
required check and its optional-check control. Observe actual handoff, counts,
and public narration; fixture/grader self-tests are not that live replay. Run in a
separate authorized subject, not by sabotaging a live candidate or bypassing its
sandbox. No new recurring reviewer, review quota, or evidence archive is required.
