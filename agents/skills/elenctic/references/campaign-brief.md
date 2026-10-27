# Campaign Preparation and Brief

Use this reference only from the PR campaign coordinator, after the exact PR epoch and
initial Viewed-state partition are frozen and before any file-review worker is
created. The primary coordinator owns this preparation.

## Purpose

Pay once to map and explain the change topology; verify locally to justify
conclusions. After campaign capability preflight, prepare the same architectural
and causal orientation for each file reviewer:

```text
exact PR epoch
  -> primary-thread deep analysis
  -> explicit source-bound Campaign Brief
  -> frozen shared context under the selected execution mode
  -> file workers using that same preparation
```

`fork` preserves the full prepared history in one immutable seed session.
`subagents` delivers the same frozen brief directly under
[subagents.md](subagents.md), without claiming full-history inheritance.

The brief is orientation, not adjudication. It may accelerate discovery and
cross-file reasoning, but it does not establish review coverage, a finding, a
merge blocker, approval, or permission to mark a file Viewed.

## Analyze the complete construction

The primary coordinator must deeply analyze the complete PR and relevant
unchanged code before worker creation. Analysis scope is broader than assignment
scope: include pre-Viewed changed files whenever they help explain the selected
unchecked files, even though they receive no new campaign assignment.

Inspect, as causally relevant:

- repository instructions, PR description, accepted requirements, and non-goals;
- the prior-thread preflight's complete discussion index, including resolved
  threads, other reviewers' threads, relevant review summaries and PR comments,
  substantive responses, and the source evidence behind them;
- the complete changed-file inventory and merge-base-to-head delta;
- full before/after contents for primary owners and contract-bearing files;
- definitions, producers, consumers, adapters, registrations, and public
  observations joined by changed contracts;
- state transitions, invariants and their enforcement owners, raw-to-domain
  boundaries, retained refinements, aliases, lifecycle, error/retry/recovery,
  persistence, serialization, migration, and compatibility paths;
- tests and their independently justified observations, permitted implementation
  variation, examples, build/schema surfaces, required verification, and material
  unverified paths;
- base-only changes that may interact with the PR at prospective merge.

Use repository-native symbol, type, route, schema, export, build, and test tools.
Run only safe targeted checks allowed by the main skill. Bound the analysis by
the PR's causal construction, not by an arbitrary file or hop count; do not turn
preparation into unrelated whole-repository review.

The coordinator may discover suspicious mechanisms, but it must not perform the
workers' adjudication in advance. Do not label a hypothesis a concern, risk, or
merge blocker, draft inline review comments, or mark any file reviewed during
preparation.

## Publish an explicit Campaign Brief

Before launching workers, publish one concise Campaign Brief in the
coordinator transcript. Private reasoning, implicit model state, scratch notes,
and a statement that analysis occurred are not transferable context. The brief
must be present in the fork's inherited history or the subagent's explicitly
delivered context. A fork may also copy earlier coordinator history. The brief
digest identifies its bytes, not the whole context or independent judgment.

Use this shape, omitting empty sections and narrative history:

```markdown
# Elenctic Campaign Brief

## Bound candidate
- Campaign ID:
- Frozen policy ID / root and selected merge policy:
- Execution mode and shared-context delivery:
- Repository / PR:
- Base tip / review merge base / head:
- Selected unchecked files:
- Pre-Viewed exclusions:

## Intended change
- Accepted objective and observable behavior:
- Accepted non-goals and compatibility constraints:
- Supported operations, trust boundaries, configurations, and workload/lifetime limits — sources, not assumed deployment facts:

## Change topology
- Primary owners and changed contracts:
- Producer, transition, and consumer paths:
- Persistence, migration, recovery, and integration paths:

## Cross-file laws
- Established invariant or obligation — authority and enforcement owner at `path:line`
- Raw/domain boundary, retained facts, permitted operations, and consumers:

## Verification map
- Relevant tests/checks — accepted obligation, oracle authority, and observation:
- Permitted implementation variation and suspected test counterfactuals:
- Required but unavailable verification:
- Material paths not yet exercised:

## Prior discussion
- Discussion index / full-exchange source references and observation point:
- Relevant thread/comment link — original obligation, mechanism, and covered paths:
- Strongest substantive response — source-backed defense, constraint, or rebuttal:
- Established facts versus unverified claims; remaining question or possible material change:
- Missing or incomplete discussion evidence:

## Established facts
- Source-backed fact — supporting `path:line` or immutable artifact identity

## Provisional review hypotheses
- Hypothesis — why it is plausible — evidence that would falsify it

## Open questions
- Question — target evidence or file most likely to resolve it
```

Keep three epistemic classes distinct:

```text
established fact
accepted requirement
provisional hypothesis or open question
```

Every material fact or requirement should identify its source. Every hypothesis
must be explicitly provisional and include a discriminator or falsifier. Do not
smuggle a preferred repair, successor architecture, severity, confidence, or
merge consequence into the brief.

Prior discussion is shared evidence, not inherited judgment or mutation authority.
Preserve the author's strongest actual argument and references to the complete
exchange, not just the original accusation or a coordinator's disposition. Make
the session-local index available through inherited history or an accessible
source reference so workers can locate related discussions beyond the brief's
examples. A summary never substitutes for reading a relevant full exchange.
Apply the [discussion-aware rule](prior-review-threads.md#evaluate-findings-against-prior-discussion)
without turning preparation into a fresh audit of every settled discussion.

Use the existing Cross-file laws and Verification map for the worker contract's
[engineering obligations](worker-review.md#engineering-obligations). Identify
what is known and what needs investigation, not a pre-adjudicated adequacy
verdict. No extra report, per-test matrix, or enforcement registry is required.

Compress to owners, contract edges, discriminating questions, and source
locations every worker can scan. Shared discovery is not shared proof: workers
verify relevant premises locally. Do not duplicate their investigation or
adjudication in preparation, reproduce the entire diff, or emit a chronology.

## Freeze the campaign context

After publishing the brief and before launching any worker, compute a stable
digest over its exact UTF-8 bytes using a safe repository-neutral mechanism,
or use a runtime content identity that binds those exact bytes. Do not invent
a digest. Record `campaign_context_id` with the epoch and execution mode.

For `subagents`, retain those exact bytes and accessible source references for
every delivery under [subagents.md](subagents.md). Record a null seed; no native
session fork is required. Freeze this preparation before any worker findings
arrive and never revise it with those findings.

For `fork`, before consuming any worker result:

1. Fork the current coordinator exactly once through the selected
   [native route](native-forks.md) to create an immutable campaign seed. Verify
   retention of its full prepared history through the brief before launching
   reviewers. A fork that omits the current preparation turn is not a seed.
2. Record the seed thread ID, fork receipt or parent edge, and the coordinator
   checkpoint represented by the seed.
3. Give the seed a navigation title when supported, but never use its title as
   identity or authority.
4. Never send a review assignment, worker result, aggregate finding, or follow-up
   message to the seed.

In `fork` mode the seed preserves one identical full prepared context, including
the deep analysis that produced the brief. Every file worker must fork directly from
that seed, not from the evolving coordinator and not from another worker.
Supplying the brief to a fresh worker does not preserve this requirement.

In that mode use [native-forks.md](native-forks.md) to distinguish unavailable wrappers from
unavailable native operations. If no qualifying native route can fork the
coordinator and explicit seed, retain the prepared history, and return direct
IDs and parent provenance, the campaign is **INCOMPLETE** before worker launch.
Do not silently substitute subagents or copied summaries for the selected fork
contract. Explicitly selected subagents use their own context/provenance contract.

## Worker epistemic independence

Use the canonical assignment prompt in [campaign.md](campaign.md). Its
orientation-not-authority boundary applies to all supplied or inherited context, not
just the brief: earlier implementation rationales, abandoned interpretations,
and prior review conclusions must be revalidated before use. Applicable user
requirements and constraints retain their authority. Matching brief digests or
shared seed ancestry do not make correlated judgments independent.

Independence does not mean ignoring prior responses. Workers must confront
relevant discussion evidence during adjudication; coordinator reconciliation
refreshes it before the final decision. A later reply or edit can change a
finding without changing the PR head. Preserve the frozen brief and seed; handle
discussion-only updates as current evidence under the prior-thread contract,
not as a claim that every worker inherited the later exchange.

Each worker performs the complete [internal file-review contract](worker-review.md)
and blocker-falsification cut without invoking the public skill or becoming a
coordinator. Shared context does not convert correlated repetition into proof.
The aggregate coordinator must likewise rebind and falsify deduplicated blockers
against the current candidate.

## Invalidation and recovery

Any change to execution mode, merge policy, PR state, base tip, review merge base, head, complete inventory,
initial Viewed-state partition, selected-set identity, or material Campaign Brief
bytes invalidates the prepared context for new work.

On invalidation:

```text
old brief and any seed -> stale context
unadmitted workers -> stale
admitted reports   -> historical hypotheses only
new campaign       -> reanalyze, republish, and bind the selected execution context
```

Do not patch an old brief in place or mix execution modes or prepared contexts
under one campaign identity.

When direct coordinator state is lost, `$seq` may recover campaign, seed, parent,
worker, and report provenance when physically observable. Existing admissible
reports may still be aggregated. Launching additional work requires the exact
recoverable brief/policy bound to the unchanged epoch and, for `fork`, its seed.
Otherwise start a new campaign instance and preparation phase rather than guessing
context provenance. Recover subagent attempts through their actual native receipts.

## Privacy and reporting

The brief contains source-backed conclusions and explicit uncertainty, never
private chain-of-thought. Sanitize secrets and private data exactly as the main
skill requires.

The final campaign report should identify execution mode, the brief digest or
exact content identity, actual seed ID or null, and whether each admitted worker's
mode-specific context and delivery provenance matched. These facts establish
context provenance only; they do not establish correctness or approval.
