---
name: architectonic
description: "Explicit-only architectural review of a PR, subsystem, repository, or proposed design. Reconstruct obligations and interactions, challenge the decomposition, and use Universalist for bounded constructive alternatives. Return evidenced defects, risks, opportunities, preservation, and uncertainty without editing or publishing."
---

# Architectonic

Reconstruct the architecture from evidence, challenge its allocation of
obligations, and distinguish necessary structure from accidental complexity.
**The architectural obligation is the causal anchor, not the evidence boundary.**
Do not accept the existing file, module, service, or team decomposition as the
partition of the problem. A better architecture is not evidence that the current
one is unacceptable; a passing implementation is not proof of adequate structure.

Elenctic reviews a change and its causal consequences. Universalist nominates a
construction for one live semantic boundary. Architectonic reviews the allocation
and interaction of those boundaries, including constructive alternatives, without
becoming an implementation workflow.

## Invocation and subject

```text
$architectonic this PR
$architectonic PR #123
$architectonic src/runtime
$architectonic this repository
$architectonic design.md
```

Resolve the target from the explicit selector or unambiguous caller context.
Without either, use the current repository and state that scope; do not silently
substitute an open PR. If no repository or design can be identified, request the
missing target without launching work. An explicit PR must resolve uniquely;
never replace a failed selector with the current branch or a repository audit.
These are subject selectors, not separate workflows or a new CLI.

Bind the evidence before assessment:

| Subject | Binding and claim boundary |
|---|---|
| PR | Repository, PR, base tip, review merge base, and head; compare the delta and unchanged causal dependencies. Distinguish introduced, newly exposed, worsened, and inherited issues. An unchanged inherited issue alone is not a merge blocker. |
| Subsystem / repository | Commit plus any explicitly included working-tree changes, with real content identities for those changes; name boundaries and scenarios examined. Existing architectural defects are in scope. |
| Proposed design | Exact document version or content identity and its attributed requirements/dependencies. Distinguish proposed guarantees, feasibility evidence, and implemented guarantees. Missing implementation is not by itself a design defect. |

Never mix base, head, working-tree, document, or deployment evidence as one
candidate. In a PR, inspect relevant base-only changes in an isolated prospective
merge or disclose missing integration coverage. Before reporting, recheck mutable
selectors and material inputs. A moved subject makes affected conclusions stale;
rebind and revalidate affected evidence, or return a historical assessment with
current coverage explicitly incomplete. Do not invent hashes or deployment facts.

## Run the assessment

1. **Reconstruct once.** After a shallow inventory, select direct or parallel
   investigation; resolve the selected parallel route before deep preparation.
   Read applicable instructions, accepted objectives,
   non-goals, contracts, and relevant implementation/design evidence. Trace
   producers, owners, consumers, state/effect transitions, and external boundaries.
   Publish a concise source-bound orientation: bound subject; required outcomes
   and constraints; current owners and interactions; known verification; and
   provisional questions with falsifiers. Separate facts, requirements, and
   hypotheses. This is shared discovery, not a pre-adjudicated verdict.
2. **Assign obligations, not components.** Derive investigations from required
   behavior, supported change scenarios, and live architectural decisions. Keep
   interacting laws together; include missing owners and cross-boundary paths.
   Do not create a lane per quality adjective, file, or auxiliary skill. For one
   coherent investigation, work directly. For useful parallel investigations,
   follow [prepared-review.md](references/prepared-review.md). Never represent
   shared context as independent judgment.
3. **Investigate and construct.** Apply [investigation.md](references/investigation.md)
   to every selected obligation. Challenge both the incumbent and its strongest
   admissible alternative. Invoke the installed sibling `$universalist` only for
   evidenced live boundary pressure, through its
   [Architectonic composition](../universalist/architectonic-composition.md).
   Assign one nomination owner per decision; reuse equivalent existing arguments.
   Unchanged adequate boundaries need no ceremonial Universalist pass.
4. **Reconcile interactions.** Revalidate findings against the bound subject,
   deduplicate by obligation and cause, and inspect consequences between proposed
   changes. Individually attractive nominations are not a jointly valid design.
   Check conflicting ownership, required observations, effect order, resources,
   compatibility, cutover dependencies, and residual checks. Where nominations
   conflict, compare the combined alternatives or leave selection unresolved;
   never present both as independently adoptable. Reopen only affected arguments
   on new evidence, without confirmation streaks or fix/review loops.
5. **Report once.** Return the architectural assessment below. Stop when selected
   obligations and their material interactions are adjudicated or have named
   evidence gaps. Finding a defect does not finish the remaining selected scope;
   absence of findings does not establish coverage.

Resolve sibling references from the installed skills tree, not a similarly named
file in the subject repository. Read deeper Universalist modules only at their
existing evidence gates. Do not invoke the public Elenctic campaign, load its file
worker as this workflow, or import Actuating execution/review-credit machinery.

## Architectural assessment

Lead with the practical conclusion and the exact scope. Keep the rest proportional;
omit empty sections rather than emitting a mandatory matrix:

- **Architecture and coverage:** evidenced owners and interactions, examined
  obligations/scenarios, exact subject, and any material uninspected or stale paths.
- **Defects and risks:** authority, mechanism, behavioral/structural witness or
  missing mandatory evidence, impact, disposition, and what would change it.
- **Justified opportunities:** incumbent and concrete challenger, obligations
  actually removed or localized, preserved behavior, material tradeoffs, a
  representative boundary/caller sketch, and the first discriminating check.
- **Preserve / unresolved:** worthwhile decisions defended against actual pressure;
  unknown premises, incomparable alternatives, residual obligations, and the
  smallest useful evidence or owner decision needed.

Use the dispositions and falsification cut in `references/investigation.md`.
Separate semantic findings from coverage: complete means only that the declared
bounded scope was covered. A failed or unavailable mandatory check remains
unmet even when the command completed or a worker called its result clean.
Withhold scoped acceptance when an applicable mandatory obligation is unmet or
material coverage is incomplete. Retain supported findings alongside that gap.
No findings with incomplete coverage means **no demonstrated defect within the
examined evidence; assessment incomplete**, not approval.

An opportunity can justify a substantial reorganization without becoming a
blocker. Explain a defensible tradeoff rather than manufacturing dominance or a
universal winner. A preservation result is useful work, not failure to find enough
improvements. Prioritize by evidenced consequence; do not add numeric architecture
scores, finding quotas, or priority labels to proposed inline comments.

## Authority and limits

Explicit invocation authorizes inspection and, when selected, read-only review
forks. It does not authorize implementation, editing the source/index/design,
staging, commits, posting comments/replies, submitting or approving reviews,
merging, changing Viewed state, or resolving/reopening review threads. No durable
Ledger decision, plan/root receipt, or automatic handoff to Actuating is required
or authorized. A recommendation is not an adopted architecture or merge authority.

Safe targeted checks and isolated scratch witnesses are allowed. Inspect commands
before execution; avoid generators that rewrite the subject, production probes,
load against external services, or other external effects. A required unsafe or
unavailable check becomes evidence debt, not permission to run it. Preserve model
and permission settings when delegating. Workers do not spawn further workers.
Sanitize source excerpts and reports; never publish secrets, private reasoning,
or raw inherited messages/tool payloads.

Skill-development evaluation cases live in [evals/scenarios.md](evals/scenarios.md).
They are not instructions to load another review lane during ordinary use.
