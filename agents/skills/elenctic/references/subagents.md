# Native subagent execution

Use when the caller explicitly requests subagents, for example
`$elenctic PR #123 with concurrency 3 and subagents`. This route changes worker
transport and context provenance; the shared campaign and worker contracts still
own preparation, investigation, admission, coverage and authority.
Do not open separate sessions, require CAS/app-server fork preflight, or change
account, model or permission settings to run this mode.

## Contents

- [Shared preparation](#prepare-once-and-deliver-the-same-brief)
- [Worker delivery and attempts](#bind-each-delivery-to-its-actual-worker)
- [Admission and recovery](#admit-and-recover-under-the-selected-mode)

## Prepare once and deliver the same brief

Before deep preparation, inspect the available native subagent tools for creation,
completion, continuation/recovery and capacity. Require direct worker attribution,
delivery of the full assignment, and access to the frozen policy and pinned source
evidence. A missing session-fork capability is irrelevant here. If the selected
subagent route is unavailable, report that obstruction without switching modes.

Follow [campaign-brief.md](campaign-brief.md) once in the coordinator. Bind the
exact frozen brief bytes to `campaign_context_id` before launching any reviewer.
Keep that brief, policy root/ID, caller constraints and discussion-source references
available for every initial worker and replacement. Deliver the full brief in the
assignment or through an accessible immutable artifact with its bound identity;
do not substitute a title, a new summary, or a worker's account of the analysis.
Workers verify the supplied brief identity and policy before investigation.

Set `execution_mode: "subagents"` and `campaign_seed_thread_id: null`. No seed
session or dispatcher subagent is needed. The brief carries source-backed analysis
and explicit uncertainty, never private reasoning. Its digest proves byte identity,
not full-history inheritance or independent judgment.

Prefer native inheritance of the coordinator's prepared history when supported
(for example, `spawn_agent` with `fork_turns: "all"`), while supplying the canonical
assignment and exact shared brief explicitly. Preserve the coordinator's resolved
model and reasoning effort. If inheritance is unavailable, deliver the brief and
source references directly to a fresh worker. Record the actual delivery behavior.
Inherited later-wave context may also contain sibling findings and subsequent
coordinator conclusions; apply the worker's orientation-only rule to all of it.
Do not claim identical starting histories or an immutable seed. Never add those
later conclusions to the frozen brief. Neither context route grants inherited
conclusions authority over pinned source evidence.

## Bind each delivery to its actual worker

Use one reviewer per selected file and the campaign's bounded FIFO window. Clamp
active reviews to available native capacity, accounting for the coordinator and
other live agents; replenish released slots until every selected assignment is
complete or concretely obstructed. Capacity is not a total file limit.

For each initial assignment, continuation or replacement:

1. Allocate a fresh opaque `attempt_id` in the existing working set before delivery.
   Preserve the assignment ID, selected path, epoch, execution mode and brief/policy.
2. Deliver the canonical assignment, exact brief or immutable reference, and this
   attempt token. Ask the worker to echo `attempt_id` in its unquoted v1 identity.
3. Record the actual returned subagent/task ID, launch or continuation receipt,
   context delivery behavior and any runtime turn ID. Where the provider exposes
   no turn ID, record `turn_id: null`; never put the agent ID or the attempt token
   in that field. The attempt token is coordinator-owned correlation, not a native
   receipt or proof of context delivery.
4. Collect a terminal result directly attributed to that worker by the runtime,
   after the recorded delivery, with the matching attempt token. Keep the native
   result/event reference when exposed. Worker status, an ordinary progress
   message or a copied report from another worker is not a terminal result.

The campaign helper's `active_attempt` includes `worker_id`, actual `turn_id` or
null, and `attempt_id`. Its `expected_identity` and the directly returned identity
include `execution_mode: "subagents"`, null seed and that attempt token. The
`report.worker_id` and `report.turn_id` come from runtime attribution, not worker
self-description. These mechanical checks supplement direct provenance; an echoed
token alone cannot authenticate a result.

Never overlap deliveries for one assignment. If launch acknowledgement or a
completion is ambiguous, recover the actual worker state before retrying. A new
token does not prove an old attempt ended. Continue a verified idle worker when
possible, giving only its own unresolved gaps, prior evidence and relevant new
sources. If replacement is necessary, first establish the old attempt is inactive,
then deliver the unchanged shared brief and bounded assignment-specific history to
the replacement. Preserve prior findings through the ordinary consolidation rule.
Late results with an earlier token may supply evidence but no current completion.

After capturing a terminal result and its provenance, release idle worker capacity
when supported and needed. Preserve the report before closing a worker; a later
replacement uses the same assignment and explicit history. Do not close an active
or ambiguously running worker merely to obtain a slot.

## Admit and recover under the selected mode

Require the frozen brief/policy, canonical assignment, actual worker attribution
and current attempt identity at admission. Do not require a nonexistent native
seed or mistake its intentional null for incomplete coverage. Apply the same
complete-file, discussion, evidence, falsification and reconciliation standards
as session forks. Workers remain read-only; permission requests retain the current
runtime's normal handling and never authorize the coordinator to grant access.

Resume from the recorded mode, exact brief/policy, assignments, native workers and
receipts. New subagents require recoverable frozen preparation, not a session seed.
Recoverable accepted reports retain their evidence when a worker is gone; use a
replacement for unfinished work only after resolving its old active state. Missing
preparation or unresolved delivery provenance blocks dependent work. A mode change
uses campaign.md's new-instance recovery rule; never relabel old fork provenance.

Report actual subagent execution, context delivery behavior and material provenance
gaps. Do not claim session-level isolation, equal full histories, or fewer permission
prompts as a verified runtime property merely because this mode was selected.
