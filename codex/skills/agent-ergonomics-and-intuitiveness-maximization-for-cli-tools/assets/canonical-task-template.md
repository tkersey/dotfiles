# Canonical Task Template

Use this template when collecting canonical-task definitions during intake. The simulator uses these as input.

A canonical task is something `<TOOL>` is *documented* to support. It's the agent's "first day on the job" workload.

---

## Task NN: <slug>

**Statement.** (One-paragraph description, written from the user's perspective. Don't pre-decide the commands; describe the *outcome*.)

Example:
> "List all items, filter to those tagged 'urgent', and produce a JSON report with their IDs and timestamps. Save the report to a file."

**Tags.** <list of relevant categories: read-only / mutating / pipe-friendly / multi-step / requires-config>

**Expected outcome.**
- exit code: 0
- stdout: ...
- side effects: ...

**Documented in.** <README example link, or `<tool> --help <verb>` where it's mentioned>

**Pre-pass round-trips estimate.** <K> (how many calls a fresh agent would need before this audit pass)

**Post-pass target.** <K-1 or K> (lower is better)

---

## Selection criteria for canonical tasks

- Document only tasks the tool's own materials (README, --help, robot-docs) actually claim to support.
- Cover at least one read-only task and one mutating task.
- Cover at least one multi-step task that would benefit from a mega-command.
- Don't pad — 5 tasks for a small CLI is fine.
- Don't include tasks that require external services (network, auth) unless those are part of the canonical use case.

## Storage

Save the task list to `<SIBLING>/audit/canonical_tasks.md` (one task per `## Task NN: <slug>` heading). The simulator reads this file as its task list input.
