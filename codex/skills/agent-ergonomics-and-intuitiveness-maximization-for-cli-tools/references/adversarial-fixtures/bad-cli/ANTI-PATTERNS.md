# bad-cli Anti-Pattern Ground Truth

The 23 anti-patterns deliberately seeded into `./badcli`. The skill should
detect each one when run end-to-end against bad-cli. The detection rate is
the skill's regression metric: every change to SCORING-RUBRIC.md or to a
scorer prompt is measured against this ground truth.

## Per-anti-pattern detection contract

| AP-ID | dim violated | location | expected_signal | severity |
|-------|--------------|----------|-----------------|----------|
| AP-001 | self_documentation | bare `--help` output | help text < 5 lines, no flag list | 750 |
| AP-002 | composability | always-on color | ANSI codes when `NO_COLOR=1` set | 600 |
| AP-003 | output_parseability | `list` verb | no `--json` flag exists | 700 |
| AP-004 | determinism_and_reproducibility | `list` output | order varies across invocations | 800 |
| AP-005 | error_pedagogy | `get` (no arg) | error is just "ERROR" string | 900 |
| AP-006 | agent_ease_of_use | `get` (no arg) | exits 0 on error | 800 |
| AP-007 | safety_with_recovery | `delete` verb | no `--dry-run` flag | 700 |
| AP-008 | safety_with_recovery | `delete` verb | no confirmation prompt | 600 |
| AP-009 | regression_resistance | `delete` verb | no audit log of deletions | 500 |
| AP-010 | output_parseability | `status` output | no key-value separator (parseable format) | 600 |
| AP-011 | intent_inference | `status` output | no flag selects machine-readable output | 500 |
| AP-012 | intent_inference | `lits` (typo) | error doesn't suggest `list` | 800 |
| AP-013 | intent_inference | `GetAll` verb | inconsistent casing (camelCase in lowercase tool) | 400 |
| AP-014 | self_documentation | bare invocation | usage prints to stdout, exits 0 (vs stderr/non-zero) | 500 |
| AP-015 | intent_inference | unknown verbs | no levenshtein-1 hint | 800 |
| AP-016 | self_documentation | `--help` flag | unrecognized as a flag (errors) | 900 |
| AP-017 | intent_inference | `--version` flag | doesn't exist | 400 |
| AP-018 | error_pedagogy | unknown-verb error | doesn't list valid verbs | 700 |
| AP-019 | error_pedagogy | exceptions | leak Python tracebacks | 800 |
| AP-020 | safety_with_recovery | exception path | no cleanup of partial state | 500 |
| AP-021 | regression_resistance | repo-level | no test suite | 600 |
| AP-022 | agent_intuitiveness | repo-level | no man page / completions / docs URL | 400 |
| AP-023 | composability | help | no exit code documentation | 500 |

## How "detection" is measured

A run of the skill against bad-cli is considered to **detect** an anti-pattern
if any of these are true:

1. The anti-pattern's affected surface gets a score on its violated dim that
   is at least **`severity` points lower** than the corresponding rubric anchor
   for "as-good-as-possible". E.g., AP-005 violates `error_pedagogy` with
   severity 900: the `get` verb's `error_pedagogy` score should be ≤ 100 (a
   1000-point rubric → 1000 − 900 = 100).
2. **OR** a recommendation from Phase 4 explicitly cites the anti-pattern's
   surface and dim, with `expected_uplift_per_dim` ≥ severity / 2 on the
   violated dim.

If neither holds, the anti-pattern is missed. Track the missed-rate per dim
to identify which rubric anchors / scorer prompts are blind spots.

## Detection-rate budgets

The skill's quality is measured by:

- **Detection rate** = detected APs / total APs. Target ≥ 80% (i.e. ≥ 18/23).
- **Per-dim detection rate** = detected APs in dim D / total APs in dim D.
  Target ≥ 70% in every dim.
- **False-positive rate** = recs that don't correspond to any planted AP and
  don't reflect a real anti-pattern. Target ≤ 20% of total recs.

Below these targets, do NOT promote a SCORING-RUBRIC.md change to main.

## How to add new anti-patterns

When you observe a real-world anti-pattern not covered by this fixture:

1. Add a `# AP-NNN` comment to `badcli` at the offending location.
2. Append a row to the table above.
3. Run `scripts/skill-self-test.sh` and confirm the skill detects (or fails
   to detect — that's a finding).
4. If the skill misses it, the rubric is the bug, not the fixture.

## What this fixture does NOT cover

Anti-patterns that require:
- Multi-step workflows (this fixture is single-invocation).
- Concurrency / race conditions (no parallel execution surface).
- Network I/O (this CLI is local-only).
- Authentication flows (no auth surface).

Those need separate fixtures. This one is the "single-binary basic CLI"
archetype baseline.
