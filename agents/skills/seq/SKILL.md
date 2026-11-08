---
name: seq
description: "Reconstruct provenance-preserving observations from Codex, Pi, and OpenCode execution/session evidence with Seq 1.x. Use for explicit `$seq`, session/tool/message forensics, skill activation and outcome audits, decision provenance, `$tune` evidence, watched-session deltas, worker attribution, or reproducible historical reports. Use native commands only for physical session structure; use the owning passive observation definition for every higher-level question."
metadata:
  version: "2.2.0"
---

# Seq

## Mission

Reconstruct:

```text
facts + provenance + corpus scope + contamination + limitations + uncertainty
```

Seq does not validate durable artifacts or grant action, repair, review,
publication, or closure authority.

## Source boundary

Seq reads only:

- Codex rollout JSONL and session/state metadata needed to locate or interpret it;
- upstream Pi session JSONL selected with `--path`, `--root`, or Pi current-session hints;
- supported OpenCode execution/session sources;
- explicit immutable input relations supplied by the caller.

Select OpenCode prompt history explicitly with
`--path ~/.local/state/opencode/prompt-history.jsonl`; its prompts, parts, and
tool lifecycle use the canonical physical relations, never a source-specific
command.

Select Pi sessions explicitly; the default Codex source remains unchanged:

```bash
pi_session_root="${PI_CODING_AGENT_SESSION_DIR:-${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/sessions}"
seq sessions --root "$pi_session_root" --format json
```

Use `--path <pi-session.jsonl>` for one file, or `--path "$PI_SESSION_FILE"`
when the host supplies that variable. `seq tail --current --once` uses Pi's
`PI_SESSION_FILE`, or resolves `PI_SESSION_ID` under the selected Pi session
root. If both Codex and Pi current-session hints are present, select `--path`
explicitly to resolve the ambiguity. Scope this adapter to upstream Pi; do not
infer support for Oh My Pi from a shared name or ancestry.

Treat Pi evidence as all persisted branches in append order, not a replay of
only the active branch. Preserve raw entry `id` and `parentId`; attribute user
turns through branch ancestry rather than adjacency in the file. Pi message
text and ordinary source payloads exclude thinking blocks; explicit `raw_json`
retains the original entry. `toolCall`/`toolResult` records use the
canonical tool lifecycle. Do not interpret branch navigation as a worker graph
or the `parentSession` file path as a worker session ID.

One user entry remains one turn: its final-answer field holds the latest
persisted answer to that entry, while message/source rows retain alternative
answers. Compaction and context edits remain physical evidence; Seq does not
replay them to reconstruct Pi's effective model context.

Seq does not scan memory roots, Ledger stores, artifact directories, or another
durable source implicitly. Compose durable facts explicitly:

```bash
# Load $ledger and complete $ledger ensure once before this composition.
ledger project \
  --definition <artifact-definition.json> \
  --projection <facts> \
  --repo <repo> \
  --payload-only \
  --format json >facts.json

seq observe \
  --definition <observation-definition.json> \
  --input facts=facts.json \
  --projection <projection> \
  --format json
```

## Bootstrap and capability boundary

Require Seq major version 1, `seq-observation-abi/v1`, and
`seq-observation-result/v2` in the capability `result_schemas` list:

```bash
seq version
seq capabilities --format json
```

Check once per unchanged executable and execution environment; reuse the result
across observations. Recheck the selected definition when its closure or required
operators change. Upgrade Seq when these contracts are absent; do not interpret
an older result envelope as if it carried the current scope and health fields.

Before reading Pi evidence, require `pi-session-jsonl/v1` in `source_adapters`.
If it is absent, upgrade Seq; do not interpret Pi files with a Codex-only reader.

Capabilities report only physical adapters, native operators, renderers, cache
format, and generic limits. A missing skill-specific flag is never a fallback
signal; load the owning definition and check its ABI/operators.

## Native surface

Use native commands only for physical session structure:

```text
seq definition check
seq definition describe
seq observe
seq explain
seq sessions
seq turns
seq session-detail
seq tool-lifecycle
seq session-graph
seq tail
seq find-session
seq datasets
seq dataset-schema
seq query
seq index
seq capabilities
seq version
```

If a higher-level question cannot be expressed, add a passive observation
definition to the semantic owner. Request a new native operator only when it is
domain-independent, explicitly bounded, and necessary for three unrelated
definitions or for preserving one live behavior without material performance
loss.

## Standard Seq definitions

Resolve this skill through the current harness's catalog or an explicitly
selected repository/package. Load definitions from that same package and
version; do not infer its location from `CODEX_HOME` or another harness's install
layout. Set `seq_skill_root` to the resolved local package directory for native
CLI access. Seq owns reusable physical analyses under:

```text
<seq-skill-root>/definitions/seq/
```

Current definitions:

```text
message-search.json
session-summary.json
token-usage.json
tool-search.json
turn-metrics.json
turn-report.json
```

`tool-search.json` searches the current scalar output and retained
`output_parts_json`, including earlier outputs of a call that later completed.
It returns metadata through `rows`. Request `rows-raw` only when raw arguments,
inputs, commands, and output parts are necessary and safe. JSON-field matches
are candidate evidence; identify the matching text or reported result before
interpreting them.

Keep wrapper lifecycle, reported inner process status, and application outcome
separate. A completed wrapper with exit code zero can contain a failed process;
a successful process does not establish the requested application effect. Read
each retained part's `process_results` and preserve its `source_event_id`, line,
timestamp, and `payload_pointer`. The result's `json_pointer` addresses JSON
decoded from that part's text, not the source payload. Printed envelopes remain
reported evidence, not independent proof of execution; quoted examples and
stdout from reading an earlier result do not establish another execution.

`turn-metrics.json` reports raw sums over the selected physical `turns` rows.
Its `selected_turn_*_sum` fields are not lineage-owned token usage and must not
answer session-tree, worker-inclusive, billing-style, or corpus token totals.
Each token sum is partial unless its matching `selected_turn_*_count` equals
`turn_count`; a zero sum with a zero count means unobserved data, not zero use.
Those questions require an owning passive definition over lineage-owned token
deltas; if the installed Seq ABI does not expose that relation or operator,
report obstruction rather than summing `turns` or `sessions` token fields.

`token-usage.json` owns Codex lineage accounting and emits
`seq-token-usage-result/v2`. For a complete modern tuple, the transition is
`(total_token_usage - last_token_usage) -> total_token_usage`, and the counted
delta is `last_token_usage`. Validate nonnegative counters, cached/input and
reasoning/output subsets, reported totals, and the implied predecessor before
deduplication. Exact repeated profiles count once; a contradictory repetition
cannot erase invalid evidence. Different plausible profiles for one cumulative
total leave ownership ambiguous.

Exclude only exact transitions replayed from a strict ancestor; retain sibling
and independent-root usage. Apply session and time selection after ownership,
preserving unresolved ancestry even when the selected child or window omits
the ancestor. Require a timestamp to assign usage to a bounded window.

Return `invalid` for inconsistent counters and `unavailable` when missing fields,
ambiguous ownership, total-only legacy snapshots, or unresolved time/ancestry
prevent accounting. Both verdicts carry null token totals and diagnostic counts.
Missing cached/reasoning fields are unknown, not observed zero; they can prevent
exact lineage attribution without making the source malformed. Do not sum
cumulative legacy snapshots or infer unsupported increments from their order.

Retain genuinely observed zero-token transitions as valid zero usage. Null-info
events are neutral observations without a usage tuple; count them separately
without treating them as zero-token transitions or invalidating otherwise known
usage. With no observed transition, return unavailable rather than valid zero.
The `usage_scope` is `observed-lineage-owned-transitions`: numeric results do not
certify that every request or selected session recorded usage. Preserve the
diagnostic counts alongside the totals. Compute cached percentage as
`cached_input_tokens / input_tokens * 100`; leave it null for zero input.

Do not apply that Codex cumulative-counter definition to Pi corpus or billing
questions; requests for Pi cumulative token events fail with
`PiCumulativeTokenEventsUnavailable`. Pi normalizes each assistant message's
usage as `input_tokens = input + cacheRead + cacheWrite`,
`cached_input_tokens = cacheRead`, and `output_tokens = output`; reported
`reasoning` is already included in `output`, and `totalTokens` supplies the
reported total. Use observed Pi session/turn totals only for the selected
assistant requests with usage, and label the scope. These sums may be partial
when other assistant requests omit usage; turn counts do not prove request-level
usage completeness. If no usage was observed, totals remain null.
Standalone compaction/summary usage remains raw and is excluded from these
totals. These sums do not establish deduplicated fork/worker usage or billing.

```bash
seq_definition_root="$seq_skill_root/definitions/seq"
seq observe \
  --definition "$seq_definition_root/token-usage.json" \
  --root "${CODEX_HOME:-$HOME/.codex}/sessions/2026/07" \
  --since 2026-07-01T00:00:00-07:00 \
  --until 2026-08-01T00:00:00-07:00 \
  --projection summary \
  --format json
```

Example:

```bash
seq_definition_root="$seq_skill_root/definitions/seq"
seq observe \
  --definition "$seq_definition_root/message-search.json" \
  --path <rollout.jsonl> \
  --param "needle=<term>" \
  --projection rows \
  --format json
```

Domain observations live with their owners. For example, `$tune` owns skill
decision audits. Resolve an existing owning definition for other higher-level
questions before querying; Seq compiles passive data and does not invent a
missing owner's vocabulary, source governance, or conclusions.

## Evidence discipline

For every report preserve:

```text
definition id and closure digest
Seq ABI and binary version
source adapter/schema version
session IDs and path/corpus digest
resolved selection and selection digest; explicit time bounds and timezone
observation time, freshness policy, and source-metadata digest
worker inclusion
current-session exclusion
files opened and bytes read
discovery files opened and bytes read
physical passes and rows scanned/materialized
parser warning count and semantic contamination assessment
limitations and uncertainty
```

Preserve the observation envelope's `seq_version`, `selection`,
`selection_digest`, and `context` alongside the definition, parameter, and corpus
digests. `context.as_of_ms`, `context.ongoing_threshold_secs`, and
`context.source_metadata_digest` bind the time, freshness policy, and file
metadata used to assess liveness. Liveness is an assessment at that time, not a
historical event. A fixed time window is not an immutable corpus snapshot.
Source-event IDs locate records within a source; bind them to the corpus digest
when citing immutable evidence. A path and line can be reused after a rewrite.

`physical_passes` counts relation execution passes. Identity discovery can read
the same files separately; preserve its I/O counters rather than treating one
physical pass as one total read.

Resolve current-session exclusion against the selected source adapter. Use the
host's verified current identity, not a variable from another harness. If the
identity is unavailable or ambiguous, report exclusion as unresolved; do not
claim that the current audit was excluded.

Distinguish:

```text
presence
decision influence
downstream outcome
workflow governance
```

Likewise, keep mutation churn, final Git delta, and semantic surface separate.
Presence does not prove influence; outcome association does not prove causality;
an observation does not grant authority.

## Worker attribution

Include linked workers only when requested or when the relevant evidence occurs
there. Preserve root session, worker session, parent edge, lane/receipt ID,
declared skills, observation, and outcome. Never merge unlinked workers into the
root denominator.

## Privacy and contamination

Default to sanitized references and bounded excerpts. Detect injected skill
blocks, current audit prompts, generated reports, quoted transcripts, memory
summaries supplied as explicit inputs, and examples. Do not expose private
reasoning as report evidence.

`corpus.parser_warning_count` describes parser health only.
`corpus.semantic_contamination: "not_assessed"` leaves semantic classification
to the observation's owner. Zero parser warnings do not establish a clean
audit corpus. Preserve suspected and unresolved contamination in the report.

## Hard rules

- Use the narrowest native physical command or owning passive definition.
- State denominators, exclusions, time bounds, and timezone.
- Preserve evidence provenance and definition identity.
- Use one fused scan when several requested projections share a source.
- Never treat raw `turns` or `sessions` token sums as lineage-owned corpus usage.
- Do not interpret a definition condition-by-condition in the hot loop.
- Do not validate SKDC, SDR, DCP, EPG, or another durable artifact with Seq;
  use its canonical Ledger definition.
- Do not read a Ledger store or memory root implicitly.
- Do not replace a missing operator with shell, `jq`, Python, a plugin, or a subprocess.
- Report unresolved units, identities, contamination, and evidence gaps.
