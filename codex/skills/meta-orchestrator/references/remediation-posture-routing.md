# Remediation posture routing

Use this quick mapping when consuming `adversarial-reviewer` output.

## `validating-check-only`
Meaning:
- the next highest-value action is evidence collection, not code change

Route:
- targeted validation subpass using `verification-closure` discipline
- no code edits first
- re-run full-scope de novo adversarial review after the check

Promote when:
- the check confirms a concrete defect or stronger failure mode

## `accretive-remediation`
Meaning:
- a narrow consequential code or config change can likely close the finding

Route:
- `rigor-doctrine` with tight scope
- preserve existing contracts unless the task explicitly changes behavior
- re-run full-scope de novo adversarial review after remediation

## `structural-remediation`
Meaning:
- the finding cannot be closed reliably by an accretive patch

Route:
- `rigor-doctrine` with a bounded structural brief
- state why a narrower fix is insufficient
- if constraints forbid the necessary change, surface `needs-decision` or `blocked`

## Mixed findings
Prioritize:
1. validation-only findings that can collapse uncertainty
2. the highest-confidence highest-severity material finding
3. compatible accretive bundles that remain reviewable

After any check or fix, re-run full-scope de novo adversarial review.
