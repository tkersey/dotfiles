---
name: validate
description: "Run validation loops (format/lint/typecheck/build/tests) and report signals. Use when asked to validate, run checks/tests, or repeat verification during work."
---

# Validate

## Double Diamond fit
Validate is Deliver (converge): turn "I think it's done" into an auditable signal trail. If "working" can't be stated, step back to Discover/Define first.

## Overview
Run the tightest available verification loop for current changes, repeat as needed, and report the signal.

## Workflow
1. Define "working" for this change (feature path, bug repro, or contract).
2. Choose the smallest scope; prefer local execution.
3. Run available loops in ascending cost: formatter -> lint/typecheck -> build -> targeted tests -> broader tests.
4. If a loop fails or is unavailable, capture the error, propose the smallest fix or ask for the exact command, then re-run the same loop.
5. Escalate only if confidence is still weak after the tighter loop.

## Guardrails
- Do not claim done without at least one real signal.
- If no validation command exists, add the smallest new signal (focused test or log) or ask for the command.
- Record what ran and what changed since the last run.

## Output
- Commands run and results.
- Remaining gaps or next loop to run.
