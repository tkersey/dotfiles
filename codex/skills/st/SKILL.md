---
name: st
description: "Durable graph-planning and execution-aperture manager for `.step/st-plan.jsonl`. Use for `use $st`, resuming durable work, dependencies, proof-carrying completion, mirroring bounded work into Codex/OpenCode plans, or turning a plan, proposal, issue, spec, markdown document, TODO list, or design into executable tasks. For material plans, compile intent and graph capsules before selecting an aperture; skip straight to `prime`/`complete` only for healthy existing `$st` graphs or explicitly simple work."
---

# st

## Mental Model

`$st` is the durable source of truth for agentic work in the current repository.

The native plan surface (`update_plan` in Codex or `TodoWrite` in OpenCode) is not the durable plan. It is a **bounded execution aperture**: the small executable slice selected from the durable graph right now.

Core invariant:

```text
source plan / issue / spec / user request
        -> intent coverage
        -> self-contained task graph
        -> graph audit
        -> execution aperture
        -> native plan projection
        -> proof-carrying completion
```

Do not use prose, memory, or `update_plan` as durable task state. Keep the durable source in `.step/st-plan.jsonl` and mutate it only through `st` commands.

## Mode Selection

Choose a mode before doing work.

### Execution Mode

Use execution mode when the repo already has a durable `$st` plan/graph and the user asks to continue, resume, implement, finish, verify, or execute known work.

Primary commands:

```bash
st prime --file .step/st-plan.jsonl --mode aperture --limit 7
st compile aperture --file .step/st-plan.jsonl --limit 7
st complete --file .step/st-plan.jsonl --id st-001 --command "<validation command>" --evidence-ref .step/proof/st-001.log
st assert-projection --file .step/st-plan.jsonl
```

### Planning / Intake Mode

Use planning/intake mode when the user asks to:

- turn a plan into tasks;
- break a proposal/spec/markdown/issue into steps;
- create implementation tasks;
- make a TODO graph;
- convert a document into work;
- plan material multi-step work before implementation;
- preserve requirements that could be lost.

For material plans, do **not** start with `st add`, `st import-proposed-plan`, `st prime`, or `st complete`.

Start with intake:

```bash
st intake plan --file .step/st-plan.jsonl --source <plan.md> --out .step/st-intake.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
st compile aperture --file .step/st-plan.jsonl --limit 7
```

If `st intake` is not available in the installed binary, use the fallback in [Material Plan Intake Fallback](#material-plan-intake-fallback) and clearly record graph debt rather than pretending the graph was compiled.

### Simple Task Mode

Use simple task mode only when the user request is small, local, and obviously bounded.

A simple task usually has all of these properties:

- 1–2 steps;
- no meaningful dependency graph;
- no source plan/spec whose requirements could be lost;
- no cross-session coordination need;
- no need for multiple agents;
- no separate proof obligation beyond the immediate validation command.

Simple tasks may use ordinary `st add` / `st set-status` / `st complete` without full intake, but still preserve durable state when the task spans turns.

## Capability Probe

Before invoking advanced graph/intake commands in a repo or session where capability is uncertain, probe once:

```bash
st --help
st prime --help
st complete --help
```

If using graph/intake mode, also probe:

```bash
st intake --help || true
st graph --help || true
st compile --help || true
```

Do not repeatedly spam `--help`. After discovering a missing command, choose the documented fallback and proceed.

## Plan Surface Contract

- Durable source: `.step/st-plan.jsonl`.
- Proposed plan: Codex Plan Mode output or markdown plan text.
- Native projection: Codex `update_plan` or OpenCode `TodoWrite`.
- Backlog: durable items with `in_plan=false`.
- Aperture/frontier: selected executable items with `in_plan=true`.

Rules:

1. Never call `update_plan` while Codex is in Plan Mode.
2. After leaving Plan Mode, import or intake the final proposed plan into `$st` before execution.
3. Treat `.step/st-plan.jsonl` as the source of truth.
4. Treat native plan tools as display/projection only.
5. Project only `plan_sync.codex.plan` or `plan_sync.opencode.todos`, never the full `plan_sync` object.
6. Preserve `[st-id]` as the first token in every Codex-visible step.
7. Project no durable-only fields into the native plan.
8. Do not emit empty native plan payloads just to satisfy a hook.
9. Keep exactly one Codex `in_progress` row unless `$st` proves a safe parallel wave.
10. Waiting-on-deps items must never be mirrored as `in_progress`.

## First-Use Storage Policy

Before the first `st init` or mutation in a repo, determine the plan-file storage policy.

- If `.step/st-plan.jsonl` is already tracked, respect shared mode.
- If `.step/st-plan.jsonl` is already ignored, respect local mode.
- If the choice is not obvious, ask one targeted question: should `.step/st-plan.jsonl` be committed for shared review, or kept local via `.git/info/exclude`?
- Shared mode: keep `.step/st-plan.jsonl` tracked; ignore only `.step/st-plan.jsonl.lock`.
- Local mode: add both `.step/st-plan.jsonl` and `.step/st-plan.jsonl.lock` to `.git/info/exclude`.

Mutating commands require the lock sidecar to be ignored inside git repos.

## Material Plan Funnel

Healthy trace for material plans:

```text
intake -> audit -> aperture -> complete
```

Preferred command trace:

```bash
st intake plan --file .step/st-plan.jsonl --source <plan.md> --out .step/st-intake.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
st compile aperture --file .step/st-plan.jsonl --limit 7
st complete --file .step/st-plan.jsonl --id <st-id> --command "<validation>" --evidence-ref <proof-log>
```

Bad trace for material plans:

```text
import-proposed-plan -> prime --mode aperture -> complete
```

That skips intent coverage and graph audit. Use it only for simple plans or when graph/intake commands are unavailable and graph debt is explicitly recorded.

## Material Plan Intake

Material plan intake converts a user plan/spec/issue/markdown document into a self-contained `$st` graph.

The intake artifact is `.step/st-intake.md`. Prefer this over separate JSON intent and graph patch files because agents reliably produce and review Markdown.

### Intake Plan Command

When available:

```bash
st intake plan --file .step/st-plan.jsonl --source <plan.md> --out .step/st-intake.md
```

The command should scaffold or normalize a Markdown intake file.

### Intake Apply Command

When available:

```bash
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
```

Expected behavior:

- parse `.step/st-intake.md`;
- create intent atoms;
- create self-contained graph capsules;
- validate dependency references;
- validate acceptance/proof/test coverage;
- emit `plan_sync:`;
- emit an intake receipt;
- fail with actionable findings if the implementation-ready gate is not met.

### Intake Template

Use this shape when creating `.step/st-intake.md`:

```markdown
# st graph intake

Source: docs/plan.md

## Intent

- intent-001 | requirement | covered
  Text: OAuth login must support Google and GitHub.
  Source: docs/plan.md#authentication

- intent-002 | test-expectation | covered
  Text: The OAuth flow must have e2e coverage.
  Source: docs/plan.md#testing

## Items

### st-001 | feature | high

Step: Implement OAuth login for Google and GitHub

Covers:
- intent-001

Depends:
- none

Locations:
- src/auth
- tests/e2e/auth

Acceptance:
- User can authenticate through Google.
- User can authenticate through GitHub.
- Session is created and cleared correctly.

Validation:
- npm run test:e2e -- auth-oauth

Proof:
- proof-001 | e2e | npm run test:e2e -- auth-oauth

Contract:
Background:
The source plan requires low-friction external-provider authentication.

Objective:
Add OAuth provider login.

Implementation Approach:
Use the existing auth boundary and add provider configuration, callback handling, and session validation.

Risks:
- Provider callback misconfiguration.
- Session persistence regression.
```

Every material intake item should include:

- stable ID;
- type;
- priority;
- step;
- intent coverage;
- dependencies;
- locations/lock roots when known;
- acceptance criteria;
- validation command(s);
- proof obligation(s);
- background;
- objective;
- implementation approach;
- risks/considerations.

## Material Plan Intake Fallback

Use this only when `st intake` is not available in the installed binary.

1. Create `.step/st-intake.md` manually using the intake template.
2. If `st graph apply` exists, convert the intake into `.step/st-graph.patch.json` and apply it:

```bash
st graph apply --file .step/st-plan.jsonl --input .step/st-graph.patch.json --gate implementation-ready
```

3. If graph apply is also unavailable, create durable items with existing commands:

```bash
st init --file .step/st-plan.jsonl
st add --file .step/st-plan.jsonl --id st-001 --step "Implement OAuth login for Google and GitHub" --priority high --backlog-only
st set-notes --file .step/st-plan.jsonl --id st-001 --notes "$(cat .step/st-001-notes.md)"
st set-deps --file .step/st-plan.jsonl --id st-001 --deps ""
```

4. Record graph debt in notes or comments:

```bash
st add-comment --file .step/st-plan.jsonl --id st-001 --author codex --text "graph_debt: material plan intake used fallback because st intake/graph apply was unavailable; intent coverage and implementation-ready audit were not machine-checked."
```

5. Do not claim that graph audit passed if it did not run.

6. Before final response, say graph intake was approximated and name the missing CLI capability.

## Graph Debt

Graph debt means `$st` is being used for execution without the material plan having been compiled/audited as a graph.

Graph debt examples:

```text
graph_debt:intent_coverage_missing
graph_debt:implementation_ready_audit_missing
graph_debt:material_plan_not_compiled
graph_debt:proof_obligations_missing
```

If `st prime --mode aperture` or `st compile aperture` emits graph-debt warnings, do not ignore them.

Remediation:

```bash
st intake plan --file .step/st-plan.jsonl --source <plan.md> --out .step/st-intake.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
```

If the CLI lacks intake/audit support, record the debt with comments and disclose it in final output.

## Importing Proposed Plans

`st import-proposed-plan` is acceptable for simple plans and Plan Mode markdown, but it is not a substitute for material graph intake.

Preferred for material plans:

```bash
st intake plan --file .step/st-plan.jsonl --source .step/proposed-plan.md --out .step/st-intake.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
```

If using `import-proposed-plan` on a material plan because intake is unavailable, immediately record graph debt and run the strongest available audit/checks.

```bash
st import-proposed-plan --file .step/st-plan.jsonl --input .step/proposed-plan.md --select-ready
st add-comment --file .step/st-plan.jsonl --id st-001 --author codex --text "graph_debt: imported proposed plan directly; material intent coverage was not compiled."
```

## Aperture Workflow

Use aperture for execution selection, not plan creation.

```bash
st prime --file .step/st-plan.jsonl --mode aperture --limit 7
```

or:

```bash
st compile aperture --file .step/st-plan.jsonl --limit 7
```

Then mirror only the emitted `plan_sync.codex.plan` into Codex `update_plan`.

If the aperture payload includes graph-debt warnings, repair the graph before implementation unless the work is simple or the user explicitly directs execution despite debt.

Aperture eligibility:

- item is pending;
- blocking dependencies are complete;
- item is not terminal;
- item is not stale-claimed;
- item is executable, not an epic/decision placeholder;
- item has adequate proof/validation metadata for graph-mode work.

## Proof-Carrying Completion

Prefer `st complete` over direct `set-status completed` when available.

```bash
mkdir -p .step/proof
<validation command> 2>&1 | tee .step/proof/st-001.log
st complete --file .step/st-plan.jsonl --id st-001 --command "<validation command>" --evidence-ref .step/proof/st-001.log
```

Rules:

- Do not mark graph-mode items complete without proof or explicit waiver.
- If validation cannot run, do not fake proof. Record a waiver or leave the item pending/blocked.
- After completion, recompile/prime the aperture and mirror the new projection.

Fallback if `st complete` is unavailable:

```bash
<validation command> 2>&1 | tee .step/proof/st-001.log
st set-proof --file .step/st-plan.jsonl --id st-001 --proof-state pass --command "<validation command>" --evidence-ref .step/proof/st-001.log
st set-status --file .step/st-plan.jsonl --id st-001 --status completed
```

## Command Shape Rules

Prefer explicit long-option form. It is the least ambiguous and most stable.

Good:

```bash
st set-status --file .step/st-plan.jsonl --id st-001 --status in_progress
st set-proof --file .step/st-plan.jsonl --id st-001 --proof-state pass --command "zig build test-st" --evidence-ref .step/proof/st-001.log
```

Avoid old positional forms unless the installed binary explicitly supports them:

```bash
st set-status st-001 in_progress
st set-proof st-001 pass "zig build test-st" .step/proof/st-001.log
```

If a command fails due to shape, retry once with long options. Do not repeatedly call `--help`.

## Projection Sync Checklist

After every mutating `st` command:

1. Capture the emitted `plan_sync: {...}`.
2. If `plan_sync.codex.plan` is nonempty, mirror it with Codex `update_plan`.
3. Preserve `[st-id]` prefixes exactly.
4. Do not project durable-only fields.
5. Do not emit empty update payloads.
6. If no payload is available, run:

```bash
st prime --file .step/st-plan.jsonl
```

Before final response after `$st` mutations:

```bash
st assert-projection --file .step/st-plan.jsonl
```

## Receipts and Telemetry

When the CLI emits receipts, preserve and surface important ones.

Expected receipt kinds:

```text
st_receipt: {"kind":"graph_intake",...}
st_receipt: {"kind":"graph_debt",...}
st_receipt: {"kind":"aperture_compiled",...}
st_receipt: {"kind":"proof_complete",...}
```

Use receipts to make final responses concrete:

- graph intake applied or approximated;
- graph debt remaining;
- aperture selected;
- proof completed;
- projection asserted.

## Graph Audit

When available, run graph audit before aperture selection for material plans:

```bash
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
```

If audit fails:

- fix by editing intake/graph patch and applying through `st`;
- do not skip to aperture unless user explicitly asks;
- use waivers only with explicit reasons.

If audit is unavailable:

- record graph debt;
- use the best available `st show`, `st ready`, `st blocked`, and `st doctor` checks;
- disclose that graph audit could not run.

## Graph Polishing

Graph polishing is valuable but secondary to first-pass intake adoption.

Use a polishing loop when the plan is material, broad, risky, or swarm-bound:

```bash
st graph polish begin --file .step/st-plan.jsonl --name <name>
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
st graph insights --file .step/st-plan.jsonl --format markdown
# apply improvements through st intake/apply or graph apply
st graph polish snapshot --file .step/st-plan.jsonl --pass 1
st graph polish gate --file .step/st-plan.jsonl --min-stable-passes 2 --gate implementation-ready
```

Do not block simple execution on multi-pass polishing.

## Ready/Blocked Inspection

Use these when deciding next work:

```bash
st show --file .step/st-plan.jsonl --surface all --format markdown
st ready --file .step/st-plan.jsonl --format markdown
st blocked --file .step/st-plan.jsonl --surface all --format markdown
```

Prefer aperture compilation for execution selection:

```bash
st compile aperture --file .step/st-plan.jsonl --limit 7
```

## Existing Commands

Common commands:

```bash
st init --file .step/st-plan.jsonl
st add --file .step/st-plan.jsonl --id st-001 --step "Reproduce issue" --priority high
st add --file .step/st-plan.jsonl --id st-002 --step "Patch core logic" --deps "st-001" --backlog-only
st select --file .step/st-plan.jsonl --ids "st-002"
st deselect --file .step/st-plan.jsonl --ids "st-002"
st set-status --file .step/st-plan.jsonl --id st-001 --status in_progress
st set-priority --file .step/st-plan.jsonl --id st-002 --priority medium
st set-deps --file .step/st-plan.jsonl --id st-002 --deps "st-001:blocks"
st set-notes --file .step/st-plan.jsonl --id st-002 --notes "Need regression proof"
st add-comment --file .step/st-plan.jsonl --id st-002 --text "Pausing until CI clears" --author codex
st remove --file .step/st-plan.jsonl --id st-002
st doctor --file .step/st-plan.jsonl
st prime --file .step/st-plan.jsonl
st prime --file .step/st-plan.jsonl --mode aperture --limit 7
st compile aperture --file .step/st-plan.jsonl --limit 7
st assert-projection --file .step/st-plan.jsonl
st reconcile-codex --file .step/st-plan.jsonl --input .step/update-plan.json
st reconcile-codex --file .step/st-plan.jsonl --transcript-path /path/to/session.jsonl
st import-proposed-plan --file .step/st-plan.jsonl --input .step/proposed-plan.md --select-ready
st export --file .step/st-plan.jsonl --output .step/st-plan.snapshot.json
st import-plan --file .step/st-plan.jsonl --input .step/st-plan.snapshot.json --replace
st claim --file .step/st-plan.jsonl --wave w1 --executor codex
st heartbeat --file .step/st-plan.jsonl --id st-001
st set-runtime --file .step/st-plan.jsonl --id st-001 --substrate spawn_agent --thread-id thread-123
st set-proof --file .step/st-plan.jsonl --id st-001 --proof-state pass --command "zig build test-st" --evidence-ref .step/proof/st-001.log
st complete --file .step/st-plan.jsonl --id st-001 --command "zig build test-st" --evidence-ref .step/proof/st-001.log
st release --file .step/st-plan.jsonl --id st-001 --reason proof_complete
st reclaim-stale --file .step/st-plan.jsonl
```

Do not use removed legacy commands such as:

```text
emit-plan-sync
emit-update-plan
import-update-plan
```

Use `prime` and `reconcile-codex` instead.

## Final Response Requirements

When `$st` was used, final response should include:

- what durable state changed;
- current aperture/projection status;
- proof command(s) run and result;
- whether graph debt remains;
- exact next move if any.

For material planning tasks, explicitly state whether the plan went through:

```text
intake -> audit -> aperture
```

If it did not, say why.

## Validation

Lightweight validation:

```bash
st --help
st doctor --file .step/st-plan.jsonl
st show --file .step/st-plan.jsonl --surface all --format json
st prime --file .step/st-plan.jsonl
st assert-projection --file .step/st-plan.jsonl
```

Material graph validation when supported:

```bash
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format json
st graph insights --file .step/st-plan.jsonl --format json
st compile aperture --file .step/st-plan.jsonl --limit 7
```

## Troubleshooting

### `st intake` is missing

Use [Material Plan Intake Fallback](#material-plan-intake-fallback). Record `graph_debt:material_plan_not_compiled`.

### `st graph audit` is missing

Use:

```bash
st doctor --file .step/st-plan.jsonl
st show --file .step/st-plan.jsonl --surface all --format json
st ready --file .step/st-plan.jsonl --format markdown
st blocked --file .step/st-plan.jsonl --surface all --format markdown
```

Record `graph_debt:implementation_ready_audit_missing`.

### `st complete` is missing

Use:

```bash
st set-proof --file .step/st-plan.jsonl --id <id> --proof-state pass --command "<cmd>" --evidence-ref <log>
st set-status --file .step/st-plan.jsonl --id <id> --status completed
```

### Command shape fails

Retry once with explicit long options.

### Aperture warns about graph debt

Do not ignore it for material plans. Run intake/audit or explicitly disclose the debt.

### Projection drift

Run:

```bash
st reconcile-codex --file .step/st-plan.jsonl --transcript-path /path/to/session.jsonl
st prime --file .step/st-plan.jsonl
st assert-projection --file .step/st-plan.jsonl
```

## References

- `references/material-plan-intake-template.md`
- `references/next-cli-patch-spec.md`
- `references/jsonl-format.md`
