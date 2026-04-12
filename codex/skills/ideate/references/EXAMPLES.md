# Example

## Example 1 — Command safety tool

### Compressed snapshot
- Problem / opportunity: users cannot safely test command-blocking patterns without trying real commands
- Users / stakeholders: end users configuring safety rules, maintainers who support misconfigurations
- Constraints: must be pragmatic, obviously useful, and fit current CLI mental model
- Existing work / overlap: current blocking exists, but testing and explanation are weak
- Leading direction: pattern testing workflow

### Top 5 ideas
1. Pattern testing mode
2. Natural-language explanations for blocked commands
3. Safer command rewrite suggestions
4. Temporary / expiring allowlist entries
5. Context-aware allowlisting

### Chosen direction
Pattern testing mode won because it addresses an immediate user pain, reduces fear and trial-and-error, is easy to validate, and makes later explanation features easier to reason about.

### Plan seed
```md
# Plan Seed: Pattern Testing Mode

## Thesis
Add a safe way for users to check whether a pattern would match a command, without executing anything, so they can configure safety rules confidently.

## Problem / Opportunity
Users currently learn rule behavior through trial and error. That creates friction, confusion, and distrust in the safety system.

## Primary Users / Stakeholders
Primary users are people authoring or debugging safety patterns. Maintainers benefit because support burden should drop.

## Why Now
The existing safety system already exists, so confidence and usability are the next leverage point. This looks like a high-value improvement without requiring a product reset.

## What Gets Better
Users can verify patterns intentionally, understand mismatches faster, and adopt stricter safety rules with less fear.

## Boundaries
### In at seed stage
- a non-destructive pattern test flow
- clear match / no-match feedback
- explanation of why a rule matched or failed

### Out for now
- automatic rule generation
- ML-driven suggestions
- broad policy redesign

## Existing Context and Overlap
This extends the current safety workflow rather than replacing it. It is adjacent to explanation features and may enable them later.

## Why This Won
It solves a sharp, recurring user pain, has a clear validation path, and creates leverage for future usability improvements.

## Assumptions to Validate
- users frequently struggle to predict rule behavior
- a test-only workflow would materially reduce misconfiguration time
- explainability can be expressed clearly enough to help, not confuse

## Risks and Unknowns
- explanations may become too verbose
- edge cases in pattern semantics may expose deeper rule inconsistencies
- users may still want examples or suggestions beyond pure testing

## Enablers / Prerequisites
- access to the same matching logic used by the real blocker
- a stable way to render match diagnostics

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
Draft a narrow planning document for a test-only CLI flow and validate it against real examples of confusing patterns.
```
