---
name: teams
description: Coordinate agent teams (multi-session) for parallel research/review/design or competing hypotheses, then synthesize a decision/report or produce a mesh-ready execution handoff (OrchPlan/units).
---

# teams

## Intent
Use agent teams (independent sessions with a shared task list + peer messaging) when parallel exploration and debate is the work.

Deliverables:
- Decision/report: recommendations + tradeoffs + risks.
- Execution handoff (for `$mesh`): a set of atomic units with `unit_scope`, `write_scope`, and `proof_command`.

## When To Use Teams

Use teams when:
- The user explicitly asks for an agent team / teammates.
- The primary deliverable is a decision/report (research, review, compare approaches, competing hypotheses).
- The work benefits from peer-to-peer challenge (avoid anchoring on the first plausible theory).

Prefer `$mesh` when:
- The primary deliverable is a proven patch set with durable artifacts and fail-closed gates.

## Preflight (Do First)

- Ensure agent teams are enabled in the runtime (Claude Code: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). If teams are unavailable, fall back to non-team parallelism or a single-session plan.
- Pick a single writer for repo state (one agent owns edits/merges); keep teammate tasks file-disjoint.
- For risky tasks: require plan approval before any code edits.

## Default Team Shape

- 3 teammates (recommended start):
  - Researcher: gathers evidence, finds codepaths, summarizes facts.
  - Architect: proposes options, boundaries, and the recommended approach.
  - Skeptic: attacks assumptions, finds failure modes, challenges the plan.

Scale to 4-5 only when tasks are truly independent.

## Task Shaping Rules

- Size tasks so each produces a concrete artifact (a doc section, a hypothesis test result, a draft plan).
- Keep tasks file-disjoint; do not assign two teammates to edit the same file.
- Aim for ~5 tasks per teammate (too few = idle; too many = thrash).

## Quality Gates (Recommended)

- Use hooks to enforce rigor:
  - `TeammateIdle`: block idling if the teammate has not produced its promised artifact.
  - `TaskCompleted`: block completion if acceptance criteria are missing.

## Completion Criteria (Required)

Close a teams run only when:
- Every claimed task has an explicit deliverable and that deliverable exists (text summary, doc update, file path, or a tested patch if you allowed edits).
- The lead has synthesized the team output into either:
  - a decision/report, or
  - a `$mesh`-ready execution handoff.
- Teammates are shut down (or explicitly kept running by user request) and the team resources are cleaned up.

If you cannot meet a criterion, stop and report what is missing.

## Final Response: Teams Ledger (Required When Teams Ran)

When teams actually ran, include a `Teams Ledger` section in the final response.

Rules:
- Prose only (no JSON block).
- Omit lines for non-events.
- Deterministic line order:
  - `Skills used`
  - `Team summary`
  - `Task summary`
  - `Artifacts produced`
  - `Handoff status`
  - `Cleanup status`

## Hybrid Handoff Schema (Required For Hybrid)

If the outcome is "hybrid" (teams -> `$mesh`), output exactly one of the following blocks (choose one), so `$mesh` can run without reinterpretation.

Option A: OrchPlan v1 (YAML)

```yaml
schema_version: 1
kind: OrchPlan

created_at: "<rfc3339>"

source:
  kind: list
  locator: "teams-handoff"

cap: auto

prereqs: []
risks: []

tasks:
  - id: t-1
    title: "<one line>"
    description: "<optional>"
    agent: worker
    scope: ["<write_scope lock; paths/globs>"]
    location: ["<paths to inspect>"]
    validation: ["<proof_command>"]
    depends_on: []

waves:
  - id: w1
    tasks: ["t-1"]
```

Option B: MeshUnits v1 (JSON)

```json
{
  "schema_version": 1,
  "kind": "MeshUnits",
  "units": [
    {
      "id": "u-1",
      "objective": "<one line>",
      "unit_scope": "<what changes>",
      "write_scope": ["<exclusive locks; paths/globs>"],
      "constraints": ["<must/never>"],
      "invariants": ["<must remain true>"],
      "proof_command": "<command to prove>",
      "risk_tier": "low"
    }
  ]
}
```

## Hybrid Handoff To `$mesh` (Common)

When teams produce an execution handoff, output one of:

1. OrchPlan (preferred): run `$select` to emit an OrchPlan with explicit `scope` locks and `validation` commands.
2. Units list (direct): for each unit, provide:
   - `objective`
   - `unit_scope` (what changes)
   - `write_scope` (exclusive locks; paths/globs)
   - `proof_command` (how to prove)
   - `risk_tier` (low|med|high)
   - `constraints` and `invariants`

Then hand off to `$mesh` to execute CRFIP (candidate -> fixer -> prover -> integrator) and write durable artifacts.

## Guardrails

- If teams are the execution substrate, do not claim `$mesh` truth/completion.
- Clean up teammates when done; lingering teammates burn tokens and create coordination noise.
