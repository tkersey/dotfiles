---
name: elenctic
description: "Explicit-only, read-only review of one file's changes and their causal consequences throughout the codebase. Fuse all Actuating auxiliary review concerns into one evidence-backed investigation and one deduplicated report. Finish with real blockers or a scoped approval. Use only when the user explicitly invokes $elenctic; not for automatic routing, implementation, or Actuating convergence credit."
---

# Elenctic

**The file is the causal anchor, not the evidence boundary.** Review both what
changed in the selected file and what that change makes wrong, unsafe,
unjustified, or unnecessarily difficult elsewhere.

## Invocation and limits

```text
$elenctic src/session.ts
$elenctic src/session.ts against origin/main
$elenctic src/session.ts in PR #123
$elenctic src/session.ts — staged changes only
```

These are natural-language scope selectors, not a separate CLI. Resolve one
file from the invocation or unambiguous caller context. Never expand the target
to every changed file or activate merely because someone requests a review.

Perform one integrated investigation in the current reviewing agent. Do not
spawn reviewers, invoke auxiliary skills, dispatch CAS reviews, or run separate
lens passes, verdicts, confirmation streaks, or fix/review loops. The concerns
are combined; the independence of five reviews is not reproduced. This is not
Codex's native/default standard review and earns no Actuating review credit.

Remain read-only: do not edit source or the index, implement repairs, stage,
commit, publish comments, submit GitHub reviews, merge, or mark files viewed.
Safe targeted tests and scratch reproductions are allowed; isolate generated
output and avoid commands that rewrite reviewed files or affect external
systems. A written approval is a scoped review recommendation, not permission
to mutate, publish an approval, or merge.

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

## End with the decision

Boil the adjudicated report down to one short bottom line at the very end:
what actually must be satisfied before this change should merge? This is
synthesis of the same evidence, not another review, a fourth finding category,
or permission to discard inconvenient blockers. Keep the findings and verdict
consistent; resolve or reclassify a blocker only with evidence or an applicable
authorized exception.

| Verdict | Decision rule |
|---|---|
| **BLOCKED — Real blockers:** | At least one supported merge blocker remains, even if other paths are incomplete. Summarize every distinct unsatisfied merge obligation, why it blocks, and the minimum evidence or outcome needed to clear it; refer to findings instead of restating the report. |
| **APPROVE — No real blockers in the reviewed scope.** | The selected review is complete, no supported merge blocker remains, and no material evidence gap prevents the decision. Approval may coexist with nonblocking risks or concerns; briefly say why they do not block. Do not demand optional improvements or invent risk-acceptance gates. |
| **INCOMPLETE — Approval withheld.** | No supported blocker is established, but missing/stale evidence, required lens coverage, relevant integration coverage, or an unreviewed/no-delta target prevents a decision. Name the specific missing evidence; do not invent a defect. |

Approval covers only the selected change and traced consequences in the
identified candidate view, not the whole PR or unverified merge integration.
Never issue conditional approval when a prerequisite remains: use BLOCKED for
an established unmet obligation or INCOMPLETE for decision-limiting evidence.
