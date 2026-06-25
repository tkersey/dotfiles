# Next CLI Patch Spec for `$st` Adoption

This reference captures the focused improvement suggested by the impact report.

## Goal

Make material plan intake the default `$st` graph path.

The observed adoption pattern is:

- aperture/proof adoption is strong;
- full graph compilation is weak;
- agents still route "turn this plan into steps/tasks" through import/select/prime instead of intent/graph/audit.

Therefore, reduce the graph path to one obvious intake artifact and one obvious apply command.

## Add Commands

```bash
st intake plan --file .ledger/st/st-plan.jsonl --source <plan.md> --out .ledger/st/intake/st-intake.md
st intake apply --file .ledger/st/st-plan.jsonl --input .ledger/st/intake/st-intake.md --gate implementation-ready
```

## Intake Markdown

`st intake plan` should scaffold a Markdown file with:

- source locator;
- intent atoms;
- items;
- covered intents;
- dependencies;
- locations;
- acceptance criteria;
- validation commands;
- proof obligations;
- contract sections.

`st intake apply` should parse and normalize it into durable `$st` graph state.

Intake must target the canonical `.ledger/st/st-plan.jsonl`. If the canonical graph has legacy debt, the CLI should either repair/audit that graph or fail with diagnostics; it must not encourage agents to create alternate durable `.ledger/st/*-st-plan.jsonl` sidecars to route around the problem.

## Graph Debt Warnings

`st prime --mode aperture` and `st compile aperture` should warn when a material-looking plan has no graph lineage.

Suggested warning payload:

```json
{
  "projection": {
    "warnings": [
      "graph_debt:intent_coverage_missing",
      "graph_debt:implementation_ready_audit_missing",
      "graph_debt:material_plan_not_compiled"
    ]
  }
}
```

## Import Proposed Plan Routing

`st import-proposed-plan` should not silently bypass graph intake for material plans.

Preferred behavior:

```bash
st import-proposed-plan --mode graph-intake --input .ledger/plan/proposed-plan.md
```

or emit:

```text
Imported as draft rows only.
For material plans, run:
  st intake plan --source .ledger/plan/proposed-plan.md --out .ledger/st/intake/st-intake.md
  st intake apply --input .ledger/st/intake/st-intake.md --gate implementation-ready
```

## CLI Shape Compatibility

Improve or alias common old-style invocations:

```bash
st set-status st-001 in_progress
st set-proof st-001 pass "zig build test-st" .ledger/proof/st/proof.log
```

If not supported, emit precise "did you mean" diagnostics with long-option form.

## Receipts

Emit easy-to-query receipts:

```text
st_receipt: {"kind":"graph_intake","gate":"implementation-ready","items":12,"intent":18}
st_receipt: {"kind":"graph_debt","reason":"aperture_without_intake"}
st_receipt: {"kind":"aperture_compiled","items":7}
st_receipt: {"kind":"proof_complete","id":"st-014","proofs":1}
```

## Adoption Metric Funnel

The next impact report should measure:

```text
material plan opportunities
  -> intake started
  -> intake applied
  -> graph audit passed
  -> aperture compiled
  -> proof completed
```

Success target:

- 60% of material plan sessions run intake/apply before aperture.
- 50% run graph audit before aperture.
- 30% reach implementation-ready gate.
