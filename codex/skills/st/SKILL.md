---
name: st
description: "Durable graph control, aperture, and proof source for `.step/st-plan.jsonl`. Use for `use $st`, resuming durable work, dependencies, proof-carrying completion, mirroring bounded work into Codex/OpenCode plans, or turning a plan, proposal, issue, spec, markdown document, TODO list, or design into executable tasks. For material work, require a current CLI-emitted GCR-v1 before execution projection."
---

# st

## Mental Model

`$st` is durable work truth. Native plans are projections.

Canonical material loop:

```text
Compile intent into durable graph state.
Audit it.
Compile one bounded safe aperture and GCR.
Project only the aperture.
Execute.
Record obligation-level proof.
Recompile.
```

Do not invent critical paths, proof cuts, safe parallel width, or graph debt in prose. Only CLI-emitted `GCR-v1` facts count as graph-control evidence.

## Modes

### Graph Mode

Use graph mode for material plans with intent atoms, contracted executable items, hard dependency edges, proof obligations, graph lineage, and implementation-ready audit.

Required control command:

```bash
st compile aperture --file .step/st-plan.jsonl --limit 7 --parallelism auto
```

For material graph work, do not execute or project a native plan without a current `GCR-v1`. Current means the receipt seq and fingerprints match the durable plan state being projected.

### Degraded Graph Mode

If graph state exists but blocking graph debt remains, aperture preview may be useful, but delivery mutation and completion claims are blocked unless an exact active waiver exists. The GCR must show the mode, debt, waiver, and gate decision.

### Ledger/Simple Mode

Use simple ledger commands only for small bounded work or legacy v3 state:

```bash
st add ...
st set-status ...
st set-proof ...
st complete ...
```

Do not silently route a material plan through simple-task mode. If no graph was compiled, say exactly:

```text
Graph not compiled; proceeding in ledger mode.
```

## Capability Surface

Assume the documented current CLI. Do not proactively call several `--help` surfaces.

Use one probe only when version is genuinely uncertain or an unknown-command error occurs:

```bash
st capabilities --format json
```

Cache that result for the session.

## Material Intake

For a new material plan, use the intake check/apply path:

```bash
st intake scaffold --source docs/plan.md --out .step/st-intake.md
# Agent fills or edits the semantic intake artifact.
st intake check --input .step/st-intake.md --gate implementation-ready --format json
st intake normalize --input .step/st-intake.md --out .step/st-intake.normalized.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.normalized.md --gate implementation-ready
st compile aperture --file .step/st-plan.jsonl --limit 7 --parallelism auto
```

`st intake plan` is a deprecated alias for scaffold. A scaffold is not semantic compilation until the agent-authored intake passes `check` and `apply`.

## Existing Healthy Graph

For existing healthy graph work, start with:

```bash
st compile aperture --file .step/st-plan.jsonl --limit 7 --parallelism auto
```

Then mirror only the emitted `plan_sync.codex.plan` into `update_plan` or `plan_sync.opencode.todos` into OpenCode.

## Projection Rules

- Durable source: `.step/st-plan.jsonl`.
- Native plan tools are projection only.
- Mutate durable state only through `st` commands.
- Project only `plan_sync.codex.plan` or `plan_sync.opencode.todos`, never the full `plan_sync` object.
- Preserve `[st-id]` as the first token of each Codex-visible step.
- Keep durable-only fields out of native plans.
- Keep exactly one Codex `in_progress` row unless the current GCR proves a selected safe parallel wave.
- Waiting-on-deps items must not be mirrored as `in_progress`.

## Execution And Proof

Execute only the selected aperture. After work, record proof at obligation level:

```bash
st proof plan --file .step/st-plan.jsonl --scope aperture --format json
st proof record \
  --file .step/st-plan.jsonl \
  --id st-001 \
  --obligation proof-001 \
  --action proof-action-test-st \
  --command "zig build test-st" \
  --evidence-ref .step/proof/st-001-proof-001.log \
  --artifact-ref "git:<sha-or-working-tree-fingerprint>"
st complete --file .step/st-plan.jsonl --id st-001
st compile aperture --file .step/st-plan.jsonl --limit 7 --parallelism auto
st assert-projection --file .step/st-plan.jsonl
```

`st set-proof` remains a compatibility convenience. Do not use one ambiguous legacy proof to satisfy several distinct required commands.

## Graph Debt

Use graph debt commands when the GCR blocks execution:

```bash
st graph debt list --file .step/st-plan.jsonl --format json
st graph debt waive --file .step/st-plan.jsonl --id debt-... --reason "..." --expires on-next-touch
st graph debt resolve --file .step/st-plan.jsonl --id debt-...
```

For material work, unwaived blocking debt means `execution_allowed: no`.

## First-Use Storage Policy

Before the first `st init` or mutation in a repo, determine whether `.step/st-plan.jsonl` is shared or local.

- If already tracked, respect shared mode.
- If ignored, respect local mode.
- If unclear, ask whether `.step/st-plan.jsonl` should be committed for shared review or kept local via `.git/info/exclude`.
- Shared mode: track `.step/st-plan.jsonl`; ignore `.step/st-plan.jsonl.lock`.
- Local mode: ignore both `.step/st-plan.jsonl` and `.step/st-plan.jsonl.lock`.

## Final Response

For material `$st` work, report:

- GCR id;
- mode: graph, degraded, or ledger;
- ready frontier;
- blocked frontier;
- selected wave;
- critical path/depth;
- safe parallel decision;
- proof basis and proof status;
- graph debt;
- projection assertion.

If no graph was compiled, include exactly:

```text
Graph not compiled; proceeding in ledger mode.
```
