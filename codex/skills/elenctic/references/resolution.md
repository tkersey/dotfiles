# Numbered findings and resolution units

This is coordinator presentation after the ordinary campaign, not a second review,
worker lane, public standalone workflow, or automatic fix loop. SKILL.md owns
selection of `comments` (default) versus explicit `resolution`. Store that selection
in the existing campaign working set and report's `workflow`; no author-based switch.
Resume preserves it unless explicitly changed. Mode changes do not rerun complete
reviews or alter selection, concurrency, provenance, coverage or mutation authority.

## Keep the original finding references

First finish reconciliation, deduplication, blocker falsification, discussion-delta
comparison and eligible comment/follow-up drafting. Keep supported findings even
when commentary is not novel or no valid inline anchor exists. All retained blockers,
risks and concerns remain visible with their own evidence and disposition.

Assign one canonical positive finding number to each reconciled finding's existing
opaque ID. Preserve already established coordinator numbers; worker-local lists are
provenance, not a shared number namespace. On first assignment use the ordinary
blocker/risk/concern order. Thereafter reuse the ID-to-number association regardless
of sorting, severity order, group, file, line or title. New findings get unused numbers
after the highest ever assigned in this campaign; withdrawn numbers are not recycled.
A changed evidence fingerprint reopens handling, not the finding's number.

Record this association in the existing working set, serialize `number` on each
finding, and preserve the report's `finding_numbers` history when regenerating.
The renderer also merges the existing same-path report's number history and rejects
renumbering/reuse. Do not invent missing original numbers from the current array
position. Legacy unnumbered comment reports remain readable; recover their original
coordinator references before claiming original-number resolution groups. An
unrecoverable association is a presentation gap, not a reason to fabricate numbers.

Use the same explicit `#2`, `#5`, `#8` references in the terminal finding headings,
blocker index, HTML cards and group handoffs. The coordinator's canonical references
replace local list ordinals, not finding evidence. Put references in report/location
metadata, not inside the rank-free proposed comment. Markdown auto-numbering must
not disguise preserved gaps. Worker v1 report identities remain unchanged.

In `comments`, stop this step after number binding: no resolution groups or helper
invocations are added by this feature. Continue normal report delivery.

## Synthesize only after the findings and drafts exist

In `resolution` with retained findings, the coordinator must load and apply the
actual installed `$glaze` skill, then the actual installed `$metanoetic` skill to
this grounded synthesis. Follow each skill's complete current contract and apply
its canonical passage unchanged. Do not copy the passages into Elenctic, imitate
invocation with a label, or replace either with a summary. Both receive the complete
reconciled findings, source evidence, counter-cases, accepted obligations, non-goals,
compatibility constraints and eligible drafts, not only the short draft text.

Resolve these two skill sources from the actual installed skills root retained by
the coordinator, not from the repository under review or the frozen review bundle's
absent siblings. They are post-adjudication synthesis helpers, not review-policy
sources or additions to the workers' immutable seed. Record their actual source
paths/content identities with the synthesis in the current working set. Use one
consistent observed pair for that synthesis. Installation or finding changes that
materially affect grouping require refreshed synthesis, not invalidation of otherwise
valid review evidence. Do not mutate the review snapshot to add late helper history.

Ask: **What coherent changes satisfy these findings without defaulting to one patch
per comment, preserving an unnecessary design, or demanding an unjustified rewrite?**
Use Glaze for resourcefulness and Metanoetic to challenge assumed constraints,
fragmented ownership and accretive repairs. Consider a shared boundary, deletion,
representation change or transition correction when evidence supports it. Grouping
is not required to be architectural; a small local correction or singleton is valid.
No prior alternative, fixed number of groups, new evaluation lane or repeated
encouragement loop is required. Reuse unchanged synthesis on resume; new relevant
evidence permits further inquiry and revision.

Select units by a concrete shared resolution objective: a missing guarantee,
competing owners, a coupled transition or a compatibility-preserving coordinated
change. Shared files, topics, wording or one speculative repair are not enough.
Distinct findings may share a unit without being deduplicated or losing their
individual satisfaction conditions. Do not force unrelated work together for fewer
groups or create one group per comment without considering evidenced coupling.

## Output a lossless grouping

Every retained finding belongs to exactly one unit, including draftless blockers
and nonblocking findings. Preserve its number, disposition, evidence, uncertainty,
existing discussion and original eligible draft. Use singleton units where appropriate.
A shared group never turns optional work into a merge prerequisite. State optionality
in its objective/completion checks; a unit may be mixed or entirely nonblocking.
Dependencies express actual coordination, not new gates or redundant membership.

Each unit has a stable `R1`-style ID, a meaningful title, original finding references,
why those findings belong together, a resolution objective with required constraints,
one completion-evidence description per constituent finding, and dependencies only
where evidenced. Dependencies must reference real units and be acyclic. Preserve
unit IDs while their resolution purpose remains the same; do not reuse a retired
unit ID for unrelated work. Membership changes remain explicit in the current report.
No separate group-completion record is maintained: progress is derived from findings.

Example terminal output (illustrative, not template findings):

```text
R1 — Establish one cancellation and recovery owner
Address findings #2, #5 and #8.
Why together: ...
Resolution objective: ... (preserve compatibility; #8 remains optional).
Completion evidence: #2 ...; #5 ...; #8 optional ... .
Depends on: none identified.
```

Deliver the original numbered report and eligible drafts unchanged, plus these
units before the report identity/final decision. The HTML view uses the same mapping
and can copy a handoff containing R1, #2/#5/#8, the campaign/head and their evidence.
The receiving implementation task must revalidate the candidate and obtain its own
authority; producing or copying a handoff does not execute it.

## Keep judgment and availability independent

The synthesis may propose a coordinated direction beyond the reviewers' diagnosis,
but cannot silently reject/reclassify findings, weaken obligations, choose an
unauthorized replacement architecture, invent requirements or create code blockers.
If it uncovers material counterevidence or an unreviewed path, return that evidence
to ordinary adjudication/continuation, update the report on the evidence, then rebuild
affected groups. Grouping alone neither proves a fix nor changes the review verdict.

With no retained findings, emit complete empty groups and do not invoke helpers for
an empty task. This is not vacuous approval. A scoped interim/incomplete report may
group available findings, but must retain its actual coverage and unfinished-work
notice; it cannot abandon runnable review work just to deliver groups.

If either helper is unreadable, do not pretend both ran or silently substitute generic
grouping. Continue available recovery within authority; when actually obstructed,
report `resolution.status: unavailable` and its reason alongside all original findings.
Likewise disclose a genuine synthesis gap rather than incomplete groups labeled
complete. Synthesis availability is separate from verdict/coverage. Recheck the exact PR epoch and relevant discussion after synthesis and before
delivery; changed evidence returns to ordinary adjudication and stale findings are
not current-head proof. Text-only requests still permit textual grouping when evidence is available, without creating artifacts.
