# Examples

## Example 1 — CLI diagnostic primitive

### Compressed repo snapshot

- Scope: command-line tool with rule matching and safety blocks
- Primary user-facing surfaces: CLI commands, config file, blocked-command messages
- Primary maintainer surfaces: matcher tests, config parser, release scripts
- Signal sources inspected: README, command files, matcher tests, TODO comments, changelog
- Assumptions / blind spots: no issue export was available

### Opportunity map

#### Theme: Hidden matcher state is not user-visible

- Evidence: `src/matcher.ts`, `tests/matcher.test.ts`, README safety configuration examples
- Observation: matching logic already computes why a rule matched, but CLI output only says a command was blocked
- Opportunity implied: expose a safe pattern-testing and explanation flow
- Confidence: High

#### Theme: Configuration debugging is trial-and-error

- Evidence: README examples, repeated tests around edge-case patterns, TODO near config validation
- Observation: users appear expected to test rules by running real or near-real commands
- Opportunity implied: non-executing dry-run diagnostic command
- Confidence: Medium

### Top 5 ideas

1. **Pattern testing mode**
   - Category: DX / diagnostics
   - Evidence: matcher tests and config docs imply users need to understand match behavior
   - Originality source: hidden primitive + diagnostic inversion
   - Benefit: users can debug safety rules without executing commands
   - Why this is not generic: it is tied to existing matcher semantics and user-facing safety configuration
   - Validation path: prototype output against existing matcher fixtures
   - Overlap status: net-new from available docs

2. **Explain blocked command output**
   - Category: UX / diagnostics
   - Originality source: diagnostic inversion
   - Benefit: users understand which rule blocked a command and what to change

3. **Config doctor command**
   - Category: DX
   - Originality source: repeated workaround
   - Benefit: users detect invalid or shadowed rules before runtime

4. **Rule fixture generator for tests**
   - Category: refactor / test harness
   - Originality source: repeated workaround
   - Benefit: maintainers add matcher cases with less brittle setup

5. **Safety-rule golden output suite**
   - Category: reliability / behavior-preserving refactor enabler
   - Originality source: behavior-preserving unlock
   - Benefit: protects matcher behavior before deeper simplification

### Next 10 ideas

1. **Shadowed-rule warning** — Diagnostics; config examples imply order matters; validates by scanning sample configs.
2. **Safer command rewrite suggestions** — UX; blocked command output could offer allowed alternatives; higher behavior-risk.
3. **Temporary allowlist entries** — Feature; adjacent to blocking workflow; requires policy decisions.
4. **Config schema export** — DX; config parser already defines shape; helps editor integration.
5. **Minimal repro bundle command** — Support; gathers config and debug traces without secrets.
6. **Matcher performance probe** — Performance; large rule sets may scale poorly; validate before optimizing.
7. **Rule naming convention** — Onboarding; examples lack stable names; weaker than diagnostics.
8. **Matcher boundary extraction** — Refactor; current CLI and tests both know matcher details.
9. **Blocked-command telemetry hook** — Observability; potentially useful but privacy-sensitive.
10. **Interactive config tutorial** — Docs/onboarding; useful but less leveraged than test mode.

### Ideas cut

- **Rewrite the rule engine** — too much risk before proving current semantics are inadequate.
- **AI-generated safety rules** — speculative and not grounded in current repo evidence.
- **Add more README examples** — useful, but weaker than a structural diagnostic workflow.

### Overlap findings

- Direct duplicates: none found in README/changelog/TODO scan.
- Adjacent / merge mentally: explanation output is adjacent to pattern testing mode.
- Conflicts: temporary allowlists may conflict with strict safety posture.
- Net-new: pattern testing mode, config doctor, golden output suite.
- Unknown due to thin evidence: user support frequency.

### Chosen direction

Pattern testing mode wins because it turns existing matcher internals into a user-facing diagnostic capability, reduces configuration trial-and-error, and creates a validation path through existing matcher fixtures.

### Plan seed

```md
# Plan Seed: Pattern Testing Mode

## Thesis

Add a safe way for users to check whether a safety pattern would match a command without executing anything, so they can configure rules confidently.

## Problem / Opportunity

Users currently learn rule behavior through trial and error. That creates friction, confusion, and distrust in the safety system.

## Primary Users / Stakeholders

Primary users are people authoring or debugging safety patterns. Maintainers benefit because support burden should drop.

## Why Now

The matcher and test fixtures already exist, so exposing a diagnostic path is likely higher leverage than adding more static examples.

## What Gets Better

Users can verify patterns intentionally, understand mismatches faster, and adopt stricter safety rules with less fear.

## Boundaries

### In at seed stage

- non-destructive pattern test flow
- clear match / no-match feedback
- explanation of which rule matched or why none matched

### Out for now

- automatic rule generation
- broad policy redesign
- persistent allowlist changes

## Existing Context and Overlap

This extends the current safety workflow rather than replacing it. It is adjacent to explanation features and may enable them later.

## Evidence Base

- `src/matcher.ts` — matching logic already centralizes rule evaluation
- `tests/matcher.test.ts` — fixtures encode expected match behavior
- README safety examples — users are expected to author patterns manually

## Originality Source

Hidden primitive plus diagnostic inversion: the system already computes useful state, but users cannot safely query it.

## Why This Won

It solves a sharp configuration problem, has a clear validation path, and creates leverage for future usability improvements without changing enforcement behavior.

## Assumptions to Validate

- users frequently struggle to predict rule behavior
- a test-only workflow would materially reduce misconfiguration time
- explanations can be expressed clearly enough to help, not confuse

## Risks and Unknowns

- explanations may become too verbose
- edge cases in pattern semantics may expose deeper rule inconsistencies
- users may still want examples or suggestions beyond pure testing

## Behavior and Compatibility Considerations

The real blocking behavior should remain unchanged. The new flow should call the same matcher path in a non-executing mode.

## Enablers / Prerequisites

- access to the same matching logic used by the real blocker
- stable way to render match diagnostics
- fixtures that can serve as golden examples

## Validation Path

- inspect support issues and user notes for configuration confusion
- prototype CLI output with sample patterns and commands
- test whether users can predict and correct rules faster

## Success Signals

- users can test patterns without running commands
- misconfiguration debugging becomes faster
- fewer support questions about why something matched

## Candidate Workstreams

- test-mode user flow
- match diagnostic output
- edge-case and rule-semantics review
- validation and usability feedback

## Questions for the Planning Pass

- what exact inputs should the test flow accept?
- how much explanation is enough without becoming noisy?
- which edge cases must be covered to make this trustworthy?

## Recommended Next Move

Draft a narrow planning document for a test-only CLI flow and validate it against real matcher fixtures and confusing pattern examples.
```
