---
name: seq
description: "Mine Codex session JSONL and memory artifacts with the Zig `seq` CLI. Use for explicit `$seq`, artifact/session/tool/memory/plan forensics, skill activation and outcome audits, decision provenance, `$tune` evidence, `$retrace` source capsules, review-compiler provenance, watched-session deltas, worker attribution, or reproducible historical reports. Prefer the narrowest lifted command and preserve denominators, provenance, contamination, and uncertainty."
metadata:
  version: "1.1.0"
---
# seq

## Mission
Use deterministic local session and memory evidence to answer:
```text
what happened
where it happened
what evidence supports it
what remains unknown
```
For skill/workflow analysis distinguish:
```text
presence
decision influence
downstream outcome
workflow governance
```
These are not interchangeable.

## Source boundary
Primary local sources:
```text
~/.codex/sessions
~/.codex/memories
```
`seq` is local-corpus forensics, not product-wide telemetry.
State the denominator and exclusion policy before counts.

## Capability-first rule
For current or post-change audits, run:
```bash
seq --version
seq capabilities --format json
<target-command> --help
```
Use the installed lifted surface as source of truth.
Do not recreate a newer native classifier with broad transcript searches when the installed binary is old.

## Routing ladder
### Skill decisions and tuning
```text
skill-decision-audit
skill-evidence
skill-success-rank
skill-audit
skill-cohort
workflow-audit
workflow-overlap
```
### Historical decisions and replay
```text
decision-capsule
historical_decisions dataset
turns
session-detail
artifact-search
```
### Review/workflow audits
```text
review-compiler-audit
resolve-churn-audit
adjudication-audit
goal-audit
routing-gap
```
### Session/artifact forensics
```text
artifact-search
plan-search
find-session
session-prompts
sessions
turns
session-detail
tail
```
### Tools and orchestration
```text
tool-lifecycle
tool-audit
tool-search
session-tooling
session-graph
orchestration-concurrency
```
### Memory
```text
memory-inventory
memory-provenance
memory-map
memory-history
memory-extension-audit
```
### Generic
```text
message-search
message-audit
token-usage
token-window
token-cost
query-diagnose
query
```
Use generic `query` when no lifted surface owns the relation.
See [command-routing.md](references/command-routing.md).

## Skill-decision audit
Use when asking:
```text
How did a skill affect decisions?
Was its decision contract followed?
Was activation missed?
What should $tune change?
```
```bash
seq skill-decision-audit \
  --root ~/.codex/sessions \
  --skill <skill> \
  --skill-root codex/skills \
  --repo <repo> \
  --last 30d \
  --exclude-current \
  --mode tune-packet \
  --format json
```
Modes:
```text
summary
episodes
misses
clauses
outcomes
matched-cohort
tune-packet
delta
```
Evidence levels:
```text
structured SDR-v1 receipt
explicit assistant attribution
contract-aligned action
associated outcome
co-occurrence only
```
Do not collapse these into one “used” count.
A receipt proves attribution structure, not a good outcome.

## Skill presence
Use `skill-evidence` for one watched session and `skill-audit --mode activation` for cohorts.
Preserve:
```text
explicit user call
implicit assistant declaration
injected skill block
manual skill-file read
target-skill lens use
outcome evidence
raw mention
```
Presence does not prove influence.

## Decision contracts and receipts
Decision-oriented skills may carry:
```text
references/decision-contract.yaml
skill_decision_contract / SKDC-v1
```
Authority order:
1. explicit `--contract`;
2. target skill contract under `--skill-root`;
3. no clause-level judgment.
Do not invent contract semantics in the CLI.
Strongest decision attribution:
```yaml
skill_decision_receipt:
  receipt_version: SDR-v1
  decision_id:
  skill:
  skill_contract_fingerprint:
  trigger_refs: []
  clause_refs: []
  question:
  alternatives_considered: []
  selected_route:
  rejected_routes: []
  expected_outcome:
  artifact_state:
```

## Decision capsules
Use `decision-capsule` to freeze one visible decision for `$retrace`.
```bash
seq decision-capsule \
  --root ~/.codex/sessions \
  --session-id <id> \
  --turn-index <n> \
  --anchor all \
  --outcome-policy conservative \
  --format json
```
Prefer `--decision-id` when candidate normalization produced one.
When candidates are empty:
```text
inspect turns/session-detail
locate the visible route boundary
use exact one-based turn index
```
DCP owns visible historical context and structural temporal anchors.
It does not infer hidden rationale.

## Review-compiler provenance
Aggregate counts are discovery only.
Before a session-level claim:
1. select the exact `denominator.included_sessions` row;
2. preserve the row’s session ID/path/protocol/classification;
3. cite evidence for true workflow, required, entered, closed, and compression;
4. distinguish present signals from absence-derived evidence;
5. classify workflow and closure provenance;
6. only then use the row as a `$retrace` source.
For C3/MRPC, workflow evidence roles are:
```text
controller_invocation
controller_event
controller_state
controller_receipt
explicit_workflow_declaration
artifact_under_repair
filename_or_path_mention
historical_reference
generic_prose
```
Only controller-grade evidence proves authoritative governance.
A path containing `resolve-c3` is not activation.
Generic completion, merge, or land evidence is not controller closure.
When evidence is incidental, exclude the row from the true C3 denominator rather than deriving `c3_required`.
Use ordered lifecycle evidence when available:
```text
begin
basis
candidate
ablation
proof
permit
realization
apply
commit
push
close/abort
```
See [review-compiler-provenance.md](references/review-compiler-provenance.md).

## `$retrace` source selection
When `$retrace` investigates a workflow:
```text
aggregate audit
-> included session row
-> provenance classification
-> SGG-v1
-> DCP-v1
```
Do not select a replay source from aggregate counts or fallback transcript similarity.
Allowed source-governance states:
```text
authoritative
declared_uncontrolled
incidental
ambiguous
absent
```
Only the first two permit workflow-specific replay, with limitations preserved.
See [retrace-decision-capsules.md](references/retrace-decision-capsules.md).

## Protocol separation
Do not evaluate one protocol with another protocol’s vocabulary.
For `$resolve` distinguish:
```text
legacy-cleanroom
c3-mrpc
mbk
mixed
none
```
Report:
```text
expected protocol
detected protocol
mismatch
```
Keep C3 compression evidence separate from MBK/RC/recomposition evidence.

## Churn, Git delta, and semantic surface
Never collapse:
```text
mutation churn
final Git delta
semantic surface
```
Mutation churn:
```text
patch operations
gross insertions/deletions
rewrites
```
Final Git delta:
```text
base/head
path classes
production/test/docs/generated/config
```
Semantic surface:
```text
metric name/version/unit
dimensions
baseline/head
value
```
Unknown units must be labeled `UNIT_UNRESOLVED`.

## Corpus reproducibility
For comparative audits preserve:
```text
sessions root
seq version
scanner/index version
candidate files
files opened
session-id/path digest
time window
worker inclusion
current-session exclusion
```
A fixed time window is not an immutable corpus snapshot.

## Worker attribution
Use linked workers only when requested or when the relevant decision occurred there.
Preserve:
```text
root session
worker session
parent edge
lane/receipt ID
declared skills
decision receipt
outcome
```
Do not merge unlinked worker sessions into the root denominator.

## Causality discipline
Report:
```text
explicit decision delta
contract-consistent but causality unproven
associated outcome only
co-occurrence only
```
Matched cohorts are observational.
Fork/retrace evidence is experimental but remains separate from historical source fact.

## Privacy and contamination
Default to sanitized refs and bounded excerpts.
Detect:
```text
injected skill blocks
current audit prompts
generated reports
quoted transcripts
memory summaries
examples
```
A schema example inside a skill body is not a historical decision.
Private reasoning must not be exposed as report evidence.

## Current patterns
```bash
seq artifact-search --contains "<term>" --surface messages --format jsonl
seq plan-search --repo <repo> --include-body --format jsonl
seq skill-audit --skill <skill> --mode activation --last 30d --exclude-current
seq tool-lifecycle --session-id <id> --format json
seq session-detail --session-id <id> --format markdown
seq review-compiler-audit --protocol auto --repo <repo> --format json
seq decision-capsule --session-id <id> --mode candidates --format table
```

## Hard rules
- Use the narrowest lifted command.
- Prove the installed CLI surface first for post-change questions.
- State denominators and exclusions.
- Preserve protocol and evidence provenance.
- Aggregate counts do not authorize session-level claims.
- Artifact/path mentions are not workflow activations.
- Generic delivery completion is not controller closure.
- Presence is not influence.
- Outcome association is not causality.
- Historical source fact is not replay consensus.
- Use generic query only for relations not owned by lifted commands.
- Report unresolved units, identities, and evidence gaps honestly.
