# Auto Gauntlet driver prompt

Use the bundled Python driver, not a manual sequence of prompts:

```sh
codex/skills/prove-it/scripts/prove-it-autogauntlet.py "<claim>"
```

The driver creates one initial Codex turn and nine continuation turns in the same conversation/thread. A valid run completes exactly 10 separate assistant turns.

## Canonical resume prompt

```text
Driver: PROVE_IT_AUTOTURN_V1

Continue prove-it from the checkpoint.
Execute exactly the next uncompleted numbered round only.
Do not execute more than one round in this reply.
Do not ask whether to continue.
Do not pause for user input.
Do not return a final verdict unless executing round 10.
Do not stop for proof, disproof, counterexample, contradiction, confidence, likely failure, or user-requested cadence changes.
If the checkpoint is already complete at 10 of 10, report completion and do not run another round.
```

## Driver loop policy

1. Start a prove-it run only through the host driver.
2. Capture each assistant reply as one turn.
3. Validate that each reply advances `Completed engine turns` by exactly one.
4. For turns 1-9, require:
   - `Status: IN PROGRESS`
   - `Verdict embargo: ACTIVE`
   - `Action: AUTO_CONTINUE_TO_ROUND_<N+1>` or `Action: CONTINUE_TO_ROUND_<N+1>`
   - no final verdict
   - no Oracle synthesis
5. For turn 10, require:
   - `Status: COMPLETE`
   - `Completed engine turns: 10 of 10`
   - `Stop reason: ROUND_10_COMPLETE`
   - Oracle synthesis
   - final verdict
6. Treat any early terminal output before turn 10 as a driver failure.

## Invalid before round 10

- `Status: COMPLETE`
- `Final verdict:`
- `Oracle synthesis:`
- `Terminality Check:`
- `Terminal verdict:`
- `Action: STOP`
- `Action: STOP_CONCLUSIVE_PROOF`

## Output artifacts

The Python driver writes each run to:

```text
.prove-it-runs/run-<timestamp>/
```

The run directory contains:

```text
claim.txt
prompt-01.txt ... prompt-10.txt
turn-01.txt ... turn-10.txt
manifest.json
```
