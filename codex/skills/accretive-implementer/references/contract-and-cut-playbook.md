# Contract and cut playbook

Use this playbook to keep the change forced, reviewable, and provable.

## Contract
- State what working means in one sentence.
- Prefer an executable contract or proof target.
- If the contract is materially ambiguous, choose the safest bounded interpretation and label it.

## Invariants
- Name what must remain true.
- Name what should become impossible after the change.
- Prefer enforcement in this order when it fits: construction/type boundary, parse/normalize/refine at the edge, tests/assertions, temporary diagnostics.

## Chosen cut
For non-trivial tasks, determine:
- **Stable boundary**: where the rule should live
- **Not smaller**: why a smaller edit would leave the bug class, ambiguity, or drift alive
- **Not larger**: why a broader rewrite is unnecessary for this contract
- **Proof signal**: the fastest credible local check you can actually run

## Truth-surface audit
When the repo has multiple “truth surfaces,” compare:
- public claim
- runtime enforcement
- proof harness
- checked artifacts

If they disagree, fix the mismatch before polishing ergonomics or comments.
