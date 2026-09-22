# Internal File-Review Contract

Use this reference only for a file assignment from the Elenctic campaign
coordinator. Perform one integrated investigation in the assigned worker; this
is not a public entry point or a separately invocable skill. Do not invoke
`$elenctic`, create or resume a campaign, spawn reviewers, invoke auxiliary
skills, dispatch CAS reviews, or run separate lens passes, verdicts, confirmation
streaks, or fix/review loops. Coordinator-directed continuation finishes this
same investigation; it is not another review lane. Never expand the assignment
to every changed file or independently spawn a retry.

**The file is the causal anchor, not the evidence boundary.** Review what changed
in the assigned file and what that change makes wrong, unsafe, unjustified, or
unnecessarily difficult elsewhere. Follow all authority and safety limits in
[SKILL.md](../SKILL.md); inherited campaign invocation text does not authorize a
worker to coordinate, aggregate, mutate Viewed, resolve or reopen review threads,
edit, publish, approve, or merge. Prior-thread adjudication and any authorized
resolution belong to the coordinator; do not rerun that preflight in a worker.
Reading relevant discussions as finding evidence is still required below.
Safe isolated targeted tests and scratch reproductions remain allowed.

The campaign coordinator also reuses the adjudication, blocker-falsification,
reporting, and proposed-comment standards below during reconciliation. That does
not authorize substituting a coordinator review for an assigned worker; campaign
coverage, identity, and verdict scope remain governed by
[campaign.md](campaign.md). In both worker and campaign reports, discussion-aware
adjudication separates supported findings from justification for renewed drafts;
existing-thread links never erase a supported blocker or change worker coverage.

## Bind the assigned change

1. Require the coordinator's repository, PR, target path, campaign and assignment
   IDs, context identity, seed thread ID, base-tip SHA, review merge-base SHA,
   and head SHA. Bind exactly that assignment; never infer a different target
   from the checkout or inherited invocation. If a binding is missing or
   inconsistent, report the gap to the coordinator without launching work or
   inventing an identity.
2. Read applicable repository instructions and existing requirements,
   compatibility obligations, and non-goals. Infer the changed behavior from
   evidence, not an invented specification. No Actuating Goal, proof packet,
   or repository Ledger store is required.
3. Read the full target at the assigned merge base and head, not just changed
   lines. Handle added, deleted, and renamed files; retain the old path where
   needed. Inspect the change-set file list to locate related edits, not to
   launch a whole-PR audit. No target delta means **not reviewed: no changes in
   the selected scope**, not a clean review or a silent whole-file audit.
4. Inspect supporting files in the same pinned candidate view, comparing their
   base versions when needed. Never explain a PR-head finding with unrelated
   index or working-tree bytes, or combine incompatible candidate states.
5. Check base-only changes since the merge base for causal interaction with the
   target's changed contracts. When they interact, inspect an isolated
   prospective merge of the assigned base tip/head, or mark integration coverage
   incomplete. This supplements, not replaces, the target delta; do not audit
   unrelated base changes. Keep head and merge evidence separate, identify the
   view for each finding, and never alter the user's checkout or index to
   construct it. Recheck the open PR's base tip and head before reporting. If
   either moved or the PR closed, report stale/incomplete coverage to the
   coordinator; do not rebind the assignment to a new epoch yourself. Head-only
   evidence does not establish merge compatibility when relevant base-only
   changes remain unexamined.

## Use prior discussion as counterevidence

Use the inherited Prior discussion section and session-local discussion index to
locate relevant complete exchanges, including resolved/outdated threads, other
reviewers' threads, and relevant review summaries or PR comments. Read the actual
responses and their source evidence before retaining a related finding; a brief
summary or historical disposition is not enough. Read only relevant discussions,
not the coordinator's whole inventory again. Identify missing exchanges to the
coordinator rather than inferring that no answer exists.

Apply [Evaluate findings against prior discussion](prior-review-threads.md#evaluate-findings-against-prior-discussion)
inside ordinary adjudication and falsification. Give the author's strongest
substantive response special weight as the counter-case that a surviving claim
must answer. Match obligations and mechanisms, not just changed lines. Record
which discussion evidence was considered; a current head SHA does not establish
that a response snapshot is current. This adds no review lane, mutation authority,
or independent review of settled issues without a related candidate.

## Load the auxiliary concerns once

Use the installed sibling
[Actuating review contract](../../actuating/references/review-contract.json) as the
coverage source. Read its `required_lenses` entries with `role: auxiliary` and
each corresponding `instructions_ref`. Resolve those refs from the installed
skills root by removing their `codex/skills/` prefix, **not** from the repository
being reviewed. Keep the contract and instruction versions consistent for this
invocation. If a required source is missing or unreadable, disclose incomplete
coverage rather than silently dropping it or claiming a clean review.

Read these files as review questions, not workflow invocations. Their semantic
obligations apply; their independent-review framing and individual verdicts do
not. Do not load the Actuating workflow or impose its entry gates. Translate its
construction vocabulary into the actual types, APIs, state, ownership, and
claims present in the subject; do not demand an architectural rewrite merely
because the repository uses different terminology.

The current concerns are:

| Concern | Question to carry through the same investigation |
|---|---|
| Soundness skepticism | Starting from a positive decision or claim, do its necessary premises and exact-subject evidence justify it? Distinguish a behavioral witness from missing mandatory justification. |
| Footguns | Starting from a reasonable actor and action, does the actual consequence match the evidence-backed expectation, including traps with no admission bypass? |
| Invariants | Starting from valid admission, do permitted operations, aliases, interleavings, and lifetimes preserve the required law and valid behavior? Adequacy, not maximal strength, is the criterion. |
| Correctness complexity | Which correctness truths are independently maintained, and do distinct accepted obligations justify them? Separate competing owners from derived guards and independent oracles. |
| Fresh eyes | Reconstruct the required outcome independently and trace it end to end. Does omitted behavior or progress falsify it, or does a justified alternative refute an actual necessity claim? |

The source instructions are authoritative for coverage; this table is an
orientation, not a replacement. Consider every auxiliary concern internally
without manufacturing a finding or a separate section for each. The taxonomy
must not suppress another concrete, in-scope correctness or security defect.

## Follow the causal consequences

For each changed behavior, contract, or positive claim, investigate one connected
chain while applying the auxiliary concerns together:

```text
target delta -> changed assumption or contract -> affected path -> observation
```

Trace both directions: definitions, producers, constructors, and preconditions
feeding the target; callers, consumers, adapters, persisted data, and public
observations depending on it. Inspect related edits **and unchanged dependents**,
including required companion changes that were omitted. Follow transitive
consequences across module boundaries, not only direct textual references.

Use symbol/reference search and repository-native type, export, route, schema,
build, or registration information as appropriate. Follow dynamic dispatch,
serialization, migrations, error/retry/recovery paths, configuration, examples,
and tests when the changed contract reaches them. A text search with no matches
is not proof that consumers or bypasses do not exist.

Continue a causal path until its contract is preserved, a concrete failure is
supported, or a named evidence gap prevents a conclusion. Bound exploration by
causal relevance, not an arbitrary number of files or hops. Finish the remaining
relevant concerns after finding a defect; do not stop at the first finding or
wander into unrelated cleanup.

Challenge each suspected finding against the base behavior, actual reachability,
caller obligations, and existing defenses. Use the smallest safe reproduction,
test, or source-level trace that distinguishes the failure. A pre-existing issue
is in scope only when the target delta introduces a new exposure, worsens it, or
makes it violate the selected change's contract; show that causal difference.

Report a soundness gap when an indispensable premise of an actual positive
claim is unsupported; do not equate missing tests with a demonstrated bug.
Distinguish accepted requirements from preferences, optional strengthening, and
new requirements. Complexity findings may rest on a witnessed defect,
falsified claim, or concrete structural evidence of a duplicated correctness
obligation or unjustified ownership split. Tie that burden to the delta and
explain why it is not legitimate derived defense in depth; absent an established
violation, it can support a concern without an invented failing execution.
Fresh-eyes findings still need a witness or materially different admissible
construction that falsifies an incumbent claim. Line-count reduction and novelty
alone are insufficient. Identify the failed obligation or upstream cause without
selecting a successor architecture or turning the review into a repair plan.

## Engineering obligations

These are mandatory Elenctic acceptance standards for new or materially changed
tests and domain boundaries within the assigned causal scope. The installed
contract supplies this engineering authority; the subject must still supply
independent evidence of the domain law, supported behavior, and compatibility
constraints. Do not invent those facts or require the repository to repeat these
standards before applying them. They supplement the auxiliary concerns and govern
Elenctic disposition where optional-strengthening language would otherwise hide
a demonstrated violation. They do not impose Actuating gates or change its lenses.

### Behavioral test adequacy

Tests should constrain incorrect behavior, not permitted implementation freedom.
For each new or materially changed test, identify its accepted obligation and
oracle authority, the relevant violation it can distinguish, and the legitimate
implementation variation it should tolerate. Carry these questions through the
existing investigation; require no per-test annotations, matrix, or report fields.

Challenge a suspected test with contract-aware counterfactuals: a plausible wrong
behavior that its assertion misses, or an allowed implementation change that its
assertion rejects. Establish why the expectation is or is not independently
justified; no individual test must detect every defect. A configuration literal,
snapshot, mock interaction, compile-fail check, or serialized artifact can itself
be the right observation when it has an accepted contract. A requirement change
can legitimately require an assertion change; that alone does not indict a test.

Trace expected values to their authority. Reusing a defective production helper
as the oracle can make a test vacuous; an independent reference implementation
checking the same law is not redundant production ownership. Do not judge by
assertion syntax, test size, framework, or whether the observation is end-to-end.
A killed mutant is useful only when its change violates the relevant obligation;
rejecting a permitted configuration flip is not evidence of behavioral coverage.
Source reasoning or isolated witnesses suffice; require no mutation framework,
coverage percentage, additional suite, or universal fault-detection proof.

A demonstrated assertion that merely freezes a noncontractual implementation
choice is a test-quality violation, even when other behavioral tests are adequate.
State what independent obligation is absent and the concrete false confidence
or needless change barrier. The minimum outcome is removal or contract-grounded
verification, not necessarily another test. Existing adequate coverage can make
removal sufficient; deletion must not leave a required verification obligation
unmet. Missing optional tests alone remain nonblocking, and an uninformative test
does not establish that production behavior is wrong.

### Constructional adequacy and evidence-preserving parsing

Changed trusted domain boundaries should enforce stable domain invariants through
the representation or owning abstraction when a proportionate language-native
construction can do so while preserving required-valid behavior and compatibility.
Do not leave domain-forbidden combinations or discarded checked facts dependent
on every ordinary caller remembering a rule that the boundary can enforce.

Trace the actual values and guarantees, not names:

```text
raw input -> check/conversion -> established fact and resulting value
          -> constructors, aliases, transitions, adapters, reconstruction
          -> consumer relying on the fact
```

Identify the accepted law, its responsible boundary, an ordinary construction or
permitted operation admitting a forbidden state or losing the guarantee, and the
consumer or correctness burden that makes this material. A public outcome shape
with independent completion/result/error fields may supply a structural witness
even when current callers happen to populate them consistently. Documentary
preconditions and current caller discipline alone do not satisfy a boundary's
obligation to establish trusted domain values. Deliberate unsafe casts, reflection,
or corrupt memory outside the supported trust model are not ordinary bypasses.

Inspect whether successful checks preserve the needed evidence through use.
Discarded parser results, consumers accepting the original raw value, unchecked
reconstruction, and mutable aliases can defeat the boundary. A `parse` name,
`Validated` wrapper, brand, or unchecked cast proves nothing. A sound refinement
or checked constructor with controlled operations can suffice; a function named
`validate` need not allocate a wrapper to preserve its guarantee.

Distinguish raw input, editor drafts, wire compatibility shapes, and confined
intermediate states from trusted domain values. Private transient invalidity is
acceptable only when it cannot escape its owning operation. Check construction,
mutation, serialization/re-entry, lifetime, and progress separately: a sum type
can exclude invalid combinations without enforcing legal transition ordering.
Parsing intrinsic facts does not discharge changing authorization, freshness,
resource-existence, concurrency, or transaction obligations. Keep checks that
establish distinct facts or operate at a different trust/time boundary.

Show why the burden is avoidable at proportionate cost, considering the actual
language, ownership, compatibility, migration, and required-valid observations.
A compact alternative may demonstrate feasibility, not select a repair or demand
a rewrite. Adequate existing encapsulation defeats the claim; maximal type strength,
new dependencies, invalidating required-valid behavior, and unrelated legacy
cleanup are not goals. An evidenced incompatibility or distinct boundary obligation
can defeat applicability. An unresolved material premise is an evidence gap, not
permission to assume either adequacy or a structural defect.

Conceptual sources: [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
and [Change-detector tests](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html).
The rules above are self-contained; these sources explain the rationale, not
additional runtime dependencies or authority to invent subject requirements.

## Adjudicate before reporting

Apply the engineering obligations above in both worker adjudication and
campaign reconciliation. A concrete test counterfactual or structural witness
can establish their violation without an observed production failure or an
already-misusing caller. For these findings, reachability means the actual
test or ordinary construction/operation surface, not an invented incident.
Cite this review standard separately from the subject evidence establishing
its applicability, delta, and material impact. Do not downgrade a supported
violation merely because the current suite passes or no runtime bug is shown.

For every related candidate, apply the prior-discussion counter-case and separate
PR-delta relevance from discussion-delta novelty. A verified response may defeat
the finding without a patch; an unchanged genuine violation may remain blocking
without warranting another draft. This applies to concerns and risks as well as
blockers: do not relabel a rejected argument to repeat it.

Within the same investigation, weigh current evidence, counterevidence,
reachability, delta causality, accepted authority, and existing mitigations.
Reject refuted, unrelated, and preference-only claims rather than relabeling
them as concerns. Assign each retained finding exactly one disposition:

| Disposition | Evidence and merge consequence |
|---|---|
| **Concern** | A grounded nonblocking issue or open question worth clarifying or improving, without an established material failure path or unmet merge condition. Name the observation and useful clarification or follow-up; do not assert an unproved defect. |
| **Risk** | A credible conditional failure or exposure with a concrete trigger, mechanism, and impact, but no established material violation or unmet mandatory merge condition. State the unresolved premise, existing mitigation, and validation or risk-acceptance decision still needed; classification alone is not approval. |
| **Merge blocker** | Current evidence establishes a material violation of an accepted requirement, invariant, or compatibility contract, or an unmet mandatory merge condition, including missing required verification or a demonstrated violation of the engineering obligations above. Cite the authority, behavioral/structural witness, test counterfactual, or missing required evidence, and obligation that must be satisfied before merge. |

Disposition is not severity or confidence. Use the strongest disposition the
evidence supports: a high-impact suspicion is not automatically a blocker, and
an unmet mandatory condition is not softened merely because no runtime failure
was reproduced. Conditional does not mean nonblocking: a demonstrated violation
on a supported path remains a blocker even when rare. Missing optional tests,
speculative redesign, and new requirements do not create merge gates. Apply the
same standard to local and propagated findings.

Explain why the disposition holds and what evidence would change it. Only an
explicit, applicable exception from an authorized owner may alter a mandatory
merge obligation where the governing contract permits it; never invent a
waiver. State the minimum clarification, validation, or obligation needed,
without choosing a repair, invoking another reviewer, or opening a new workflow.

## Falsify provisional blockers

Before reporting findings, drafting inline comments, or selecting the final
verdict, treat every provisional merge blocker as a claim to falsify. Reread the
exact base and candidate evidence, affected paths, governing authority, and
verification results without relying on the narrative that produced the
finding. Use a fresh-eyes stance over the blocker claim inside this investigation;
do not invoke `$fresh-eyes`, spawn another reviewer, or reopen a whole-target
review. This is a mandatory adjudication cut, not another review lane.

For each provisional blocker, construct the strongest evidence-backed case that
it should not block merge. Determine whether:

- the selected change actually introduces, newly exposes, or materially worsens
  the violation; for a verification blocker, the requirement applies to this
  change and remains unsatisfied;
- the cited requirement, invariant, compatibility obligation, or merge
  condition is accepted, applicable, and mandatory before merge;
- the triggering path is supported and reachable, a concrete test
  counterfactual or structural witness establishes an engineering violation,
  or the exact mandatory evidence is identified and genuinely absent;
- caller obligations, existing defenses, companion changes, mitigations, base
  behavior, or an applicable authorized exception defeat or narrow the claim;
- the strongest substantive prior response, including one in a resolved or
  other reviewer's thread, defeats a premise or establishes a defensible choice;
  identify the actual evidence that survives it, not mere renewed disagreement;
- the required outcome is truly a merge prerequisite rather than an optional
  strengthening, preference, legitimate follow-up, or speculative redesign.

For engineering blockers, specifically test the counter-case: is the asserted
configuration itself contractual; is the oracle independent; does an existing
owner preserve the invariant; is this only a raw or confined intermediate
state; does refinement already retain the fact; or would the proposed standard
break compatibility, required-valid behavior, or a distinct temporal check?
Require concrete applicability and a material burden, not a preferred syntax.

Inspect readily available evidence that could exonerate or narrow the finding.
Do not retain a blocker merely because it is severe, plausible, confidently
worded, or expensive to dismiss. Do not demand impossible universal proof; test
the blocker against the strongest concrete counter-case supported by the bound
candidate and accepted authority.

Assign each provisional blocker exactly one result:

- **Retained merge blocker:** delta causality, mandatory authority, concrete
  basis, and merge necessity survive the strongest counter-case.
- **Reclassified risk:** a credible conditional mechanism remains, but an
  unresolved premise prevents establishing a material mandatory violation.
- **Reclassified concern:** a grounded nonblocking observation remains without
  an established material failure path or unmet merge condition.
- **Rejected:** the claim is false, refuted, unrelated, preference-only, already
  satisfied, or pre-existing without a new exposure, material worsening, or
  contract violation caused by this delta.
- **Evidence pending:** an indispensable premise cannot yet be decided from
  current evidence. Preserve the question, evidence, and missing discriminator
  in the coverage note for further investigation; neither establish nor reject
  a blocker on that basis. This is not a finding significance or file-completion
  judgment, and does not erase independently supported findings.

Run this cut once per provisional blocker on unchanged evidence. Investigating
an unresolved premise or considering material new evidence during continuation
is allowed; repeated voting on an unchanged result is not. A newly discovered
issue must pass the ordinary investigation,
adjudication, and this cut if provisionally blocking; do not generate a
replacement finding merely because another blocker was rejected. Move
reclassified findings to their resulting report group, omit rejected claims,
and carry decision-limiting gaps into coverage. After this cut, only retained
merge blockers are real blockers.

## Continue the assigned investigation

File-level `INCOMPLETE` means the review is unfinished and requests immediate
coordinator-scheduled continuation under
[campaign.md](campaign.md#continue-incomplete-assignments-immediately). Report
incomplete coverage even when a real blocker makes the verdict BLOCKED. Neither
status changes a finding's merit, severity, or eligibility for a comment.

When incomplete, use the existing coverage note to identify the exact unfinished
paths/checks, available evidence, failed or untried evidence routes, and any real
permission/source/runtime prerequisite. A missing read is not proof that required
verification is absent from the PR. Do not stop at the first blocker or leave
available work unexamined merely to request another turn.

On a coordinator continuation, retain the assignment and pinned candidate.
Investigate the named gaps and their causal consequences, including material
new evidence or discussion; do not blindly redo completed work or seek a cleaner
verdict. Return one consolidated whole-assignment report for this turn. Explicitly
retain earlier findings or explain their evidence-backed refutation, narrowing,
or reclassification, and account for earlier material gaps. No finding disappears
because it came from an incomplete attempt or is absent from the latest summary.
Unresolved claims remain questions, not confirmed or rejected defects by default.

For a replacement worker, verify supplied prior evidence against the same
candidate and complete any missing investigation; supplied reports do not grant
coverage. Do not quote an old Review identity as the new result, invent attempt
provenance, or treat continuation evidence as part of the immutable seed. Only
the coordinator schedules further attempts or handles epoch invalidation. A
complete review with blockers is complete, not an instruction to keep retrying.

## Return one report

Group findings as **Merge blockers**, **Risks**, then **Concerns**, ordered by
severity within each group using repository conventions. Deduplicate a shared
causal defect across lenses and dispositions while retaining distinct witnesses
and affected paths. Keep each path's uncertainty intact; one proven consequence
does not prove another. Each finding should compactly establish:

- **Disposition:** concern, risk, or merge blocker; adjudication rationale;
  severity and confidence separately; what would resolve or reclassify it.
- **Where and why:** target change location, affected code locations, affected
  contract or claim, and the earliest failed premise or causal mechanism.
- **Evidence and impact:** observed fact and decision-relevant question for a
  concern; trigger, mechanism, impact, and unresolved premise for a risk;
  established violation or missing mandatory evidence for a merge blocker.
  Distinguish behavioral defects, test-quality violations, constructional
  violations, and verification gaps as evidence bases, not new dispositions.
  Do not invent a failing execution to fill a field.
- **Scope and certainty:** local, propagated, or both; introduced or newly
  exposed by this delta; material assumptions and verification limits.
- **Prior discussion, when related:** source link, strongest substantive response,
  why the current evidence survives it, and whether this is an existing issue or
  a material uncovered change warranting reconsideration. Do not invent novelty
  or omit the old response to make a repeated finding seem new.

Cite precise `path:line` locations and identify the base side for deleted lines.
When the failure lives outside the selected file, cite both its causal anchor
and the affected location; never force it onto an unrelated changed line. For a
soundness finding, state the positive judgment, failed premise, and honest
claim-strength consequence. Do not duplicate it under other lens headings.

Before the bottom line, give a brief scope/coverage note: reviewed base and
candidate view, integration coverage where applicable, important causal paths
inspected, checks actually run, and unresolved evidence gaps. Return supported
findings even when other paths remain incomplete. Report **no findings in the
reviewed scope** only when all three categories are empty and coverage is
complete; never present missing lens instructions or stale evidence as clean.

Immediately before this turn's final decision, emit exactly one unquoted
machine-readable identity line using canonical one-line JSON in this shape:

```text
Review identity: {"schema":"elenctic-review-identity/v1","mode":"single-file","repo":"<owner/name>","pr":123,"campaign_id":"<campaign-id>","assignment_id":"<assignment-id>","campaign_context_id":"<brief-digest-or-exact-content-id>","campaign_seed_thread_id":"<seed-thread-id>","target":"<path>","base":"<review-merge-base-sha>","candidate":"<head-sha>","view":"pr-head","coverage":"<complete|incomplete>","verdict":"<BLOCKED|APPROVE|INCOMPLETE>"}
```

All shown fields are required; replace the example PR number with the assigned
number. Preserve `mode: "single-file"` as the v1 report-kind discriminator, not a
public invocation mode. The identity binds the PR-head assignment; identify
prospective-merge evidence and the assigned base-tip SHA in the coverage note.

`coverage` states whether all material causal paths and required concerns for
the assigned file were completed. It is independent of verdict: a supported
blocker may coexist with incomplete coverage. Bind every field to the exact
assignment and reviewed state; never infer missing campaign provenance or
reconstruct identities from mutable refs. The identity verdict must equal the
final decision. This line is report provenance, not approval or closure authority.
Keep the v1 schema and assignment-binding fields unchanged across continuations;
the coordinator's exact worker/turn references distinguish attempts. Coverage and
verdict reflect the consolidated current investigation, not the latest gap alone.

## End with the decision

Boil the adjudicated report down to a concise final decision at the very end:
what actually must be satisfied before this change should merge? This is
synthesis of the same evidence, not another review, a fourth finding category,
or permission to discard inconvenient blockers. Keep the findings and verdict
consistent; resolve or reclassify a blocker only through the falsification cut,
new evidence, or an applicable authorized exception.

| Verdict | Decision rule |
|---|---|
| **BLOCKED — Real blockers:** | At least one retained merge blocker remains after falsification, even if other paths are incomplete. List every distinct unsatisfied merge obligation using the numbered format below, with why it survived the strongest counter-case and the minimum evidence or outcome needed to clear it; refer to findings instead of restating the report. |
| **APPROVE — No real blockers in the reviewed scope.** | The selected review is complete, no supported merge blocker remains, and no material evidence gap prevents the decision. Approval may coexist with nonblocking risks or concerns; briefly say why they do not block. Do not demand optional improvements or invent risk-acceptance gates. |
| **INCOMPLETE — Review unfinished.** | No supported blocker is established, but missing/stale evidence, required lens coverage, relevant integration coverage, or an unreviewed/no-delta target prevents a decision. Identify the unfinished work and any actual obstruction for immediate coordinator handling; do not invent or discard a finding. |

For **BLOCKED**, give a numbered list with one entry per distinct real merge
blocker, ordered by severity. Each entry names the blocker, references its
finding, states why it survived falsification, and carries either an eligible
draft or the existing-discussion reference required below. For a new inline draft,
keep the comment separate from its location metadata:

```markdown
1. **<Blocker title>** — `<path>:<line or range>` (<diff side/view>; <finding>)

   **Why this is a real blocker:** <How this delta introduces, newly exposes, or
   materially worsens the violation; the mandatory authority; and why the
   strongest relevant counter-case or defense does not defeat it.>

   **Proposed inline review comment:**
   > <Subject> should <minimum required outcome>, because <failure or unmet obligation and its impact>.
```

The survival explanation must identify evidence, not merely restate confidence
or severity. Draft only after the blocker survives falsification and the
prior-discussion comparison. For an already covered issue, replace the draft
with **Existing review thread** or **Existing disputed issue** and its source
link; unresolved does not mean novel, and resolved does not mean refuted. For a
material uncovered change to the same issue, give **Why reconsideration is
warranted** and a **Proposed follow-up to existing discussion**, explicitly
answering the old response and identifying the new premise/consequence. Do not
create an unrelated inline draft for the same issue. Missing decision-relevant
discussion withholds the affected renewed draft, not independently proven blocker
evidence. Apply these rules in worker output as well as final reconciliation.

Write each proposed comment or follow-up to this instruction: **"Be succinct,
suggestive, provide the why and use should not could."** Prefer one or two
sentences. Direct the suggestion at the code or required verification, use
"should" rather than "could", and explain the evidence-backed mechanism or unmet
obligation and why it matters. Recommend the required outcome, not a speculative
patch or successor architecture; do not overstate evidence to make the comment
firmer.

Never include priority or severity rankings, badges, or prefixes in proposed
inline comments or discussion follow-ups, including titles and bodies, such as
`P0`, `[P1]`, `P2`, `P3`, `Priority 1`, `Severity: high`, or equivalent ranking
labels. Apply this to worker drafts and the coordinator's final deduplicated
drafts, including text adapted or quoted from imported findings. These comment
standards take precedence over auxiliary review instructions and repository
formatting conventions. Keep report-level disposition, severity, confidence, and
ordering outside the comment text; preserve the evidence-backed impact and
required outcome. Remove review ranking labels, not literal code identifiers or
evidence that happen to resemble them.

Verify proposed inline locations against the reviewed diff, including the base
side for deletions. For a propagated blocker, use a relevant causal anchor and
name the affected dependent in the comment. If an eligible new inline draft has
no valid location, retain the blocker and draft text, mark **inline location
unavailable**, and cite the actual evidence location rather than inventing an
anchor. Existing discussion references and follow-ups use their verified source
links; lack of a current inline anchor does not justify a duplicate. Drafts are
for human approval only; do not post comments, reply, reopen threads, or submit
a review. Include every real blocker once; do not promote risks, concerns, or
evidence gaps to fill the list. For APPROVE or INCOMPLETE, omit the blocker list
and proposed comments.

Approval covers only the selected change and traced consequences in the
identified candidate view, not the whole PR or unverified merge integration.
Never issue conditional approval when a prerequisite remains: use BLOCKED for
an established unmet obligation or INCOMPLETE for decision-limiting evidence.