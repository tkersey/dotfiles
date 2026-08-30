---
name: elenctic
description: "Explicit-only, read-only review of one file's changes and their causal consequences throughout the codebase. Fuse all Actuating auxiliary review concerns into one evidence-backed investigation and one deduplicated report. Use only when the user explicitly invokes $elenctic; not for automatic routing, implementation, or Actuating convergence credit."
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
commit, publish comments, approve, or mark files viewed. Safe targeted tests and
scratch reproductions are allowed; isolate generated output and avoid commands
that rewrite the reviewed files or affect external systems. Return evidence to
the caller, not permission to mutate or merge.

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
new requirements. Complexity and fresh-eyes findings need a witnessed defect or
falsified incumbent claim, not line-count reduction or novelty alone. Explain
why a suspected compensator is not legitimate defense in depth. Identify the
failed obligation or upstream cause without selecting a successor architecture
or turning the review into a repair plan.

## Return one report

Lead with material findings, ordered by severity using repository conventions.
Deduplicate a shared causal defect across lenses while retaining distinct
counterexamples and affected paths. Each finding should compactly establish:

- **Where and why:** target change location, affected code locations, violated
  law or positive claim, and the earliest failed premise or causal mechanism.
- **Witness and impact:** triggering input, actor, or execution path; expected
  versus actual behavior; downstream consequence and supporting evidence.
- **Scope and certainty:** local, propagated, or both; introduced or newly
  exposed by this delta; material assumptions and verification limits.

Cite precise `path:line` locations and identify the base side for deleted lines.
When the failure lives outside the selected file, cite both its causal anchor
and the affected location; never force it onto an unrelated changed line. For a
soundness finding, state the positive judgment, failed premise, and honest
claim-strength consequence. Do not duplicate it under other lens headings.

Close with a brief scope/coverage note: reviewed base and candidate view,
important causal paths inspected, checks actually run, and unresolved evidence
gaps. Report **no material findings in the reviewed scope** only when the review
was completed; this is not proof of soundness or approval of the whole PR.
Return supported findings even when other paths remain **incomplete**, but never
present partial coverage, missing lens instructions, or stale evidence as clean.
