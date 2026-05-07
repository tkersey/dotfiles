# Examples

## Example — CLI diagnostic primitive escalated into a proof surface

### 1. Compressed repo snapshot

- Scope: command-line tool with rule matching and safety blocks
- Primary user-facing surfaces: CLI commands, config file, blocked-command messages
- Primary maintainer surfaces: matcher tests, config parser, release scripts
- Signal sources inspected: README, command files, matcher tests, TODO comments, changelog
- Assumptions / blind spots: no issue export was available

### 2. Opportunity map

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

### 3. Escalation ledger

#### Chosen direction escalation chain

- Baseline idea: Add a pattern testing CLI command.
- Why the obvious version loses: A simple test command helps debugging, but it remains a local convenience feature and does not change how the project proves safety behavior over time.
- Glaze material delta: Reframe the command as a reusable **policy proof surface**: the same matcher explanation artifact powers user diagnostics, golden tests, regression fixtures, and support repros.
- Stronger move: Define one canonical match-explanation format and expose it through a non-executing CLI mode plus golden fixtures.
- ASI 10x frame: Make safety policy behavior explainable and falsifiable instead of tribal knowledge embedded in code and scattered examples.
- Systemic leverage point: A proof surface that lets users, maintainers, and future tools coordinate around one shared explanation of why a command matched or did not match.
- Smallest proof-bearing artifact: A JSON/text match-explanation trace for one existing matcher path, validated against current matcher fixtures.
- Cash-out type: Proof surface + interface.
- First proof signal: Existing matcher fixtures can produce stable explanation traces without changing enforcement behavior.
- Evidence anchor: `src/matcher.ts`, `tests/matcher.test.ts`, README safety examples.

### 4. Top 5 breakthrough ideas

#### 1. Canonical policy proof surface

- Category: DX / diagnostics / reliability
- Evidence: matcher tests and config docs imply users need to understand match behavior
- Originality source: hidden primitive + diagnostic inversion + proof surface
- User / maintainer benefit: users debug safety rules without executing commands; maintainers get stable regression artifacts for policy behavior
- Why this beats alternatives: it turns a one-off diagnostic command into a reusable proof layer for docs, tests, support, and future tooling
- Why this is not generic: it is tied to existing matcher semantics and user-facing safety configuration
- Glaze material delta: command → canonical explanation artifact
- ASI 10x frame: make safety behavior explainable and falsifiable across users, maintainers, and tools
- Smallest proof-bearing artifact: one stable matcher explanation trace emitted from existing fixtures
- Cash-out type: Proof surface + interface
- First proof signal: fixture-backed traces match current blocking behavior exactly
- Validation path: prototype output against existing matcher fixtures
- Risks / behavior-change concerns: explanation output could expose confusing internals; enforcement behavior must remain unchanged
- Overlap status: net-new from available docs

#### 2. Config doctor as policy preflight

- Category: DX / reliability
- Evidence: README pattern examples plus TODO near config validation
- Originality source: repeated workaround + sharp edge
- Glaze material delta: linting command → preflight protocol for policy changes
- ASI 10x frame: make policy configuration safely reviewable before runtime
- Smallest proof-bearing artifact: detect one shadowed or unreachable rule in sample configs
- Cash-out type: Mechanism

#### 3. Rule fixture generator

- Category: test harness / refactor enabler
- Originality source: repeated workaround
- Glaze material delta: helper utility → contributor protocol for adding policy cases
- ASI 10x frame: make matcher behavior extensible without weakening confidence
- Smallest proof-bearing artifact: generate one fixture from a command + expected rule
- Cash-out type: Interface

#### 4. Safety-rule golden output suite

- Category: reliability / behavior-preserving refactor enabler
- Originality source: behavior-preserving unlock
- Glaze material delta: tests → compatibility contract
- ASI 10x frame: make future matcher refactors safe by making behavior externally stable
- Smallest proof-bearing artifact: golden output for existing high-risk patterns
- Cash-out type: Proof surface

#### 5. Shadowed-rule warning

- Category: diagnostics
- Originality source: negative space + sharp edge
- Glaze material delta: warning → policy order explanation
- ASI 10x frame: make rule interactions understandable before they create surprising blocks
- Smallest proof-bearing artifact: detect one rule shadowed by an earlier rule
- Cash-out type: Mechanism

### 5. Next 10 ideas

1. **Explain blocked command output** — Diagnostics; hidden matcher state; kept as adjacent to the proof surface.
2. **Config schema export** — DX; parser already defines shape; ASI artifact could be editor validation, but less central.
3. **Minimal repro bundle command** — Support; could use the proof trace, but weaker as a first move.
4. **Matcher performance probe** — Performance; validate only if large rule sets are common.
5. **Rule naming convention** — Onboarding; useful but lower leverage than a proof surface.
6. **Matcher boundary extraction** — Refactor; valuable after golden traces exist.
7. **Blocked-command telemetry hook** — Observability; privacy-sensitive, demoted.
8. **Interactive config tutorial** — Docs/onboarding; better after canonical traces exist.
9. **Temporary allowlist entries** — Feature; possible conflict with strict safety posture.
10. **Safer command rewrite suggestions** — UX; useful but higher behavior-risk.

### 6. Ideas cut

- **Rewrite the rule engine** — ASI failed: too large and not proof-bearing before value appears.
- **AI-generated safety rules** — ASI failed: ungrounded in repo evidence.
- **Add more README examples** — Glaze failed: no material delta beyond documentation.
- **Generic test coverage push** — Glaze failed: generic cleanup rather than a proof surface.

### 7. Overlap findings

- Direct duplicates: none found in README/changelog/TODO scan.
- Adjacent / merge mentally: blocked-command explanation and config doctor should share the canonical trace.
- Conflicts: temporary allowlists may conflict with strict safety posture.
- Net-new: canonical policy proof surface, fixture generator, golden output suite.
- Unknown due to thin evidence: user support frequency.

### 8. Chosen direction

The canonical policy proof surface wins because the escalated version turns a useful diagnostic idea into a reusable proof artifact. It helps users debug rules, gives maintainers behavior-preserving confidence, and creates a stable interface future tools can consume without changing enforcement behavior.

### 9. Plan seed

```md
# Plan Seed: Canonical Policy Proof Surface

## Thesis

Create a stable, non-executing matcher explanation artifact so safety policy behavior becomes explainable, testable, and reusable across user diagnostics, golden tests, and support workflows.

## Problem / Opportunity

Users currently learn rule behavior through trial and error. Maintainers protect matcher behavior through tests, but the system lacks a shared artifact that explains why a rule matched or did not match.

## Primary Users / Stakeholders

Primary users are people authoring or debugging safety patterns. Maintainers benefit because regression confidence and support reproduction improve.

## Why Now

The matcher and fixtures already exist, so exposing a proof surface is likely higher leverage than adding more static examples.

## What Gets Better

Users can verify patterns intentionally, maintainers can preserve behavior during refactors, and future diagnostic commands can reuse the same explanation artifact.

## Breakthrough Frame

- Baseline idea: Add a pattern testing CLI command.
- Glaze material delta: Reframe it as a canonical policy proof surface.
- ASI 10x horizon: Make safety policy behavior explainable and falsifiable across users, maintainers, and tools.
- Smallest proof-bearing artifact: A stable matcher explanation trace for one existing matcher path, validated against current fixtures.
- Cash-out type: Proof surface + interface.
- First proof signal: Fixture-backed traces match current blocking behavior exactly.

## Boundaries

### In at seed stage

- non-destructive matcher explanation artifact
- one existing matcher path
- stable rendering suitable for tests and diagnostics

### Out for now

- automatic rule generation
- broad policy redesign
- telemetry
- persistent allowlist changes

## Existing Context and Overlap

This extends the current safety workflow rather than replacing it. It is adjacent to blocked-command explanation output and config doctor ideas, which should reuse the same proof surface later.

## Evidence Base

- `src/matcher.ts` — matching logic already centralizes rule evaluation
- `tests/matcher.test.ts` — fixtures encode expected match behavior
- README safety examples — users are expected to author patterns manually

## Originality Source

Hidden primitive plus diagnostic inversion plus proof surface: the system already computes useful state, but users and maintainers lack a stable artifact for explaining and preserving it.

## Why This Won

It beats a simple CLI test mode because it creates a reusable artifact that can support diagnostics, tests, support, and future refactors while keeping enforcement behavior stable.

## Assumptions to Validate

- users frequently struggle to predict rule behavior
- a stable explanation trace can be expressed clearly enough to help
- the trace can be generated without changing enforcement behavior

## Risks and Unknowns

- explanations may become too verbose
- edge cases in pattern semantics may expose deeper rule inconsistencies
- the canonical artifact may accidentally freeze internals that should remain flexible

## Behavior and Compatibility Considerations

The real blocking behavior should remain unchanged. The proof surface should observe the matcher path without altering it.

## Enablers / Prerequisites

- access to the same matching logic used by the real blocker
- stable way to render match diagnostics
- fixtures that can serve as golden examples

## Validation Path

- prototype traces against existing matcher fixtures
- verify traces do not require behavior changes
- check whether traces make confusing examples easier to understand

## Success Signals

- fixture-backed traces are stable and understandable
- maintainers can use traces as golden outputs before refactoring
- users can diagnose pattern behavior without executing commands

## Candidate Workstreams

- explanation trace shape
- fixture-backed proof examples
- non-executing diagnostic surface
- edge-case and compatibility review

## Questions for the Planning Pass

- what exact fields belong in the canonical trace?
- should the first surface be CLI text, JSON, or both?
- which matcher edge cases must be covered to make this trustworthy?

## Recommended Next Move

Draft a narrow planning document for one matcher explanation trace format and validate it against real matcher fixtures before designing broader diagnostics.
```
