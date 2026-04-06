# Self-Test: reality-check-for-project

## Trigger Phrases (should activate)

- "where are we on this project?"
- "reality check on this project"
- "does this actually work end to end?"
- "are we on track to deliver the vision?"
- "what's the REAL status of this project?"
- "come to jesus moment for this project"
- "gap analysis between vision and code"
- "what's missing from the project?"
- "what's blocking us from finishing?"
- "is the code living up to the README promises?"
- "do we have a working implementation?"
- "is this project essentially finished?"
- "what isn't functioning properly yet?"
- "assess project health against the plan"
- "what would it take to fully deliver the vision?"
- "bridge the gap between plan and implementation"

## Non-Trigger Phrases (should NOT activate)

- "create a new project" (starting, not assessing)
- "write a README for this" (creating docs, not checking against them)
- "run the tests" (just running tests, not assessing vision delivery)
- "what does this code do?" (understanding code, not assessing against vision)
- "find bugs in this code" (bug hunting, not vision alignment — use multi-pass-bug-hunting)
- "find stubs and mocks" (mock finding, not vision alignment — use mock-code-finder)
- "plan the implementation" (initial planning, not reality-checking existing work — use planning-workflow)
- "what beads should I work on next?" (triage, not assessment — use bv skill)
- "audit the codebase for security" (domain audit, not vision alignment — use codebase-audit)

## Adjacent Skills (may co-activate or be confused)

| Skill | When to use THAT instead |
|-------|--------------------------|
| `mock-code-finder` | Finding stubs/mocks specifically, not assessing vision delivery |
| `codebase-audit` | Auditing for a specific domain (security, perf, UX), not holistic vision check |
| `comprehensive-codebase-report` | Producing architecture documentation, not gap analysis |
| `bv` | Getting next work item or triage, not holistic assessment |
| `multi-pass-bug-hunting` | Finding and fixing bugs, not vision alignment |
| `planning-workflow` | Creating initial plans, not reality-checking existing implementation |
| `idea-wizard` | Brainstorming new ideas, not auditing existing work against vision |
