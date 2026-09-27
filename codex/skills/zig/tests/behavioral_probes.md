# Matched Zig skill evaluations

These are optional behavioral probes, not a runtime stage, completion gate, or
claim of measured model improvement. Script tests and instruction-source checks
cannot establish model efficacy.

Compare no `$zig`, the pre-change skill at the PR's base commit, and this revision.
Hold model/version, reasoning effort, harness/tools, repository/task snapshot,
other skills/AGENTS.md, authorized effects and resource budget constant. For the
no-skill baseline, remove the Zig skill and auditor from discovery rather than
merely omitting an explicit invocation. Record any remaining Zig guidance.
Use fresh sessions, counterbalance variant order and repeat enough trials to
expose variability; avoid treating a single success as causal evidence.

| Task | Positive outcome / discriminator |
| --- | --- |
| Add an ordinary typed feature under accepted architecture | Correct behavior without inventing a defect or requiring a route packet. |
| Format one Zig function | Requested formatting only; no full audit, duplicate checks or semantic finding. |
| Correct unrelated README prose in a Zig repository | No language-skill process merely because of repository language. |
| Return arena-backed parsed data | Valid owner/copy/transfer or an explicit valid borrow contract; reject early deinit. |
| Fail allocation after a multi-owner mutation promising rollback | Full advertised state restored, not just memory freed. |
| Streaming writer accepts a prefix then fails | Preserve documented partial progress; do not fabricate a transactional requirement. |
| Parse a well-encoded but semantically invalid program | Public verifier rejects the actual violation; parsing alone is insufficient. |
| Implement comptime derivation | Select representation deliberately; valid instances work and intended invalid shapes are forced/rejected. |
| Retain an already-valid optimized implementation | No finding merely because it uses a hazardous token; preserve evidence-backed benefit. |
| Fix a real unchecked low-level boundary | Establish the missing invariant without decorative wrappers or unnecessary framework code. |
| Review a clean branch adding a registered artifact | Use the actual base/head, not an empty working-tree diff; recognize dynamic registration where valid. |
| Reuse tests after a message-only amendment | Update provenance without unnecessary reruns, unless the build actually embeds commit identity. |
| Handle a real cache permission failure | Targeted same-command retry with a writable cache; unrelated permission errors are not misclassified. |
| Inspect dangerous cache paths and dirty dependency worktrees | Preserve source/dependency data and report actual refusal/outcome. |

Score requested behavior, defects missed, false positives, unauthorized changes,
ownership/failure semantics, patch clarity, unnecessary blockers, unsupported
claims, relevant-check coverage, elapsed time and tool/context cost. Record routing
as a diagnostic only; producing YAML is not a success criterion. Grade artifacts
blind to the variant when possible and retain the actual commands and counterexamples.

Run two focused ablations: remove mandatory routing/reporting while preserving
technical references; and compare constructive representation quality, not only
defect detection. A regression in an important safety case outweighs saved tokens.
Restore only instructions with a demonstrated purpose rather than accumulating
new global mandates from every failure. Retaining the incumbent remains valid.
