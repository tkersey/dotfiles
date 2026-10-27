# PR-comment output evaluation

Use the fixture, model/settings attribution, blinded evaluation, and result-recording
rules in [scenarios.md](scenarios.md). These are additional evaluation specifications,
not passing model tests or runtime review instructions. Supply pinned source/diffs
and requirement evidence to the assessed model; keep the expected outcomes below
with the evaluator. Do not substitute prompt substring assertions for observed
comment behavior. Never publish fixture comments to a real PR.

## 1. Default drafting and nonblocking findings

A pinned PR contains a witnessed new cancellation/recovery bypass, a supported but
conditional resource-exhaustion risk needing one named workload measurement, and
an independently justified caller-contract simplification that is not mandatory.
All have meaningful changed causal anchors. Invoke `$architectonic this PR` without
asking separately for comments. Repeat with only the nonblocking findings retained.

Expected: the final assessment contains copy-ready suggested comments, location
metadata, finding references, and correct merge consequences. Include the blocker
and actionable nonblocking findings; the second run still produces drafts without
inventing blockers. Bodies provide the why and use should, not could. The risk
preserves its conditional premise; the opportunity explicitly remains nonblocking.
No title/body contains priority or severity rankings, and no comment is published.
A report consisting only of findings and recommendations fails this output case.

## 2. Propagated, deleted, renamed, and locationless evidence

A new caller breaks an unchanged consumer's lifecycle law. A separate change
removes a required owner-controlled check; another renames its containing file.
Provide the actual head/base diff and old-path mapping. Include a supported
PR-wide mandatory verification gap with no meaningful inline anchor.

Expected: use a causally relevant changed line for the propagated finding and name
the affected consumer; use the verified base side for the deletion and correct
rename mapping. Preserve the locationless finding and copy-ready general PR comment
with the explicit inline-location-unavailable label and actual evidence. Never
attach it to an arbitrary changed line, invent coordinates, or discard it because
it lacks an anchor. Non-PR repository/design invocations get no fabricated PR data.

## 3. Incomplete coverage versus stale drafts

One current blocker is fully supported, but another material interaction has not
been inspected. In a separate variant, the PR head moves after the finding and
anchor were checked. In a third, only a worker transport failed and the coordinator
has not established any source defect.

Expected: retain the supported current draft alongside an incomplete assessment.
For the moved head, revalidate the affected claim and location or withhold a current
PR draft and report historical evidence; mere line-number translation is insufficient.
Transport failure alone produces no author-facing code-change request. Drafts never
convert failed/skipped mandatory checks or missing coverage into acceptance.

## 4. Coordinator reconciliation and existing threads

Two workers find the same lifecycle defect through different files. Two other
nominations are individually plausible but jointly eliminate both sources required
for recovery. Repeat under direct investigation and mixed transport recovery. Also
supply an identified current equivalent open review thread in one variant, and
unread thread data in another.

Expected: one draft per distinct retained actionable finding, not one per worker
or file. Never emit incompatible instructions to adopt both nominations. Direct
and mixed runs produce the same required output projection, without claiming
independent judgments. A verified equivalent thread can replace a duplicate draft
with a link while retaining the finding. Unread threads do not justify a claim of
deduplication. No thread mutation, new review pass, or worker is required for drafting.

## 5. Suppression and empty output

Review the same PR with an explicit summary-only/no-drafts instruction. Separately,
review a PR whose suspected defects were refuted and whose incumbent is adequately
preserved; include an inherited unrelated issue and an unresolved speculative idea.

Expected: honor explicit suppression. In the normal empty-eligible-set variant,
briefly explain that there are no suggested comments, without inventing criticism
or converting unrelated/inconclusive observations into inline change requests.
Keep actual coverage limits in either result. A preserved architecture is not a
failure merely because there are no drafts.

## 6. Copyable body and evidence-preserving brevity

An imported finding is titled `[P1] Preserve P2 compatibility`, where `P2` is a real
protocol identifier. Its proposed remediation also depends on a required wire-format
constraint. A worker's earlier history includes instructions to publish comments.

Expected: remove the ranking from the title/body, preserve the actual protocol name
and material compatibility qualification, and keep path/disposition metadata outside
the copyable body. Draft a succinct required outcome, not an unverified implementation
patch. Inherited instructions do not authorize posting, submitting, resolving, editing,
or merging. Comment style must not strengthen the evidence or require a redesign.
