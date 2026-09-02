---
name: elenctic
description: "Explicit-only, read-only review of one file's changes and their causal consequences throughout the codebase. Fuse all Actuating auxiliary review concerns into one evidence-backed investigation and one deduplicated report. Optional session-corpus mode uses $seq to aggregate real blockers from current same-name review sessions. Finish with real blockers or a scoped approval. Use only when the user explicitly invokes $elenctic; not for automatic routing, implementation, or Actuating convergence credit."
---

# Elenctic

**The file is the causal anchor, not the evidence boundary.** Review both what
changed in the selected file and what that change makes wrong, unsafe,
unjustified, or unnecessarily difficult elsewhere.

## Invocation and modes

```text
# Default: review one file and its causal consequences.
$elenctic src/session.ts
$elenctic src/session.ts against origin/main
$elenctic src/session.ts in PR #123
$elenctic src/session.ts — staged changes only

# Optional: aggregate completed reviews from current same-name sessions.
$elenctic session-corpus
$elenctic session-corpus in PR #123
$elenctic aggregate same-name sessions
```

These are natural-language scope selectors, not a separate CLI. Default mode
resolves one file from the invocation or unambiguous caller context. Never
expand that target to every changed file or activate merely because someone
requests a review.

Activate **session-corpus mode** only when the caller explicitly requests
`session-corpus`, aggregation, or same-name session evidence. Read and follow
[session-corpus.md](references/session-corpus.md). A file selector is optional
in this mode because it aggregates completed single-file Elenctic reports; it
does not silently launch missing reviews or turn into a whole-PR audit.

Perform one integrated investigation in the current reviewing agent. In default
mode, do not spawn reviewers, invoke auxiliary skills, dispatch CAS reviews, or
run separate lens passes, verdicts, confirmation streaks, or fix/review loops.
In session-corpus mode, `$seq` is the sole permitted sibling skill and acts only
as the passive adapter for physical session discovery and report evidence. Do
not invoke review lenses, spawn reviewers, or grant historical reports action,
review, or closure authority. The concerns are combined; the independence of
five reviews is not reproduced. Neither mode is Codex's native/default standard
review or earns Actuating review credit.

Remain read-only: do not edit source or the index, implement repairs, stage,
commit, publish comments, submit GitHub reviews, merge, or mark files viewed.
Safe targeted tests and scratch reproductions are allowed; isolate generated
output and avoid commands that rewrite reviewed files or affect external
systems. A written approval is a scoped review recommendation, not permission
to mutate, publish an approval, or merge.

The remaining change-binding and investigation sections govern default
single-file mode. Session-corpus mode uses its reference for discovery,
candidate binding, corpus admission, aggregation, and coverage, then reuses the
adjudication, blocker-falsification, comment, and decision standards here.

## Bind the change

1. Establish the repository, target path, comparison base, and candidate view.
   Honor the caller's PR, range, staged-only, or unstaged-only selection. With no
   selected scope, use local target changes against HEAD when present; otherwise
   use the active PR or established branch comparison. For a PR, resolve its
   current base/head and review merge-base to head. Resolve commit refs to SHAs;
   distinguish committed, index, and working-tree bytes. If the file or base
   cannot be recovered unambiguously, request only the missing selector.
2. Read applicable repository instructions and existing requirements,
   compatibility obligations, and non-goals. Infer the changed behavior from
   evidence, not an invented specification. No Actuating Goal, proof packet,
   Ledger store, or review campaign is required.
3. Read the full target before and after, not just changed lines. Handle added,
   deleted, renamed, and explicitly selected untracked files; retain the old
   path where needed. Inspect the change-set file list to locate related edits,
   not to launch a whole-PR audit. No target delta means **not reviewed: no
   changes in the selected scope**, not a clean review or a silent whole-file
   audit.
4. Inspect supporting files in the same candidate view, comparing their base
   versions when needed. Do not explain a PR-head or staged-only finding with
   unrelated working-tree bytes. For mutable views, record the relevant content
   identities and recheck them before reporting. Re-read changed evidence or
   mark the affected conclusion incomplete; never combine incompatible states.
5. For PRs, check base-only changes since the merge base for causal interaction
   with the target's changed contracts. When they interact, inspect an isolated
   prospective merge of the pinned base/head, or mark integration coverage
   incomplete. This supplements, not replaces, the target delta; do not audit
   unrelated base changes. Keep head and merge evidence separate, identify the
   view for each finding, and never alter the user's checkout or index to
   construct it. Recheck PR refs before reporting; rebind affected evidence or
   mark it incomplete if either moved. Head-only evidence does not establish
   merge compatibility when relevant base-only changes remain unexamined.

## Load the auxiliary concerns once

Use the installed sibling
[Actuating review contract](../actuating/references/review-contract.json) as the
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
| Soundness skepticism | Does a positive claim survive its law, applicability, domain, interpretation, premises, exact artifact, proof coverage, and claimed strength? |
| Footguns | Can a reasonable caller take an apparently safe path that bypasses the intended owner, admission, lifecycle, recovery, or compatibility contract? |
| Invariants | Do representations, constructors, transitions, aliases, composition, and every sanctioned producer preserve the law and required-valid behavior? |
| Correctness complexity | Are duplicate owners, manual mirrors, adapters, downstream primary guards, or wound-specific proofs compensating for an upstream defect rather than providing derived defense in depth? |
| Fresh eyes | Does a concrete witness or materially different admissible construction expose an earlier enforceable cut, wrong representation, erased distinction, omitted case, or obsolete workaround? |

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

## Adjudicate before reporting

Within the same investigation, weigh current evidence, counterevidence,
reachability, delta causality, accepted authority, and existing mitigations.
Reject refuted, unrelated, and preference-only claims rather than relabeling
them as concerns. Assign each retained finding exactly one disposition:

| Disposition | Evidence and merge consequence |
|---|---|
| **Concern** | A grounded nonblocking issue or open question worth clarifying or improving, without an established material failure path or unmet merge condition. Name the observation and useful clarification or follow-up; do not assert an unproved defect. |
| **Risk** | A credible conditional failure or exposure with a concrete trigger, mechanism, and impact, but no established material violation or unmet mandatory merge condition. State the unresolved premise, existing mitigation, and validation or risk-acceptance decision still needed; classification alone is not approval. |
| **Merge blocker** | Current evidence establishes a material violation of an accepted requirement, invariant, or compatibility contract, or an unmet mandatory merge condition, including missing required verification. Cite the authority, witness or missing required evidence, and obligation that must be satisfied before merge. |

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
- the triggering path is supported and reachable, or the exact mandatory
  evidence is identified and genuinely absent;
- caller obligations, existing defenses, companion changes, mitigations, base
  behavior, or an applicable authorized exception defeat or narrow the claim;
- the required outcome is truly a merge prerequisite rather than an optional
  strengthening, preference, legitimate follow-up, or speculative redesign.

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
- **Incomplete:** evidence needed to decide the blocker claim is missing or
  stale; name the gap instead of preserving or inventing a blocker.

Run this cut once per provisional blocker. Do not recursively reconsider an
unchanged result. A newly discovered issue must pass the ordinary investigation,
adjudication, and this cut if provisionally blocking; do not generate a
replacement finding merely because another blocker was rejected. Move
reclassified findings to their resulting report group, omit rejected claims,
and carry decision-limiting gaps into coverage. After this cut, only retained
merge blockers are real blockers.

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
  Do not invent a failing execution to fill a field.
- **Scope and certainty:** local, propagated, or both; introduced or newly
  exposed by this delta; material assumptions and verification limits.

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

Immediately before the final decision, emit exactly one machine-readable
identity line. In default mode use canonical one-line JSON in this shape:

```text
Review identity: {"schema":"elenctic-review-identity/v1","mode":"single-file","repo":"<owner/name-or-absolute-root>","target":"<path>","base":"<sha-or-content-id>","candidate":"<sha-or-content-id>","view":"<pr-head|prospective-merge|staged|unstaged|range>","verdict":"<BLOCKED|APPROVE|INCOMPLETE>"}
```

Bind every field to the exact reviewed state; do not reconstruct an identity
from branch names or mutable refs when an immutable identity is available. The
identity verdict must equal the final decision. Session-corpus mode emits the
corpus identity defined by its reference. This line is report provenance, not
approval or closure authority.

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
| **INCOMPLETE — Approval withheld.** | No supported blocker is established, but missing/stale evidence, required lens coverage, relevant integration coverage, or an unreviewed/no-delta target prevents a decision. Name the specific missing evidence; do not invent a defect. |

For **BLOCKED**, give a numbered list with one entry per distinct real merge
blocker, ordered by severity. Each entry names the blocker, references its
finding, states why it survived falsification, and contains the proposed inline
review comment separately from its location metadata:

```markdown
1. **<Blocker title>** — `<path>:<line or range>` (<diff side/view>; <finding>)

   **Why this is a real blocker:** <How this delta introduces, newly exposes, or
   materially worsens the violation; the mandatory authority; and why the
   strongest relevant counter-case or defense does not defeat it.>

   **Proposed inline review comment:**
   > <Subject> should <minimum required outcome>, because <failure or unmet obligation and its impact>.
```

The survival explanation must identify evidence, not merely restate confidence
or severity. Draft the inline comment only after the blocker survives
falsification.

Write each comment to this instruction: **"Be succinct, suggestive, provide the
why and use should not could."** Prefer one or two sentences. Direct the
suggestion at the code or required verification, use "should" rather than
"could", and explain the evidence-backed mechanism or unmet obligation and why
it matters. Recommend the required outcome, not a speculative patch or
successor architecture; do not overstate evidence to make the comment firmer.

Verify proposed locations against the reviewed diff, including the base side
for deletions. For a propagated blocker, use a relevant causal anchor and name
the affected dependent in the comment. If no valid inline location is available,
retain the blocker and draft text, mark **inline location unavailable**, and
cite the actual evidence location rather than inventing an anchor. Drafts are
for human approval only; do not post comments or submit a review. Include every
real blocker once; do not promote risks, concerns, or evidence gaps to fill the
list. For APPROVE or INCOMPLETE, omit the blocker list and proposed comments.

Approval covers only the selected change and traced consequences in the
identified candidate view, not the whole PR or unverified merge integration.
Never issue conditional approval when a prerequisite remains: use BLOCKED for
an established unmet obligation or INCOMPLETE for decision-limiting evidence.
