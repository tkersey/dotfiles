# Suggested PR review comments

Load for a PR subject's final assessment, after investigation, falsification, and
cross-nomination reconciliation. The coordinator owns these drafts in direct,
prepared-parallel, and mixed execution. This is an output projection of adjudicated
findings, not another review pass, a worker quota, or publication authority.
Explicit requests for summary-only output or no comment drafts take precedence.

## Which findings receive drafts

Provide one suggested comment for each distinct retained actionable PR-related
finding: every real merge blocker, and grounded nonblocking defects, risks, or
justified opportunities with a concrete outcome or verification request. Comment
eligibility does not require a blocking verdict. Keep disposition and merge
consequence beside the draft; do not promote an opportunity to obtain a comment.
Do not turn inherited issues unrelated to the PR, preservation, rejected claims,
or unresolved speculation into inline requests. Retain useful assessment-only
observations in their existing report groups.

Draft only after the finding survives adjudication. Reconcile overlapping worker
findings by cause and obligation, retaining distinct evidence without repeating
the same request at every affected file. Conflicting nominations cannot become
separate instructions to adopt both. Reference the adjudicated finding rather
than repeat its full analysis. An already identified, verified equivalent open
review thread may replace a duplicate draft with a thread link; keep the finding
and explain that choice. This adds no thread-resolution or mandatory thread-audit
workflow, and does not imply uninspected threads were checked.

Incomplete overall coverage does not suppress independently supported, current
findings or their drafts. Preserve the assessment's incomplete status and each
finding's actual uncertainty. A stale finding needs revalidation before becoming
a current-PR draft; retain it only as historical evidence otherwise. Transport
failure alone is not a code defect or an author-facing change request. When no
eligible drafts remain, say why briefly; never manufacture findings to fill a list.

## Verify the location

Use the report's exact repository, PR, base tip, review merge base, and head.
Verify each proposed path, line or minimal range, and diff side against that
reviewed PR diff. Use head-side locations for additions/current code and base-side
locations for deletions, naming the relevant evidence view. For renames, distinguish
the PR diff's path from the old-path evidence. Do not use working-tree line numbers
or an unreviewed prospective-merge file as PR-head coordinates.

A cross-file finding may use a relevant changed causal anchor, with the affected
consumer or boundary named in the text and precise supporting locations in the
finding. Do not force it onto an unrelated changed line merely because the defect
lives elsewhere. If no valid inline anchor exists, retain the finding and body as
a **General PR comment draft — inline location unavailable**, explain why, and
cite the actual evidence locations. Do not invent a diff position or claim a
source citation is an inline anchor. A missing anchor alone does not erase a
finding or make completed architectural investigation incomplete.

Before final output, apply the entry contract's mutable-subject recheck to both
findings and locations. A moved head/base requires affected evidence and anchors
to be revalidated, not just their line numbers translated. Never label historical
coordinates as ready for the current PR.

## Write a copy-ready comment

Use Elenctic's comment discipline without invoking its campaign or importing its
blocker-only output gate: **Be succinct, suggestive, provide the why and use should
not could.** Prefer one or two sentences directed at the code or verification.
State the concrete outcome, evidence-backed mechanism, and why it matters.

For a blocker, request the minimum required outcome rather than mandate an
unproved successor architecture. For a risk, request the specific verification or
clarification and preserve its conditional premise. For an opportunity, make the
nonblocking nature clear in the body as well as the surrounding metadata, and
suggest only the justified improvement with its material constraint intact.
Do not flatten these into equally mandatory requests. Keep substantive migration,
authority, or compatibility qualifications when omitting them changes the advice.

Never put priority/severity rankings, badges, or prefixes in comment titles or
bodies, including imported worker text: no `P0`, `[P1]`, `Priority 1`, `Severity:
high`, or equivalent labels. Preserve literal code identifiers that happen to
resemble rankings. Use repository/domain language; omit skill names, transport
bookkeeping, and private reasoning. Draft prose, not an unverified code patch.

In **Suggested inline PR comments**, give each draft with location and disposition
outside its copyable body:

```markdown
### <Finding title>
Finding: <reference to the adjudicated finding>
Disposition: <defect / risk / opportunity>; <blocking / nonblocking>
Location: `<path>:<line or range>` (<head/base diff side; evidence view>)

> <Subject> should <required outcome or qualified suggestion>, because <mechanism and impact>.
```

For a locationless draft, replace Location with the General PR comment label,
reason, and real evidence locations. For a verified existing thread, give its link
instead of a duplicate body. Omit an empty comment section except for the brief
explanation when a PR assessment has no eligible drafts. Honor caller suppression.
Drafts are for human approval only: never post comments/replies, submit reviews,
mark files Viewed, resolve threads, edit code, or merge.
