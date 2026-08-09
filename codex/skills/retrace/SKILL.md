---
name: retrace
description: "Reconstruct and experimentally challenge decisions from prior Codex sessions. Use for historical decision replay, counterfactual forks, alternative-route challenges, hindsight-separated retrospectives, workflow-governance audits, skill-decision attribution, or why a session chose a route. $seq owns source evidence, $cas owns safe replay transport, and $retrace owns bounded experiment design and synthesis. Never present replay output as hidden chain of thought."
metadata:
  version: "1.3.0"
  activation_cost: high
  default_depth: standard
---
# Retrace

## Mission

Use a historical session as an experimental branch point while preserving the
epistemic boundary between visible evidence and new replay executions.

```text
$seq      freezes historical evidence
$cas      runs controlled source-bound replays
$retrace  designs, compares, and adjudicates experiments
```

## Evidence classes

Keep distinct:

```text
historically_explicit
trace_inferred
fork_consistent
counterfactual_stable
outcome_informed
unsupported
unknown
```

A replay is a new model execution. It cannot recover the source model's private
reasoning.

## Common path

1. Bind the exact source session, decision question, claimed workflow, artifact
   state, and contamination boundary.
2. When workflow governance matters, prove whether the workflow was
   authoritative, merely declared, incidental, ambiguous, or absent.
3. Freeze the pre-decision evidence through `$seq`.
4. Choose one mode: `explain`, `replay`, `challenge`, `retrospective`, `compare`,
   or `audit`.
5. Stage experiments rather than opening a large portfolio:
   - source-governance gate;
   - one outcome-blind positive control;
   - minimal historical-context versus intervention A/B;
   - conditional expansion only when A/B changes the route or leaves material
     ambiguity.
6. Use `$cas` for read-only, network-off, source-bound replay and receipt
   lifecycle.
7. Separate contemporaneous reconstruction from hindsight.
8. State the strongest surviving route, the fact that flips it, limitations,
   and what remains unknowable.

Default to no more than four forks and one turn per fork unless the evidence
requires a narrower or explicitly authorized larger experiment.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for an audit or simple
historical explanation.

Load it only for:

- SGG-v1, DCP-v2, RIP-v1, DRR-v1, or FIR-v1 schemas;
- exact Seq observation definitions and source-selection commands;
- CAS session-inquiry preflight, replay, receipt, and cleanup mechanics;
- staged lane prompts, budgets, persistence, or validation;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Do not claim source-governance from a filename, generic mention, or delivery
  event.
- Do not mix outcome-aware evidence into an outcome-blind lane.
- Do not treat replay agreement as proof of the original hidden rationale.
- Stop before replay when the source or governance gate is incidental, absent,
  or irreducibly ambiguous.
