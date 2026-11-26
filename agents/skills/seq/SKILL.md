---
name: seq
description: "Reconstruct bounded, provenance-preserving observations from supported native sessions and explicit input relations with Seq 1.x. Use for `$seq`, session, tool, and message forensics, token accounting, worker attribution, or historical evidence reports."
metadata:
  version: "2.4.0"
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

Seq reads Codex rollouts, Claude Code transcripts, upstream Pi session JSONL,
OpenCode prompt history, and caller-supplied immutable relations. Select sources
by the executable's advertised adapter capabilities, independently of the agent
running this skill. A shared skill directory does not itself supply an adapter.

### Codex

The default corpus includes Codex's `sessions` and `archived_sessions`
directories. An explicit `--root` limits discovery to that directory; it
does not silently add its sibling archive. Both `.jsonl` and `.jsonl.zst`
rollouts are supported. Preserve the resolved active/archive roots from the
result, and treat unreadable, corrupt, or unsupported evidence as an obstruction
to a complete historical claim.

Select time through `--since`/`--until`, not calendar subfolders. A session's
folder reflects its start date; later work and fork ancestors can live outside
the requested month. Time selection does not reduce input bytes read before
filtering, and compression does not reduce the decoded input budget. Do not
describe a bound failure or an omitted archive as zero activity.

A fork can begin with child metadata followed by copied ancestor metadata and
history. Use the primary identity, `forked_from_id`, and the
`subagent_history_start_ordinal` replay boundary;
inherited metadata is not another child or an independent execution. Worker
edges require recorded linkage; copied history alone proves neither a spawn nor
new work. Use `CODEX_THREAD_ID` only when it identifies this audit's actual
Codex session, and bind that ID to a definition's exclusion parameter.

### Claude Code

Require `claude-code-transcript-jsonl/v1` in `source_adapters`. Select a
transcript with `--path <session.jsonl>` or a known session directory with
`--root`; do not feed
Claude transcripts to an executable that lacks the adapter. Resolve the actual
configured source location; an encoded project directory name is not reliable
repository identity. Explicit selection does not change the default Codex corpus.

Preserve `native_id` and `native_parent_id` from source events for Claude's
`uuid` and physical `parentUuid`; these fields require Seq 1.6.0 or newer, and
other adapters leave them null. Read persisted branches in physical source order;
branch ancestry is not a worker edge and does not reconstruct the active model
context. Compaction and summaries remain evidence of context changes, not a
replacement for omitted history. Report unsupported record kinds and parser
limitations instead of treating skipped data as an empty conversation.

Ordinary text excludes thinking, redacted thinking, and signatures. Tool-use and
tool-result blocks retain call identity; a tool-result wrapper is not another
human request. Keep all retained result parts and distinguish reported tool
errors from process exit status. Only recorded worker linkage supports worker
attribution. Claude token rows are per-request; account for them with
`token-usage.json`, never by summing message or turn counters. Missing token
counters remain unknown.

### Pi and OpenCode

Select upstream Pi with `--path <pi-session.jsonl>` or `--root <pi-sessions>`.
Its usual root is `PI_CODING_AGENT_SESSION_DIR`, otherwise
`${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/sessions`.
`seq tail --current --once` uses the host's `PI_SESSION_FILE` or resolves
`PI_SESSION_ID`. Select a path when Codex and Pi hints conflict. Do not infer
Oh My Pi support. Pi evidence includes all persisted branches in append order;
use entry ancestry for turns. Branch navigation and a `parentSession` file
path are not worker edges. Ordinary text omits thinking; explicit `raw_json`
retains the original entry. Compaction does not reconstruct effective context.
One user entry remains one turn: its final answer is the latest persisted answer,
while message/source rows retain alternatives. Preserve raw `id` and `parentId`
when attributing Pi evidence.

Select OpenCode only with
`--path ~/.local/state/opencode/prompt-history.jsonl`. This is prompt history,
not a general execution-session reader. It rejects `--repo`, `--since`,
`--until`, and `--last`, and does not support lineage observations. Its
file-derived identity cannot isolate the current conversation within that file.

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
`seq-observation-result/v2` in `result_schemas`. Search excerpts additionally
require the advertised `derive` operator version 3 or newer (`text-prefix`):

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
Before reading Claude evidence, require `claude-code-transcript-jsonl/v1`.
For compressed history, require `jsonl.zst` in `source_encodings`; a clean result
from an older executable does not prove it discovered compressed files.

Capabilities report physical adapters, native operators, renderers, cache
format, and generic limits. A missing skill-specific flag is never a fallback
signal; load the owning definition and check its ABI/operators.

## Native surface

Use native commands for physical session structure. Use `<command> --help`
for its selectors; a definition's selectors are independently declared.
For `observe`, `--path` cannot be combined with `--root` or `--session-id`.

| Need | Command |
| --- | --- |
| Find a path from an ID | `seq find-session --session-id <id> --format json` |
| Inspect one session | `seq session-detail --path <rollout> --format json` |
| Inspect turns, tools, or edges | `seq turns`, `seq tool-lifecycle`, or `seq session-graph`, with `--path <rollout> --format json` |
| Discover fields | `seq datasets --format json`; `seq dataset-schema --dataset <name> --format json` |
| Check a definition | `seq definition check --definition <file> --format json` |
| Inspect its interface and plan | `seq definition describe --definition <file> --format json`; `seq explain --definition <file> --projection <name> --param <name>=<value> --format json` |

`seq query --spec <json|@file>` accepts only `dataset`, `select`,
`where`, `sort`, `limit`, and `format`. Use passive observations for
grouping, aggregates, and higher-level questions. Native failures remain failures;
read their diagnostics or use an observation that preserves parser limitations.
Never parse a failed command's stdout as successful rows.

For a one-off question, write a temporary passive definition, check it, and
preserve its closure digest with the result. Reuse an owning definition when one
fits; save a recurring interpretation with its semantic owner. A temporary
checked definition needs no skill edit and grants no new authority.

## Standard Seq definitions

Resolve this skill through the current harness's catalog or an explicitly
selected repository/package. Load definitions from that same package and
version; do not infer its location from `CODEX_HOME` or another harness's install
layout. Set `seq_skill_root` to the resolved local package directory for native
CLI access. Seq owns reusable physical analyses under:

```text
<seq-skill-root>/definitions/seq/
```

| Definition | Accepted selection | Projection |
| --- | --- | --- |
| `message-search.json`, `tool-search.json` | `path`, `root`, `session-id`, `repo`, `since`, `until`, `last` | `rows`; `rows-raw` for necessary payloads |
| `session-summary.json`, `turn-report.json` | `path` only; resolve an ID through `find-session` first | `rows` |
| `turn-metrics.json` | `path`, `root`, `session-id`, `repo`, `since`, `until`, `last` | `summary` |
| `token-usage.json` | `path`, `root`, `session-id`, `repo`, `since`, `until` | `summary` |

Both searches require `needle` and an explicit `exclude_session_id`. Bind the
verified current identity for historical audits; bind an empty string only for
intentional non-exclusion and report that choice. Missing or ambiguous identity
remains unresolved. `message-search` also accepts `role=user` or
`role=assistant`; its default empty role selects all public message roles.
Private messages are excluded; remaining rows can still be injected instructions
or quoted prompts.

Searches return at most 100 rows with deterministic timestamp/path/identity ties.
`rows` includes UTF-8-safe excerpts capped at 512 bytes and an explicit
per-excerpt truncation flag. Bounded text is not automatic redaction. A full
100-row page may omit more matches: narrow the selection or check a temporary
count/projection before making an exhaustive claim. A definition-bound limitation
states a configured bound, not proof that truncation occurred.

`tool-search.json` searches the current scalar output and retained
`output_parts_json`, including earlier outputs of a call that later completed.
Its `rows` projection adds `request_kind`, `request_excerpt`, and
`request_excerpt_truncated`, choosing recorded command text, then input text,
then argument JSON. An `exec` input is code supplied to a wrapper, not proof of
which commands ran. Request `rows-raw` only when full arguments, inputs, commands,
and output parts are necessary and safe. JSON-field matches
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
Its `selected_turn_*_sum` fields are not owned token usage and must not answer
session-tree, worker-inclusive, billing-style, or corpus token totals. Each token
sum is partial unless its matching `selected_turn_*_count` equals `turn_count`;
a zero sum with a zero count means unobserved data, not zero use. Answer those
questions with `token-usage.json`; if the installed executable cannot emit
`token_events` for the selected adapter, report that obstruction rather than
summing `turns` or `sessions` token fields.

`token-usage.json` owns token accounting for every adapter that emits
`token_events` and returns `seq-token-usage-result/v3`. Route each row by the
evidence it carries, never by adapter name: rows asserting cumulative totals use
cumulative lineage accounting, and rows declaring `usage_model: "per-request"`
use per-request accounting. Both feed one result:
`usage_count = transition_count + request_count`, shared totals, one verdict, and
`usage_scope: "observed-owned-usage"`. An adapter whose token events Seq refuses
(Pi returns `PiCumulativeTokenEventsUnavailable`) is an obstruction; report it
rather than substituting another sum.

Every accounting model reports the same quantities. `input_tokens` includes
cache reads and cache writes, `cached_input_tokens` is cache reads,
`cache_creation_input_tokens` is cache writes, `output_tokens` includes
reasoning, and `total_tokens = input_tokens + output_tokens`. A field total is
null when any counted unit lacks that field: cumulative counters report no cache
writes, and an adapter may omit reasoning. Unknown is not zero. Compute cached
percentage as `cached_input_tokens / input_tokens * 100`; leave it null for zero
or unknown input.

Return `invalid` for inconsistent counters and `unavailable` when missing fields,
ambiguous or unresolved ownership, total-only legacy snapshots, unresolved time
or ancestry, or no counted usage prevent accounting. Both verdicts carry null
token totals and diagnostic counts. A `valid` verdict means the observed counters
are consistent and owned, not that corpus coverage is complete: numeric results
do not certify that every request or selected session recorded usage. Preserve
the diagnostic counts alongside the totals. Require a timestamp to assign usage
to a bounded window.

`--session-id` and `--path` are tree-inclusive: they count the selected session
and its control descendants. `control_parent_session_id` selects workers;
`parent_session_id` records history ancestry. They may differ legitimately.
Workers without recorded linkage are not included; report worker inclusion. For
an exact-session question, use a checked variant that selects only the seed
after ownership; do not silently present a tree total as the selected session
alone. `--repo` excludes evidence outside that repository. Use a broader source
scope without a repository filter when the question requires complete ownership.

**Cumulative accounting.** A cumulative row asserts running totals. For a
complete modern tuple, the transition is
`(total_token_usage - last_token_usage) -> total_token_usage`, and the counted
delta is `last_token_usage`. Validate nonnegative counters, cached/input and
reasoning/output subsets, reported totals, and the implied predecessor before
deduplication. Exact repeated profiles count once; a contradictory repetition
cannot erase invalid evidence. Different plausible profiles for one cumulative
total leave ownership ambiguous.

Exclude a matching ancestor transition only when the child's persisted rollout
ordinal places the record before `subagent_history_start_ordinal`. The physical
`source_ordinal` is an occurrence index, not that persisted ordinal. A record
after the boundary can repeat a seeded baseline without new usage. For child
progress, require the latest preceding complete observed cumulative tuple to
equal `total_token_usage - last_token_usage` in all five components. Neutral
records preserve that baseline; incomplete or invalid assertions break it.
Preserve same-session exact-profile deduplication across the boundary. This
retains proven child work even when an ancestor later records the same tuple.

A fork-linked record with unknown ordinal/boundary, an unobserved initial
baseline, or unmatched inherited usage leaves attribution unavailable. Older
logs without those facts no longer receive a confident total from counter
equality alone. Retain sibling and independent-root usage. Apply session and
time selection after ownership, preserving unresolved ancestry even when the
selected child or window omits the ancestor. Tree-inclusive selection loads
history ancestors for ownership; an ancestor outside the selected control tree
is read without counting its work. Under `--repo`, an in-repository child of an
out-of-repository ancestor can therefore be unavailable.

Missing cached/reasoning fields are unknown, not observed zero; they can prevent
exact lineage attribution without making the source malformed. Do not sum
cumulative legacy snapshots or infer unsupported increments from their order.
An absent, excluded, or unread history ancestor, or one with no asserted token
tuples, also leaves descendant ownership unavailable under this attribution rule.
`token_usage_observation_count` measures asserted records before replay removal;
replayed counters and observed zero remain evidence. Neutral records alone do not
establish an ancestor's usage baseline, though neutral leaves remain harmless.
Retain genuinely observed zero-token transitions as valid zero usage. Null-info
events are neutral observations without a usage tuple; count them as no-usage
observations without treating them as zero-token transitions.

**Per-request accounting.** A per-request row reports one request's own usage,
identified by `request_key`. Count a request once when its usage is `usable`,
its `usage_finality` is `final`, it has a key, and its owner is in the
selection. History ancestry does not apply: request identity, not counter
equality, removes replayed history.

Ownership comes from `request_record`. `here` proves the source issued the
request; `elsewhere` proves a copy, which never owns usage and is reported as
replayed. A key without a proven author (`unplaced` or null) counts once only
when the selection is the whole read corpus. A `--session-id`, `--path`, or
`--repo` selection cannot read copies held elsewhere, so such keys leave
ownership unresolved. Two sessions that both claim to have issued one key, or
copies of one key with different usage profiles, are unresolved or ambiguous.

A request without asserted usage (unanswered, or a response with no usage) is a
no-usage observation. A provisional request has not finished; report it without
counting it. Asserted but unreadable usage is missing core evidence, a usable
request without a key is unkeyed, and impossible counters (a declared invalid
quantity, negative cache writes, or cache reads plus writes above input) are
invalid. Apply the time window to the owning record's timestamp.

Adapters differ only in the evidence they supply. Claude transcripts with
request records mark `here`, `elsewhere`, or `unplaced`; older transcripts
without them leave authorship null.

```bash
seq_definition_root="$seq_skill_root/definitions/seq"
seq observe \
  --definition "$seq_definition_root/token-usage.json" \
  --source claude-code \
  --since 2026-11-01T00:00:00-07:00 \
  --until 2026-11-08T00:00:00-08:00 \
  --projection summary \
  --format json
```

`--source codex|claude-code` selects that adapter's default root; Seq's
default without one is the Codex corpus, which includes both default Codex
directories. Replace these example bounds with the requested window and its
actual timezone offsets. An explicit root must contain every relevant session
and ancestor, not just session starts inside the window.

Example for deliberate inspection of one supported file:

```bash
seq_definition_root="$seq_skill_root/definitions/seq"
seq observe \
  --definition "$seq_definition_root/message-search.json" \
  --path <rollout.jsonl> \
  --param "needle=<term>" \
  --param exclude_session_id= \
  --param role=user \
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
Treat a zero count as no worker evidence in the selected sources, not proof that
no worker existed. Preserve edge relation and provenance so a continuation fork
is not silently counted as a worker spawn. Keep control-parent linkage separate
from the history-parent relation used to exclude replayed token transitions.

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
- `observe` accepts one projection. Design one projection carrying the needed
  evidence when a shared scan matters; separate invocations perform separate work.
- Never treat raw `turns` or `sessions` token sums as owned corpus usage.
- Do not validate SKDC, SDR, DCP, EPG, or another durable artifact with Seq;
  use its canonical Ledger definition.
- Do not read a Ledger store or memory root implicitly.
- Do not replace a missing operator with shell, `jq`, Python, a plugin, or a subprocess.
- Report unresolved units, identities, contamination, and evidence gaps.
