# Fresh-Eyes Review Lens

Once again, check over everything again with fresh eyes looking for any blunders, mistakes, errors, oversights, omissions, problems, misconceptions, bugs, etc. Be SUPER thorough and meticulous!

Start from the accepted outcome, not the candidate's architecture or explanation.
Using accessible requirements, independently reconstruct the actors, required
observations, compatibility, effects, and resource constraints of the exact bound
subject. Shared authoritative facts are necessary; incumbent or sibling conclusions
are hypotheses, not substitutes for this investigation.

Inspect the ordinary implementation path and current semantic owner for the same
task. Prioritize changes that create a parallel mechanism, independently writable
truth, new coordination or recovery duties, or a broader interface or supported
mode. Trace the concrete obligation imposed on callers, operators, or later
changes and the accepted requirement it serves. Check what existing enforcement
and host guarantees already supply; passing the new path's local tests does not
establish that this integration remains adequate.

Trace a representative required scenario end to end, then attack a materially
different required case or failure path when supported by the domain. Work backward
from the required outcome: what must be known, distinguished, or controlled for it
to follow, and where does the candidate supply it? Seek a source-permitted case
where the candidate's guarantee holds but that outcome fails. For a consequential
decision, can its available observations merge cases with no common source-permitted
answer? Account for interactions, pending effects, observation age, and actual
authority when they change that answer. Inspect existing paths and protocol
guarantees that may supply the distinction or make one response adequate for all
compatible cases before reporting a defect.

Look for omitted behavior, erased distinctions, integration gaps, unhandled
recovery, and required progress or ordering that can fail while every internal
state remains valid. Neither rejecting legitimate work nor leaving it permanently
pending satisfies the outcome. Ground liveness claims in the actual
scheduler/environment assumptions, not an arbitrary wait or imagined unfair execution.

Then challenge inherited constraints. Is a burden created by the representation,
owner, API, language, runtime, or process rather than the Goal? Is a workaround
still necessary in the current host? Could an earlier adequate boundary, different
representation, or repository-native mechanism expose an omitted case or false
necessity claim? Retain checks for duplicate representations, missing sibling
dimensions, incomplete migrations, and bypasses without adopting the incumbent's
family list as the domain.

Challenge stronger guarantees introduced by the candidate or by review itself.
Established tolerance for stale data, bounded inconsistency, latency, or ephemeral
state remains part of the accepted task. An imagined edge case does not establish
a need for another lock, retry, fallback, or persistence layer. Conversely, missing
requirements are an evidence gap, not permission to assume such tolerance.

Distinguish new independent authority from derived caches, required trust-boundary
checks, independent oracles, and migration paths with an established retirement
condition. Necessary async work, new interfaces, and repairs of an inadequate owner
remain admissible. Judge the obligations and their consequences, not novelty,
line count, or departure from convention alone.

A different admissible construction does not by itself falsify correctness.
It may refute an actual necessity or impossibility claim only when that claim is
identified and the alternative is justified under the same accepted constraints.
Otherwise it is at most a grounded nonblocking opportunity, not a defect. Do not
expand the Goal, reward novelty, or turn this review into successor selection.

For a structural finding, identify the accepted ownership, compatibility, scope,
or resource obligation violated and show the conflicting authority, added duty,
or affected path in the candidate. Such evidence need not invent a runtime
failure. Unjustified complexity without an established violation remains a
grounded nonblocking opportunity; do not manufacture a defect to force reduction.

For each finding, give the required outcome or actual challenged claim, independently
reconstructed scenario, concrete mismatch or justified claim-refuting alternative,
and decisive evidence/countercase. Inspect existing paths and companion changes
that could satisfy the obligation. Missing accessible authority remains a named
evidence gap; do not reconstruct parent-only requirements from a digest.

This search priority does not exclude other concrete in-scope defects. Do not
implement repairs, invoke other skills, or select the successor.

This applies Sean Goedecke's
[blunder-avoidance argument](https://www.seangoedecke.com/to-code-well-avoid-blunders/)
within the existing review: inspect introduced obligations without inventing new
ones or adding another pass.

## Native output (Actuating only)

Return the native structured review object with `findings`, `overall_correctness`,
`overall_explanation`, and `overall_confidence_score`, never a bare status word.
Supported findings retain native `title`, `body`, `confidence_score`, `priority`,
and `code_location` (`absolute_file_path` and `line_range.start`/`line_range.end`).
An empty `findings` array means no actionable defect was established in the
inspected scope, not that validation or the review obligation is complete. Retain
the native correctness vocabulary: `"patch is correct"` with no supported findings,
`"patch is incorrect"` with supported findings. Neither label grants closeout credit.
In `overall_explanation`, state inspected scope and material evidence limitations:
the missing observation, attempted check/mode, actual blocker (or unknown cause),
and affected conclusion. Do not fabricate a code finding for unavailable validation
or report a blocked/skipped check as passed. Actuating owns evidence adequacy and
credit; confidence does not supply missing evidence. Review Fold owns admission.
