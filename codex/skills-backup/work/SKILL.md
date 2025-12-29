---
name: work
description: "Explicit-only: run the end-to-end bead workflow (WK -> inlined TRACE-Guard loop -> select -> SI merge/close/sync)."
---

# Work

## Overview
End-to-end execution: complete the in-progress bead, open a PR, then run an inlined TRACE-Guard review/fix loop (including CI gating) until the change is ready to merge. Findings must be fully resolved; non-blocking notes are only allowed if they are tracked via follow-on beads.

## Workflow
1) **do the work**
   - Identify the in-progress bead (e.g., `bd list -s in_progress --pretty`).
   - Complete the task.
   - Run build/tests/formatters.
   - Open a PR with the changes; do not merge yet.
2) **review + fix (inlined TRACE-Guard loop)**
   - Determine the review target and review set (required):
     - Prefer PR diff if a PR exists:
       - Review target: `gh pr diff`
       - Candidate file list: `gh pr diff --name-only`
       - If `gh pr diff` fails, fall back to `git diff --name-only main...HEAD`.
     - Otherwise use the branch diff vs `main`:
       - Candidate file list: `git diff --name-only main...HEAD`
       - Review target is the corresponding `main...HEAD` diff.
     - Filter out gitignored paths from the candidate file list:
       - Exclude any file where `git check-ignore -q -- <file>` is true.
     - If no PR exists and the `main...HEAD` diff cannot be determined, emit `HUMAN INPUT REQUIRED` asking for the target and stop.
   - If the review set is empty, state that explicitly and skip Phase 2.

   - Loop until exit criteria are met (no cap on iterations):

     **Review iteration N (required each iteration)**
     1. **Heat map (TRACE)**
        - Produce a cognitive heat map over the review set (required every iteration):
          - Mark each reviewed file/area as ⚪ (smooth), 🟡 (pause-and-think), or 🔥 (hot).
          - Record surprise events: misleading names, implicit state, hidden side effects, type assertions, complex branching.

     2. **Triage failure modes**
        - Rank potential failure modes by severity: crash > corruption > logic error.

     3. **Unsoundness scan (must include concrete counterexamples)**
        - Trace nullables, lifetimes/ownership, concurrency, resource management, and IO boundaries.
        - For each applicable risk class, provide at least one concrete counterexample input or scenario; if not applicable, explicitly say why.
        - Apply the smallest sound fix that removes the class, and state the new invariant.

     4. **Invariant strengthening**
        - Name at-risk invariants and their current protection level (hope-based → runtime → construction-time → type-level).
        - Prefer construction-time/type-level enforcement over scattered runtime validation.

     5. **Footgun defusal (proactive)**
        - List hazards ordered by likelihood × severity.
        - Provide minimal misuse snippets that demonstrate the surprise.
        - Prefer safer API redesigns (named params, clearer naming, richer types, typestate) rather than documentation-only mitigations.
        - Add a test/assertion when it locks down a sharp edge.

     6. **Complexity mitigation + TRACE findings**
        - Separate essential vs incidental complexity.
        - Prefer flatten → rename → extract.
        - Report findings ordered by severity with file:line references and violated TRACE letters (T/R/A/C/E).

     7. **Classify outcomes**
        - **Findings (blocking):** any correctness/safety/maintainability issues in the changed code. Must be fixed before continuing.
        - **Notes (tracked):** non-blocking improvements allowed only if each note is tracked by a follow-on bead.

     8. **Apply fixes and validate (required)**
        - If there are blocking findings: apply fixes.
        - Re-run the relevant tests/formatters (required every iteration in which changes are made).
        - Update the PR with the fixes.

     9. **CI gate (required)**
        - Wait for green checks: `gh pr checks --watch`.
        - If checks fail, treat CI failures as blocking findings: fix, re-run tests/formatters, update PR, and start the next iteration.

   - Exit criteria (required):
     - Findings: None
     - CI: green
     - Notes (if any): every note has a follow-on bead created and linked (see below)

3) **Select next bead**
   - Invoke `$select` to choose the next bead, mark it in progress, and comment rationale.

4) **merge/close/sync**
   - Confirm CI is green (use `gh pr checks --watch` if uncertain).
   - Merge: `gh pr merge --squash --delete-branch`.
   - If merge fails due to checks/merge queue, stop and report the failure (no fallback).
   - Close the completed bead: `bd close <completed-id>`.
   - Sync beads: `bd sync`.

## Notes (tracked) and follow-on beads
Notes are allowed only when they are explicitly tracked as follow-on beads.

Required mechanics:
- Create a follow-on bead for each note.
- Add dependencies as needed (typical: follow-on depends on the current bead): `bd dep add <follow-on-id> --depends-on <current-bead-id>`.
- Comment on the original bead with the follow-on ids and why they exist.

## Guardrails
- If you need to ask *any* questions, stop and ask the human before proceeding.
- Bead bookkeeping (create/comment/dep/close/sync) is not a question; proceed.
- Never bypass failing checks or merge queues.
- Never merge with any remaining blocking findings.
- Keep status output concise and action-oriented.

## Output
- **Structured Run Report required** in the assistant response (verbatim section headers and fields below).
- **Include every question and insight surfaced during the run**, even if answered immediately.
- If a field is unknown, write `Not provided`. If a section has nothing, write `None`.
- In Phase 2, explicitly state review target, review set, iteration count, findings/notes, and CI status.

### Structured Run Report (required)
```
Run Report
- Date/Time:
- Repo/Branch:
- Bead (in progress):
- Goal:

Phase Summary
1) Do the work:
   - Work done:
   - Tests/formatters run:
   - PR created:
2) Review + fix (inlined TRACE-Guard loop):
   - Review target:
   - Review set (non-gitignored):
   - Iterations:
   - Findings (blocking):
   - Notes (tracked):
   - Follow-on beads created:
   - Tests/formatters rerun:
   - CI status (gh pr checks --watch):
   - Final status:
3) Select next bead:
   - Selected bead id:
   - Rationale:
4) Merge/close/sync:
   - CI wait:
   - Merge result:
   - Bead closed:
   - bd sync:

Questions Surfaced
- Q1:
  - Answer:

Insights / Next Steps
- Insight 1:
- Next step 1:

Artifacts
- PR link or id:
- Follow-on bead ids:
- Key diffs/files touched:
- Logs or notable outputs:
```
