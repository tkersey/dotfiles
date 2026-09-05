---
name: plan
description: "Govern candidate specifications against user authority and repository evidence, then produce one self-contained, architecture-aware execution specification. Bare `$plan` defaults to spec-to-plan and human output, without EPG or Ledger. Use `$plan direct` only for accepted decision-complete intent, and `$plan revise` for an existing plan identity. Export EPG-v1 only for explicit machine-readable output or EPG persistence. Implicitly invoke for detailed specifications, execution plans, migrations, proof/rollback planning, and plan revision; never seize implementation, debugging, review, explanation, or divergent options."
---

# Plan

## Mission and authority

```text
candidate + user authority + repository evidence
-> governed requirements and architecture
-> executable actions, evidence-conditioned branches, proof and rollback
-> one self-contained <proposed_plan>
```

The execution specification is the primary semantic representation. EPG-v1 is an
optional derived export, not a prerequisite for ordinary planning. Neither creates
user authority, runtime facts, mutation permission, or implementation proof. Do not
select an execution consumer.

User requirements govern intended behavior. Repository artifacts establish current
facts and existing obligations, not a veto against an authorized change. A candidate
mechanism is a proposed means unless current authority makes it a required outcome,
hard constraint, or compatibility obligation. Accepting a plan does not silently
lock every selected means. Decision-complete means no material decision is unowned,
not that implementation choices are irrevocable.

## Invocation

```text
spec-to-plan   default for bare $plan, including candidate specification text
direct         only for literal $plan direct; accepted decision-complete intent
revise         $plan revise or an unambiguous revision of an existing plan_id
```

`spec-to-plan` dispositions the candidate as `adopt`, `repair`, `reconstruct`, or
`block`. With only an objective, first construct the smallest evidence-grounded
candidate. A polished specification makes governance cheap; it never selects `direct`.
`direct` skips the specification front end, not source authority, architecture,
execution completeness, or proof. `revise` preserves identity for the same objective
and emits a complete replacement; a different objective gets a different ID.

Within `spec-to-plan`, `full` is default. Explicit `gate-only` or `challenge-only`
stops after that inspection; `repair` changes only implicated sections and their
derivations. `spec only` is an output boundary, not another mode. Bounded inspections
are not certified as complete execution plans or EPGs.

Output is independent of mode:

```text
--format human  default; complete execution specification, no EPG required
--format json   explicit EPG-v1 export only; raw JSON without prose or fence
--format both   complete specification followed by its EPG-v1 export
```

A complete machine-readable EPG request also selects export. Complexity, a plan ID,
and ordinary planning intent do not. Do not bootstrap Ledger, invent utility
scores, or build a hidden EPG for human output unless EPG persistence or stored-EPG
revision is also requested.

Invoke implicitly when the primary deliverable is a specification, execution plan,
migration/rollout plan, proof-and-rollback plan, or plan revision. Do not seize
implementation, debugging, review, factual explanation, architecture archaeology
without planning intent, or divergent options. An execution owner may plan internally
without discarding requested execution.

## Compiler

### Inspect and govern

Read relevant code, tests, schemas, migrations, configuration, history, prior plans,
and supplied evidence before asking questions. At consequential boundaries inspect
representation, admission, ownership, transitions, lifetime, interpretation, and
bypasses. Files and layers are not automatically the semantic factorization.
Ask only for material user judgment, private constraints, irreversible approval,
or an authority conflict that artifacts cannot resolve.

Read [specification-governance.md](references/specification-governance.md). Recover
requirements, non-goals, compatibility, fixed decisions, proof bar, and rollback;
distinguish selected means and defaults. Repair affected derivations or reconstruct
an unsound organization without losing valid requirements or failed evidence.

### Choose architecture and derive work

Read [architectonic-specification.md](references/architectonic-specification.md)
when a boundary is a live semantic decision. Compare the ordinary repository-native
candidate with preservation, domain restriction, stronger representation/ownership,
and ablation/normalization. Required-valid behavior must survive; fewer features is
not conceptual compression. Do not invent architecture for unchanged owner-local work.

Read [specification-challenge.md](references/specification-challenge.md) for the
strongest invariant challenge, reusing an equivalent challenge on the same decision
surface. Source-fixed contradictions return to the affected internal specification
decision, not another skill or a handoff packet.

Read [action-contract.md](references/action-contract.md). Derive dependency-ordered,
bounded actions with exact targets, intended changes, preserved invariants,
observations, proof, and failure routes. Realization includes migration and retirement.
For consequential constructions bind the invalid family, required-valid domain,
enforcement mechanism, independently derived coverage, preselected discriminator,
claim strength, and residuals. Plan prepares proof; execution establishes it on code.

Use known actions, adaptive probes, or containment/observability first as evidence
requires. Every live unknown needs an exact deciding observation, admissible routes,
forbidden results, and a safe default or blocker. Read
[architectonic-policy-synthesis.md](references/architectonic-policy-synthesis.md)
when architecture changes the action structure. Implementation choices remain
revisable within their source-bounded or delegated local envelope; changing required
outcomes or fixed constraints needs new authority.

### Refine the result

[policy-synthesis-fixed-point.md](references/policy-synthesis-fixed-point.md) alone
owns the lenses and stopping rule. Refine source, architecture, actions, and proof
together without a fixed iteration cap. Concrete defects or genuinely better
admissible candidates justify affected restarts; rewording, speculative scope,
extra categories, and process elaboration do not.

Retain the mandatory private radical candidate; reuse an equivalent challenger on
the unchanged decision surface. Perform one final independent source reread including
fresh-session executability of the exact emitted block. A material change reopens
affected decisions and their dependents. Do not emit iteration histories, no-op rows,
receipts, readiness certificates, or claims that every possible design was exhausted.

## Identity, revision, and persistence

Read [source-binding.md](references/source-binding.md). Every complete plan names
its stable ID, revision, authoritative objective, target, inspected repository state,
and material invalidators. Provenance is not runtime currentness. Never manufacture
hashes or source facts.

Revision recovers the exact prior specification and identity, reconsiders the earliest
affected decision, transports actions and proof, and emits a complete new revision.
A digest cannot recover lost source; never choose a prior plan just because it is
recent. Read [artifact-root.md](references/artifact-root.md) only for persistence.
Ordinary plans need no store; a requested saved human plan uses an ordinary selected
Markdown path. Planning artifacts do not authorize implementation changes.

For explicit EPG export or stored-EPG revision, read
[epg-export.md](references/epg-export.md). Preserve the existing wire format and
Ledger custody, with stricter new-export admission. Never silently migrate an old
store or certify missing legacy source as execution-complete.

## Human output

Read [human-projection.md](references/human-projection.md). Emit one block using:

```text
Summary
Governed Specification
Architecture Decisions
Implementation Sequence
Decision Points and Branches
Proof, Rollback, and Done-State
Plan Identity and Source
```

Omit empty/inapplicable sections, never required semantics. The block and target
repository alone must let a fresh implementation session realize, prove, roll back,
and determine completion, without the candidate, earlier conversation, private
reasoning, or omitted EPG. Every material judgment is decided or evidence-conditioned;
an unresolved done-state dependency blocks successful synthesis.

Name the first action and binary done-state. Compress repetition and representation
noise, not implementation detail. For `human` and `both`, say `Plan synthesized.`
only after this contract is satisfied. Never claim EPG validation for human-only
output. Successful `json` export contains only its exact validated EPG bytes.
