# Auto Gauntlet driver prompt

Use the bundled Python driver for a normal `$prove-it` launch. Do not try to run the ten rounds manually in one assistant response.

```sh
codex/skills/prove-it/scripts/prove-it "<claim>"
```

The driver creates one initial Codex turn and nine continuation turns in the same conversation/thread. A valid run completes exactly 10 separate assistant turns and writes no prove-it state artifacts.

## Direct activation behavior

When no driver marker is present, a `$prove-it` request is a launcher request, not a round-execution request.

- If shell/tool execution is available, launch the driver command above.
- If shell/tool execution is unavailable, emit `PROVE_IT_REQUIRES_AUTOTURN_DRIVER` and the command.
- Never execute Round 1 directly from a non-driver prompt.
- Never compress all ten rounds into the current reply.
- Never create progress templates, progress files, run directories, manifests, prompt dumps, or transcript artifacts.

## Canonical resume prompt

```text
Driver: PROVE_IT_AUTOTURN_V1

Continue prove-it from the inline Checkpoint in the conversation.
Execute exactly the next uncompleted numbered round only.
Do not execute more than one round in this reply.
Do not ask whether to continue.
Do not pause for user input.
Do not return a final verdict unless executing round 10.
Do not create progress files, run directories, manifests, or transcript artifacts.
Do not stop for proof, disproof, counterexample, contradiction, confidence, likely failure, or user-requested cadence changes.
If the checkpoint is already complete at 10 of 10, report completion and do not run another round.
```

## Driver loop policy

1. Start a prove-it run only through the host driver.
2. Capture each assistant reply from stdout in memory.
3. Validate that each reply advances `Completed engine turns` by exactly one.
4. For turns 1-9, require:
   - exactly one top-level `Round N — <Focus>` heading;
   - `Status: IN PROGRESS`;
   - `Verdict embargo: ACTIVE`;
   - `Action: AUTO_CONTINUE_TO_ROUND_<N+1>` or `Action: CONTINUE_TO_ROUND_<N+1>`;
   - no final verdict;
   - no Oracle synthesis;
   - no artifact/progress/manifest contract.
5. For turn 10, require:
   - exactly one top-level `Round 10 — Oracle synthesis` heading;
   - `Status: COMPLETE`;
   - `Completed engine turns: 10 of 10`;
   - `Action: COMPLETE_ROUND_10`;
   - `Stop reason: ROUND_10_COMPLETE`;
   - Oracle synthesis;
   - final verdict;
   - no artifact/progress/manifest contract.
6. Treat any early terminal output before turn 10 as a driver failure.

## Invalid before round 10

- `Status: COMPLETE`
- `Final verdict:`
- `Oracle synthesis:`
- `Terminality Check:`
- `Terminal verdict:`
- `Action: STOP`
- `Action: STOP_CONCLUSIVE_PROOF`

## Artifact policy

The driver must not write:

```text
.prove-it-progress.md
.prove-it-progress.template.md
.prove-it-runs/
manifest.json
prompt/output transcript files
```

The conversation and the inline Checkpoint are the only state surfaces.
