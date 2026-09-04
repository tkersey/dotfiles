# Campaign Preparation and Brief

Use this reference only from PR campaign mode, after the exact PR epoch and
initial Viewed-state partition are frozen and before any file-review worker is
created. The primary coordinator owns this preparation.

## Purpose

The campaign should pay once for understanding the change as a whole, then let
each file reviewer specialize with the same architectural and causal context:

```text
exact PR epoch
  -> primary-thread deep analysis
  -> explicit source-bound Campaign Brief
  -> one immutable campaign seed
  -> file workers forked from that seed
```

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
- the complete changed-file inventory and merge-base-to-head delta;
- full before/after contents for primary owners and contract-bearing files;
- definitions, producers, consumers, adapters, registrations, and public
  observations joined by changed contracts;
- state transitions, invariants, ownership, lifecycle, error/retry/recovery,
  persistence, serialization, migration, and compatibility paths;
- tests, examples, build or schema surfaces, required verification, and material
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

Before creating the campaign seed, publish one concise Campaign Brief in the
coordinator transcript. Private reasoning, implicit model state, scratch notes,
and a statement that analysis occurred are not transferable context. The exact
brief text is the context workers inherit.

Use this shape, omitting empty sections and narrative history:

```markdown
# Elenctic Campaign Brief

## Bound candidate
- Campaign ID:
- Repository / PR:
- Base tip / review merge base / head:
- Selected unchecked files:
- Pre-Viewed exclusions:

## Intended change
- Accepted objective and observable behavior:
- Accepted non-goals and compatibility constraints:

## Change topology
- Primary owners and changed contracts:
- Producer, transition, and consumer paths:
- Persistence, migration, recovery, and integration paths:

## Cross-file laws
- Established invariant or obligation — supporting `path:line` evidence

## Verification map
- Relevant tests and checks:
- Required but unavailable verification:
- Material paths not yet exercised:

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

Compress the result to decision-relevant context that every worker can scan.
Deep analysis is measured by the quality of the causal model, not by reproducing
the entire diff or emitting a long chronology.

## Freeze the campaign context

After publishing the brief and before consuming any worker result:

1. Compute a stable digest over the exact UTF-8 Campaign Brief bytes when a safe
   repository-neutral digest mechanism is available; otherwise use a runtime
   content identity that binds those exact bytes. Do not invent a digest.
2. Record the brief identity with the campaign epoch.
3. Fork the current coordinator exactly once to create an immutable campaign
   seed.
4. Record the seed thread ID, fork receipt or parent edge, and the coordinator
   checkpoint represented by the seed.
5. Give the seed a navigation title when supported, but never use its title as
   identity or authority.
6. Never send a review assignment, worker result, aggregate finding, or follow-up
   message to the seed.

The seed exists only to preserve one identical prepared context. Every file
worker must fork directly from that seed, not from the evolving coordinator and
not from another worker.

If the runtime cannot fork the coordinator, cannot later fork the seed by direct
thread ID, cannot return direct worker IDs, or cannot preserve the parent
relation, campaign mode is **INCOMPLETE** before worker launch. Do not silently
substitute clean `create_thread` tasks, generic subagents, shell-managed
processes, or copied summaries: those routes do not preserve the requested
prepared context.

## Worker epistemic independence

The worker assignment must say that inherited context is untrusted orientation:

```text
Use the inherited Campaign Brief as orientation, not authority. Verify every
relevant fact and requirement against the exact candidate, challenge provisional
hypotheses, and report material contradictions or omissions. Do not repeat a
hypothesis as a finding without ordinary Elenctic evidence and adjudication.
```

Each worker still performs the complete ordinary `$elenctic file <path>`
investigation and blocker-falsification cut. Shared context does not convert
correlated repetition into proof. The aggregate coordinator must likewise
rebind and falsify deduplicated blockers against the current candidate.

## Invalidation and recovery

Any change to PR state, base tip, review merge base, head, complete inventory,
initial Viewed-state partition, selected-set identity, or material Campaign Brief
bytes invalidates the seed for new work.

On invalidation:

```text
old brief and seed -> stale context
unadmitted workers -> stale
admitted reports   -> historical hypotheses only
new epoch          -> reanalyze, republish, and create a new seed
```

Do not patch an old brief in place or mix workers descended from different seed
contexts under one campaign identity.

When direct coordinator state is lost, `$seq` may recover campaign, seed, parent,
worker, and report provenance when physically observable. Existing admissible
reports may still be aggregated. Launching additional work requires an exact
recoverable seed bound to the unchanged brief and epoch; otherwise start a new
campaign instance and preparation phase rather than guessing context lineage.

## Privacy and reporting

The brief contains source-backed conclusions and explicit uncertainty, never
private chain-of-thought. Sanitize secrets and private data exactly as the main
skill requires.

The final campaign report should identify the brief digest or exact content
identity, seed thread ID, and whether every admitted worker's fork lineage and
context identity matched. These facts establish context provenance only; they do
not establish correctness or approval.
