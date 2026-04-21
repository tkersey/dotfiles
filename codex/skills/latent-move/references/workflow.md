# Latent Move workflow

The workflow spine is mandatory:

```text
$latent-diver -> $creative-problem-solver -> $accretive -> $dominance -> Dominant Move Brief -> stop
```

Subagents are optional evidence lenses. They are not phases of the workflow.

## Algorithm

1. Classify entry state.
2. Create an artifact state label.
3. Build Evidence Snapshot.
4. Optionally run a small read-only subagent set.
5. Run or emulate `$latent-diver` and produce a Latent Frame Set.
6. Run or emulate `$creative-problem-solver` and produce a Five-Tier Portfolio.
7. Run or emulate `$accretive` and produce Candidate Compression + Nominee.
8. Optionally run `candidate_red_team`.
9. Run or emulate `$dominance` and produce a Dominance Verdict.
10. Produce a Dominant Move Brief.
11. Stop before execution.

## Full workflow requested

Run every companion-skill phase in order. Do not skip phases because the answer seems obvious.

## Resume requested

Resume at a later phase only when the user explicitly asks to resume and provides prior phase artifacts.

## Proposed winner already exists

Run `$dominance` directly only if the user asks specifically for validation. Otherwise recover alternatives and continue the full chain.

## Evidence gap known

Gather/read evidence first, then run the phase that uses it. Do not execute.
