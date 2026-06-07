# Material Plan Intake Template

Copy this file to `.step/st-intake.md` when the installed `st` binary does not yet provide `st intake plan`.

```markdown
# st graph intake

Source: <path-or-description>

## Intent

- intent-001 | requirement | covered
  Text: <material requirement from the source plan>
  Source: <source locator>

- intent-002 | test-expectation | covered
  Text: <material validation expectation>
  Source: <source locator>

## Items

### st-001 | feature | high

Step: <actionable task title>

Covers:
- intent-001

Depends:
- none

Locations:
- <file-or-directory>
- <test-file-or-directory>

Acceptance:
- <user-visible done criterion>
- <another criterion>

Validation:
- <command that proves the work>

Proof:
- proof-001 | <unit|integration|e2e|command|manual> | <command or evidence expectation>

Contract:
Background:
<Why this exists and what source-plan context must not be lost.>

Objective:
<What this item accomplishes.>

Implementation Approach:
<How to implement at a useful level of specificity.>

Risks:
- <risk or edge case>
- <risk or edge case>
```

Intake quality rules:

- Every material requirement, non-goal, risk, compatibility obligation, migration expectation, and validation expectation should appear under `Intent`.
- Every executable item should cover at least one intent.
- Every executable item should have acceptance criteria.
- Every executable item should have validation/proof.
- Features and bugs should have test or verification coverage.
- Dependencies should be explicit.
- Do not use this artifact as durable state. Apply it through `st intake apply`, `st graph apply`, or the documented fallback `st` commands.
