# Technique: Crazy 8s (rapid variation)

## One-liner
Force range fast: create eight distinct variations in eight minutes to escape your first idea (works for UI *and* for text-only designs).

## Use when
- You keep iterating on one obvious solution.
- You want range before you select.
- You need “different”, not “better”.

## Avoid when
- You need structured contradictions resolved (use TRIZ).
- You need systematic combinations across axes (use Morphological Analysis).

## Inputs
- A target: “design 8 variants of …”.
- A hard timer.

## Procedure (fast, 8–12 min)
1. Define the target artifact (CLI, API, process, page, policy).
2. Set the timer: 8 minutes.
3. Produce 8 variants; no polishing.
4. Pick 2 variants; hybridize into 1 candidate.

## Procedure (full, 15–20 min)
1. Variant forcing functions (rotate per slot)
   - Slot 1: baseline.
   - Slot 2: minimal.
   - Slot 3: “expert mode”.
   - Slot 4: “guided wizard”.
   - Slot 5: “defaults-first”.
   - Slot 6: “batch mode”.
   - Slot 7: “safety-first”.
   - Slot 8: “wild card”.
2. Converge
   - Score for signal + reversibility.
   - Convert the best into an experiment.

## Prompt bank (copy/paste)
- “Variant that removes a step.”
- “Variant that makes the safe choice the default.”
- “Variant that shifts complexity to tooling/automation.”
- “Variant optimized for first-time user.”

## Outputs (feed CPS portfolio)
- Range: 8 clearly distinct patterns.
- A hybrid candidate that steals the best elements.

## Aha targets
- A new default.
- A new unit of work.

## Pitfalls & defusals
- Pitfall: eight minor tweaks → Defusal: enforce forcing functions per slot.
- Pitfall: no convergence → Defusal: pick top 2; hybridize.

## Examples
### Engineering
Target: “8 CLI designs for the same task.”
Variants: flags-only, interactive prompts, config-file-first, wizard, presets, subcommands, safety gates, dry-run default.
Pick: dry-run default + presets; signal: fewer mistakes; escape hatch: allow `--force`.

### Mixed domain
Target: “8 ways to ask for feedback.”
Variants: anonymous form, 1:1, group retro, written prompt, office hours, rotating buddy, quick poll, ‘start/stop/continue’.
Pick: quick poll + monthly 1:1; signal: response rate; escape hatch: change cadence if fatigue rises.