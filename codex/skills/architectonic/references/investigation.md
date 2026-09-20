# Architectural investigation

Use within Architectonic for one assigned obligation or interacting law family.
The coordinator uses this same contract for direct work and reconciliation.
Stay read-only under the entry contract. Do not start another campaign, invoke
Elenctic or Actuating, or select an architecture for implementation.

## Establish the obligation and actual construction

Bind the subject and assignment; verify relevant shared premises in current
source evidence rather than inheriting their conclusion. Inspect the actual
construction, public operations, bypasses, observations, and failure paths. Trace
both upstream and downstream, including unchanged callers, adapters, persistence,
serialization/re-entry, configuration, deployment contracts, and recovery when
causally relevant. Search misses do not prove absence of dynamic consumers.

Use one connected investigation, not independent lens passes:

**Ownership and construction.** Identify the accepted law and who establishes and
preserves it. Can ordinary constructors, aliases, transitions, compositions, or
re-entry violate it or discard evidence on which a consumer relies? Is one rule
independently maintained across owners, or are additional guards derived from one
authority at distinct trust/time boundaries? Inspect valid behavior and progress
as well as forbidden states. Raw inputs, drafts, confined intermediate states,
and supported unsafe primitives are not automatically trusted domain values.

**Information hiding and evolution.** Sketch a representative caller. What must
it know, choose, sequence, synchronize, recover, or clean up? Trace a change
supported by requirements, history, or a concrete requested variant: which owners
must change together and why? Fewer exports, an added facade, relocated checks,
syntactic deduplication, or fewer lines alone do not establish reduced burden.
Do not invent future flexibility requirements to justify generalization.

**Execution and operation.** Trace relevant failure, retry, cancellation,
concurrency, persistence, deployment, trust, and recovery scenarios end to end.
Bind availability, security, latency, throughput, and resource claims to their
actual workload, threat model, failure model, and environment evidence. A type,
state machine, or lawful composition is not evidence of sufficient capacity,
authorization freshness, durable atomicity, or safe distributed execution.

Carry soundness skepticism, footgun analysis, invariant preservation, correctness
complexity, and fresh-eyes reconstruction through those same traces. Start from
required outcomes independently of the current component diagram. Ask what the
reasonable actor expects, what each positive claim requires, and which correctness
truths are independently maintained. Do not manufacture a finding per concern.

Stable trusted-domain invariants should be enforced by a proportionate native
representation or owning abstraction when required-valid behavior and compatibility
can be preserved. An ordinary construction admitting forbidden combinations, or
a check whose evidence is discarded before use, can establish a structural defect
without a production incident. Demonstrate the accepted domain law, actual public
surface, avoidable material burden, and feasibility of enforcement. Names, brands,
maximal type strength, and theoretical elegance establish none of these premises.
Adequate encapsulation, distinct temporal checks, or evidenced migration constraints
can defeat the criticism. Do not centralize physical execution merely to name one
semantic authority.

For verification relied on by an architectural claim, identify its independent
oracle and the relevant incorrect behavior it distinguishes. Check whether it
merely freezes a noncontractual implementation choice or rejects a permitted
variation. A contractual configuration value or independent reference interpreter
may be a sound oracle. Missing optional tests is not a demonstrated defect;
uninformative tests are not evidence that the architecture works.

Continue each material causal path until preservation, a supported failure, or a
named evidence gap decides it. Bound scope by causal relevance, not file/hop limits
or a quota of findings. Do not let existing boundaries hide missing behavior.

## Constructive challenge

On live semantic boundary pressure, read the installed Universalist entry and its
[Architectonic composition](../../universalist/architectonic-composition.md).
Supply the incumbent, attributed requirements and observations, constraints,
pressure, and any already derived challenger. The assigned nomination owner runs
one bounded comparison; do not manufacture alternatives for settled seams.

Seek the smallest adequate ordinary construction and at most one grounded
law-derived challenger under Universalist's existing discipline. Establish a
material object-level difference: an illegal public composition excluded, a
correctness obligation eliminated or owned, caller choreography removed, or a
source-supported change localized. A more general encoding can be warranted;
ordinary-first is not a prohibition on reorganization or first-use abstractions.

Challenge the alternative at least as hard as the incumbent. Preserve required
valid states, future observations, effect order, authority, resources, compatibility,
and lifecycle/progress. Inspect migration and rollback feasibility, not just the
steady state. A transition sketch should identify one witness seam, cutover
constraints, and obligations/bypasses retired; do not produce an unsolicited task
plan or implement the sketch. Keep residual runtime checks with their owner,
check time, failure behavior, and discharge condition.

Use a representative caller/boundary sketch and a discriminating trace, test, or
source-level argument. Label sketches and unexecuted checks honestly. A structural
argument cannot substitute for an operational measurement. If candidates have
unranked material tradeoffs, return underdetermination and the missing preference
or evidence rather than a winner. A failed challenger does not prove the incumbent
sound; an established defect does not require a successful redesign to be reported.

## Adjudicate and try to falsify

Before retaining a defect, blocker, or opportunity, reconstruct the strongest
evidence-backed case against it. Re-read the exact source and requirement rather
than the narrative that produced it. Check reachability, existing defenses,
companion changes, raw versus trusted states, derived guards, required-valid
behavior, compatibility, and the cost or hidden duties of the challenger. In a PR,
prove the causal difference from the base. Reject refuted and preference-only
claims rather than relabeling them as risks. No additional reviewer or repeated
clean streak is required for this falsification cut.

Use these meanings; consequence is not severity or confidence:

| Disposition | Required support |
|---|---|
| Defect | A material violation of an accepted requirement/invariant/contract, a demonstrated applicable constructional or test-adequacy violation above, or genuinely missing mandatory justification for a positive claim. Identify authority, witness or exact missing evidence, consequence, and unmet obligation. |
| Risk | A concrete conditional mechanism and impact with a still-unresolved premise; state trigger, mitigation, and evidence or risk-acceptance decision needed. Do not imply an unproved violation. |
| Opportunity | A concrete admissible alternative with an evidenced architectural benefit and explicit costs/residuals. It does not imply that the incumbent is defective or must be replaced before merge. |
| Preserve | A challenged incumbent remains adequate under the examined obligations, and the challenger is unnecessary, inadmissible, or not beneficial under the accepted constraints. Do not emit this for every untouched boundary. |
| Unresolved | Evidence is insufficient or adequate candidates are incomparable. Name the gap and discriminator; uncertainty is neither preservation nor an obstruction. |

A **merge blocker** additionally requires an applicable mandatory pre-merge
obligation and PR-delta causality (including a mandatory check for this change).
An inherited defect alone, optional improvement, new requirement, or attractive
redesign is not a merge gate. For a proposed design, name an acceptance blocker
only against an attributed design-acceptance condition; do not demand runtime
proof merely because implementation has not begun. A repository assessment names
required corrections without inventing a pending merge decision. An explicit
applicable exception may change an obligation only where its authority permits.

A risk classification is not risk acceptance; identify any required owner decision.

Keep evidence kind and coverage distinct: behavioral witness, structural witness,
missing mandatory evidence, unexecuted hypothesis, and unavailable inspection are
not interchangeable. Passing checks support only the obligations they examine;
failed, skipped, stale, or invalid checks never become clean credit because a tool
returned successfully. A material coverage gap withholds scoped acceptance without
erasing supported findings. State what would falsify each retained conclusion.
