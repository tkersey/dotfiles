# Session-Derived Environment Atlas

Use this reference whenever the source is a session or session corpus. It owns
the operational path from exact Seq evidence to honest partial charts, fresh
harness comparison, and eligible exports.

## Governing model

A session witnesses one finite path through a partially observed world:

~~~text
state_0 --historical action_0--> observed state_1
state_1 --historical action_1--> observed state_2
~~~

It does not define transitions for unchosen actions. Preserve that partiality.
Historical actions and recoveries may supply diagnosis or evaluator evidence;
they are not preferred labels or fresh comparison arms.

The atlas represents two complementary worlds:

~~~text
task world
  repositories, files, tests, tools, services, processes, attachments

normative world
  what the harness should notice, infer, ask, route, verify, avoid, and stop
~~~

Executable charts reconstruct task worlds. Normative charts evaluate bounded
decisions without pretending to reconstruct downstream state.

## Storage and privacy

Use a private user-local root by default:

~~~text
${CODEX_HOME:-$HOME/.codex}/emulators/<atlas-id>/
  emulator-spec.yaml
  charts/
  source/<chart-id>/queries/
  source/<chart-id>/results/
  source/<chart-id>/source-maps/<source-id>.yaml
  actors/
  worlds/
  harnesses/baseline/
  harnesses/candidates/<candidate-id>/
  runs/<run-group-id>/
  reports/<run-group-id>/
  datasets/<dataset-digest-hex>.<kind>.jsonl
~~~

Use directory mode 0700 and source/evaluator file mode 0600 where supported.
Create a directory only when it will contain a requested artifact. Do not commit
raw sessions, corrections, private tool output, credentials, or hidden
evaluators. Sanitize any authorized shareable report.

Network and external side effects are denied by default. Production services
require fixture/replay substitution under EC-v1. Explicitly authorized live
access routes to a separate designed contract with admitted live effects; user
authorization alone does not widen EC-v1. Never extract or evaluate private
chain-of-thought.

## 1. Capability gate

Before session work:

~~~bash
seq version
seq capabilities --format json
~~~

Require Seq major version 1, seq-observation-abi/v1, and native
datasets/query support. No skill-specific Seq flag is expected.

Before a CAS-backed fresh run:

~~~bash
cas app-server preflight \
  --cwd <workspace> \
  --profile core \
  --app-server-transport managed-ws \
  --json
~~~

Use a more specific already-installed profile when required. Do not change Seq
or CAS for the first proof. If no existing runner supports a chart, classify it
`skipped` with canonical stop reason `runner_unavailable`; it is a pre-run
capability gap, not an agent failure or runtime error.

## 2. Discover and freeze sources

Use existing physical commands:

~~~bash
seq sessions \
  --root "${CODEX_HOME:-$HOME/.codex}/sessions" \
  --repo <repo> \
  --since <time> \
  --until <time> \
  --format json
~~~

`seq find-session --prompt` is a semantic source read. Before running it,
resolve and preflight the user-global exposure registry, acquire its
`.partition-freeze.lock`, and construct immutable RFC 8785
`semantic-discovery-query/v1` provenance bytes for that registry:

~~~json
{"corpus_snapshot_fingerprint":"sha256:<hex>","corpus_snapshot_ref":"semantic-discovery/snapshots/<digest-hex>.json","query_spec_fingerprint":"sha256:<hex>","query_spec_ref":"semantic-discovery/query-specs/<spec-digest-hex>.json","registry_id":"sha256:<hex>","schema":"semantic-discovery-query/v1","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"],"status":"whole_snapshot_discovery_query"}
~~~

Before the query, copy the complete physically selected corpus into a private,
read-only snapshot root and materialize the referenced physical corpus snapshot
from non-semantic metadata. The snapshot records that root plus every copied
relative path, source identity, source-group identity, and exact source-file digest in query scope;
`corpus_snapshot_fingerprint` hashes those exact manifest bytes. Rewalk the
copy and require every byte and path to match before querying. Run
`seq find-session` against that copied snapshot root, never against the live
mutable sessions root. A copy or rewalk mismatch stops with
`source_contaminated` before the semantic read.

Only after the pre-read claim/attempt gate below is durable may the semantic
command run:

~~~bash
seq find-session \
  --prompt <bounded-text> \
  --root <copied-snapshot-root> \
  --format json
~~~

The retained manifest is exact RFC 8785 `physical-corpus-snapshot/v1` bytes:

~~~json
{"entries":[{"relative_path_base64url":"<base64url>","sha256":"sha256:<hex>","source_format":"<adapter-format>","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"]}],"raw_root":"<canonical-absolute-root>","schema":"physical-corpus-snapshot/v1"}
~~~

Relative paths are unpadded RFC 4648 base64url of exact path bytes. Entries sort
by decoded path bytes with unique paths; nested fingerprint arrays are sorted
and duplicate-free; regular files only are admitted. The manifest covers every
copied file exactly once, and its exact-byte SHA-256 is
`corpus_snapshot_fingerprint`.

The fixed private cleanup namespace for one selected storage domain is
`<storage_domain_root>/private/raw-snapshots/v1/`, mode `0700`. It is custody
data, not exposure authority; changing it never changes the distinct
OS-account-global exposure registry.
It contains only `roots/<snapshot-key>/`, `markers/<snapshot-key>.json`, and
`markers/<snapshot-key>.lock`. `snapshot-key` is the lowercase SHA-256 hex of
exact RFC 8785
`{"atlas_instance_id":"sha256:<hex>","invocation_id":"<opaque-invocation-id>","schema":"raw-snapshot-key/v1"}`
bytes. The marker's `raw_root`, marker path, and lock path MUST equal those
three component-safe derivations; no caller-chosen path is admitted. This exact
namespace and the one intended root/marker/lock set must be positively present
in `authorized_files.allowed` before copying; otherwise stop before reading raw
bytes.

Before copying any raw byte, acquire the already-derived
`markers/<snapshot-key>.lock`
exclusive owner lock, then create and fsync an owner-only cleanup marker outside
the raw root with exact RFC 8785
`{"owner_invocation_id":"<opaque-invocation-id>","owner_process_opaque_id":"<opaque-process-id>","raw_root":"<canonical-absolute-root>","schema":"raw-snapshot-cleanup/v1","snapshot_fingerprint":null}`
bytes, then fsync the marker directory. After the snapshot manifest is durable,
atomically replace the marker under that lock with the same exact object except
for its non-null matching snapshot fingerprint, and fsync the marker directory
again. At capability preflight and before any new copy, enumerate this fixed
private temporary namespace, validate every marker/root remains beneath it,
and acquire the marker-scoped exclusive recovery lock before inspecting an
orphan. Recovery MUST prove the recorded owner process is absent, atomically
replace the marker's owner fields with the recovery invocation/process while
holding that lock, and only then treat the isolated root as invocation-owned
under the common removal gate. A null snapshot fingerprint covers the complete
interval before the marker replacement is directory-durable, including a crash
after manifest publication; recovery may verify an extant manifest but never
requires it to delete the invocation-owned raw root. If owner liveness or atomic transfer cannot be
proved, stop with `source_contaminated`; a second invocation never deletes the
first invocation's live root. Delete each recovered orphan root, then its
marker, and fsync the marker directory before releasing the recovery lock. On normal success the original
owner holds the same marker-scoped lock and deletes the raw root before its
marker, then fsyncs the marker directory. A crash at any
point therefore leaves a discoverable cleanup obligation without retaining
session contents in the marker. Explicitly authorized retention removes the
marker only after its exact retained root and purpose are bound as source
limitations.

`query_spec_fingerprint` binds the exact Seq query specification and snapshot
fingerprint; `query_spec_ref` resolves those exact content-addressed bytes and
its digest suffix agrees. Both identity arrays are sorted, duplicate-free, and equal the
complete identities recorded by that immutable snapshot. Group fingerprints
remain query provenance; partition claims range only over individual source
identities. A group is holdout-eligible only when every member identity is
holdout-eligible, so one exposed member makes the group discovery-only without
inventing an aggregate identity claim.

This pre-read identity set is complete only when the bound physical
identity-completeness asset proves that no stable task/session alias requires
semantic source bytes to discover. Without that proof, select the locked
discovery-only fallback before reading: keep `.partition-freeze.lock` through
the semantic query, extract every newly visible stable alias from the complete
result/source window, publish its `discovery_exposed` claim and marker, and
revalidate the union before releasing the lock. A post-read alias absent from
the locked union is `source_contaminated`. An already consumed alias applies
the same retirement-backed transition defined in Section 7 while the lock is
still held: valid marker/successor evidence makes it permanently
`discovery_exposed`; absent retirement evidence is `source_contaminated`.
query success never retroactively establishes completeness.

The fallback semantic query is crash-closed. Before launching Seq, create and
fsync one owner-global `semantic-discovery-attempt/v1` pending record under the
exposure registry. Let `<pending-digest-hex>` be the lowercase SHA-256 hex of
those exact bytes. Its only directory is
`semantic-discovery/attempts/<pending-digest-hex>/`, containing exactly
`pending.json`, optional `result.json`, and optional `completed.json`; the exact
`pending.json` contents hash to the directory
digest. Construct the directory privately, create and fsync `pending.json`
inside it, then atomically rename the complete directory to its digest path and
fsync `semantic-discovery/attempts/` before launching Seq. An empty or
pending-less digest directory is never globally visible. Create-new each later
file and fsync the attempt directory after every file
publication. The pending record binds the owner invocation/process, snapshot
pair, query spec pair, complete physically known identity set, and one exact
invocation-owned private staging root outside the exposure registry.
The staging root is beneath the atlas's invocation-owned cleanup namespace.
Before publishing pending bytes, create and fsync a mode-0600 owner marker that
binds attempt ID, process identity, canonical root path, and an unpredictable
nonce; the pending record binds its fingerprint. Hold the namespace owner lock
through live use.
The marker is always `<private_staging_root_path>/.semantic-discovery-owner.json`
and contains exact RFC 8785 bytes
`{"attempt_id":"<opaque-attempt-id>","nonce":"<base64url>","owner_process_opaque_id":"<opaque-process-id>","private_staging_root_path":"<canonical-absolute-path>","schema":"semantic-discovery-staging-owner/v1"}`.
No other marker path or shape is admitted.
The exclusive lock is the create-new file
`<cleanup-namespace>/.semantic-discovery-locks/<attempt-id>.lock`; its exact path
is bound by the pending record. Lock acquisition is no-follow and atomic, and a
dead holder is reclaimed only after OS-backed process-death proof.
Seq runs
behind a wrapper that exposes no semantic payload on stdout or to the compiler;
its raw output is create-new mode-0600 bytes only in that staging root. The
wrapper computes the raw digest, extracts stable aliases there, and applies the
Privacy and rollback retention gate before any result bytes enter the global
registry. Copy only the authorized or scrubbed retained projection with
create-new semantics to
`semantic-discovery/results/<result-digest-hex>.json`, require the filename and
fingerprint to agree, and fsync the results directory. That content-addressed
copy is the recorded retained projection. Then publish
`semantic-discovery-attempt-result/v1` as `result.json`; it binds the raw digest
without a global raw ref, the retained projection pair and disposition, and the
complete sorted stable-alias identity descriptors/fingerprints. Only after that
asset is durable may the wrapper return its fingerprint. Credentials, secret
values, and private tool output are never written to the global registry. An
exact raw preimage needed for a later chart stays only in separately authorized
private source-bundle custody; otherwise delete it after `result.json` is
durable. If scrubbing would destroy required provenance, stop or downgrade the
claim rather than publishing sensitive bytes globally.

~~~json
{"alias_extractor_fingerprint":"sha256:<hex>","alias_extractor_ref":"semantic-discovery/alias-extractors/<digest-hex>.json","attempt_id":"<opaque-attempt-id>","owner_invocation_id":"<opaque-invocation-id>","owner_process_opaque_id":"<opaque-process-id>","physically_known_source_identity_fingerprints":["sha256:<hex>"],"private_staging_lock_path":"<canonical-absolute-lock-path>","private_staging_owner_fingerprint":"sha256:<hex>","private_staging_root_path":"<canonical-absolute-path-outside-registry>","query_spec_fingerprint":"sha256:<hex>","query_spec_ref":"semantic-discovery/query-specs/<digest-hex>.json","schema":"semantic-discovery-attempt/v1","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"semantic-discovery/snapshots/<digest-hex>.json"}
{"attempt_id":"<opaque-attempt-id>","pending_fingerprint":"sha256:<hex>","raw_result_envelope_fingerprint":"sha256:<hex>","retained_projection_fingerprint":"sha256:<hex>","retained_projection_ref":"semantic-discovery/results/<result-digest-hex>.json","retention_disposition":"exact_authorized","schema":"semantic-discovery-attempt-result/v1","stable_alias_identity_descriptors":[{"identity_kind":"external_task","identity_ref":"task-uri:<base64url>"}],"stable_alias_identity_fingerprints":["sha256:<hex>"]}
{"attempt_id":"<opaque-attempt-id>","exposure_claims":[{"fingerprint":"sha256:<hex>","holdout_key":"<hex>"}],"identity_exposure_markers":[{"fingerprint":"sha256:<hex>","ref":"semantic-discovery/identity-exposures/<holdout-key>.json"}],"pending_fingerprint":"sha256:<hex>","result_fingerprint":"sha256:<hex>","schema":"semantic-discovery-attempt-completed/v1"}
~~~

Arrays are sorted and duplicate-free; descriptor fingerprints use the canonical
identity preimage rule, and the claim/marker rows cover every physical and
alias identity in the result. A claim's canonical global path is derived from
the bound registry root and holdout key; the completion record never stores an
atlas-local snapshot ref. Recovery locates `result.json` and `completed.json`
from the enumerated pending directory alone; no adjacency convention or
caller-chosen filename participates.
Initial extraction and private-staging recovery both execute the exact extractor
ref/fingerprint bound by the pending record; drift or an unresolved extractor
is `source_contaminated`. `retention_disposition` is exactly
`exact_authorized` or `scrubbed`. The latter proves physical discovery and alias
exposure but is not an exact semantic-payload preimage; any later claim needing
removed bytes must resolve an authorized private source-bundle copy or stop.

While still holding `.partition-freeze.lock`, the compiler resolves the result,
publishes or preserves the required exposed claim and marker for every alias,
revalidates the complete union, and then writes the matching immutable
completion record, fsyncing each affected registry directory after claim,
marker, and completion publication. Capability preflight and holdout admission enumerate every
pending attempt before proceeding. For a dead owner with a durable result,
recovery must publish and revalidate all result aliases before completion. With
no durable `result.json`, recovery never opens, interprets, or deletes the
path-named private staging payload as evidence. After proving the owner process
dead, recovery acquires the exclusive cleanup-namespace lock, opens the root
no-follow, and requires the exact pending-bound owner marker before recursively
deleting it without reading payload bytes. Before deletion it atomically
replaces that marker with exact `semantic-discovery-staging-transfer/v1` bytes
binding the prior marker fingerprint, recovery invocation/process, and root;
that compare-and-swap transfers the isolated root to the recovery invocation.
The transfer bytes also bind the pending fingerprint and previous transfer
fingerprint (null for the first transfer). If recovery crashes, a later
dead-owner recovery validates that transfer marker, atomically chains a new
transfer to itself under the same lock, and resumes deletion. Thus every
transfer state is recoverable and no prior-owner marker must reappear.
A missing or unequal marker forbids
cleanup and cannot become evidence. It may clear the attempt only after proving
the wrapper never returned or delivered semantic bytes; otherwise the attempt remains unresolved and returns
`source_contaminated`. Unprovable owner/output state is
`source_contaminated`. No raw semantic byte is a registry recovery dependency,
and no unresolved semantic-discovery attempt permits a new
`holdout_unexposed` claim.

For each individual source identity, construct exact RFC 8785
`semantic-discovery-identity-exposure/v1` bytes:

~~~json
{"exposure_registry_id":"sha256:<hex>","exposure_status":"discovery_exposed","schema":"semantic-discovery-identity-exposure/v1","source_identity_fingerprint":"sha256:<hex>"}
~~~

Its query-independent global ref is
`semantic-discovery/identity-exposures/<holdout-key>.json`. While still holding
the lock and before the semantic read, stage a permanent `discovery_exposed`
partition claim for every identity not already classified
`discovery_exposed`, `development_exposed`, or `optimizer_exposed` in
`source_identity_fingerprints`; each new claim binds its own identity-exposure
ref and fingerprint. An existing `discovery_exposed`, `development_exposed`,
or `optimizer_exposed` claim is already conservative enough and is retained
without replacement, including a legacy claim whose semantic-discovery
evidence fields are null. Publish each new claim before its marker; for an
already-exposed identity, publish or reuse the query-independent marker as a
monotonic evidence supplement without rewriting the claim. Then re-read the
complete marker/claim set and require each identity to have both an exposed
claim and its exact marker. A missing marker leaves an unresolved conservative
claim and is `source_contaminated`; the query has not run. This exposed-claim
plus marker union is the only admitted upgrade. It never changes an exposed
identity back to holdout-eligible state, while later overlapping queries may
record new query provenance without requiring byte-identical old claim bytes.

Hash the query-provenance bytes and publish them at
`semantic-discovery/queries/<query-digest-hex>.json` only after the complete
identity gate passes. Only then may the semantic read run. Every individual
identity in the whole snapshot is therefore durably discovery-exposed before
the semantic read, while no query record controls permanent claim identity.
`query_record_fingerprint` is the SHA-256 of those complete exact record bytes
and `<query-digest-hex>` is its suffix; it is distinct from the embedded
query-spec fingerprint. Result records pair `query_ref` only with this record
fingerprint and carry the spec fingerprint separately.

Retain exact RFC 8785 `semantic-discovery-result/v1` bytes containing the query
provenance ref/fingerprint, snapshot ref/fingerprint, raw Seq-envelope digest,
and retained projection ref/fingerprint. Results do not narrow exposure:
matching and non-matching
sessions in the searched snapshot are all permanently excluded from holdout.
New claims are discovery-only, while existing development/optimizer exposure
remains at that status. The later source-bundle
`corpus_digest` remains a post-selection closure identity and is never required
by this pre-read record. Query completion never rewrites an existing exposure
claim.

~~~json
{"query_record_fingerprint":"sha256:<hex>","query_ref":"semantic-discovery/queries/<query-digest-hex>.json","query_spec_fingerprint":"sha256:<hex>","query_spec_ref":"semantic-discovery/query-specs/<spec-digest-hex>.json","raw_result_envelope_fingerprint":"sha256:<hex>","retained_projection_fingerprint":"sha256:<hex>","retained_projection_ref":"semantic-discovery/results/<result-digest-hex>.json","retention_disposition":"exact_authorized","schema":"semantic-discovery-result/v1","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"semantic-discovery/snapshots/<snapshot-digest-hex>.json"}
~~~

Those are the exact closed fields; all four pairs resolve exact retained bytes,
the query bytes name the same snapshot pair, and raw digest plus retained
projection fields equal the attempt result. No missing raw ref is synthesized.
After the retained projection and every required sanitized selected-source asset
are durable, unmount and delete the copied raw corpus root through the common
write/removal authority gate. The content-addressed snapshot manifest, query,
result, and sanitized source evidence remain; raw session/tool payload copies
do not. Retaining the raw copy requires separate explicit user authorization
for that exact root and purpose and is recorded as a source limitation.
To discover a holdout candidate, use only physical metadata after publishing a
complete `holdout_unexposed` identity claim, then perform the first semantic
read under the partition-freeze and selection rules in Section 7. If complete
identity cannot be known without prompt search, use the discovery-only
fallback; do not retroactively call the match untouched.
The physical `seq sessions` route uses one frozen verified projection containing
only session ID, source path digest, repository identity, source adapter, event
range, lineage IDs, and lifecycle status. It excludes thread/session names,
prompt excerpts, summaries, tags, and every adapter field derived from message
or tool content. Unknown or extra fields make the projection invalid and route
to the locked discovery-only fallback before exposure.

Exclude:

- the current compilation session;
- ongoing, trivial, or chat-only sessions;
- generated atlas reports;
- prompts that merely quote prior sessions;
- audit sessions whose current request contaminates the target;
- unlinked worker sessions unless their root lineage is intentionally selected.

Freeze more than a time window:

~~~text
session id and exact path
root/parent/worker lineage
source file digest and adapter/format
selected event range
exact Seq query specs and result envelopes
Seq version and ABI
current-session exclusion
known limitations
~~~

corpus_digest binds the selected immutable source set, not the complete mutable
session root.

## 3. Build the source bundle

Run bounded seq query definitions against exact session ids or paths for:

~~~text
sessions
source_events
turns
tool_lifecycle
session_edges
~~~

Store each exact query specification beside its exact result envelope. Preserve
source order and source-event identity. Prefer sanitized message and tool
projections; extract raw payloads only for the selected chart window and only
when required.

Canonical source map:

~~~yaml
session_source_map:
  seq_version:
  seq_abi:
  source_adapter:
  source_format:
  source:
    session_id:
    path:
    content_sha256:  # SHA-256 of the exact source-file bytes at `path`
    root_session_id:
  queries:
    sessions:
      spec_ref:
      spec_fingerprint:
      result_ref:
      result_fingerprint:
    events:
      spec_ref:
      spec_fingerprint:
      result_ref:
      result_fingerprint:
    turns:
      spec_ref:
      spec_fingerprint:
      result_ref:
      result_fingerprint:
    tools:
      spec_ref:
      spec_fingerprint:
      result_ref:
      result_fingerprint:
    edges:
      spec_ref:
      spec_fingerprint:
      result_ref:
      result_fingerprint:
  exclusions:
    current_session:
    worker_policy:
    contamination: []
  limitations: []
~~~

The chart binds the source-map bytes; the source map recursively binds every
query and result byte. A paraphrased transcript without these references is not
source provenance.

`source_bundle_ref` names the closure-root-relative
`source/<chart-id>/source-bundle.json`, whose exact RFC 8785 bytes are:

~~~json
{"assets":[{"fingerprint":"sha256:<hex>","ref":"<closure-root-relative-ref>"}],"schema":"session-source-bundle/v1","source_maps":[{"fingerprint":"sha256:<hex>","ref":"source/<chart-id>/source-maps/<source-id>.yaml"}]}
~~~

Refs are normalized, nonempty POSIX paths relative to the closure root and
cannot escape it. `assets` is sorted by ref, duplicate-free, and contains the
source map plus every query specification, result envelope, selected raw event,
attestation, and other byte transitively referenced by a source map; it
contains no extra file. `source_maps` is sorted by ref, duplicate-free, and
contains exactly one entry for every contributing physical source. Each entry
also occurs byte-identically in `assets`. A single-session chart has one map;
`session_corpus` and `mixed` charts bind all maps rather than selecting one.
This typed `source_maps` array replaces ambiguous parallel
`source_map_refs`/`source_map_fingerprints` arrays while preserving both values
in each entry.
`source_bundle_fingerprint` is SHA-256 of these exact manifest bytes, never a
directory walk or archive digest. The corpus digest uses only these canonical
bundle fingerprints.

## 4. Compile correction windows

### Detect candidates

Model analysis may nominate windows, but lexical negativity is not authority.
A correction candidate needs:

1. a later user message, deterministic result, or human attestation indicating
   a defect;
2. an identifiable earlier consequential agent action;
3. enough pre-action context to state what the agent legitimately knew;
4. one bounded harness surface.

High-value patterns include an unnecessary question, invented behavior, ignored
scope, wrong skill/tool route, completion without proof, continuing past a stop,
failure to inspect available evidence, or overengineering instead of direct
action. Generic dissatisfaction without attributable behavior stays diagnostic.

### Choose the exact cut

Let:

~~~text
A = rejected or disputed historical action
C = later correction or objective contradiction
S = latest state immediately before A containing all facts legitimately available to A
~~~

The actor packet includes state through S and excludes A, C, all later recovery
and outcome evidence, the historical final answer, and evaluator labels.

### Classify attribution

| Attribution | Meaning | Maximum default use |
|---|---|---|
| direct | Correction identifies the behavior and no competing action materially intervenes | harness selection and preference training, subject to authority and freshness |
| bounded | A small decision cluster is implicated but no unique action is established | diagnostic and development evaluation |
| ambiguous | Multiple explanations remain plausible | diagnostic only |

Before first promotion to harness-selection or preference-training use, a human
MUST record review of the exact source refs, cut, hidden correction, harness
surface, and hard-oracle interpretation. The exact RFC 8785 review asset is
bound by `human_review_ref` and `human_review_fingerprint`; it identifies the
reviewer, the reviewed-subject fingerprint, those five reviewed surfaces, and
`evaluator_informed: true` and
`independent_of_candidate_generation: true` attestations. The reviewer is
evaluator-informed because this review necessarily inspects the hidden
correction; candidate-generation blindness is proved by the optimizer access
boundary, not asserted by this reviewer. Without that evidence the chart stays diagnostic. A proven
recurring evaluator pattern may be reused only when `reviewed_pattern_ref` and
`reviewed_pattern_fingerprint` bind the independently reviewed pattern and
`applicability_ref` and `applicability_fingerprint` bind evaluator-produced
evidence that the exact chart satisfies it. Direct review fields and
reviewed-pattern fields are mutually exclusive, and `reviewer_independence` is
true for either route. A chart author cannot self-declare applicability. For
holdout, the reviewer must not participate in factor selection or candidate
authoring. If no independent reviewer is available, the chart remains
diagnostic/development-only and cannot enter holdout, harness selection,
promotion, or preference training. There is no same-reviewer exception whose
choices can be revised after correction reveal.

First parse the finalized chart as data. For a pending design and every
materialized descendant that retains its frozen materialization plan, normalize
only the `ref`/`fingerprint` pair at every field pointer named by that plan to
the same closed
`{"field_pointer":"<pointer>","materializer_fingerprint":"sha256:<hex>","materializer_ref":"materializers/<digest-hex>.json"}`
placeholder taken from that field's plan entry. Preserve every sibling field,
including seed control, seed, failure schedule, and other execution semantics,
verbatim. The subject does not contain
the plan fingerprint or finalized chart fingerprint. Thus filling planned implementation bytes does not change the
reviewed semantic subject; any unplanned or changed-plan field still changes it
and requires fresh review.
Then remove the entire `/environment_chart/evaluator/authority/correction_review`
subtree and remove from `/environment_chart/closure/assets` the exact transitive
ref set reachable only from that subtree, including the subject, review,
pattern, applicability, reviewer, and review-input preimages. The finalized
chart retains those entries; only the reviewed projection excludes them. Encode
the remaining `environment_chart` value as the
`chart_semantics` member of the exact RFC 8785
`correction-review-subject/v1` asset:

~~~json
{"chart_semantics":{"chart_version":"EC-chart-v1"},"schema":"correction-review-subject/v1"}
~~~

The abbreviated `chart_semantics` object above stands for the complete
remaining chart value, not a selectable field list. The projection rejects a
review ref or fingerprint anywhere outside the removed subtree. Store the exact
bytes at `evaluators/review-subjects/<digest-hex>.json`; the chart binds that
asset through `reviewed_subject_ref` and `reviewed_subject_fingerprint` inside
`correction_review`. The subject cannot point to the review, pattern, or
applicability assets, while those assets may point to the subject. This makes
the content-addressed dependency graph acyclic.

The direct review asset is exact RFC 8785:

~~~json
{"cut_fingerprint":"sha256:<hex>","cut_ref":"evaluators/review-inputs/<digest-hex>.cut.json","evaluator_informed":true,"hard_oracle_interpretation_fingerprint":"sha256:<hex>","hard_oracle_interpretation_ref":"evaluators/review-inputs/<digest-hex>.oracles.json","harness_surface":"<surface>","hidden_correction_fingerprint":"sha256:<hex>","hidden_correction_ref":"evaluators/review-inputs/<digest-hex>.correction.json","independent_of_candidate_generation":true,"reviewed_subject_fingerprint":"sha256:<hex>","reviewed_subject_ref":"evaluators/review-subjects/<digest-hex>.json","reviewer_identity_fingerprint":"sha256:<hex>","reviewer_identity_ref":"principals/<principal-digest-hex>.json","schema":"correction-human-review/v1","source_event_refs":["source-event:<id>"]}
~~~

Each of the three review-input refs is a normalized evaluator-only static ref
whose companion fingerprint hashes its exact bytes. `cut_ref` has RFC 8785
shape `{"cut":{},"schema":"correction-review-cut/v1"}` and copies the
complete cut value from the reviewed subject. `hidden_correction_ref` contains
exact RFC 8785
`{"events":[{"event":{},"source_event_ref":"source-event:<id>"}],"schema":"correction-review-hidden-evidence/v1"}`
bytes; each `event` is the complete sanitized source-event value, and entries
are in source order and resolve through the bound source
bundle. `hard_oracle_interpretation_ref` has RFC 8785 shape
`{"evaluator_projection":{"hard_oracles":[],"state_diff":[],"success_condition":null,"trace_invariants":[]},"schema":"correction-review-oracle-interpretation/v1"}`
and is projected from the complete corresponding evaluator values in the
reviewed subject. The shown empty arrays and null are illustrative; the actual
asset copies the exact values. None of these assets
contains a correction-review ref or finalized
chart fingerprint, so the closure remains acyclic. A missing ref, mismatched
fingerprint, unresolved source event, or unequal projection is not review
authority.

The reviewed-pattern route binds exact RFC 8785 bytes:

~~~json
{"evaluator_informed":true,"independent_of_candidate_generation":true,"pattern_id":"<stable-pattern-id>","predicate_fingerprint":"sha256:<hex>","predicate_ref":"evaluators/correction-patterns/<pattern-id>.json","reviewer_identity_fingerprint":"sha256:<hex>","reviewer_identity_ref":"principals/<principal-digest-hex>.json","schema":"correction-reviewed-pattern/v1"}
~~~

and exact applicability bytes:

~~~json
{"applies":true,"evaluator_implementation_fingerprint":"sha256:<hex>","evaluator_implementation_ref":"evaluators/implementation.json","reviewed_pattern_fingerprint":"sha256:<hex>","reviewed_pattern_ref":"evaluators/correction-patterns/<pattern-id>-review.json","reviewed_subject_fingerprint":"sha256:<hex>","reviewed_subject_ref":"evaluators/review-subjects/<digest-hex>.json","schema":"correction-pattern-applicability/v1"}
~~~

The review, pattern, applicability, and every fingerprinted preimage are
evaluator-only closure assets. A ref without its exact bytes is not review
authority.

### Construct the evaluator

Extract semantic constraints:

~~~text
rejected behavior
required or preferred behavior
facts already available
scope and authority
prohibited inference
required verification
accepted recovery evidence, if any
~~~

The historical recovery is evidence, not automatically the preferred answer.
Prefer decision constraints over text matching:

~~~yaml
hard_oracles:
  - id: no-unnecessary-question
    type: decision_class_forbidden
    action_class: ask
    when: required_information_already_visible
  - id: act-on-resolvable-request
    type: decision_class_required
    one_of: [inspect, act, tool]
protected_dimensions:
  - dimension_id: no_unapproved_mutation
    evaluator_result_ids: [oracle-no-unapproved-mutation]
  - dimension_id: no_claim_beyond_evidence
    evaluator_result_ids: [oracle-evidence-required]
~~~

Normative charts normally request one bounded decision envelope:

~~~yaml
decision:
  action_class:
  content:
  tool:
  arguments:
  relied_on_facts: []
  unresolved_blocker:
~~~

## 5. Compile executable charts

Prefer sessions with a known repository and commit, reconstructable initial
state, content-addressable fixtures, dependency locks, bounded tools,
deterministic tests or state assertions, and no indispensable production
service.

### Fidelity

Exact requires:

~~~text
exact Git commit and tree
declared clean/dirty-state handling
exact fixtures and dependency locks
tool manifest and effect policy
repeatable reset recipe and pre-state fingerprint
deterministic evaluator
~~~

Approximate may support harness selection only when the chart binds an exact
difference inventory plus an inspectable equivalence witness showing those
differences cannot affect the evaluated behavior. Without both refs and
fingerprints it is diagnostic. Transcript-only
supports reasoning/routing/synthesis decisions without task transitions. Absent
supports no executable claim.

A commit is insufficient if the task depended on staged, unstaged, untracked,
generated, or local-only bytes. If those bytes cannot be recovered and
attributed, do not reset to the commit and call the world exact.

### World manifest

~~~yaml
world:
  world_id:
  fidelity: exact | approximate
  repository:
    url:
    commit:
    tree:
    expected_clean: true | false
  reset:
    kind: none | git_worktree | fixture | custom
    commands: []
    fixtures: []
    dependency_setup: []
    expected_prestate:
      fingerprint:
      assertions: []
  tools:
    asset_ref:
    asset_fingerprint:
    allowed: []
    denied: []
    schemas: {}
    fixtures: {}
  effects:
    network: deny | fixture_only | replay_recorded
    filesystem: deny | read_only | isolated_write | declared_roots
    filesystem_roots: []
    external_side_effects: deny | fixture_only | explicit
    policy_ref:
    policy_fingerprint:
  evaluator:
    asset_ref:
    asset_fingerprint:
    commands: []
    state_assertions: []
    trace_invariants: []
  closure:
    assets: []
  limitations: []
~~~

`world.reset` is the sole reset-recipe owner. The chart reset block points to
that world manifest and repeats only the contracted reset kind, world digest,
and expected pre-state fingerprint; it contains no independent commands or
fixtures. Mismatch is `invalid_environment`. Non-closed world effects require
the exact effect-policy ref and fingerprint above, matching the chart effects
block.
Chart `environment.world_fidelity` MUST equal `world.fidelity`; neither field
wins by precedence.
World and chart network, filesystem, external-side-effect modes, policy ref,
and policy fingerprint MUST also match exactly.
When the world repeats `filesystem_roots`, that list deep-equals the roots in
the effect-policy asset; neither inline data nor the asset wins by precedence.

For executable charts, the chart owns semantic tool permission and evaluation;
the tool and evaluator assets own their operational implementation. The chart
and world both bind the same exact tool asset ref/fingerprint. World
`evaluator.asset_ref/fingerprint` MUST equal chart
`evaluator.implementation_ref/fingerprint`; the separate semantic
`evaluator_ref/fingerprint` is validated independently. The world's inline tool/evaluator fields are exact RFC
8785 projections of those assets, not independent definitions. Admission
verifies reference equality, fingerprints, and projections before reset or
execution. Missing references or drift is `invalid_environment`; a runner
cannot choose one copy by precedence.

Run the reset twice before admitting exact fidelity. Both runs must produce the
same expected pre-state fingerprint.
Each admission reset, including dependency setup, runs in its own newly created
disposable worktree or fixture instance under the declared effect policy. The
two proofs start from the same captured source bytes but use distinct instances;
neither may run in the live source checkout, a candidate worktree, or an actor
worktree. Destroy each instance after its pre-state fingerprint is durable. If
any reset or setup command can read or mutate outside the declared roots, or if
the runner cannot prove that confinement, admission stops with
`reset_not_repeatable` or `world_not_reconstructable`; it never downgrades the
same execution to approximate fidelity.
Bind both admission-reset result refs/fingerprints in each later EER that claims
exact fidelity; the actor-run reset result is additional evidence, not a
substitute for repeatability admission.

Whole-harness comparisons cut before the first assistant action. A later skill
or synthesis cut is admissible only with explicit proof that the selected factor
had no earlier influence.

## 6. Prove visibility and closure

Before admitting any chart:

1. recursively verify every closure reference and digest;
2. render the actor packet from actor-visible inputs only;
3. verify that no historical suffix source ref occurs in it;
4. search for excerpts from the disputed action, correction, recovery, outcome,
   and final answer;
5. remove or unmount hidden suffix/evaluator files and rerender;
6. require identical actor-packet bytes;
7. record the actor-readable file/root inventory, its fingerprint, and tool
   access policy;
8. prove the fresh actor invocation could access only that declared inventory.

After mounts and tool policy freeze but before actor instructions are
delivered, the runner emits exact RFC 8785 `actor-readable-inventory/v1` bytes:

~~~json
{"effect_policy_fingerprint":"sha256:<hex>","entries":[{"fingerprint":"sha256:<hex>","kind":"regular","metadata_fingerprint":"sha256:<hex>","mode":"100644","path":"<sandbox-relative-path>"},{"kind":"directory","metadata_fingerprint":"sha256:<hex>","mode":"040700","path":"<sandbox-relative-path>"},{"kind":"symlink","link_target_base64url":"<base64url>","metadata_fingerprint":"sha256:<hex>","path":"<sandbox-relative-path>"}],"metadata_observation_policy_fingerprint":"sha256:<hex>","metadata_observation_policy_ref":"environment/metadata-observation-policy.json","readable_roots":["<sandbox-relative-path>"],"run_id":"<run-id>","sandbox_instance_id":"<runner-opaque-id>","schema":"actor-readable-inventory/v1","tool_access_policy_fingerprint":"sha256:<hex>"}
~~~

`entries` is the complete recursive `lstat` walk of every readable root after
mount freeze, sorted by normalized path, with exactly one type-valid row per
path. Regular fingerprints bind exact bytes; modes are six-digit octal text;
symlink targets use unpadded RFC 4648 base64url. Roots are sorted,
duplicate-free, sandbox-relative, and contain every entry. The runner enforces
a closed filesystem namespace that denies paths outside those roots and keeps
the namespace unchanged for the actor lifetime. The inventory fingerprint is
SHA-256 of those exact bytes. `tool_access_policy_fingerprint` equals the
contract-owned `environment.tools.asset_fingerprint` repeated by the world;
a runtime-generated substitute is invalid.
Each `metadata_fingerprint` hashes the entry's actor-observable ownership,
timestamps, inode/link semantics, ACLs, extended attributes, and platform stat
projection under the bound `metadata-observation-policy/v1`. Its ref/fingerprint
has one canonical static asset identity: strip an exact
`roots/<root-digest-hex>/` archive prefix before comparing the closure-relative
suffix, then require that suffix plus fingerprint to equal the chart tools
metadata-policy pair, access proof, execution row, and both arm inventories.
All forms resolve the same exact contract-owned bytes. That policy is
equal across arms and either virtualizes those observations to exact normalized
values or proves the actor tool surface cannot observe them. A shell/stat-
capable actor without normalization is ineligible; ambient metadata is never
left unbound.
`effect_policy_fingerprint` equals the chart's complete resolved effect-policy
identity, the world/reset boundary, and the execution row; it covers filesystem,
network, and external-effect authority independently of the tool manifest.

The same runner then emits exact RFC 8785 `actor-access-proof/v1` bytes:

~~~json
{"actor_context_fingerprint":"sha256:<hex>","actor_context_ref":"runs/<run-group-id>/actor-context/<run-id>.json","actor_input_fingerprint":"sha256:<hex>","actor_process_opaque_id":"<runner-opaque-id>","actor_readable_inventory_fingerprint":"sha256:<hex>","actor_runner_fingerprint":"sha256:<hex>","effect_policy_fingerprint":"sha256:<hex>","metadata_observation_policy_fingerprint":"sha256:<hex>","metadata_observation_policy_ref":"environment/metadata-observation-policy.json","run_id":"<run-id>","sandbox_instance_id":"<runner-opaque-id>","schema":"actor-access-proof/v1","status":"observed","tool_access_policy_fingerprint":"sha256:<hex>"}
~~~

The proof is emitted only for the actual fresh process created inside that
already-observed sandbox. Its run, sandbox, inventory, runner, tool policy, and
effect policy
plus actor input and context fingerprints must equal the execution row and
frozen assets; proof reuse across runs is
invalid. A runner that cannot enforce and completely enumerate this surface
cannot produce selecting or training evidence.
Before such a run, probe the selected existing actor route for this exact
inventory/access capability. If CAS does not expose it, use an already-supported
direct runner that does or stop with `runner_unavailable`; the first skill-only
implementation does not add a CAS route or a new runner.

For `paired_compare`, after all cohort runs finish, the evaluator emits one
report-owned RFC 8785 `actor-readable-surface-validation/v1` artifact. It
contains a complete pair for every chart/repeat tuple and binds both inventory
ref/fingerprint pairs, their run IDs, and the frozen factor-delta validation.
Readable roots, tool policy, and every inventory entry outside factor-owned
manifest deltas MUST be byte-equal between arms. Each differing, added, or
removed entry MUST correspond exactly to one declared factor-owned harness
delta and to the matching arm's manifest bytes, type, mode, and path. No other
readable-surface delta is allowed.
For each arm independently, the validator also derives the complete expected
runtime inventory from that arm's frozen harness manifest plus chart/runtime
assets and requires exact set equality with the observed inventory before
cross-arm comparison. An equal undeclared file in both arms is still
`comparison_drift`.
Pairs sort by `(chart_id, repeat_id,
baseline_run_id, candidate_run_id)`, are complete and unique for the frozen
cohort, and each contains the complete sorted root-qualified factor path set.
The pairwise comparison and EER bind this post-run ref/fingerprint separately
from the pre-run `factor-delta-validation/v1`. Missing/incomplete coverage or
a status other than `pass` or `unavailable_prestart` is `comparison_drift`, even when both
per-arm access proofs pass.

~~~json
{"derivation_implementation_fingerprint":"sha256:<hex>","derivation_implementation_ref":"comparison/actor-readable-surface-validator.json","factor_delta_validation_fingerprint":"sha256:<hex>","pairs":[{"authorized_factor_delta_paths":[{"path":"<logical-path>","root_id":"<root-id>"}],"baseline_actor_started":true,"baseline_inventory_fingerprint":"sha256:<hex>","baseline_inventory_ref":"runs/<run-group-id>/actor-readable-inventory/<run-id>.json","baseline_run_id":"<run-id>","baseline_sandbox_created":true,"baseline_unavailable_reason":null,"candidate_actor_started":true,"candidate_inventory_fingerprint":"sha256:<hex>","candidate_inventory_ref":"runs/<run-group-id>/actor-readable-inventory/<run-id>.json","candidate_run_id":"<run-id>","candidate_sandbox_created":true,"candidate_unavailable_reason":null,"chart_id":"<chart-id>","nonfactor_entries_equal":true,"readable_roots_equal":true,"repeat_id":"<repeat-id>","status":"pass","tool_policy_equal":true}],"schema":"actor-readable-surface-validation/v1"}
~~~

The derivation implementation is an evaluator-only immutable asset frozen by
the pre-candidate policy. The validator loads those exact bytes and recomputes
root equality, tool-policy equality, and every authorized and non-factor delta;
a self-described result without that recomputation is invalid. A cohort tuple
whose actor never started still has exactly one pair row with
`status: unavailable_prestart` and the affected `*_actor_started: false`.
`*_sandbox_created` equals the execution row. When it is false, inventory
refs/fingerprints are null; when true, they preserve the observed inventory
pair. Cross-arm equality booleans are null because agent evidence is
unavailable, and that arm's nonempty `*_unavailable_reason` matches its
execution row. Each started arm has a null
reason; if both fail, both reasons are retained independently. The other arm's fields retain
their observed values. No other row may use that variant. Thus pre-start
failure makes the required comparison insufficient without making the runtime
validation artifact incomplete.

`actor_context_ref` retains the exact RFC 8785 `actor-context/v1` bytes under
the run directory, and `actor_context_fingerprint` hashes those bytes:
`{"actor_input_message_indexes":[2],"harness_instruction_message_indexes":[0],"messages":[{"content":"<exact-arm-harness-instructions-UTF-8>","role":"system"},{"content":"<exact-task-prompt-UTF-8>","role":"user"},{"content":"<exact-actor-input-UTF-8>","role":"user"}],"prompt_message_indexes":[1],"run_id":"<run-id>","schema":"actor-context/v1"}`.
The ordered message array admits roles `system`, `developer`, `user`, and
`assistant` and contains every delivered exact content value. The context includes system/developer instructions and
any reused history; selecting and training runs require a fresh context with no
prior messages. `actor_input_fingerprint` equals the separately frozen actor
packet and SHA-256 of the exact UTF-8 content at
`actor_input_message_indexes[0]`. The array has exactly one index and names a user
message. Extra, missing, prepended, or reused messages
invalidate the proof.
`prompt_message_indexes` likewise has exactly one index and names the system or
user message whose exact UTF-8 content SHA-256 equals the chart's
`actor.prompt_fingerprint` and whose bytes equal `actor.prompt_ref`. Prompt and
actor-input indexes are distinct; omitted or substituted prompt bytes make the
run `invalid_environment` even when both arms receive the same context.
`harness_instruction_message_indexes` names every system/developer instruction
message except an index named by `prompt_message_indexes`; the two arrays are
disjoint. A chart-owned system prompt stays prompt-owned and equal across arms.
All indexed harness bytes come from the frozen arm harness; paired context validation
requires equality except exact message deltas derived from the selected harness
factor. Task prompt and actor input are never factor-owned deltas.

Run the forbidden-ref and excerpt scan over every byte in the complete
actor-readable inventory, including harness, memory, tool fixtures, and mounted
roots. Any unscannable or unsanitized readable asset is excluded or makes the
run `status: invalid_environment` with `status_reason: historical_leakage`.

Exact matching is not sufficient for source-derived execution surfaces. Before
actor start, emit exact RFC 8785 `semantic-leakage-review/v1` bytes over every
readable inventory entry and every delivered message. After actor termination,
emit a second review over those surfaces plus every tool result or other tool
observation delivered to the actor. The post-run payload is
`{"actor_hidden_target_fingerprint":null,"actor_hidden_target_ref":null,"context_fingerprint":"sha256:<hex>","coverage":[{"derivation_evidence_fingerprint":"sha256:<hex>","derivation_evidence_ref":"runs/<run-group-id>/semantic-leakage-derivations/<occurrence-digest-hex>.json","hidden_access":"excluded","inventory_entry_ref":"runs/<run-group-id>/actor-readable-inventory/<run-id>.json#/<pointer>","occurrence_id":"sha256:<hex>","provenance_classes":["predates_source"],"result":"clear","semantic_overlap":null,"surface_fingerprint":"sha256:<hex>","surface_kind":"filesystem_entry","surface_ref":"runs/<run-group-id>/semantic-leakage-surfaces/<surface-digest-hex>.json"}],"execution_id":"<run-id>","execution_kind":"actor","generation_attempt_id":null,"holdout_target_fingerprint":null,"holdout_target_ref":null,"inventories":[{"fingerprint":"sha256:<hex>","kind":"actor_readable","ref":"runs/<run-group-id>/actor-readable-inventory/<run-id>.json"}],"pending_fingerprint":null,"phase":"post_run","pre_phase_review_fingerprint":"sha256:<hex>","provenance_derivation_fingerprint":"sha256:<hex>","provenance_derivation_ref":"evaluators/provenance-derivation.json","schema":"semantic-leakage-review/v1","semantic_evaluator_fingerprint":null,"semantic_evaluator_ref":null}`.
The pre-start form uses `phase: pre_start`, a null
`pre_phase_review_fingerprint`, and contains no tool-observation rows. Optimizer
reviews instead use `execution_kind: optimizer` with `pre_generation` and
`post_generation` phases. Optimizer forms have non-null
`generation_attempt_id` and `pending_fingerprint` equal to the candidate access
proof and pending intent. When `holdout_evidence` is non-null they also have the
non-null frozen target pair and bind the global attempt closure; the non-holdout
variant requires both target fields null and binds only the local intent. Actor
forms require generation, pending, and optimizer holdout-target fields null.
For a selecting actor or any chart with `claim.class: preference_training`,
`actor_hidden_target_ref`/fingerprint are non-null and
bind exact `actor-hidden-target/v1` bytes containing the chart-local tagged
target entry defined below. The target therefore binds historical projections
when they exist and hidden evaluator semantics when history does not. Only a
nonselecting, non-training actor requires both null. Both
artifacts are evaluator-visible and never actor input.
A `preference_training` actor_hidden_target binding is therefore mandatory even
outside holdout selection.

`inventories` is sorted by `kind`, duplicate-free, and every ref/fingerprint
pair resolves exact retained bytes. Actor phases contain exactly
`actor_readable`. Optimizer `pre_generation` contains exactly
`optimizer_input` and `candidate_output_prestate`; `post_generation` contains
those two plus `candidate_output_poststate`. The refs and fingerprints equal
the candidate-generation access proof. Missing, extra, or phase-wrong
inventory bindings are `historical_leakage`.

`surface_kind` is exactly `filesystem_entry`, `delivered_message`,
`filesystem_root_descriptor`, `tool_definition`, `tool_policy`,
`tool_observation`, `optimizer_trace_event`, `regular_file_content`,
`arguments_payload`, `effect_payload`, `observation_payload`, `result_payload`,
or `error_payload`. A filesystem identity hashes
the exact RFC 8785 bytes of
`{"entry":{},"inventory_kind":"<kind>","schema":"leakage-filesystem-entry/v1"}`,
where `entry` is the complete type-specific inventory value;
including inventory kind keeps equal entries from distinct inventories
separately accountable. A message identity hashes
`{"content":"<exact-UTF-8>","index":<zero-based-index>,"role":"<role>","schema":"delivered-message/v1"}`.
A tool-observation identity hashes the exact RFC 8785 bytes
`{"call_arguments":<exact-JSON-value>,"call_id":"<id>","index":<zero-based-index>,"result":<exact-JSON-value>,"schema":"tool-observation/v1","tool":"<tool-name>"}`;
the row covers both the call exposed to the tool boundary and the result exposed
back to the actor. Non-JSON or binary values first use their contracted lossless
JSON representation; an unrepresentable or unscannable observation is
`historical_leakage`. An optimizer-trace-event identity hashes the complete
exact RFC 8785 event row, including a standalone `kind: observation` row that
is not paired with a tool call. Every tool-call arguments ref and every
generation-effect payload ref contributes its own exact payload surface before
candidate generation can be certified. Every observation delivered by the optimizer
runner appears exactly once as either that standalone event or the
observation/result/error preimage of its tool event; an argument, effect, or observation outside the
retained trace is invalid. This is the `standalone_observation` case of the
closed `optimizer_trace_event` surface.

Every readable regular file additionally contributes a
`regular_file_content` surface whose preimage is the exact raw file bytes at a
content-addressed ref, not its inventory row. Every optimizer trace argument,
generation-effect payload, observation, result, or error ref additionally contributes the corresponding payload surface
whose preimage is the exact delivered JSON value or contracted lossless binary
representation. Trace-event metadata never substitutes for these semantic
payload rows.

A filesystem-root-descriptor identity hashes the exact retained descriptor
delivered to the process, including normalized path and access mode. A
tool-definition identity hashes the exact ordered tool name, description, and
input/output schema value delivered through the tool API. A tool-policy
identity hashes the complete exact tool/effect policy value delivered to that
process. Every root descriptor, tool definition, and policy input appears once
in both phases for which the process can observe it; deterministic pre-holdout
provenance may make the row clear but never removes it from coverage.

Before review, materialize every exact surface preimage at the content-addressed
`surface_ref`; its digest suffix, `surface_fingerprint`, and exact bytes agree.
The access-lineage validator resolves and inspects those bytes rather than
trusting a hash-only assertion. Equal content may reuse one surface ref but never one
coverage occurrence. `occurrence_id` hashes exact RFC 8785 bytes of
`{"execution_id":"<run-or-generation-attempt-id>","inventory_entry_ref":"<complete-ref-or-message-locus>","surface_fingerprint":"sha256:<hex>","surface_kind":"<kind>"}`.
The locus includes the complete inventory ref plus pointer or actor-context ref
plus message index; an index alone is invalid. Equal content in distinct arms
or repeats therefore retains distinct occurrence and derivation evidence.
`<occurrence-digest-hex>` is the validated lowercase 64-hex suffix of the
prefixed `occurrence_id`; the `sha256:` prefix never enters a path component.
Coverage sorts by `occurrence_id` and contains exactly one row for every
required occurrence. `inventory_entry_ref` points to its inventory row, message
index, or trace-event pointer. `provenance_classes` is the sorted nonempty
conservative union for that occurrence; `possibly_derived` dominates
`independent`, which dominates `predates_source`. Each exact derivation-evidence
pair resolves the complete transitive access lineage used to assign that
class. `hidden_access` is `excluded`, `witnessed`, or `unresolved`;
`semantic_overlap` is null by default; when optional diagnostics are enabled it
is `none`, `possible`, or `material` and remains non-authoritative.
`result` is `clear` exactly for excluded access, `leak` exactly for witnessed
hidden access, and `uncertain` exactly for unresolved access. Semantic overlap
without an access witness never changes `clear` to `leak` or `uncertain`. No
missing, duplicate, or extra row is allowed. Actor start requires a
clear pre-start review; selection, promotion, and training require a clear
post-run review whose pre-phase fingerprint matches. Runs and EER bind both
review refs/fingerprints. A witnessed or unresolved access path is
`historical_leakage`; when it cannot be excluded, the
chart is diagnostic-only and cannot enter holdout, selection, or training.

Every review binds the same evaluator-owned `provenance_derivation` ref and
fingerprint. Its deterministic law assigns `predates_source` only when the exact
occurrence asset is transitively present in the immutable source bundle before
the chart cut; assigns `independent` only to frozen baseline/world assets whose
captured provenance predates factor selection and has no source-derived input;
and assigns `possibly_derived` only when a retained access lineage reaches
hidden evaluator/source bytes or cannot exclude such a dependency. Candidate-
generated bytes whose complete access proof contains only frozen baseline/world
and authorized discovery/development inputs are `independent` of the hidden
target even when their content is semantically similar. Optimizer or actor
outputs and tool observations with incomplete lineage remain
`possibly_derived`. The evaluator
recomputes each row from retained occurrence evidence; producers cannot choose
the class.

An optional diagnostic review may bind one frozen evaluator-owned
`semantic-leakage-evaluator/v1` ref/fingerprint. Its closed exact RFC 8785 bytes are
`{"configuration_fingerprint":"sha256:<hex>","configuration_ref":"evaluators/semantic-leakage-configuration.json","implementation_fingerprint":"sha256:<hex>","implementation_ref":"evaluators/semantic-leakage-implementation.json","model_runtime_fingerprint":null,"model_runtime_ref":null,"rubric_fingerprint":"sha256:<hex>","rubric_ref":"evaluators/semantic-leakage-rubric.json","schema":"semantic-leakage-evaluator/v1"}`.
Every pair resolves exact bytes. Both outer fields are null when diagnostics
are disabled. When enabled, the pre-candidate policy freezes the pair and every
pre/post review in both arms repeats it exactly; disagreement degrades only the
diagnostic result and never changes `hidden_access` or admission status.

When `holdout_evidence` is non-null, optimizer reviews also bind an
evaluator-only content-addressed
`holdout-semantic-target/v1` asset containing every selected chart's
actor-visible pre-cut state, prompt, source bytes, chart semantics, hidden
action, correction, recovery, and outcome projections. The access-lineage
validator uses this as the complete hidden-asset set; optional semantic
comparison may inspect it but is never an admission gate. Hash-only or omitted
hidden assets cannot yield `candidate_generation_blind: true`.
For a non-holdout comparison both holdout-target fields are null: the review
still validates complete surface coverage, provenance, and authorized inputs,
but it neither fabricates nor claims comparison
against a holdout corpus.

The target is closed exact RFC 8785 bytes:
`{"charts":[{"actor_visible_state_fingerprint":"sha256:<hex>","actor_visible_state_ref":"actors/<chart-id>.md","chart_fingerprint":"sha256:<hex>","chart_semantics_fingerprint":"sha256:<hex>","chart_semantics_ref":"<root-chart-ref>","correction_fingerprint":"sha256:<hex>","correction_ref":"source/<chart-id>/correction.json","hidden_action_fingerprint":"<rejected_historical_action_fingerprint>","hidden_action_ref":"<rejected_historical_action_ref>","hidden_evaluator_fingerprint":"sha256:<hex>","hidden_evaluator_ref":"evaluators/<chart-id>.json","outcome_projection_fingerprint":"sha256:<hex>","outcome_projection_ref":"source/<chart-id>/outcome.json","prompt_fingerprint":"sha256:<hex>","prompt_ref":"actors/<chart-id>-prompt.md","recovery_fingerprint":"sha256:<hex>","recovery_ref":"source/<chart-id>/recovery.json","source_byte_evidence":[{"fingerprint":"sha256:<hex>","ref":"source/<chart-id>/source-maps/<source-id>.yaml"}],"target_kind":"historical_correction"}],"schema":"holdout-semantic-target/v1"}`.
Charts sort by fingerprint and equal the complete selected holdout chart set;
every nested pair resolves exact closure bytes and source evidence arrays are
sorted and duplicate-free. No omitted selected chart or hidden projection can
validate.
`chart_semantics_ref`/fingerprint is exactly that chart's root
`chart_ref`/`chart_fingerprint` pair for every chart kind; no synthesized or
correction-only alternate preimage is admitted.
Each chart entry is a tagged union. Actor-visible state, prompt, chart
semantics, chart fingerprint, and the exact hidden evaluator pair are non-null
in every variant. `actor_visible_state_ref`/fingerprint equal the chart's exact
`actor.input_ref`/fingerprint; the target cannot substitute another visible
asset. `target_kind: historical_correction` uses the displayed
non-null hidden-action/correction pairs, the chart's canonical nullable
recovery/outcome pairs, and its complete source-evidence array. Its hidden-
action pair is copied exactly from the chart's singular rejected historical
action fields and never synthesized from a conventional path. Its prompt pair
equals `actor.prompt_*`; correction, recovery, and outcome pairs equal the
chart's singular hidden source projection pairs; chart semantics and hidden
evaluator pairs equal their chart-owned assets. Every equality is validated
before target fingerprinting, so the target cannot substitute a chart-owned
projection or turn present evidence into absence.
`target_kind: source_no_history` requires hidden-action, correction, recovery,
and outcome pairs null while retaining a nonempty complete source-evidence
array. `target_kind: designed_no_history` requires those four pairs null and
the source-evidence array empty. The latter two compare possibly-derived
surfaces with the hidden evaluator semantics without inventing historical
events or discarding available source bytes.

An `actor-hidden-target/v1` object is closed with exactly `schema` and `chart`;
`schema` is the literal `actor-hidden-target/v1`. Its `chart` is the
hidden-only projection of one target entry: remove actor-visible-state and
prompt pairs, retain chart fingerprint/kind, hidden evaluator, and every
available historical action/correction/recovery/outcome and source-evidence
pair. Nullability still follows the tagged union. Legitimate actor input and
prompt refs are therefore never classified as hidden merely because the full
evaluator target also records them. Its RFC 8785 bytes are content-addressed.
The chart fingerprint equals the actor's chart, and its tagged entry is
constructed by the same projection even when no holdout target exists. Thus every
selecting or preference-training actor has a non-vacuous semantic target for
the evidence actually present.

A file containing both projections is not separation. For harness selection,
promotion, or training, absent actor-readable inventory or access proof makes
the run invalid_environment and limits the chart to diagnostic use.

## 7. Partition the atlas

One split group contains all charts derived from the same root session, root
task, issue, PR, linked worker lineage, or nearly duplicated request. A group
never crosses partitions.

Each group also has a corpus-independent `source_group_fingerprint`. For a root
session, its input is exactly the RFC 8785 canonical UTF-8 encoding of:

~~~json
{"identity_kind":"root_session","identity_refs":["seq:<adapter>:<root-session-id>"],"schema":"emulator-source-group/v1"}
~~~

`external_task` governs the group whenever an exact repository issue/PR/task
identity is available; otherwise the group kind is `duplicate_cluster` for a
human-attested retry/near-duplicate cluster, `root_session` for one session
lineage, or `designed_task` with the actor-input fingerprint. The group
`identity_refs` is the byte-lexicographically sorted,
duplicate-free array of the selected kind's exact refs; kinds are never mixed.
Compute SHA-256 over those exact canonical bytes for
`source_group_fingerprint`. Also hash each ref independently from the RFC 8785
canonical bytes of
`{"identity_kind":"<kind>","identity_ref":"<ref>","schema":"emulator-source-identity/v1"}`
and retain the sorted descriptor preimages in `source_identity_descriptors`
beside the sorted `source_identity_fingerprints`. Canonical refs are:

~~~text
github-pr:<base64url(repository-node-id)>:<base64url(pull-request-node-id)>
github-issue:<base64url(repository-node-id)>:<base64url(issue-node-id)>
seq:<adapter>:<root-session-id>
designed-task:<actor-input-fingerprint>
task-uri:<base64url(issuer-canonical-absolute-uri UTF-8 bytes)>
duplicate-cluster:sha256:<digest>
~~~

The individual `identity_kind` is canonical by ref family: GitHub and
`task-uri` refs use `external_task`, `seq` refs use `root_session`,
`designed-task` refs use `designed_task`, and `duplicate-cluster` refs use
`duplicate_cluster`. No other kind/ref pairing is valid.

Base64url uses the RFC 4648 URL-safe alphabet without padding. GitHub refs use
immutable GraphQL node IDs, not owner/repository slugs or issue numbers. A
`task-uri` is admissible only when the source system supplies one canonical
absolute URI containing an immutable object identity; generic URI spelling
normalization is not invented here. Otherwise retain every verified alias or
keep the group out of holdout. `designed-task` contains the literal `sha256:`
actor-input fingerprint.
An approved duplicate cluster first materializes the exact RFC 8785 canonical
UTF-8 bytes of:

~~~json
{"member_source_identity_fingerprints":["sha256:<hex>","sha256:<hex>"],"schema":"emulator-duplicate-cluster/v1"}
~~~

The member array is byte-lexicographically sorted, duplicate-free, contains at
least two individual source identities, and contains every source identity
covered by the human attestation. Each member is a `root_session` or
`designed_task` identity; a mixed set is allowed. This lets paraphrased designed
tasks share an attested duplicate cluster instead of becoming independent
holdouts merely because their actor-input bytes differ. `<digest>` is SHA-256
of those exact bytes.
Approval is exact RFC 8785
`{"approved":true,"cluster_digest":"sha256:<hex>","holdout_blind":true,"independent_of_candidate_generation":true,"member_source_identity_fingerprints":["sha256:<hex>"],"principal_identity_fingerprint":"sha256:<hex>","principal_identity_ref":"principals/<principal-digest-hex>.json","schema":"duplicate-cluster-attestation/v1"}`
bytes. The member set equals the cluster preimage exactly; the chart and
pre-candidate policy bind the approval ref/fingerprint. Missing, split, or
self-authored approval makes the cluster ineligible for holdout.
The attester principal differs from the factor selector and every candidate
author/attester principal for the cycle. It also differs by canonical person
ID from every human named by a selected chart's
`correction-human-review/v1` or `correction-reviewed-pattern/v1` evidence; any
such reviewer has evaluator
knowledge and is not holdout-blind for clustering that chart. It likewise
differs from every `designed-chart-authorship/v1` principal for any member
designed task. Otherwise the cluster is
discovery/development-only.
The cluster then uses identity kind `duplicate_cluster` and ref
`duplicate-cluster:sha256:<digest>`; its descriptor preimage is exactly
`{"identity_kind":"duplicate_cluster","identity_ref":"duplicate-cluster:sha256:<digest>","schema":"emulator-source-identity/v1"}`.
The canonical cluster bytes and human attestation are retained and
fingerprinted. No other identity kind or digest preimage is valid for that ref.
Aliases for one task are all retained. For session-derived groups, this individual set always
includes every participating root-session identity (linked workers use the
root, never worker IDs), the duplicate-cluster identity when used, and every
stable external-task alias;
individual aliases may span kinds even though the aggregate group kind does
not. Cross-atlas claims and locks use every individual identity fingerprint, so
groups that overlap by one underlying task/session collide. Local chart IDs, atlas IDs, partition, and the
surrounding corpus are excluded. Root chart entries repeat the chart's
`source_group_fingerprint` exactly; ambiguity, mismatch, or mutable refs make
the group ineligible for holdout.
Atlas validation additionally requires every connected component of charts
whose individual source-identity sets overlap to have exactly one
`split.group_id`; assigning an overlapping identity to different groups is
`invalid_environment` and cannot multiply holdout evidence.
Retried or near-duplicate sessions without a shared stable external-task or
human-attested duplicate-cluster descriptor are ineligible for holdout.
Likewise, near-duplicate designed tasks without a stable external-task or one
shared human-attested duplicate cluster are ineligible for holdout. The global
partition registry locks every member identity as well as the cluster identity.

- discovery is visible for failure mining, mechanism hypotheses, and chart
  design;
- development is visible for bounded candidate and evaluator iteration;
- holdout is frozen before candidate generation and hidden from the author,
  optimizer prompt, candidate worktree, and development reports.

For every paired comparison, freeze the exact baseline harness and have the
human owner select exactly one factor from discovery/development evidence.
Publish immutable
RFC 8785 `factor-selection/v1` bytes:

~~~json
{"baseline_harness_fingerprint":"sha256:<hex>","discovery_development_evidence":[{"evidence_fingerprint":"sha256:<hex>","evidence_ref":"evidence/<digest-hex>.json","partition":"development"}],"factor_selector_identity_fingerprint":"sha256:<hex>","factor_selector_identity_ref":"principals/<principal-digest-hex>.json","generation_runner_fingerprint":"sha256:<hex>","generation_runner_ref":"comparison/candidate-generation-runner.json","holdout_semantics_seen":false,"model_runtime_configuration_fingerprint":"sha256:<hex>","model_runtime_configuration_ref":"comparison/model-runtime.json","optimizer_visible_policy":{"authorized_input_evidence":[{"evidence_fingerprint":"sha256:<hex>","evidence_ref":"evidence/<digest-hex>.json","message_projection_fingerprint":"sha256:<hex>","message_projection_ref":"evidence/projections/<digest-hex>.json"}],"candidate_budget":1,"factor":"question_policy","factor_owner_paths":[{"path":"<logical-path>","root_id":"<root-id>"}],"inventory_template_schema_fingerprint":"sha256:<hex>","inventory_template_schema_ref":"optimizer/inventory-template-schema.json","non_holdout_selectors":[{"kind":"whole_file","ownership_authority_fingerprint":"sha256:<hex>","ownership_authority_ref":"<static-ref>","path":"<logical-path>","root_id":"<root-id>","selector_id":"<selector-id>"}],"optimizer_tool_policy_template_fingerprint":"sha256:<hex>","optimizer_tool_policy_template_ref":"optimizer/tool-policy-template.json","pre_holdout_optimizer_templates":[{"candidate_id":"candidate-1","candidate_metadata_template_fingerprint":"sha256:<hex>","candidate_metadata_template_ref":"harnesses/candidates/candidate-1/candidate-metadata-template.json","generation_attempt_id":"<generation-attempt-id>","optimizer_inventory_template_fingerprint":"sha256:<hex>","optimizer_inventory_template_ref":"harnesses/candidates/candidate-1/inventory-template.json"}],"runtime_configuration_keys":["<key>"],"runtime_constraints":{},"runtime_surface_fields":["<field>"],"tool_schema_fingerprints":["sha256:<hex>"]},"schema":"factor-selection/v1"}
~~~

Every evidence ref resolves inside discovery or development material, its
fingerprint matches exact bytes, and its recorded partition equals the entry;
holdout evidence is forbidden. Evidence entries, root-qualified owner paths,
complete structured selectors, runtime keys, and derived runtime fields are sorted and
duplicate-free. Each `evidence_ref`, `evidence_fingerprint`, and `partition`
triple is validated as one resolvable identity. `optimizer_visible_policy` is
the complete semantic policy the optimizer may later receive, including tool
policy, tool schemas, authorized message projections, and the inventory-template
schema; none may be added or changed after this freeze. When any selected chart
is holdout, the artifact is created under the global partition mutex before the
first semantic holdout read. A comparison with no holdout creates the same
closed asset locally before candidate generation and does not acquire or claim
the global holdout mutex. In both routes it binds the already-frozen baseline,
and the root, evaluator-only pre-candidate policy, and final reports bind its
exact ref/fingerprint. `pre_holdout_optimizer_templates` is keyed by
candidate ID, has exactly the candidate budget rows, and binds the exact
optimizer input inventory and metadata templates—including discovery file
selection, hypothesis, and changed paths—before the first semantic holdout
read or, without holdout, before candidate generation. For each candidate, the
corresponding `candidate-generation-commitment/v1` repeats the same candidate
ID and both ref/fingerprint pairs exactly. Its canonical projection obtained by
removing only its `schema`, author, and tool-policy-template fields MUST equal the factor-
selection row byte-for-byte; no ref transformation or field rename is allowed.
A holdout-seeing compiler therefore cannot choose or rewrite them. The optimizer policy is the deterministic exact
projection of `optimizer_visible_policy`; it receives no outer ref,
outer fingerprint, discovery/development evidence, selector-principal identity,
or baseline/holdout commitment. Selector ownership fingerprints inside
`non_holdout_selectors` are policy-local proof and remain present. The
pre-candidate policy binds the factor-selection pair and adds evaluator-only
fields; it does not duplicate that semantic object. Neither the baseline nor factor selection can be revised
after a holdout semantic read. If factor selection requires holdout contents,
those charts become discovery/development and a new untouched group is
required. Any baseline drift after this artifact is published restarts factor
selection and requires a new untouched holdout group.

The generation-runner and model/runtime pairs are likewise frozen in these
pre-read bytes. The pre-candidate policy and every candidate access proof repeat
them exactly; a post-read choice, alternate runtime, or missing pair is
`holdout_contaminated` before optimizer start.

The candidate-independent optimizer tool policy template is exact RFC 8785
`optimizer-tool-policy-template/v1` bytes containing allowed tool names,
logical schema IDs/fingerprints, denied names, per-tool effects, external-effect
policy, network policy, and every filesystem permission expressed as a logical
root role. It contains no candidate ID, candidate path, absolute sandbox root,
or fresh process identity. A concrete candidate policy resolves the same schema
bytes and maps every root role to that candidate's sandbox. Projecting the
concrete policy back verifies its `template_fingerprint`, replaces each verified
schema ref with its logical schema ID, replaces each absolute root with its
frozen role, removes only `template_fingerprint`, and changes only the schema
tag. The result MUST equal the frozen template byte-for-byte; no permission or
effect field is discarded.

~~~json
{"allowed_tools":[{"effects":["filesystem_read","filesystem_write"],"name":"<tool-name>","schema_fingerprint":"sha256:<hex>","schema_id":"<logical-schema-id>"}],"denied_tools":[],"external_side_effects":"deny","filesystem_root_roles":[{"access":"isolated_write","role":"candidate_output"},{"access":"read_only","role":"optimizer_input"}],"network":"deny","schema":"optimizer-tool-policy-template/v1"}
~~~

Each authorized message projection ref resolves exact RFC 8785
`{"content":"<exact-UTF-8>","role":"user","schema":"optimizer-authorized-message/v1"}`
bytes. The projection_implementation is the fixed direct role/content equality
rule; `message_projection_fingerprint` is SHA-256 of the exact RFC 8785
projection bytes. Delivered message
role/content must equal this preimage exactly.

Every human-role identity ref resolves exact RFC 8785
`{"aliases":[{"issuer":"<authority-namespace>","principal_id":"<issuer-subject-id>"}],"person_id":"<owner-assigned-stable-person-id>","schema":"emulator-principal-identity/v1"}`
bytes; aliases are sorted and duplicate-free, and the companion fingerprint,
digest filename, and bytes agree. The human owner assigns one stable
cross-issuer `person_id` and admits all verified aliases into that single asset;
overlapping aliases or multiple assets for one person are invalid.
In schemas below, `principal_identity_ref` denotes this common ref/fingerprint
contract; role-specific fields retain their selector, reviewer, or attester
prefix.

A chart with `source_kind: user_design`, or `mixed` containing designed
material, binds non-null exact RFC 8785
`designed-chart-authorship/v1` bytes through its source authorship pair:
`{"actor_input_fingerprint":"sha256:<hex>","author_principal_identity_fingerprint":"sha256:<hex>","author_principal_identity_ref":"principals/<digest-hex>.json","schema":"designed-chart-authorship/v1","source_identity_fingerprints":["sha256:<hex>"]}`.
The identity array equals the chart split exactly and the actor input equals the
chart actor packet. Purely source-derived charts keep both authorship fields
null. For a selected designed holdout, the normalized author `person_id` MUST
differ from the factor selector and every candidate author/attester in the
cycle; otherwise that chart is discovery/development-only. This is the
designed-holdout blindness witness—`holdout_semantics_seen: false` cannot
override a person-ID collision.

`factor_selector_identity_ref` and fingerprint identify the principal that
selected the factor. Before admitting any selected holdout
correction-derived chart, require it to differ from every
reviewer identity ref/fingerprint pair in that holdout chart's
`correction-human-review/v1` or `correction-reviewed-pattern/v1` assets. All
roles compare `person_id` under this alias-normalized scheme, so alternate
emails, accounts, or issuer namespaces cannot manufacture inequality. Selector identity is evaluator-only
outer evidence and is absent from the optimizer policy projection.
Before candidate generation, every candidate-author principal in the frozen
generation commitments MUST likewise have a different normalized `person_id`
from every correction reviewer for every selected holdout chart. The access
proof repeats that author identity; missing or equal identity is
`holdout_contaminated` and cannot yield `candidate_generation_blind: true`.

Before the first semantic holdout read, while holding the user-global partition
mutex, atomically create one immutable `holdout-selection-intent/v1` marker per
source identity with exact RFC 8785 bytes:

~~~json
{"atlas_instance_id":"sha256:<hex>","baseline_capture_provenance_fingerprint":"sha256:<hex>","baseline_capture_provenance_ref":"harnesses/baseline/capture-provenance.json","baseline_harness_fingerprint":"sha256:<hex>","exposure_registry_id":"sha256:<hex>","factor_selection_fingerprint":"sha256:<hex>","factor_selection_ref":"partitions/factor-selection.json","factor_selector_identity_fingerprint":"sha256:<hex>","factor_selector_identity_ref":"principals/<principal-digest-hex>.json","holdout_exposure_attestation_fingerprints":["sha256:<hex>"],"holdout_exposure_attestation_refs":["partitions/holdout-exposure-attestations/<digest-hex>.json"],"schema":"holdout-selection-intent/v1","source_identity_fingerprint":"sha256:<hex>"}
~~~

Store it at
`holdout-selection-intents/<holdout-key>.json`. A byte-identical marker may be
reused only by the same frozen selection and pre-read witnesses. Fsync the
new file and containing directory before any semantic holdout read. An absent, partial, or mismatched
marker blocks the read as `source_contaminated`. A crash after the semantic read
cannot reopen the identity for another baseline or factor.
The pre-candidate policy and final root bind every `selection_intent_ref` and
fingerprint. Reservation creation and the immediate pre-actor gate revalidate
the global bytes against those snapshots; a missing or changed selection intent
stops before exposure.
Each `selection_intent_ref` is the atlas-relative immutable copy at
`partitions/selection-intents/<holdout-key>.json`. Exact RFC 8785
`selection-intent-validation/v1` bytes are:

~~~json
{"exposure_registry_id":"sha256:<hex>","intents":[{"canonical_intent_path":"<absolute-path>","holdout_key":"<hex>","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"partitions/selection-intents/<holdout-key>.json"}],"schema":"selection-intent-validation/v1"}
~~~

Entries sort by `holdout_key` with unique keys, paths, and snapshot refs; each
canonical intent path, snapshot ref/fingerprint, and holdout key resolves exact
byte equality under the named registry. The
pre-candidate policy and root bind this validation ref/fingerprint; reservation
and pre-actor checks rerun the mapping under the global mutex.
Validation also enumerates every global intent matching this atlas instance,
baseline fingerprint, and factor-selection fingerprint and requires exact set
equality with the root snapshots. An omitted matching intent is
`holdout_contaminated`; semantically read groups cannot be cherry-picked away.

After each holdout chart and evaluator closure is compiled, recursively verified,
and structurally validated—but before candidate generation, actor execution, or
arm outcomes—the evaluator-informed holdout compiler classifies every
non-observational chart as selection-eligible or ineligible from its frozen
claim class, maximum claim, attribution, and oracle/invariant presence. Every
selection-eligible holdout entry is `required: true`. `required: false` is
permitted only for discovery/development entries or for an observational or
structurally selection-ineligible chart. The classification is part of the
frozen pre-candidate policy and cannot change after candidate generation begins
or any arm outcome is seen. An invalid, unsupported, skipped, or ambiguous
required holdout yields `insufficient_evidence`; it is never moved to
`excluded_charts` to improve the recommendation.
Eligibility therefore freezes after chart and evaluator validation and before
candidate generation or arm outcomes.

Compile and validate holdout charts in a fresh context that terminates before
candidate optimization starts. Candidate authoring and optimization use a
separate fresh context that receives discovery/development material only; prior
model context that saw holdout contents is not an admissible optimizer. Freeze
all chart, evaluator, and partition fingerprints before that handoff.

Do not rely on prompts or same-user file modes to hide holdout material from an
optimizer with filesystem tools. Run optimization in a workspace where holdout
roots are not mounted/readable. The pre-candidate policy binds the exact
run-independent `optimizer-inventory-template/v1` and the evaluator-owned candidate-generation
runner ref/fingerprint. That runner creates the readable-root boundary, keeps
its mounts immutable for the optimizer process lifetime, and, after the process
exits but before teardown, re-enumerates the complete readable roots and
requires them to equal the planned inventory. It then emits the exact RFC 8785
bytes of:

~~~json
{"candidate_author_principal_identity_fingerprint":"sha256:<hex>","candidate_author_principal_identity_ref":"principals/<digest-hex>.json","candidate_generation_blind":true,"candidate_harness_fingerprint":"sha256:<hex>","candidate_id":"<candidate-id>","candidate_metadata_template_fingerprint":"sha256:<hex>","candidate_metadata_template_ref":"harnesses/candidates/<candidate-id>/candidate-metadata-template.json","candidate_output_poststate_fingerprint":"sha256:<hex>","candidate_output_poststate_ref":"harnesses/candidates/<candidate-id>/output-poststate.json","candidate_output_prestate_fingerprint":"sha256:<hex>","candidate_output_prestate_ref":"harnesses/candidates/<candidate-id>/output-prestate.json","cycle_id":"<cycle-id>","fresh_context_id":"<runner-opaque-id>","generation_attempt_id":"<generation-attempt-id>","generation_effects_fingerprint":"sha256:<hex>","generation_effects_ref":"harnesses/candidates/<candidate-id>/generation-effects.json","generation_runner_fingerprint":"sha256:<hex>","generation_runner_ref":"comparison/candidate-generation-runner.json","holdout_target_fingerprint":null,"holdout_target_ref":null,"model_runtime_configuration_fingerprint":"sha256:<hex>","model_runtime_configuration_ref":"comparison/model-runtime.json","optimizer_context_fingerprint":"sha256:<hex>","optimizer_context_ref":"harnesses/candidates/<candidate-id>/optimizer-context.json","optimizer_input_inventory_fingerprint":"sha256:<hex>","optimizer_input_inventory_ref":"harnesses/candidates/<candidate-id>/optimizer-input-inventory.json","optimizer_inventory_template_fingerprint":"sha256:<hex>","optimizer_inventory_template_ref":"harnesses/candidates/<candidate-id>/inventory-template.json","optimizer_policy_fingerprint":"sha256:<hex>","optimizer_process_opaque_id":"<runner-opaque-id>","optimizer_runtime_observation_fingerprint":"sha256:<hex>","optimizer_runtime_observation_ref":"harnesses/candidates/<candidate-id>/optimizer-runtime-observation.json","optimizer_tool_policy_fingerprint":"sha256:<hex>","optimizer_tool_policy_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-policy.json","optimizer_tool_policy_template_fingerprint":"sha256:<hex>","optimizer_tool_policy_template_ref":"optimizer/tool-policy-template.json","optimizer_tool_trace_fingerprint":"sha256:<hex>","optimizer_tool_trace_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-trace.json","parent_context_id":null,"pending_fingerprint":"sha256:<hex>","pending_ref":"harnesses/candidates/<candidate-id>/generation-intents/<generation-attempt-id>.json","post_generation_leakage_review_fingerprint":"sha256:<hex>","post_generation_leakage_review_ref":"harnesses/candidates/<candidate-id>/leakage-postgeneration.json","pre_candidate_policy_fingerprint":"sha256:<hex>","pre_generation_leakage_review_fingerprint":"sha256:<hex>","pre_generation_leakage_review_ref":"harnesses/candidates/<candidate-id>/leakage-pregeneration.json","sandbox_instance_id":"<runner-opaque-id>","schema":"candidate-generation-access-proof/non-holdout-v1","status":"completed"}
~~~

The displayed payload is the exact non-holdout variant. The exact holdout
variant has the identical closed field set, uses
`schema: candidate-generation-access-proof/holdout-v1`, and replaces both null
target values with the frozen holdout target pair. Before authoring the holdout
proof, copy the exact global pending-intent bytes with create-new semantics to
`harnesses/candidates/<candidate-id>/generation-intents/<generation-attempt-id>.json`,
verify byte equality and fingerprint against the global record, and include
that local snapshot transitively in the final root closure. Its `pending_ref`
points only to this closure-local snapshot; after root archival the ordinary
`roots/<root-digest-hex>/` prefix resolves it without consulting the live
registry. The non-holdout schema is
`candidate-generation-access-proof/non-holdout-v1`; mixed schema and target
nullability is invalid.

The runner emits this artifact only for the actual process that produced the
named candidate bytes; `sandbox_instance_id` is nonempty and unique within the
cycle. Candidate metadata and the root candidate entry bind its static ref and
fingerprint. The proof's cycle, runner, input inventory, optimizer context and fresh
context identity, optimizer policy, and
pre-candidate policy must equal the frozen cycle commitments, and its candidate
fingerprint must equal the frozen candidate manifest. The pre-candidate
generation-runner and model/runtime ref/fingerprint pairs equal factor selection
and the pre-candidate policy exactly; fingerprint-only or post-freeze runtime
selection is invalid. The pre-candidate
commitment and access proof repeat the same metadata-template pair; final
candidate metadata is post-generation and binds that template without being a
pre-candidate dependency. Candidate metadata,
commitment, and access proof repeat the same canonical
`candidate_author_principal_identity_ref`/fingerprint; duplicate-cluster
independence compares that principal with the attester. Missing, mismatched,
pre-run, or externally supplied access
evidence contaminates the holdout.
The two holdout-target fields are both non-null and equal the closed policy's
holdout target exactly when `holdout_evidence` is non-null; both are null for a
discovery/development-only paired comparison. No other mixed nullability is valid.
Its `generation_attempt_id` equals the pending intent and both leakage reviews;
its `pending_fingerprint` hashes the exact pending bytes for that attempt. The
proof cannot be reused across attempts even when candidate and cycle IDs match.
`candidate_generation_blind: true` is emitted only after the runner proves that
the optimizer context, readable input roots, tool observations, and writable
output roots contain no holdout semantics; it is a result of the retained
access and leakage evidence, not a reviewer attestation.
The optimizer runtime-observation pair resolves exact RFC 8785
`optimizer-runtime-observation/v1` bytes:
`{"fresh_context_id":"<runner-opaque-id>","generation_attempt_id":"<generation-attempt-id>","model_runtime_configuration_fingerprint":"sha256:<hex>","observed_runtime_config":{},"optimizer_process_opaque_id":"<runner-opaque-id>","runner":{"binary_sha256":"sha256:<hex>","name":"<name>","version":"<version>"},"sandbox_instance_id":"<runner-opaque-id>","schema":"optimizer-runtime-observation/v1"}`.
The runner observes these values from the actual fresh optimizer process; they
equal the frozen model/runtime asset, access proof, context, attempt, and
sandbox. Before inventory capture the runner allocates exactly one optimizer
process ID and then launches only that process in the sandbox. The access proof,
runtime observation, optimizer context, input inventory, both output inventories, generation
effects, and tool trace all repeat that ID. A missing/mismatched ID or a second
optimizer process in the sandbox is `holdout_contaminated`; evidence cannot be
spliced across processes. Requested-only or copied runtime evidence is `holdout_contaminated`.
`optimizer_context_ref` retains the exact RFC 8785 bytes and
`optimizer_context_fingerprint` hashes them:
`{"authorized_input_messages":[{"evidence_fingerprint":"sha256:<hex>","evidence_ref":"evidence/<digest-hex>.json","message_index":1}],"fresh_context_id":"<runner-opaque-id>","messages":[{"content":"<exact-optimizer-policy-UTF-8>","role":"system"},{"content":"<authorized-input-UTF-8>","role":"user"}],"optimizer_policy_message_indexes":[0],"optimizer_process_opaque_id":"<runner-opaque-id>","schema":"optimizer-context/v1"}`
with the same closed roles and complete ordered message semantics. The generation
runner creates that context with `parent_context_id: null`; reuse, import, or
hidden prior messages invalidate the proof. The context receives only the
frozen optimizer policy and discovery/development inputs and is covered by the
same leakage review as the readable inventory.
`optimizer_policy_message_indexes` is nonempty, sorted, and duplicate-free;
the selected message content is exactly the UTF-8 RFC 8785 bytes of a closed
two-field object. Its `schema` is the literal `optimizer-policy/v1`; its
`policy` value is the complete exact
`factor-selection.optimizer_visible_policy` JSON object.
No prose rendering, omission, added instruction, or alternate interpretation is
admitted. The SHA-256 of those exact bytes equals `optimizer_policy_fingerprint`
in the pending intent and access proof, and the frozen pre-candidate policy's
factor-selection pair resolves the sole `optimizer_visible_policy` that
recomputes the wrapper. Every other message is a separately inventoried
authorized discovery/development input; an unbound extra message is
`holdout_contaminated`.
Every non-policy message index appears exactly once in
`authorized_input_messages`; its evidence ref/fingerprint is frozen in the
pre-candidate policy and resolves bytes whose contracted message projection
equals the delivered role/content. Missing, extra, or mismatched mappings are
`holdout_contaminated`. After removing policy-message indexes, the remaining
delivered message sequence is an ordered exactly-once projection of
`factor-selection.optimizer_visible_policy.authorized_input_evidence`: same
cardinality and order, contiguous message indexes, and byte-equal role/content
for each referenced projection. Omission, duplication, or reordering is
`holdout_contaminated` even when each surviving message is individually valid.
The optimizer input inventory is immutable and is exactly the RFC 8785 bytes:

~~~json
{"entries":[{"file_type":"regular","mode":"100644","path":"<logical-path>","root_id":"<root-id>","sha256":"sha256:<hex>"}],"input_roots":[{"path":"<canonical-absolute-root>","root_id":"<root-id>"}],"optimizer_process_opaque_id":"<runner-opaque-id>","sandbox_instance_id":"<runner-opaque-id>","schema":"optimizer-input-inventory/v1","tool_policy_fingerprint":"sha256:<hex>"}
~~~

The candidate output inventory is exactly:

~~~json
{"entries":[],"optimizer_process_opaque_id":"<runner-opaque-id>","output_roots":[{"path":"<canonical-absolute-root>","root_id":"<root-id>"}],"phase":"pre_generation","sandbox_instance_id":"<runner-opaque-id>","schema":"candidate-output-inventory/v1"}
~~~

The post-generation form uses `phase: post_generation` and contains every exact
generated regular-file, directory, and symlink entry admitted by the closed
variants below. Each directory or symlink requires its matching retained
filesystem effect just as a regular file does; special files remain forbidden.

The pre-generation output inventory has an empty `entries` array; only the
predeclared isolated output roots exist. Replay the complete ordered
`generation_effects` from that empty prestate using exact create, overwrite,
rename, symlink, mkdir, and delete semantics. The replay-derived final inventory
must equal the post-generation inventory byte-for-byte. This admits atomic-save
temporaries and overwritten/deleted intermediates while proving that every
surviving byte has traced provenance and no effect is unaccounted. An unchanged
prestate byte, unrepresentable effect, replay error, or final mismatch
invalidates candidate provenance.

The access proof's generation-effects pair resolves exact RFC 8785
`generation-effects/v1` bytes:

~~~json
{"effects":[{"after_fingerprint":"sha256:<hex>","before_fingerprint":null,"kind":"create","path":"<logical-path>","payload_fingerprint":"sha256:<hex>","payload_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-events/<sequence>-payload.json","root_id":"<root-id>","sequence":1,"source_path":null}],"generation_attempt_id":"<generation-attempt-id>","optimizer_process_opaque_id":"<runner-opaque-id>","schema":"generation-effects/v1"}
~~~

Sequence starts at one and is contiguous. `kind` is `create`, `overwrite`,
`rename`, `symlink`, `mkdir`, or `delete`; each kind has exact nullability for
source path, before/after digests, and payload. Paths are logical output-root
paths qualified by `root_id`; `(root_id, path)` identifies one output entry
even when several roots contain the same logical path. Rename is admitted only
within that one `root_id`; cross-root rename is denied by the tool policy and
must be expressed as separately evidenced create/delete effects. Every tool-trace effect ref resolves one identical row, in order, and
the envelope contains no extra or missing row. The fixed replay implementation
consumes these bytes; producers cannot assert replay without the sealed log.

The closed tagged-union variants are:

- `create`: null source/before; non-null after and payload; the after-state's
  content projection equals the payload fingerprint.
- `overwrite`: null source; non-null before, after, and payload; the after-state's
  content projection equals the payload fingerprint.
- `rename`: non-null source and after, nullable before, null payload; the source
  entry-state fingerprint equals after and replay removes the source.
- `symlink`: null source/before; non-null after and payload, where payload is
  the exact link-target bytes.
- `mkdir`: null source/before/payload and non-null after.
- `delete`: null source/after/payload and non-null before.

Before/after values fingerprint exact canonical, path-independent entry-state
bytes containing file type, mode, and the content digest, link-target digest,
or directory marker appropriate to that type. Payload fingerprints hash only
raw regular-file or link-target bytes. Replay verifies the payload digest inside
the entry state, then derives the path-qualified inventory entry from `root_id`,
`path`, and that state. Rename requires its source entry state to equal the
after state even though the path-qualified inventory fingerprints differ.
Mixed variants are invalid.

The pre-generation semantic leakage review covers every entry in both the
optimizer input inventory and `candidate_output_prestate`, plus every delivered
optimizer message, before the optimizer process starts. Candidate generation
is forbidden until that complete review is clear. An existing output byte can
therefore neither seed the candidate nor evade the post-generation delta check.

Both optimizer inventory schemas use exactly these closed, schema-local entry
variants and no others:

~~~json
{"file_type":"regular","mode":"100644","path":"<logical-path>","root_id":"<root-id>","sha256":"sha256:<hex>"}
{"file_type":"directory","mode":"040700","path":"<logical-path>","root_id":"<root-id>"}
{"file_type":"symlink","link_target_base64url":"<base64url>","path":"<logical-path>","root_id":"<root-id>"}
~~~

Special files make the inventory invalid. Symlink targets use unpadded RFC 4648
base64url and are never followed while inventorying. Entries sort by
`(root_id, path)`, roots sort by `root_id`, and each array is duplicate-free.
The sandbox ID equals the
access proof. Input and output roots are canonical, pairwise disjoint, and
together cover the optimizer's complete filesystem namespace; no third
readable or writable root exists. Pre- and post-generation output inventories
have byte-identical `output_roots` and differ only in `phase` and `entries`.
The input inventory is re-enumerated after generation and must remain
byte-identical. Candidate output roots are accessible only under the output
policy, not as immutable input roots. The runner inventories them immediately
before and after generation. Their concrete ref/fingerprint pairs are bound
after enumeration by the access proof; the pre-candidate policy binds only
their run-independent projection templates and MUST NOT contain a concrete
pre- or post-generation output inventory ref/fingerprint. Only differences represented by the
frozen candidate manifest and completely covered by
`factor-delta-validation/v1` may appear. An arbitrary writable root, an input
mutation, or an unaccounted output byte is `holdout_contaminated` or
`multiple_factors` as applicable.

The pre-candidate policy binds the exact candidate-independent tool-policy
template ref/fingerprint. After the sandbox exists, the access proof binds the
concrete `optimizer_tool_policy_ref`/fingerprint and proves its lossless
template projection. That policy permits only declared
tools, schemas, filesystem roots, and effects; network and
`external_side_effects` are denied unless a fixture-only exception is frozen
there. The runner enforces it and retains an exact ordered
`optimizer_tool_trace_ref`/fingerprint containing every optimizer observation,
tool call, arguments, result, error, and effect. No-tool generation binds the
canonical empty trace rather than omitting it. The trace is complete only when
the runner-observed call/result sequence and enforced policy agree; the runner
cannot emit `status: completed` otherwise.

The policy is exact RFC 8785 `optimizer-tool-policy/v1`:

~~~json
{"allowed_tools":[{"effects":["filesystem_read","filesystem_write"],"name":"<tool-name>","schema_fingerprint":"sha256:<hex>","schema_ref":"harnesses/candidates/<candidate-id>/tool-schemas/<tool-name>.json"}],"denied_tools":[],"external_side_effects":"deny","filesystem_roots":[{"access":"read_only","path":"<canonical-absolute-input-root>","role":"optimizer_input","root_id":"<input-root-id>"},{"access":"isolated_write","path":"<canonical-absolute-output-root>","role":"candidate_output","root_id":"<output-root-id>"}],"network":"deny","schema":"optimizer-tool-policy/v1","template_fingerprint":"sha256:<hex>"}
~~~

Tools sort by name, denied names lexically, roots by `(role, root_id)`, and
effects lexically; all arrays are duplicate-free. `template_fingerprint` equals
the frozen `optimizer-tool-policy-template/v1` bytes. `filesystem_write` is admitted only for the predeclared output
roots whose access is `isolated_write`; input roots remain `read_only`, and no
other output roots are writable. Unlisted tools, roots, and effects are denied. The trace is
exact RFC 8785 `optimizer-tool-trace/v1`:

~~~json
{"events":[{"arguments_fingerprint":"sha256:<hex>","arguments_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-events/000001-arguments.json","call_id":"<runner-call-id>","effects":[],"error_fingerprint":null,"error_ref":null,"kind":"tool_call","observation_fingerprint":null,"observation_ref":null,"result_fingerprint":null,"result_ref":null,"sequence":1,"tool":"<tool-name>"},{"arguments_fingerprint":null,"arguments_ref":null,"call_id":"<runner-call-id>","effects":[{"effect_fingerprint":"sha256:<hex>","effect_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-events/000002-effect-000001.json"}],"error_fingerprint":null,"error_ref":null,"kind":"tool_result","observation_fingerprint":null,"observation_ref":null,"result_fingerprint":"sha256:<hex>","result_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-events/000002-result.json","sequence":2,"tool":"<tool-name>"}],"optimizer_process_opaque_id":"<runner-opaque-id>","policy_fingerprint":"sha256:<hex>","policy_ref":"harnesses/candidates/<candidate-id>/optimizer-tool-policy.json","sandbox_instance_id":"<runner-opaque-id>","schema":"optimizer-tool-trace/v1"}
~~~

Each event has exactly those fields. `kind` is `observation`, `tool_call`, or
`tool_result`. An `observation` has one non-null observation ref/fingerprint
pair and null call, tool, arguments, result, and error fields with empty
`effects`. A `tool_call` has non-null call, tool, and arguments fields, null
observation/result/error fields, and empty `effects`. A `tool_result` has
non-null call and tool fields, null observation/arguments fields, exactly one
non-null result or error ref/fingerprint pair, and the complete ordered
`effects` array. Each effect object has exactly `effect_ref` and
`effect_fingerprint`; every present ref/fingerprint binds exact retained bytes.
Sequence starts at one and is contiguous, calls and results join one-to-one by
`call_id`, and observed effects equal the policy. The input inventory's `tool_policy_fingerprint`, the
access proof's optimizer-tool-policy fingerprint, and the trace policy
fingerprint are identical.

Before generation, run the same exact and semantic-derivative leakage checks
over every optimizer input entry, every candidate-output prestate entry, and
every delivered optimizer message. After
generation, repeat them over those surfaces, every entry in the complete
optimizer tool trace, and every candidate-output entry. The access proof's pre/post leakage
fingerprints bind those two complete `semantic-leakage-review/v1` artifacts.
The runner may emit `status: completed` only after input equality, output-delta
coverage, policy/trace completeness, and a clear post-generation review are
proved. When `holdout_evidence` is non-null, missing, stale, `leak`, or
`uncertain` evidence first triggers the durable exposure transition below and
then returns `holdout_contaminated`; it is never merely a failed local run. On
the non-holdout route there is no global exposure authority to mutate: retain
the local leakage evidence and return `status: invalid_environment` with
`status_reason: historical_leakage`. That route MUST NOT execute a holdout
claim or registry transition.

Before any candidate-generation process can read an input or receive a
message, choose a unique `generation_attempt_id`. When `holdout_evidence` is
non-null, acquire
`.partition-freeze.lock`, render the exact optimizer-policy bytes that will be
supplied to the process, and set `optimizer_policy_fingerprint` to their
SHA-256. Construct the exact RFC 8785 pending bytes below and compute
`pending_fingerprint = SHA-256(exact pending bytes)` before any write:

~~~json
{"candidate_id":"<candidate-id>","cycle_id":"<cycle-id>","exposure_registry_id":"<registry-id>","generation_attempt_id":"<generation-attempt-id>","optimizer_policy_fingerprint":"sha256:<hex>","pre_candidate_policy_fingerprint":"sha256:<hex>","schema":"optimizer-exposure-intent/v1","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"]}
~~~

This global `optimizer-exposure-intent/v1`, its registry ID, lock, sentinels,
and semantic holdout target are the `holdout_intent` route and are
required only when `holdout_evidence` is non-null. For a non-holdout comparison,
the registry and lock roots are not applicable and no global record is created.
Instead the candidate directory contains closed exact RFC 8785
`{"candidate_id":"<candidate-id>","cycle_id":"<cycle-id>","generation_attempt_id":"<generation-attempt-id>","optimizer_policy_fingerprint":"sha256:<hex>","pre_candidate_policy_fingerprint":"sha256:<hex>","schema":"candidate-generation-intent/v1"}`
bytes exactly at
`harnesses/candidates/<candidate-id>/generation-intents/<generation-attempt-id>.json`,
which is the access proof's canonical `pending_ref`. Create-new and fsync that
file before the optimizer receives any message or readable root. Its digest is
the access proof's `pending_fingerprint`, and the sealed attempt evidence
closure includes the exact file under role `generation_intent`; holdout target
fields remain null. Both routes retain one attempt identity without fabricating
holdout authority.

The pending policy fingerprint equals the candidate-generation access proof's
`optimizer_policy_fingerprint`; both hash the same canonical
`optimizer-policy/v1` bytes defined above. Authorized discovery/development
inputs remain separate context messages and never alter that policy payload.

The remaining mutex, holdout-key, sentinel, cohort-intent, and
global clearing steps in this subsection apply to the `holdout_intent` route
only. The non-holdout route ends its intent work after the local
`candidate-generation-intent/v1` becomes durable and resumes directly at the
candidate-generation runner; it MUST NOT execute any global step below.

Both arrays are complete, sorted, and duplicate-free for the frozen cohort.
Before the first global sentinel, create-new and fsync the exact holdout pending
preimage at atlas-local
`partitions/optimizer-intents/<pending-digest-hex>.pending.json`; its digest must
equal the pending fingerprint. This private frozen copy is the sole recovery
source and is never optimizer-readable.
While still holding the partition mutex, first atomically create one immutable
`pending_sentinel` per source identity at
`optimizer-intent-sentinels/<holdout-key>/<pending-digest-hex>.json`, with exact
RFC 8785 `{"pending_fingerprint":"sha256:<hex>","schema":"optimizer-intent-pending-sentinel/v1","source_identity_fingerprint":"sha256:<hex>"}` bytes.
The sentinel is the sole durable per-identity intent record. Reservation and
generation gates scan that directory and join every row to the one cohort
intent; an orphan sentinel blocks. Only after all sentinels are durable may the compiler atomically
create the one immutable cohort intent at
`<holdout_lock_root>/optimizer-intents/<pending-digest-hex>.pending.json`.
Sentinels cover exactly the intent identity array. The access proof and both
leakage reviews bind the one cohort `pending_fingerprint`, so every identity is
cleared by the same attempt evidence.
If a crash leaves a partial or complete sentinel set before cohort-intent
publication, recovery reacquires the partition mutex, resolves the exact frozen
pending preimage from the atlas-local intent, verifies its digest and every
existing sentinel, create-news any missing deterministic sentinel, and publishes
that same cohort intent before release. If the preimage is unavailable or any
sentinel differs, recovery proves the optimizer never launched and removes only
the exact dead-attempt sentinel set; otherwise it stops `holdout_contaminated`.
After the complete pending intent and sentinel set is durable, release the
partition mutex before launching the optimizer. A later leakage transition
reacquires that mutex; no path recursively acquires a lock it still holds.
Required ordering is: release partition mutex before optimizer launch.

After generation and both complete clear leakage reviews, construct the exact
RFC 8785 clear bytes below:

~~~json
{"candidate_generation_access_proof_fingerprint":"sha256:<hex>","candidate_generation_evidence_closure_fingerprint":"sha256:<hex>","candidate_generation_evidence_closure_ref":"optimizer-attempts/<pending-digest-hex>/closure.json","candidate_harness_fingerprint":"sha256:<hex>","candidate_id":"<candidate-id>","cycle_id":"<cycle-id>","generation_attempt_id":"<generation-attempt-id>","pending_fingerprint":"sha256:<hex>","schema":"optimizer-cleared/v1","source_identity_fingerprints":["sha256:<hex>"]}
~~~

A clear writer recursively copies the access proof, contexts, rendered policy,
frozen holdout target, inventories, generation effects, tool policy/trace and payload preimages, both
leakage reviews, every leakage surface preimage, and candidate output bytes
under the private global attempt directory. It emits exact RFC 8785
`candidate-generation-evidence-closure/v1` bytes:

Before any copy, apply the same retention gate as semantic discovery to the
complete transitive set. Credentials and private tool outputs are never copied
globally. Other sensitive preimages require explicit bounded authorization.
Scrubbing records the raw digest and retained projection separately only when
the leakage proof remains exact; otherwise do not publish clear evidence,
durably mark the affected identities `optimizer_exposed`, and return
`holdout_contaminated`.

~~~json
{"candidate_id":"<candidate-id>","closure_inventory":[{"dependency_kind":null,"fingerprint":"sha256:<hex>","ref":"access-proof.json","role":"access_proof"}],"cycle_id":"<cycle-id>","generation_attempt_id":"<generation-attempt-id>","pending_fingerprint":"sha256:<hex>","schema":"candidate-generation-evidence-closure/v1","source_identity_fingerprints":["sha256:<hex>"]}
~~~

The exact top-level fields are those displayed. `closure_inventory` is sorted
by `(role, ref)`, has unique refs, and admits `access_proof`,
`candidate_output`, `generation_effect`, `generation_intent`, `holdout_target`, `leakage_review`,
`leakage_surface`, `derivation_evidence`, `optimizer_context`, `optimizer_input`, `optimizer_policy`,
`pre_candidate_policy`, `tool_payload`, `tool_policy`, and `tool_trace`.
Any recursively referenced asset without a primary role uses `dependency` and
sets nonempty `dependency_kind` to the referring field name; primary entries
set it null. This covers comparison implementations, generation runners,
factor selection, partition/selection/retirement evidence, manifests, and
evaluator assets without adding a role per field. Derivation-evidence assets
and their dependencies are copied and verified. The inventory contains every copied asset exactly once. The source
identity array is sorted and duplicate-free and equals both pending and clear
records. Every recursive ref
resolves within that immutable directory; no atlas-local ref remains.
A clear marker is atomically created beside its pending file at
`<pending-digest-hex>.cleared.json`. It matches only when cycle, candidate,
generation attempt, and complete source identity array equal the pending record,
`pending_fingerprint` hashes those exact pending bytes and equals both path
digest stems, and the evidence closure resolves and verifies transitively. Its
review and access proof attempt and pending fields equal the clear marker. The
copied access proof's candidate, cycle, optimizer-policy, and pre-candidate-policy
fields equal the pending intent. It clears only that attempt. Any pending intent without its exact
matching clear blocks the source identity as `source_contaminated`; a later
retry or another candidate cannot clear it, so crashes fail closed. On
`leak` or `uncertain`, do not clear the intent: first publish the durable
`optimizer_exposed` partition claim and then return `holdout_contaminated`.
Pending and cleared markers are global evidence, not a new store or campaign
protocol, and are never hidden in an atlas-local namespace.

The clear marker's access-proof and candidate-harness fingerprints equal the
copied closure assets. Reservation, candidate metadata, and the final root entry
repeat those exact fingerprints; substituting a later proof or harness under
the same administrative IDs is `holdout_contaminated`.

Use holdout only after candidate fingerprints freeze. An active holdout never
enters training data. When deliberately consumed, retire it from holdout and
replace it with an untouched group before another optimization cycle.

Retirement never edits the fingerprinted chart or an earlier root in place.
Before retirement, seal exact RFC 8785 `holdout-cycle-completion/v1` bytes
containing the reservation fingerprint and one sorted row per reserved arm with
candidate/comparison IDs plus exact EER and runs ref/fingerprint pairs. The
union of those sealed runs must realize every reserved chart/repeat/harness
tuple exactly once per comparison; tuple identity is `(comparison_id,
chart_fingerprint, repeat_id, harness_fingerprint)`. A missing pair or tuple
blocks retirement. Before sealing, copy each exact EER and runs file into the
static successor-owned `holdout-retirements/evidence/cycles/<cycle-id>/`
namespace, recursively copy every EER/runs dependency, and fsync the complete
tree; runtime directories are never transitive refs. A sealed reference mapping
maps every embedded canonical runtime or prior-root ref to its static snapshot
pair. It is closed exact RFC 8785
`holdout-retirement-reference-mapping/v1` bytes:
`{"entries":[{"snapshot_fingerprint":"sha256:<same-hex>","snapshot_mode":"<mode>","snapshot_ref":"holdout-retirements/evidence/cycles/<cycle-id>/<candidate-id>/dependencies/<snapshot-key-digest-hex>","source_fingerprint":"sha256:<hex>","source_mode":"<same-mode>","source_ref":"<normalized-runs-reports-or-roots-ref>"}],"schema":"holdout-retirement-reference-mapping/v1"}`.
Entries sort by `source_ref`, are duplicate-free, preserve fingerprints and
exact modes, and derive each snapshot path digest from the complete mapping
key preimage
`{"schema":"holdout-retirement-snapshot-key/v1","snapshot_mode":"<mode>","source_fingerprint":"sha256:<hex>","source_mode":"<same-mode>","source_ref":"<normalized-runs-reports-or-roots-ref>"}`.
The preimage explicitly excludes `snapshot_ref`; its SHA-256 suffix is
`<snapshot-key-digest-hex>`, which is inserted afterward. `<mode>` is the exact
regular-file mode admitted by the source closure, without a narrower retirement
whitelist, and source/snapshot modes are equal. Source refs may originate under `runs/`, `reports/`, or an
archived `roots/` prefix. They
cover every distinct transitive ref embedded in the copied EER, runs rows, and
their dependencies, including `runs/`, `reports/`, and
`roots/<prior-root-digest-hex>/` refs. The snapshot ref resolves inside the
successor closure. Missing, extra, conflicting, or recursively unmapped refs
block retirement.
Its closed payload is
`{"arms":[{"candidate_id":"<candidate-id>","comparison_id":"<comparison-id>","eer_fingerprint":"sha256:<hex>","eer_ref":"holdout-retirements/evidence/cycles/<cycle-id>/<candidate-id>/EER-v1.yaml","reference_mapping_fingerprint":"sha256:<hex>","reference_mapping_ref":"holdout-retirements/evidence/cycles/<cycle-id>/<candidate-id>/reference-mapping.json","runs_fingerprint":"sha256:<hex>","runs_ref":"holdout-retirements/evidence/cycles/<cycle-id>/<candidate-id>/runs.jsonl"}],"reservation_fingerprint":"sha256:<hex>","schema":"holdout-cycle-completion/v1"}`.
Arms sort by candidate ID with unique candidate/comparison IDs and equal the
reservation arm set exactly; each EER/runs pair resolves and accounts its
reserved tuples.
Write the RFC 8785 canonical bytes of each marker at
`holdout-retirements/markers/<marker-digest-hex>.json`:

~~~json
{"chart_fingerprints":["sha256:<hex>"],"consumption_purpose":"evaluation","cycle_completion_fingerprint":"sha256:<hex>","cycle_completion_ref":"holdout-retirements/evidence/<completion-digest-hex>.json","prior_root_fingerprint":"sha256:<hex>","reservation_fingerprint":"sha256:<hex>","reservation_ref":"holdout-retirements/evidence/<reservation-digest-hex>.json","schema":"holdout-retirement/v1","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"],"training_authorization_fingerprint":null,"training_authorization_ref":null}
~~~

`consumption_purpose` is exactly one of `evaluation` or `training`; the example
shows evaluation. Evaluation requires both training-authorization fields null.
Training requires both non-null and resolving exact human approval bytes bound
to a canonical principal identity, the selected charts/groups, and the explicit
training purpose; the emulator cannot self-authorize. Before writing the marker, copy the reservation's exact bytes
to the static content-addressed `reservation_ref`, require its filename and
fingerprint to agree, and include it in every successor closure that contains
the marker. The cycle-completion pair likewise resolves the complete sealed
arm/report set and is included transitively. The identity array is the exact sorted, duplicate-free union of
the retired charts' `source_identity_fingerprints` in the named prior root and
equals the identity set bound by the copied reservation's global lock evidence;
the chart and group arrays equal that same reservation and prior-root cohort.
All three arrays are byte-lexicographically sorted and duplicate-free. The marker
filename digest is SHA-256 of those exact bytes. Maintain immutable index
snapshots as RFC 8785 bytes under
`holdout-retirements/snapshots/<snapshot-digest-hex>.json`:

Training approval bytes are closed exact RFC 8785
`holdout-training-authorization/v1`:

~~~json
{"authorized_chart_fingerprints":["sha256:<hex>"],"authorized_source_group_fingerprints":["sha256:<hex>"],"consumption_purpose":"training","principal_identity_fingerprint":"sha256:<hex>","principal_identity_ref":"principals/<digest-hex>.json","schema":"holdout-training-authorization/v1"}
~~~

Both arrays equal the marker arrays, are sorted and duplicate-free, and the
principal resolves the human owner under the canonical identity rules.

~~~json
{"markers":[{"fingerprint":"sha256:<hex>","ref":"holdout-retirements/markers/<digest-hex>.json"}],"schema":"holdout-retirement-index/v1"}
~~~

`markers` is sorted by `ref`, duplicate-free, and transitively contains every
effective marker. The empty snapshot has an empty array. The mutable
`holdout-retirements/current.json` pointer contains exactly the RFC 8785 bytes
`{"fingerprint":"sha256:<hex>","ref":"holdout-retirements/snapshots/<digest-hex>.json","schema":"holdout-retirement-pointer/v1"}`;
the referenced snapshot digest, filename, and fingerprint must agree. The
pointer is outside prior closures. The
next root binds the current immutable snapshot and each effective marker through
`partition_policy` and recursive closure. When finalizing any root and before
its first run or report, copy its complete exact closure under
`roots/<root-digest-hex>/`, preserving relative paths and bytes. Reports cite
that archived root, and subordinate refs resolve from the archived root
directory rather than the live atlas root. Later roots never mutate an archived
root or any asset it references.

When no retirement index exists, the first selecting root with a holdout
creates both an immutable empty snapshot and `current.json`; otherwise it
preserves and binds the existing current snapshot. The pointer is mandatory
even when there are no retirements. A root without holdout charts may omit both
only when it is not a retirement successor. A retirement successor that removes
the last holdout retains the updated `retirement_index` and every effective
marker in its closure so deferred training evidence remains resolvable.

Before acquiring either validation lock, compute—but do not publish—the exact
canonical `holdout-use/v1` bytes from the already-frozen root, paired cohort,
candidate manifests, chart repeats, and holdout-only identity/group sets. Its
SHA-256 is the active reservation fingerprint used by any disjoint-advance
witness below. This computation has no dependency on the pending/clear gate or
live retirement pointer; those gates decide whether the precomputed bytes may
later be published, not what their identity is.

Before every selecting run, acquire `.partition-freeze.lock`, then the
retirement-index update lock in that fixed global order. Every path that needs
both locks uses this order and releases them in reverse. Revalidate the exact global
claim bytes against the root snapshots, resolve the current pointer, and require
its target snapshot fingerprint to equal the root's bound snapshot or admit one
exact `retirement-snapshot-disjoint-advance/v1` witness. That witness proves the
current index is an append-only extension, every prior marker is byte-identical,
and every added marker's source groups/identities are disjoint from the active
reservation and selected cohort. Any overlap, removal, or changed prior marker
makes the root stale; a disjoint completed cycle does not abort an active one.
The witness is exact RFC 8785 bytes at
`runs/<run-group-id>/retirement-disjoint-advance.json`:
`{"active_reservation_fingerprint":"sha256:<hex>","added_markers":[{"canonical_ref":"holdout-retirements/markers/<digest-hex>.json","fingerprint":"sha256:<hex>","snapshot_ref":"runs/<run-group-id>/retirement-disjoint-assets/root/holdout-retirements/markers/<digest-hex>.json","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"]}],"current_snapshot_canonical_ref":"holdout-retirements/snapshots/<digest-hex>.json","current_snapshot_fingerprint":"sha256:<hex>","current_snapshot_ref":"runs/<run-group-id>/retirement-disjoint-assets/root/holdout-retirements/snapshots/<digest-hex>.json","predecessor_snapshot_fingerprint":"sha256:<hex>","predecessor_snapshot_ref":"roots/<root-digest-hex>/holdout-retirements/snapshots/<digest-hex>.json","schema":"retirement-snapshot-disjoint-advance/v1"}`.
While holding both locks, copy and fsync the exact current snapshot and every
added marker beneath the displayed run-local closure root while preserving
their canonical relative layout. Recursively copy every added marker's
reservation, cycle-completion, and non-null training-authorization dependency
under the same root, preserving canonical relative refs and byte identity; the
closure is invalid if any dependency is missing. Embedded snapshot refs resolve within that
root; equality checks use `canonical_ref`, while offline reads use
`snapshot_ref`. The
predecessor ref resolves the archived root-bound snapshot. No witness or report
consults a later live retirement path.
Added markers sort by canonical ref and are unique; nested arrays are sorted and unique;
the current snapshot equals the predecessor marker set plus exactly these
markers. Every added row's source groups and identities equal its referenced
marker exactly, so the marker's prior-root and reservation derivation is the
identity preimage for this witness; no caller-supplied identity list is
admitted. All added identities/groups are disjoint from the active reservation
and selected cohort.
While still
holding both locks, enumerate every regular, non-symlink
`optimizer-intent-sentinels/<holdout-key>/*.json`. Each
sentinel's pending fingerprint must resolve one cohort pending intent and the
complete matching source-identity array; an orphan sentinel is reconciled only by an
exact matching cleared closure or stops `source_contaminated`. Only after the
sentinel domain is complete, recognized, and duplicate-free may the gate
require each common pending fingerprint's exact matching `.cleared.json` and the complete
transitive evidence closure defined above. A malformed file, unrecognized
path, mismatched cohort, dangling closure, or unresolved
optimizer intent stops with `source_contaminated` before reservation. Only
after this complete pending/clear gate passes may the writer use the already
precomputed canonical cycle-reservation bytes.

Each successful gate seals exact RFC 8785
`optimizer-clear-validation/v1` bytes at
`runs/<comparison-id>/optimizer-clear-validation-<phase>.json` in every pair's
already-reserved run group, where phase is `pre_reservation` for this gate and
`pre_actor` for the repeated gate:
`{"cycle_id":"<cycle-id>","phase":"pre_reservation","rows":[{"candidate_id":"<candidate-id>","clear_fingerprint":"sha256:<hex>","clear_ref":"runs/<comparison-id>/optimizer-clear-evidence/pre_reservation/<candidate-id>/clear.json","evidence_closure_fingerprint":"sha256:<hex>","evidence_closure_ref":"runs/<comparison-id>/optimizer-clear-evidence/pre_reservation/<candidate-id>/closure.json","generation_attempt_id":"<generation-attempt-id>","pending_fingerprint":"sha256:<hex>","pending_ref":"runs/<comparison-id>/optimizer-clear-evidence/pre_reservation/<candidate-id>/pending.json","reference_mapping_fingerprint":"sha256:<hex>","reference_mapping_ref":"runs/<comparison-id>/optimizer-clear-evidence/pre_reservation/<candidate-id>/reference-mapping.json","sentinel_fingerprints":["sha256:<hex>"],"sentinel_refs":["runs/<comparison-id>/optimizer-clear-evidence/pre_reservation/<candidate-id>/sentinels/<holdout-key>.json"],"source_identity_fingerprints":["sha256:<hex>"]}],"schema":"optimizer-clear-validation/v1"}`.
Before releasing the mutex, copy and recursively verify the exact global
pending, clear, sentinel, and evidence-closure bytes into those run-local refs.
The reference-mapping pair resolves exact RFC 8785 `sealed-ref-mapping/v1`
bytes containing every transitive canonical ref embedded in those copied bytes
and its run-local snapshot ref/fingerprint. Mappings sort by canonical ref,
are unique and complete; offline resolution substitutes only through this
sealed map, so the copied clear marker's `optimizer-attempts/...` closure ref
never consults the live registry.
Its closed payload is
`{"mappings":[{"canonical_ref":"optimizer-attempts/<pending-digest-hex>/closure.json","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"runs/<comparison-id>/optimizer-clear-evidence/<phase>/<candidate-id>/closure.json"}],"schema":"sealed-ref-mapping/v1"}`;
no other fields or mapping row shapes are admitted.
Rows sort by candidate ID; every array is sorted and duplicate-free; ref and
fingerprint arrays are same-length ordered pairs. The rows cover every
enumerated cohort pending/sentinel exactly once, and every clear/closure joins
the same candidate, attempt, pending fingerprint, identity set, and cycle ID.
The validation top-level cycle, every pending/clear/access-proof embedded cycle,
and the final root `comparison_policy.cycle_id` are equal. An
unresolved attempt cannot be represented as a successful validation. Every
pair-local artifact covers the complete cycle candidate set but owns only refs
beneath that comparison's run group. Every holdout execution and its pairwise
EER bind its own two phase artifacts; offline
validation therefore replays both gates without consulting mutable registry
state.

Acquire every user-global group lock in
sorted key order with payloads that bind that precomputed fingerprint, then
durably publish the exact precomputed bytes at the atlas-local reservation ref.
Release the retirement lock and then the partition lock only after the
reservation, locks, snapshots, and validation bytes are durably present. If
lock acquisition or reservation publication is interrupted, every created
global lock remains fail-closed; an absent local reservation never makes that
identity available. Human resolution may remove an incomplete pre-exposure
attempt only after proving that no semantic read, optimizer generation, or
actor handoff occurred.
Claim writers therefore cannot expose or reclassify
a group between revalidation and reservation. A stale
root therefore remains auditable but is ineligible for selection until a new
pre-candidate policy and candidate cycle restart from the advanced snapshot;
rebinding only the final root cannot restore eligibility. Record the partition-snapshot fingerprint
in every selecting run and report. For a root with no holdout,
partition-snapshot, validation, and reservation fields are absent rather than
invented. A group named by the current index is inactive and cannot be reused
as holdout.

While holding the retirement-index lock, write one run-group-local RFC 8785
`partition-validation/v1` artifact with exactly:

~~~json
{"current_pointer_snapshot_fingerprint":"sha256:<hex>","current_pointer_snapshot_ref":"runs/<run-group-id>/current-pointer-snapshot.json","disjoint_advance_fingerprint":null,"disjoint_advance_ref":null,"exposure_registry_id":"sha256:<hex>","resolved_snapshot_fingerprint":"sha256:<hex>","resolved_snapshot_ref":"roots/<root-digest-hex>/holdout-retirements/snapshots/<digest-hex>.json","root_contract_fingerprint":"sha256:<hex>","root_snapshot_fingerprint":"sha256:<hex>","run_group_id":"<run-group-id>","schema":"partition-validation/v1","storage_domain_id":"sha256:<hex>"}
~~~

The writer copies the exact observed `holdout-retirements/current.json` bytes to
the run-local immutable pointer snapshot before releasing the lock. Its ref,
fingerprint, filename, and exact bytes agree. The writer resolves the copied
pointer bytes and requires their target ref/fingerprint to equal the root-bound
snapshot or the current pair in the bound disjoint-advance witness before
emitting the artifact. Later live-pointer replacement cannot
change sealed run evidence. `resolved_snapshot_fingerprint`,
`root_snapshot_fingerprint`, and the EER `partition_snapshot_fingerprint` are
identical when the pointer has not advanced. The disjoint-advance pair is null
in that case and non-null exactly for the admitted monotonic extension; then
`resolved_snapshot_fingerprint` is current while `root_snapshot_fingerprint`
remains the root-bound predecessor. In that admitted branch every selecting
run and EER sets `partition_snapshot_fingerprint` to the resolved current
snapshot and `resolved_snapshot_ref` equals the disjoint witness's run-local
`current_snapshot_ref`; the validation artifact retains the distinct root predecessor and
sealed disjoint-advance witness. Store it
at `runs/<run-group-id>/partition-validation.json`; runs and EER bind that ref
and exact fingerprint. This runtime proof is distinct from the static
`partition-claim-validation/v1` asset.

Once per comparison cycle and before its first actor sees a holdout, atomically
create the exclusive RFC 8785 `holdout-use/v1` reservation at
`runs/<cycle-id>/holdout-reservation.json` with exactly:

~~~json
{"arms":[{"baseline_harness_fingerprint":"sha256:<hex>","candidate_harness_fingerprint":"sha256:<hex>","candidate_id":"<candidate-id>","chart_repeats":[{"chart_fingerprint":"sha256:<hex>","repeat_ids":["<repeat-id>"]}],"comparison_id":"<comparison-id>"}],"atlas_instance_id":"sha256:<hex>","chart_fingerprints":["sha256:<hex>"],"cycle_id":"<cycle-id>","exposure_registry_id":"sha256:<hex>","root_contract_fingerprint":"sha256:<hex>","schema":"holdout-use/v1","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"],"storage_domain_id":"sha256:<hex>"}
~~~

`arms` contains the full frozen candidate set and is sorted by `candidate_id`;
each arm's `chart_repeats` contains every selected chart exactly once, sorted by
chart fingerprint. Each chart's `repeat_ids` is sorted, duplicate-free, and has
the exact deterministic or stochastic count frozen by policy. Every arm's
complete `chart_repeats` bytes are identical to every other arm and to the
root's singular `comparison_policy.paired_cohort.selected_chart_repeats` array;
candidates cannot choose
different repeat IDs. All three top-level fingerprint arrays are sorted and
duplicate-free. The top-level chart, group, and identity arrays contain only
selected holdout charts: charts are the holdout subset of `chart_repeats`,
groups are their exact group set, and identities are their exact identity
union. Discovery/development regression guards remain in every arm's execution
cohort but never enter reservation, lock, consumption, or retirement domains.
Every acquired global group lock binds that same holdout-only identity set.
Candidate IDs and comparison IDs are each unique,
and every selecting holdout chart/group in the frozen cycle appears. The
reservation filename cycle ID equals the payload and the root's
`comparison_policy.cycle_id`; `atlas_instance_id` equals the recomputed root
instance identity. IDs use disjoint syntax before any directory creation:
`cycle_id` starts `cycle-`, `run_group_id` starts `run-`, and `comparison_id`
starts `cmp-`; the remainder obeys the ordinary component grammar. A value with
the wrong prefix is invalid, so the three owners cannot alias without a shared
reservation index. Each pair keeps its own EER and run group under
that one cycle reservation. Later arms/repeats validate and reuse the exact
bytes and matching group locks; they do not create them again. Holdout use
outside compare mode is unsupported. Bind that atlas-root-relative reservation
ref and fingerprint in every affected run. Any existing or incomplete
reservation makes the group unavailable outside the named cycle and fails
closed. On completion, create a content-addressed `holdout-retirement/v1`
marker referencing the reservation, consumed groups, chart fingerprints,
purpose, and prior root; incorporate that marker in the next immutable
snapshot. Prefer discovery/development for standalone examples; do not spend a
holdout casually.

The frozen execution cohort is exactly the expansion of each arm's comparison
ID and per-chart repeat list across the baseline and named candidate harness
fingerprints. Exactly one execution row
consumes each tuple. Missing, extra, or duplicate tuples are
`invalid_environment`; retries require a new comparison identity and cannot be
selectively appended to the frozen cohort.

Before creating the reservation, atomically create-new
`reports/<comparison-id>/` as the comparison-identity reservation for every
pair, then create `runs/<comparison-id>/`. A
comparison ID that already exists anywhere in this atlas, including an earlier
cycle, is invalid and is never reused or replaced. Likewise, `cycle_id` owns
its reservation directory for the lifetime of the atlas. Partial creation
before actor exposure is removed only by the same failed attempt; after
exposure it remains fail-closed for human resolution.

Constrain every path-derived identifier as specified by the contract profile
before use, and prove each resolved destination remains under its owner root
before create, replace, or removal. Derive the
cross-atlas holdout key as SHA-256 of the exact UTF-8 tuple
`"emulator-holdout/v1" NUL source_identity_fingerprint` for every individual
source identity in the group. Before reading any message, tool, attachment, or
other semantic source byte, either obtain a caller-attested complete identity
set or derive it completely from physical discovery metadata, then atomically
publish the applicable claims. Retain and fingerprint the attestation or
physical envelope; a merely asserted incomplete list is not holdout authority.
The caller route uses exact RFC 8785
`{"attester_identity_fingerprint":"sha256:<hex>","attester_identity_ref":"principals/<principal-digest-hex>.json","complete":true,"issuance_id":"<opaque-issuance-id>","schema":"identity-completeness-attestation/v1","source_group_fingerprints":["sha256:<hex>"],"source_identity_fingerprints":["sha256:<hex>"],"source_state_fingerprint":"sha256:<hex>","source_state_ref":"identity/source-states/<digest-hex>.json"}`
bytes. The physical route retains the exact non-semantic discovery envelope.
That envelope is closed RFC 8785 `physical-identity-completeness/v1` bytes:
`{"complete":true,"physical_snapshot_fingerprint":"sha256:<hex>","physical_snapshot_ref":"semantic-discovery/snapshots/<digest-hex>.json","schema":"physical-identity-completeness/v1","source_group_fingerprints":["sha256:<hex>"],"source_identity_descriptors":[{"identity_kind":"root_session","identity_ref":"seq:<adapter>:<root-session-id>"}],"source_identity_fingerprints":["sha256:<hex>"]}`.
Arrays are sorted and duplicate-free, descriptor fingerprints recompute the
identity array, and both identity/group sets equal the chart split exactly;
missing physically discoverable aliases make `complete: true` invalid.
The source-state pair binds the immutable physical snapshot/corpus selection
and alias-bearing metadata observed for issuance. Reuse against any different
source-state fingerprint is invalid; a newly discovered alias requires a new
attestation and exposure reconciliation.
`source-state/v1` is closed exact RFC 8785
`{"alias_identity_fingerprints":["sha256:<hex>"],"corpus_snapshot_fingerprint":"sha256:<hex>","corpus_snapshot_ref":"semantic-discovery/snapshots/<digest-hex>.json","schema":"source-state/v1","source_file_fingerprints":["sha256:<hex>"]}`.
Arrays are sorted and duplicate-free and are recomputed from the complete bound
physical snapshot and non-semantic alias metadata; omission or mutable source
selection invalidates the attestation.
Every session-derived chart binds exactly one per-chart physical or attested
`identity_completeness_ref`/fingerprint; pure designed charts use
`not_applicable` with both fields null. After chart fingerprints freeze, the
root and pre-candidate policy bind the aggregate
`identity-completeness-manifest/v1` pair defined by the contract profile. A
chart MUST NOT bind that aggregate pair because the manifest contains the chart
fingerprint. Claims, locks, and reservations revalidate the aggregate manifest
and each referenced per-chart identity set before publication.

For registry-backed compilation, when completeness cannot be established
without semantic source bytes, acquire
the global partition-freeze lock, ensure every physically known identity has an
exposed claim (publishing `discovery_exposed` only for an unclassified
identity), perform the bounded semantic read while still
holding the lock, derive all newly visible stable aliases, and publish
`discovery_exposed` claims for them before releasing it. That group is
permanently holdout-ineligible; existing development/optimizer status remains
unchanged. If a newly discovered alias already has a
selection lock/reservation but no consumption marker, atomically replace its
`holdout_unexposed` claim with `discovery_exposed`; the selector's mandatory
pre-actor revalidation then fails. If its consumption marker exists, the alias
is already consumed and cannot be reused as holdout. A later semantic read is
admitted only after the exact retirement marker and successor snapshot prove
that identity's holdout group retired with `consumption_purpose: evaluation |
training`; while holding the partition lock, atomically replace its claim with
`discovery_exposed` and retain both consumption and retirement evidence
permanently. The identity can then be discovery/development or authorized
training input but can never become holdout again. Without that retirement
evidence, stop with
`source_contaminated`; any other incompatible claim also stops. Claims never
transition from an exposed state back to holdout. This fallback makes the
unavoidable first read honest without pretending the alias was knowable.

Before chart compilation, resolve one private, writable
`storage_domain_root`. The atlas lives at
`<storage_domain_root>/emulators/<atlas-id>` and binds
`storage_domain_id = SHA-256("emulator-storage-domain/v1" NUL canonical-realpath-UTF-8)`.
It also binds
`atlas.instance_id = SHA-256("emulator-atlas-instance/v1" NUL storage_domain_id NUL canonical-atlas-root-realpath-UTF-8)`.
The instance ID is frozen in the root, reservation, canonical locks, and
consumption markers. Moving or copying a closure to another atlas root changes
the recomputed instance ID and makes it ineligible for execution; copied local
run/report directories cannot reuse a prior cohort.
Storage may follow `${CODEX_HOME:-$HOME/.codex}` or an explicit private root,
but storage location never scopes exposure authority. All selection-capable
roots use the single user-global registry at canonical-realpath
`<os-account-home>/.codex/emulator-holdout-locks`, where `os-account-home` is
resolved from the effective OS account record (for example
`getpwuid(geteuid())`) and never from caller-controlled `HOME` or `CODEX_HOME`.
Bind it as `exposure_registry_root`, and
bind exact persistent `registry-filesystem-identity/v1` bytes at
`<exposure_registry_root>/registry-filesystem-identity.json`:
`{"filesystem_uuid":"<host-filesystem-uuid>","home_directory_file_id":"<stable-host-file-id>","registry_directory_file_id":"<stable-host-file-id>","schema":"registry-filesystem-identity/v1","shared_host_backed":true}`.
The runtime derives these values from the effective account's host-backed home
mount and verifies them from a second independent host process. It rejects a
container/mount namespace whose same pathname resolves to a different
filesystem identity or whose host sharing cannot be proved. Create the asset
once with create-new semantics and fsync its directory; later compilers require
byte equality. Then bind
`exposure_registry_id = SHA-256("emulator-exposure-registry/v1" NUL canonical-realpath-UTF-8 NUL registry-filesystem-identity-fingerprint)`.
`holdout_lock_root` equals that registry root. Changing `CODEX_HOME`, atlas
location, caller storage root, or process `HOME` therefore cannot create a fresh exposure
namespace. Before any holdout read, the actual compiler runtime MUST prove that
the bound filesystem-identity asset matches the host-backed mount and that
it can create, lock, atomically replace, and fsync a probe file under that exact
registry, then remove only the probe. When filesystem policy denies the probe,
request the smallest user-approved permission grant for the exact registry root;
never substitute an atlas-local or repository-local authority. If the grant is
declined or the probe still fails, or if prior exposure outside the registry
cannot be excluded for the candidate/optimizer contexts in scope, stop with
`source_contaminated` before reading semantic session bytes. An absent but
creatable registry is not unavailable. Any holdout, including a designed
holdout, requires the registry. A pure designed root with no holdout may proceed
without it.
For any source identity whose semantic exposure outside this registry cannot be
excluded—including pre-registry sources and newer sessions reachable through
ordinary Seq or file access—and for every designed holdout, first bind exact
RFC 8785 `holdout-exposure-attestation/v1` bytes:

~~~json
{"atlas_instance_id":"sha256:<hex>","attester_identity_fingerprint":"sha256:<hex>","attester_identity_ref":"principals/<principal-digest-hex>.json","baseline_harness_fingerprint":"sha256:<hex>","factor_selection_fingerprint":"sha256:<hex>","factor_selector_identity_fingerprint":"sha256:<hex>","factor_selector_identity_ref":"principals/<selector-digest-hex>.json","holdout_blind":true,"independent_of_candidate_generation":true,"no_prior_baseline_harness_exposure":true,"no_prior_candidate_or_evaluator_exposure":true,"no_prior_factor_selector_exposure":true,"schema":"holdout-exposure-attestation/v1","source_identity_fingerprints":["sha256:<hex>"],"source_kind":"designed"}
~~~

The sorted, duplicate-free identity array is complete for the group and the
human attester is holdout-blind and independent of candidate generation.
`source_kind` is exactly `pre_registry`, `registry_bypass_risk`, or `designed`.
By canonical `person_id`, the attester differs from the factor selector, every
candidate author/attester, every correction-human or reviewed-pattern reviewer
for the covered charts, and every covered designed-chart author. A collision
makes the attestation invalid regardless of its booleans.
The baseline and factor-selection fingerprints equal the exact frozen selection
that admits this legacy source; changing either requires a new attestation from
an independently blind principal and never reuses stale evidence.
The selector identity equals the factor-selection asset, and the attestation is
invalid unless the attester can directly attest that selector had no prior
semantic access to the covered source identities.
`no_prior_baseline_harness_exposure` means no selected source content, correction,
outcome, or evaluator interpretation was used to author, tune, choose, or review
the frozen baseline harness. The
attestation ref/fingerprint is evaluator-only and appears in the
pre-candidate policy and final-root `holdout_exposure_attestations` arrays.
Those arrays cover every selected holdout requiring evidence exactly once,
including pure designed charts even though their `session_provenance` is null.
For `source_kind: pre_registry`, the session-provenance legacy pair references
the same attestation; other kinds never misuse that legacy slot. False,
unknown, incomplete, missing, or self-authored
outside-registry exposure evidence makes every affected source ineligible for
holdout; it may be discovery/development only. Creating a new registry never
resets exposure history.
The attestation may be omitted only when owner evidence proves every semantic
read since source creation was mediated by this exact registry; source creation
time alone is never that proof.
Claims and canonical
locks bind the exposure-registry ID; reservations, partition validations,
selecting runs, and reports bind both the registry and storage-domain IDs. The
canonical lock is `<holdout_lock_root>/<hex>.lock`, so corpus membership or a
local group rename cannot give the same source group a second identity. Acquire
multiple keys in sorted digest order with an atomic create-new operation that
fails if the key already exists; never use check-then-create. The lock contains
the exact RFC 8785 bytes
`{"atlas_instance_id":"sha256:<hex>","cycle_id":"<cycle-id>","exposure_registry_id":"sha256:<hex>","holdout_key":"<hex>","pre_candidate_policy_fingerprint":"sha256:<hex>","reservation_fingerprint":"sha256:<hex>","root_contract_fingerprint":"sha256:<hex>","schema":"holdout-lock/v1","source_identity_fingerprint":"sha256:<hex>"}`.
The filename, holdout key, source identity, and registry ID agree. An existing lock is reusable only when all
those fields exactly match the current cycle reservation; otherwise acquisition
fails. Any incomplete lock or reservation remains fail-closed for human
resolution. It is never removed automatically; a human may authorize removal
only after retained intent, query, optimizer, and actor evidence proves that no
semantic read, generation, or actor exposure occurred.
After successful acquisition, copy each lock's exact bytes into the run group's
atlas-relative `runs/<run-group-id>/holdout-locks/<hex>.lock` and bind only
those snapshots as EER/run refs. The atlas-relative lock-validation artifact
maps each snapshot fingerprint to its canonical absolute lock path and frozen
identity. Its exact RFC 8785 payload is:

~~~json
{"atlas_instance_id":"sha256:<hex>","cycle_id":"<cycle-id>","exposure_registry_id":"sha256:<hex>","locks":[{"canonical_lock_path":"<absolute-path>","holdout_key":"<hex>","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"runs/<run-group-id>/holdout-locks/<hex>.lock","source_identity_fingerprint":"sha256:<hex>"}],"reservation_fingerprint":"sha256:<hex>","root_contract_fingerprint":"sha256:<hex>","schema":"holdout-lock-validation/v1","source_group_fingerprints":["sha256:<hex>"],"storage_domain_id":"sha256:<hex>"}
~~~

`locks` contains every and only lock required by the run's selected holdout
groups, sorted by `holdout_key`, with unique keys, identities, paths, and refs;
`source_group_fingerprints` is the sorted, duplicate-free exact selected
holdout group set from the reservation; no other fields are admitted. Each
snapshot's exact bytes must equal its
canonical lock and must bind the same cycle, reservation, root, registry,
atlas instance, holdout key, and source identity as this validation asset. Canonical paths are
evaluator-only runtime facts, not report refs. Store the artifact at
`runs/<run-group-id>/holdout-lock-validation.json` and bind its exact
fingerprint in every affected run and EER.

Immediately before the first actor receives any holdout byte, acquire
`.partition-freeze.lock` and then `.retirement-index.lock` in the same global order,
reread `current.json`, and require its resolved immutable snapshot to equal the
root-bound retirement snapshot or the exact current snapshot in the sealed
partition-validation disjoint-advance witness. Revalidate that witness and
require no later pointer advance. Then rerun the complete optimizer pending/clear
gate above and revalidate every claim, lock, reservation, and consumption state
against the frozen cycle. Any newly unresolved optimizer intent stops with
`source_contaminated` before actor handoff. Seal the `pre_actor` optimizer-clear
validation artifact in every pair's run group under the same mutex before
proceeding. Only after every revalidation passes
may the runner atomically create one immutable global
`<holdout_lock_root>/<hex>.consumed.json` per identity. Its exact RFC 8785 bytes
are
`{"atlas_instance_id":"sha256:<hex>","cycle_id":"<cycle-id>","exposure_registry_id":"sha256:<hex>","holdout_key":"<hex>","reservation_fingerprint":"sha256:<hex>","root_contract_fingerprint":"sha256:<hex>","schema":"holdout-consumption/v1","source_identity_fingerprint":"sha256:<hex>"}`.
The filename, key, identity, registry, atlas instance, cycle, root, and
reservation must agree.
Keep both locks held while the first actor packet or mount is handed to the
fresh actor, and release them in reverse order only after every marker is
durable and that actor has acknowledged loading the exact actor-input
fingerprint. That acknowledgment is the first holdout exposure boundary. A
handoff failure leaves the identities consumed and yields
`invalid_environment`; it does not reopen them. A concurrent retirement
advance before lock acquisition makes the root stale and the run
`invalid_environment` unless it is the same validated disjoint extension;
overlapping or later advances are never ignored.
Later arms/repeats in the same cycle validate and reuse the exact markers; any
other cycle is permanently blocked. These non-lock markers are the global
completion/consumption authority. Lock cleanup never removes them, and a lock
without a marker remains active or incomplete and fails closed.
Copy their exact bytes to
`runs/<run-group-id>/holdout-consumption/<digest-hex>.json` for each pair and
bind those snapshots in every affected run and EER.

Before the fallback semantic read, claim writers check the canonical holdout
lock, reservation, and consumption marker for every identity known before the
read while holding `.partition-freeze.lock`. An active or incomplete selection
lock/reservation on a pre-read known identity makes the source unavailable and
the semantic read does not occur. A stable alias learned only by that bounded
read is instead handled by the post-read rule above: publish or atomically
replace its claim as `discovery_exposed`, invalidate any unconsumed selection,
and stop. The post-read discovery is never reinterpreted as a read that did not
occur. Thus a discovery writer cannot silently contaminate a group after the
selector releases the partition lock but before first actor exposure.

Before any managed semantic session read, acquire the exclusive global
`<holdout_lock_root>/.partition-freeze.lock`, validate the complete sorted
identity-key set before any semantic source read, stage all new claims, then
publish them before releasing the lock. Create or validate
`<holdout_lock_root>/<hex>.partition.json` for every individual source identity.
Its file contains exactly the RFC 8785 canonical UTF-8 bytes of:

~~~json
{"exposure_evidence_fingerprint":null,"exposure_evidence_ref":null,"exposure_registry_id":"sha256:<hex>","exposure_status":"holdout_unexposed","partition":"holdout","schema":"emulator-partition-claim/v1","source_identity_fingerprint":"sha256:<hex>"}
~~~

For discovery or development, `partition` is that exact value and
`exposure_status` is respectively `discovery_exposed` or
`development_exposed`. Candidate-generation leakage uses partition
`development` and exposure status `optimizer_exposed`; these are the only
admitted status/partition combinations. Both exposure-evidence fields are null
for a claim created without semantic discovery. A new claim caused by semantic
discovery has both non-null and binds the exact
query-independent `semantic-discovery-identity-exposure/v1` asset whose source
identity equals this claim. One null field, an unresolved asset, or a mismatched
identity or registry makes that new-claim variant invalid. An already
`discovery_exposed`, `development_exposed`, or `optimizer_exposed` claim with
both fields null remains
valid when semantic discovery later occurs only if the same exact identity-
exposure asset exists and the semantic-discovery gate validates the claim plus
marker union described in Section 2. The marker augments evidence; it does not
replace or downgrade the permanent exposed claim. Query-specific
`semantic-discovery-query/v1` and `semantic-discovery-result/v1` assets are
provenance and cannot replace or narrow the already-published exposure set.
Aggregate group fingerprints never enter this claim schema; group eligibility
is derived from its complete member identities. The filename's
holdout-key hex, identity fingerprint, and registry ID must agree with the
claimed identity and exposure registry. Aggregate group identity is deliberately
absent: claims record exposure of each stable identity, so later alias discovery
does not invalidate already published discovery claims. Claims are finalized before compilation
and before the pre-candidate policy, except for the locked discovery-only alias
fallback above; the policy binds their final fingerprints. Claims never point
back to that policy. The atlas copies each canonical claim's
exact bytes to the atlas-relative
`partitions/claims/<holdout-key>.partition.json` and binds those snapshot refs
and fingerprints in the pre-candidate policy and root closure. For every
required discovery marker, including one supplementing a legacy exposed claim
whose evidence pair is null, it also copies the canonical identity-exposure
bytes to `partitions/identity-exposures/<holdout-key>.json`. It then creates
an atlas-relative `partition-claim-validation/v1` asset mapping every snapshot
to its canonical holdout key, global claim location, exposure-registry ID, and
identical fingerprint. The validation asset is evaluator-only and is bound by
the final root, runs, and EER; external absolute claim paths are runtime facts,
not closure refs. Its RFC 8785 payload is exactly
`{"claims":[{"canonical_claim_path":"<absolute-path>","holdout_key":"<hex>","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"partitions/claims/<hex>.partition.json"}],"exposure_registry_id":"sha256:<hex>","identity_exposures":[{"canonical_ref":"semantic-discovery/identity-exposures/<holdout-key>.json","fingerprint":"sha256:<hex>","holdout_key":"<hex>","snapshot_ref":"partitions/identity-exposures/<holdout-key>.json"}],"schema":"partition-claim-validation/v1"}`
with both arrays sorted by `holdout_key`; identity-exposure rows cover every
required marker exactly once and provide the only closure-local
resolution mapping. No other fields are admitted. An existing
byte-identical compatible claim is reused. An existing claim for
another partition, or any prior
discovery/development exposure when the new claim is holdout, is
`holdout_contaminated`. Record every known identity's partition exposure before
the compiler, author, actor, or optimizer can read that group; the locked
discovery fallback publishes newly learned aliases before releasing the read.
Claims are not deferred until partition freeze or execution. If any key is
incompatible before exposure, remove only staged or published claims created by
that attempt while still holding the global lock; compatible pre-existing
claims are never removed. The only replacement exceptions are atomic
`holdout_unexposed` to `discovery_exposed` for discovery fallback and
retirement-backed consumed exposure, plus `holdout_unexposed` to
`optimizer_exposed` for optimizer leakage. All preserve
exposure and invalidate the stale holdout snapshot.
The `optimizer_exposed` replacement is therefore explicitly admitted.
Bind only atlas-relative claim snapshots in the
pre-candidate policy, final root closure, runs, and EER, plus their
atlas-relative validation artifact.

If either semantic leakage review reports `leak` or `uncertain` involving a
holdout identity, acquire the user-global `.partition-freeze.lock` before
returning. This pre-root mutex exists before a final atlas root or reservation
and does not require either one or any reservation-derived identity lock.
While holding it, atomically replace every affected
`holdout_unexposed` claim with its durable `optimizer_exposed` exposure marker,
and create equivalent markers for newly identified aliases before releasing
the mutex. A compatible exposed claim is retained; no exposed state may return
to `holdout_unexposed`. Only after every marker is durably present may the run
return `holdout_contaminated`. A failed or partial transition blocks all
affected identities as `source_contaminated`; it never leaves them eligible for
selection.

Retirement-index updates use the ordinary exclusive
`<holdout_lock_root>/.retirement-index.lock`. After acquiring it, reread
`current.json`, union the new
markers with that current immutable snapshot, write the successor snapshot,
atomically replace the pointer, and release the update lock. A stale expected
pointer or failed atomic replace aborts without publishing a successor; two
writers may not derive successors independently from the same snapshot.

Filesystem and process separation are sufficient for the initial accidental
leakage threat model; do not build a cryptographic broker.

## 8. Freeze harness bundles

Before candidate generation, first sample, write, and fsync the complete
evaluator-only `randomness-cohort-commitment/v1` described below. Then write and
fingerprint the pre-candidate policy asset containing its exact pair plus the selecting chart commitments,
partition snapshot, model/runtime configuration, repeat counts, randomness
matching, improvement rule, protected dimensions, candidate budget, and
the exact pre-generation `factor-selection/v1` ref/fingerprint and comparison-
implementation ref/fingerprint that will aggregate results and choose the
recommendation. It binds the actor-readable-surface derivation-implementation
ref/fingerprint used after execution. The optimizer-visible policy is derived
only from the already-bound factor-selection asset; it is not copied into a
second authority field.
When `holdout_evidence` is non-null it additionally binds one canonical
`holdout-semantic-target/v1` ref/fingerprint. Its exact projection contains the
sorted selected chart fingerprints and, for each chart, complete actor-visible
pre-cut state, prompt, source-byte refs/fingerprints, chart semantics, hidden
action, correction, recovery, and outcome projections. The target is frozen
before any optimizer starts; both leakage reviews, the access proof, final root,
and global attempt closure repeat it unchanged.

The policy is closed exact RFC 8785 `pre-candidate-policy/v1` bytes:

~~~json
{"actor_readable_surface_derivation_fingerprint":"sha256:<hex>","actor_readable_surface_derivation_ref":"comparison/actor-readable-surface-validator.json","baseline_harness_fingerprint":"sha256:<hex>","baseline_harness_ref":"harnesses/baseline/harness-manifest.json","candidate_budget":1,"candidate_generation_commitments":[{"candidate_author_principal_identity_fingerprint":"sha256:<hex>","candidate_author_principal_identity_ref":"principals/<digest-hex>.json","candidate_id":"candidate-1","candidate_metadata_template_fingerprint":"sha256:<hex>","candidate_metadata_template_ref":"harnesses/candidates/candidate-1/candidate-metadata-template.json","generation_attempt_id":"<generation-attempt-id>","optimizer_inventory_template_fingerprint":"sha256:<hex>","optimizer_inventory_template_ref":"harnesses/candidates/candidate-1/inventory-template.json","schema":"candidate-generation-commitment/v1","tool_policy_template_fingerprint":"sha256:<hex>","tool_policy_template_ref":"optimizer/tool-policy-template.json"}],"comparison_implementation_fingerprint":"sha256:<hex>","comparison_implementation_ref":"comparison/implementation.json","factor_selection_fingerprint":"sha256:<hex>","factor_selection_ref":"partitions/factor-selection.json","generation_runner_fingerprint":"sha256:<hex>","generation_runner_ref":"comparison/candidate-generation-runner.json","holdout_evidence":null,"holdout_exposure_attestations":[],"improvement_rule":{"chart_outcome":"strict_majority_of_paired_valid_repeats","maximum_targeted_regressed_charts":0,"minimum_targeted_improved_charts":1,"require_all_required_charts_determinate":true,"schema":"paired-stochastic-improvement-rule/v1","tie_disposition":"insufficient_evidence"},"model_runtime_configuration_fingerprint":"sha256:<hex>","model_runtime_configuration_ref":"comparison/model-runtime.json","non_hard_regression_tolerance":{"cost":{"input_tokens":0,"latency_ms":0,"output_tokens":0},"residual_dimensions":{},"reward_channels":{},"schema":"non-hard-regression-tolerance/v1"},"protected_dimensions":[],"provenance_derivation_fingerprint":"sha256:<hex>","provenance_derivation_ref":"evaluators/provenance-derivation.json","randomness_cohort_commitment_fingerprint":"sha256:<hex>","randomness_cohort_commitment_ref":"comparison/randomness-cohort-commitment.json","randomness_matching":{"mode":"match_when_controllable","schema":"randomness-matching/v1"},"repeat_policy":{"deterministic":1,"stochastic":3},"runtime_surface_derivation_fingerprint":"sha256:<hex>","runtime_surface_derivation_ref":"comparison/runtime-surface-derivation.json","schema":"pre-candidate-policy/v1","selected_charts":[{"chart_fingerprint":"sha256:<hex>","chart_id":"<chart-id>","partition":"development","required":true,"split_group":"<group-id>"}],"semantic_evaluator_fingerprint":null,"semantic_evaluator_ref":null,"session_provenance":null,"targeted_chart_rules":[{"chart_fingerprint":"sha256:<hex>","factor":"question_policy","targeted":true}]}
~~~

The already-materialized commitment has exact RFC 8785
`randomness-cohort-commitment/v1` bytes:

~~~json
{"arm_schedule":[{"candidate_id":"candidate-1","chart_fingerprint":"sha256:<hex>","first_arm":"baseline","repeat_id":"<repeat-id>"}],"rows":[{"actor_seed":null,"actor_seed_control":"unavailable","chart_fingerprint":"sha256:<hex>","environment_seed":17,"environment_seed_control":"sampled","failure_schedule_fingerprint":"sha256:<hex>","failure_schedule_ref":"comparison/failure-schedules/<chart-hex>-<repeat-id>.json","repeat_id":"<repeat-id>"}],"schema":"randomness-cohort-commitment/v1"}
~~~

Rows sort by `(chart_fingerprint, repeat_id)`, are complete and unique for the
frozen paired cohort, and record every controllable draw and sampled schedule.
`arm_schedule` sorts by `(candidate_id, chart_fingerprint, repeat_id)`, covers
every pair tuple exactly once, and freezes baseline-first or candidate-first
before execution. Actual start order must match; alternation/randomization is
therefore evidence, not a post-run claim.
Fixed or sampled controls require a concrete seed; `unavailable` requires null.
The schedule pair is both null when none is sampled and otherwise resolves
exact bytes already durable before candidate generation. The commitment is
evaluator-only and actor/optimizer-inaccessible. The final root, both arms,
execution rows, EER, and comparison repeat its exact ref/fingerprint; no later
draw selection or schedule substitution is admitted.
`randomness_matching` is the closed
`{"mode":"match_when_controllable","schema":"randomness-matching/v1"}`
object and is the exact projection of root
`stochastic_evidence.matched_randomness_when_available: true`. It applies to
every paired chart/repeat: fixed or sampled controls must match; unavailable
controls use the frozen repeat cohort without invented equality.

The policy's `improvement_rule` equals
`comparison_policy.stochastic_evidence.improvement_rule` byte-for-byte. It is
the sole stochastic adoption rule; the final root cannot rename, project, or
replace it after outcomes.

The arrays are sorted by their displayed identities and duplicate-free. The
top-level factor-selection pair is mandatory for every paired comparison,
whether or not a holdout is selected, and equals the root partition-policy
pair. The provenance-derivation pair is frozen before candidate generation,
repeated by the final root comparison policy, and equals every leakage review;
post-output derivation selection is `evaluator_contaminated`. The optional
semantic-evaluator pair equals every semantic leakage review in the
cycle.
The displayed `candidate_budget: 1` is illustrative. Its normative domain is an
integer from one through three, equal in factor selection, optimizer-visible
policy, pre-candidate policy, reservation arm count, and final candidate set.
`candidate_generation_commitments` has exactly `candidate_budget` rows, keyed
by candidate ID, each with exactly the displayed
`candidate-generation-commitment/v1` fields. The access proof repeats the
candidate ID, author principal, optimizer-inventory-template pair, tool-policy-template
pair, and candidate-metadata-template pair exactly. The referenced template is
closed pre-generation `candidate-metadata-template/v1` bytes containing only
candidate ID, baseline harness fingerprint, selected factor, author principal,
hypothesis, expected delta, falsifier, and declared root-qualified changed-path
objects. It contains
no candidate harness, access-proof, factor-delta, or final metadata fingerprint,
so the dependency graph is acyclic. Final candidate metadata is authored after
generation and binds this template pair plus the generated evidence. Its
candidate, baseline, factor, author, hypothesis, expected delta, falsifier, and
declared changed-path values equal the referenced template byte-for-byte. The
factor-delta validation's complete actual changed-file set equals the sorted
declared `changed_paths` as `(root_id, path)` objects; arrays sort by that pair
and are duplicate-free. A missing, extra, root-ambiguous, or rewritten path is
`comparison_drift`.
Each candidate commitment also freezes exactly one globally unique
`generation_attempt_id`, repeated by factor selection, pending intent, access
proof, clear marker, candidate metadata, and the matching final-root
`comparison_policy.candidate_harnesses` entry. A second completed or
cleared attempt for the same `(cycle_id, candidate_id)` is
`holdout_contaminated`; retries require a new cycle and untouched holdout.
`targeted_chart_rules` covers every selected chart exactly once. Each closed
row has exactly `chart_fingerprint`, `factor`, and boolean `targeted`, as
required by the contract profile. It is frozen before candidate generation;
both targeted true or false values are admitted and false regression guards are
preserved. The factor and result cannot depend on outcomes.
`non_hard_regression_tolerance` is the required frozen closed object defined by
the contract profile and covers every supported reward, residual, cost, and
latency channel; missing channels have zero tolerance.
`session_provenance` is non-null for every session-derived comparison regardless
of partition and otherwise null. Its closed value is
`{"identity_completeness_fingerprint":"sha256:<hex>","identity_completeness_ref":"identity/completeness-manifest.json","legacy_exposure_attestation_fingerprints":[],"legacy_exposure_attestation_refs":[],"partition_claim_validation_fingerprint":"sha256:<hex>","partition_claim_validation_ref":"partitions/partition-claim-validation.json","partition_claims":[{"fingerprint":"sha256:<hex>","ref":"partitions/claims/<holdout-key>.partition.json"}],"schema":"session-provenance/v1"}`.
The legacy arrays are sorted same-length ref/fingerprint pairs and contain every
pre-registry group attestation admitted to holdout. A pre-registry
discovery/development source may keep both empty and is
therefore permanently holdout-ineligible. The final
root's `session_provenance` ref/fingerprint resolves exact bytes equal to this
complete object; the root never embeds a competing inline shape. Non-compare
session roots author that same referenced asset directly from their root source
and partition evidence. These provenance fields are not hidden inside holdout-only evidence.
For a pure designed holdout, `session_provenance` is null and identity
completeness remains `not_applicable`; holdout selection alone never makes
session identity-completeness fields non-null. Any recursive session source,
holdout or not, requires the non-null session object.
`holdout_evidence` is non-null exactly when any selected chart is holdout and is
then closed exact RFC 8785 bytes within the policy:

~~~json
{"factor_selection_fingerprint":"sha256:<hex>","factor_selection_ref":"partitions/factor-selection.json","holdout_semantic_target_fingerprint":"sha256:<hex>","holdout_semantic_target_ref":"comparison/holdout-semantic-target.json","partition_claim_validation_fingerprint":"sha256:<hex>","partition_claim_validation_ref":"partitions/partition-claim-validation.json","partition_claims":[{"fingerprint":"sha256:<hex>","ref":"partitions/claims/<holdout-key>.partition.json"}],"retirement_index_fingerprint":"sha256:<hex>","retirement_index_ref":"holdout-retirements/snapshots/<digest-hex>.json","selection_intent_snapshots":[{"fingerprint":"sha256:<hex>","ref":"partitions/selection-intents/<holdout-key>.json"}],"selection_intent_validation_fingerprint":"sha256:<hex>","selection_intent_validation_ref":"partitions/selection-intent-validation.json"}
~~~

The access proof's scalar `holdout_target_ref` and
`holdout_target_fingerprint` repeat exactly this object's
`holdout_semantic_target_ref` and `holdout_semantic_target_fingerprint`; they do
not hash or repeat the whole nested object. `selection_intent_snapshots` equals
the root's complete sorted per-identity array and `retirement_index` equals the
root partition policy pair.
There is no competing `partition_snapshot_ref`: that semantic identity is the
canonical `retirement_index_ref`. The scalar `holdout_semantic_target_ref` is
copied unchanged to the access proof.
Every ref/fingerprint resolves exact bytes, all
selected charts and candidate commitments are complete, and no extra field is
allowed. The root policy fingerprint is valid only after this closed payload
and every transitive ref validate.

The policy also carries sorted `candidate_generation_commitments` keyed by
candidate ID. Each binds a run-independent
`optimizer-inventory-template/v1` describing logical input/output entries,
tool policy, and allowed root roles without absolute sandbox paths or
`sandbox_instance_id`. The concrete candidate inventory must be the
deterministic instantiation of its template; candidate-specific sandboxes may
differ without sharing a concrete fingerprint.
The exact template is RFC 8785
`{"candidate_id":"<candidate-id>","input_projection":{"entries":[{"file_type":"regular","mode":"100644","path":"<logical-path>","root_id":"<root-id>","sha256":"sha256:<hex>"}],"root_roles":["optimizer_input"],"schema":"optimizer-input-projection/v1","tool_policy_template_fingerprint":"sha256:<hex>"},"poststate_projection":{"entry_policy":"generation_effects_exact","phase":"post_generation","root_roles":["candidate_output"],"schema":"candidate-output-projection/v1"},"prestate_projection":{"entries":[],"phase":"pre_generation","root_roles":["candidate_output"],"schema":"candidate-output-projection/v1"},"schema":"optimizer-inventory-template/v1"}`.
`input_projection` removes `sandbox_instance_id`, maps `input_roots` to their
frozen roles, proves the concrete tool policy instantiates the frozen template,
replaces `tool_policy_fingerprint` with that template fingerprint under the
`tool_policy_template_fingerprint` key, and changes the schema tag. `prestate_projection` performs
the analogous output-root mapping and requires exact empty entries.
`poststate_projection` first proves concrete entries equal the complete
generation effects, then replaces those entries with the literal
`generation_effects_exact` policy. These three deterministic
template-to-concrete projections must equal the candidate's frozen template;
no rename, phase, or field is implicit. The access proof repeats the template
ref/fingerprint and the validator rejects any other delta.
The pre-candidate policy contains this inventory template and the independent
tool-policy template only. Concrete optimizer input, output-prestate,
output-poststate, and tool-policy refs/fingerprints are created and bound by the
post-generation access proof; they cannot be required by or written back into
the already-frozen pre-candidate policy.
Do not expose that asset, its holdout fields, or its evaluator criteria to the
optimizer. Candidate generation receives a separate optimizer policy whose
semantic fields are exactly the deterministic projection frozen as
`factor-selection/v1.optimizer_visible_policy`, plus only the referenced
discovery/development inputs. Before candidate generation, require that object
to equal the subobject resolved through the pre-candidate factor-selection pair
exactly. The optimizer policy contains no
factor-selection ref or outer fingerprint, discovery/development evidence,
selector-principal identity, baseline or holdout fingerprint, or other outer
commitment digest. Policy-local ownership and tool fingerprints required to
interpret the allowed selectors and tools remain present.
The final root binds both exact policy refs and
fingerprints; candidate manifests cannot rewrite either snapshot.
The final root and each pairwise report repeat the same comparison
implementation identity.

Manifest every behavior-bearing root:

~~~json
{
  "schema": "emulator-harness-manifest/v1",
  "roots": [
    {"root_id": "user", "precedence": 0, "mount_path": ".", "path": "AGENTS.md", "file_type": "regular", "mode": "100644", "sha256": "..."},
    {"root_id": "repo", "precedence": 1, "mount_path": ".", "path": "skills/example/SKILL.md", "file_type": "regular", "mode": "100644", "sha256": "..."}
  ],
  "runtime_config": {
    "model": "...",
    "reasoning_effort": "...",
    "relevant_settings": {}
  }
}
~~~

Fingerprint the exact RFC 8785 JSON Canonicalization Scheme UTF-8 bytes.
The manifest file itself MUST contain exactly those canonical bytes, so its
exact-file closure SHA-256 and manifest identity are the same digest. Implicit global harness state
invalidates comparison.
Arm IDs, candidate IDs, and the selected factor are administrative comparison
metadata and MUST NOT appear in this behavior manifest or fingerprint. Each
entry repeats one declared `target.harness_roots` root ID, precedence, and mount
path exactly. Entries are sorted by `(precedence, root_id, path)` and
`(root_id, path)` is unique; roots materialize in ascending precedence and the
higher numeric precedence wins an effective-path collision. Precedence values
are unique across distinct root declarations; all entries from one root repeat
that root's same precedence.
Before materialization, probe and bind the runtime volume's case and Unicode
normalization semantics, compute an equivalence key for every effective path,
and reject duplicate keys. `Foo`/`foo` or normalization-equivalent names can
never alias one destination even when their contract strings differ.
After exact-path precedence is resolved, no winning effective path may be a
regular file or symlink ancestor of another winning path. Such
ancestor/descendant collisions are `invalid_environment`; runners never invent
replacement or directory-overlay semantics.
Every `path` is normalized, relative, nonempty, and non-escaping. Every
`mount_path` is `.` or a nonempty normalized POSIX-relative non-escaping path;
absolute paths, backslashes, and `..` segments are invalid. Before copying a
file, resolve the effective `mount_path/path` and require it to remain beneath
the isolated runtime root. A `file_type: regular` entry resolves relative to the manifest directory at
`files/<root-id>/<path>` and exact bytes/mode match the entry. This arm-local
layout lets baseline and candidate carry different bytes at the same logical
path without changing its runtime meaning.
The bundle also stores the exact RFC 8785 bytes of the manifest's
`runtime_config` object at manifest-relative `runtime-config.json`. Its digest
is the run's `runtime_fingerprint`; the archived asset ref and digest are
recorded in every execution. The actor runner must materialize that exact
closed behavior-bearing non-secret configuration. Credentials, tokens, secret
values, and their digests are forbidden from both the manifest and runtime
observation; the run binds only the sanitized non-secret credential descriptor
ref/fingerprint defined by EER-v1. A runtime-factor experiment may change only predeclared runtime
keys; otherwise baseline/candidate runtime fingerprints must be equal. The
runner implementation/version is recorded separately and must be equal across
arms. It is a run fact, not a selectable harness factor; changing it requires a
different experiment subject outside EC-v1.
Capture from an immutable snapshot or locked worktree. If the source cannot be
made immutable, perform a complete ordered second metadata-and-content scan
after capture and require byte-identical path, type, mode, link target, and
digest results before freezing the manifest; any drift restarts capture.
Reject any captured regular file with link count greater than one; EC-v1
harness manifests do not encode or recreate hard-link equivalence groups, so
silently materializing separate files would change harness behavior.
Source symlinks are resolved exactly once within that stable capture;
dangling links and loops are invalid. A symlink manifest entry records
`file_type: symlink`, its exact raw relative `link_target_base64url`, and the included
target entry; it omits regular-file mode/digest. The archive stores this
description as regular manifest bytes, and the isolated runtime recreates the
same link from decoded bytes only after proving its effective resolution remains beneath the
runtime root and reaches the bound target. Thus raw `readlink` and resolved-path
behavior are preserved, including non-UTF-8 targets. Encoding is unpadded RFC
4648 base64url of exact `readlink` bytes. A harness whose behavior observes symlink ownership,
timestamps, inode, link count, or other unbound `lstat` metadata is ineligible;
those observations are not silently claimed equivalent. A link that cannot be
safely recreated makes the harness ineligible rather than being silently
flattened.
A separately fingerprinted,
evaluator-only `harness-capture-provenance/v1` asset binds every source link
path, owning root ID, source-root path, raw-target base64url, and final resolved source
path, plus a complete walk of every declared source root. Its canonical
`roots` entries contain `root_id`, absolute source root, every regular or
symlink path with mode/digest and `included: true`; entries and paths are sorted
and unique. `excluded_paths` is an exact empty array: the first implementation
does not certify non-behavior by assertion. Every discovered regular or symlink
path is included in the manifest, and every manifest entry occurs in the inventory.
Missing, extra, or unaccounted behavior-bearing files invalidate baseline
capture. The provenance asset is included in the root
closure and the corresponding baseline/candidate root entry. That provenance
validates capture but is excluded from harness
identity and factor-delta comparison, so equivalent captures in different
worktrees have the same behavior fingerprint. The staged archive contains only
regular files; runtime materialization creates only manifest-declared internal
symlinks and regular files with bound bytes and executable modes. No materialized
bundle symlink may resolve back into the live harness. Absolute logical paths,
`..`, and duplicate normalized paths are invalid.
Every required directory must be derivable as a parent of a manifest entry.
Empty directories and directory ownership, timestamps, inode, link count, or
mode are not bound; a harness whose behavior depends on any such directory
observation is ineligible. Runtime parent-directory metadata is therefore not
part of the harness equivalence claim.
The final resolved source of every symlink must remain inside some declared
source root. When it crosses roots, provenance records both owning and target
root IDs and capture uses the target root's inventory entry. A target outside
all declared roots stops capture; there is no implicit host-path allowlist.

Candidate metadata:

~~~yaml
candidate:
  candidate_id:
  generation_attempt_id:
  candidate_metadata_template_ref:
  candidate_metadata_template_fingerprint:
  candidate_author_principal_identity_ref:
  candidate_author_principal_identity_fingerprint:
  baseline_harness_fingerprint:  # harness subject only
  candidate_harness_fingerprint: # harness subject only
  factor:
  candidate_generation_access_proof_ref:
  candidate_generation_access_proof_fingerprint:
  factor_delta_validation_ref:
  factor_delta_validation_fingerprint:
  semantic_delta_attestation_ref:  # null unless a mixed-owner file changes
  semantic_delta_attestation_fingerprint:
  hypothesis:
  changed_paths:
    - root_id:
      path:
  affected_chart_tags: []
  protected_chart_tags: []
  expected_delta:
  falsifier:
  limitations: []
~~~

Use exactly one semantic owner, though its implementation may span files that
jointly own that behavior. At most three candidates run in one cycle. Stage
candidates outside the live harness. Candidate and evaluator changes require
separate experiments.

EC-v1 candidates may change only the bytes of existing regular manifest files
and predeclared runtime-configuration values. Baseline and candidate manifest
path sets, entry types, executable modes, and symlink targets must be identical;
file add/delete/rename, mode changes, and symlink retargeting are prohibited by
the optimizer policy before generation. A candidate containing such a delta is
invalid for this experiment and cannot be recommended. This keeps non-byte
manifest changes out of `factor-delta-validation/v1` rather than inventing
uncontracted selectors for them. A changed regular entry must also win
precedence at its effective materialized path; changing only a shadowed entry
is an invalid no-op candidate and cannot satisfy the required-delta rule.

The pre-candidate policy enumerates exact root-qualified behavior-bearing path
pairs (`root_id`, logical `path`), runtime-configuration keys, and
deterministically derived runtime-surface fields owned by the selected factor.
Each path declaration also gives an exact structured selector for the bytes
owned by that factor and its evaluator-only ownership authority. A path
allowlist alone is not factor-locality.

Selectors are a closed array in the pre-candidate policy. Each is exactly one
of:

~~~json
{"kind":"whole_file","ownership_authority_fingerprint":"sha256:<hex>","ownership_authority_ref":"<static-ref>","path":"<logical-path>","root_id":"<root-id>","selector_id":"<selector-id>"}
{"end_anchor_base64url":"<base64url>","kind":"utf8_anchor_region","ownership_authority_fingerprint":"sha256:<hex>","ownership_authority_ref":"<static-ref>","path":"<logical-path>","root_id":"<root-id>","selector_id":"<selector-id>","start_anchor_base64url":"<base64url>"}
~~~

`ownership_authority_ref` is a normalized closure-relative static ref. IDs are
unique and selectors sort by `(root_id, path, selector_id)`. Base64url
uses the RFC 4648 URL-safe alphabet without padding and decodes to nonempty
UTF-8 bytes. For an anchor selector, each anchor occurs exactly once in both
baseline and candidate, the start precedes the end, and the owned half-open
region runs from the first byte of the start anchor to the first byte of the
end anchor. Regions in one file are nonoverlapping. Remove the ordered owned
regions from baseline and candidate; the remaining bytes must be identical.
Selected regions for one file are disjoint, and `whole_file` cannot be combined
with another selector for that file.
A `whole_file` selector is valid only when its authority asset attests exclusive
factor ownership of that file. These are the only selector and addressing
semantics in EC-v1.

After candidate freeze, one factor-delta validation asset per
candidate computes the complete byte-level baseline/candidate manifest diff,
requires at least one change, maps every changed byte, runtime key, and derived
runtime-surface field to exactly one predeclared selector or approved
derivation, and rejects uncovered changes. When a changed file
contains other semantic owners, the asset also binds a human
`semantic-delta-attestation/v1` covering every diff hunk and affirming that each
hunk implements only the selected factor. This attestation is an explicitly
permitted fourth validation input, is separately fingerprinted in candidate
metadata and the validation asset, and cannot widen the predeclared owner set
or selectors. Its attester is independent of candidate generation and has not
seen holdout chart contents, corrections, evaluator details, or outcomes; the
attestation binds that holdout-blindness declaration. The
matching `candidate_harnesses` root entry, candidate metadata, and pairwise EER
bind the same ref and fingerprint. A missing, incomplete, mismatched, or
out-of-factor delta is `multiple_factors` and cannot be recommended; one
candidate's validation never covers another candidate.

The attestation is exact RFC 8785:

~~~json
{"attester_identity_fingerprint":"sha256:<hex>","attester_identity_ref":"principals/<principal-digest-hex>.json","baseline_harness_fingerprint":"sha256:<hex>","candidate_harness_fingerprint":"sha256:<hex>","candidate_id":"<candidate-id>","factor":"<factor>","holdout_blind":true,"hunks":[{"baseline_end":0,"baseline_fingerprint":"sha256:<hex>","baseline_start":0,"candidate_end":0,"candidate_fingerprint":"sha256:<hex>","candidate_start":0,"factor_only_justification":"<nonempty-text>","path":"<logical-path>","root_id":"<root-id>","selector_ids":["<selector-id>"]}],"independent_of_candidate_generation":true,"ownership_authority_fingerprints":["sha256:<hex>"],"pre_candidate_policy_fingerprint":"sha256:<hex>","schema":"semantic-delta-attestation/v1"}
~~~

Hunk offsets are half-open byte ranges; a zero-length side represents an
insertion or deletion. Hunks sort by `(root_id, path, baseline_start,
candidate_start)`, never overlap, and cover every changed byte exactly once.
Each side fingerprint hashes the exact selected slice, and every `selector_ids`
array plus the ownership-authority fingerprint array is sorted and unique. Each
hunk maps only to selectors declared by the pre-candidate policy. The candidate,
baseline, factor, policy, owner authorities, and harness fingerprints equal the
candidate metadata and factor-delta asset. The attester principal is canonical
and differs by canonical person ID from every correction reviewer and the
`candidate_author_principal_identity` in candidate metadata/access proof;
it also differs from every selected designed-holdout author. Both independence
booleans are required true. Arbitrary bytes, an uncovered hunk, a mismatched authority, or an
attestation produced by candidate generation is `multiple_factors`.
This candidate_author-to-attester person-ID inequality is mandatory.

The validation asset is exact RFC 8785 `factor-delta-validation/v1`:

~~~json
{"baseline_harness_fingerprint":"sha256:<hex>","candidate_harness_fingerprint":"sha256:<hex>","candidate_id":"<candidate-id>","changed_files":[{"baseline_fingerprint":"sha256:<hex>","candidate_fingerprint":"sha256:<hex>","path":"<logical-path>","root_id":"<root-id>","selector_ids":["<selector-id>"]}],"factor":"<factor>","generation_attempt_id":"<generation-attempt-id>","owner_policy_fingerprint":"sha256:<hex>","owner_policy_ref":"comparison/pre-candidate-policy.json","runtime_config_changes":[{"baseline_value_fingerprint":"sha256:<hex>","candidate_value_fingerprint":"sha256:<hex>","key":"<key>"}],"runtime_surface_changes":[{"baseline_value_fingerprint":"sha256:<hex>","candidate_value_fingerprint":"sha256:<hex>","derivation_path_refs":[{"path":"<logical-path>","root_id":"<root-id>"}],"derivation_runtime_keys":["<key>"],"field":"<field>"}],"runtime_surface_derivation_fingerprint":"sha256:<hex>","runtime_surface_derivation_ref":"comparison/runtime-surface-derivation.json","schema":"factor-delta-validation/v1","semantic_delta_attestation_fingerprint":null,"semantic_delta_attestation_ref":null}
~~~

`changed_files` is the complete regular-file content-difference set sorted by
`(root_id, path)`; each `selector_ids` array is sorted, duplicate-free, and
contains every and only selector covering that file's differences. Runtime
arrays are the complete changed-key/field sets sorted by `key` and `field`;
value fingerprints hash the exact RFC 8785 value bytes, including `null`.
`derivation_path_refs` and `derivation_runtime_keys` are sorted and
duplicate-free, and each contains only approved changed paths or runtime keys.
At least one derivation input is present for every changed surface field. The two attestation fields are both null unless a mixed-owner
file changes, when both contain the exact attestation asset ref and fingerprint
bound by candidate metadata. `owner_policy_ref` and
`owner_policy_fingerprint` exactly equal the evaluator-only frozen
pre-candidate policy ref and `pre_candidate_policy_fingerprint` already bound
by the root and generation-access proof. `generation_attempt_id` equals the
candidate commitment, access proof, candidate metadata, and root candidate
entry. The validator receives that immutable
asset from the evaluator, never from candidate output; a stale, self-selected,
or ref/fingerprint-mismatched policy is `evaluator_contaminated`. No other
fields are admitted. The derivation ref/fingerprint names the immutable
evaluator-owned implementation already frozen by the pre-candidate policy. The
validator runs those exact bytes over the frozen baseline and candidate
manifests plus runtime configuration, recomputes every derived surface value,
and requires the resulting before/after fingerprints and complete changed-
field set to equal the asset. A path list without this executable,
fingerprinted recomputation is `evaluator_contaminated`.

## 9. Run both arms freshly

The baseline is the current harness frozen at an exact fingerprint, not the
historical session. Freeze candidates before holdout execution.

For every arm and repeat:

- use a fresh actor process or container for every arm and repeat;
- use an isolated worktree or read-only workspace;
- materialize only the selected harness bundle;
- supply only the actor packet;
- keep evaluator roots unmounted or inaccessible where possible;
- disable mutable memories unless memory is the selected factor; when it is,
  restore the same isolated frozen initial memory snapshot independently for
  every arm and repeat before applying the factor-local difference;
- record runtime identity, readable inventory, tool policy, and effect policy.

The exact actor contexts are compared pairwise after removing only the
`run_id` field. Role order and message count must match. Every remaining content
difference must occur exactly once in the candidate's existing
`factor-delta-validation/v1.runtime_surface_changes`, using a field such as
`actor_context.messages[<index>].content` and nonempty derivation refs to the
approved changed harness paths or runtime keys. Every other context byte is
equal. A system, developer, user, or history difference that is neither
run-local nor factor-derived is `comparison_drift`; a context fingerprint alone
cannot establish cross-arm equivalence.

Default normative instruction:

~~~text
Use the loaded harness. Given the supplied state, take exactly one consequential
next decision and return the required decision envelope. Do not speculate beyond
the supplied state. Stop after that decision.
~~~

Executable actors run to terminal state or a bounded stop while the environment
captures messages, actions, tool calls/results, mutations, tests, cost, and
termination.

Default repeats:

~~~text
exact-fidelity executable chart: one arm run after two identical reset proofs
normative or observational chart without reset: no reset proof
stochastic chart: three fresh runs per arm
uncontrolled actor nondeterminism: record actor_seed_control unavailable and use repeats
~~~

Alternate or randomize arm order. Blind residual judges to harness identity,
judge both A/B orders, and classify order disagreement as ambiguous.

## 10. Evaluate

Order is fixed:

~~~text
environment validity
actor output and action schema validity
exclusive support classification
hard oracles
required state assertions and state diff
trace invariants
protected dimensions
contracted reward channels
cost and latency
residual judgment
~~~

Preferred hard oracles:

~~~text
decision_class_required / decision_class_forbidden
fact_already_available
tool_called / tool_not_called
state_assert / file_diff_assert / side_effect_assert
schema_assert / budget_assert / terminal_assert
confirmation_before_side_effect
scope_assert / evidence_required_before_claim
~~~

Executable charts compare required state achieved, forbidden state absent,
allowed roots respected, tests passing, and protected state unchanged. Different
valid trajectories are allowed.

### Status mapping

~~~text
malformed actor output or action -> hard_fail
executable or judgeable + all required checks pass -> pass
executable or judgeable + hard oracle failure -> hard_fail
failed required state assertion -> hard_fail
failed trace invariant -> hard_fail
denied action -> hard_fail
attempted observed_only or unsupported transition -> unsupported_counterfactual
malformed, leaked, drifted, or unverifiable environment -> invalid_environment
runner failure unrelated to agent decision -> runtime_error
order-unstable or genuinely indeterminate result -> ambiguous
policy-excluded chart -> skipped
runner unavailable before actor start -> skipped with reason runner_unavailable
~~~

unsupported_counterfactual and invalid_environment are not agent defects and do
not count as promotion passes or failures.

### Candidate decision

Return `adopt`, `reject`, or `insufficient_evidence` exclusively through the
complete EER-v1 recommendation law. This reference contributes chart
eligibility, untouched-holdout inputs, stochastic observations, and claim caps;
it does not restate or independently decide adoption conditions.

Promotion is only an evidence strength: it means these conditions and every
included chart's realized claim eligibility support a separately authorized
adoption decision. A chart contributes no stronger claim than the weaker of its
declared class, maximum supported claim, and the authority actually proved by
that run. It never mutates
the live harness. Ties, unsupported required charts, evaluator disagreement,
access-proof gaps, or inadequate holdout coverage yield insufficient_evidence.
Apply the same total precedence rule as EER-v1 on every selecting surface.
This reference supplies selecting holdout inputs only: observational and other
non-selecting rows remain diagnostic. EER-v1 exclusively owns aggregation,
decisive-regression precedence, incomplete-coverage handling, and the exact
`adopt | reject | insufficient_evidence` disposition; do not reimplement that
law in atlas code.

Record paired_replay_delta, observed_association, regression, or
insufficient_evidence as the evidence relation, separately from the adoption
recommendation. Do not claim a causal mechanism from an uncontrolled comparison.

## 11. Export

Originating `run`, `mutate`, and `compare` modes emit chart-aware EER-v1 plus
runs.jsonl as specified in eer-v1.md. Originating `design` and `implement`
emit the contract-only EER-v1 with no runs artifact and may authorize only
contract-derived curriculum. `compare` additionally emits one
comparison.json per baseline/candidate pair; standalone `run` omits comparison
artifacts and uses an independent run-group directory. Explicit deferred
`mode: export` validates and binds that sealed originating EER and its
mode-correct nullable runs pair, then
emits only eligible datasets and `emulator-export-manifest/v1`; it never creates
or rewrites EER or runs evidence.
For compare, `<run-group-id>` is the comparison ID; for standalone run it is
the independent `run_group_id` recorded in every row and EER execution.

Preference rows require:

~~~text
direct preference authority
exact source-bound rejected action
fresh passing chosen action
hard-oracle pass
partition is discovery/development, or a holdout was explicitly retired for
this training use
authority stronger than model judgment alone
~~~

Rows exported from a deliberately retired holdout additionally bind the exact
`holdout-retirement/v1` marker, successor snapshot, and `training` retirement
purpose by ref and fingerprint. They also bind `successor_root_ref` and
`successor_root_fingerprint`; that root transitively contains the marker and
snapshot and sets `retirement_predecessor_root_fingerprint` to the marker's
`prior_root_fingerprint`. The deferred export
manifest repeats the same successor-root pair. Missing or mismatched retirement evidence keeps
the row ineligible.

Do not export a historical recovery as chosen unless separately re-executed or
objectively validated.

Trajectory rows require fresh executable runs, a valid reset fingerprint,
complete observable transition trace, hard-oracle results, no evaluator leakage,
and permitted data handling. Historical trajectories are not training
trajectories by default. A holdout-derived trajectory is eligible only after it
binds the exact retirement marker and successor snapshot with
`consumption_purpose: training`; evaluation-only retirement never authorizes a
trajectory training export.

Curriculum rows may record family, difficulty, tools, prerequisites, failure
cluster, fidelity, and supported claim. Every export retains chart and authority
provenance.

Counterexample rows require a fresh environment-valid mutation run, exact
mutation assignment, a reproducible minimized failing artifact, evaluator
evidence, and a chart whose partition is exactly discovery or development.
Active and retired holdouts are ineligible; every retirement and successor
field is null. Bind the external generator when one exists. For finite built-in enumeration, derive
`mutation_generator_fingerprint` from the chart fingerprint and complete
mutation declaration, including dimensions, interactions, laws, and shrink
strategies, exactly as specified by the contract profile. Both routes derive
`mutation_case_id` from the chart fingerprint, generator fingerprint, and exact
ordered assignment bytes under the same profile formula. A
historical failure alone is not an exportable counterexample row.

## Stop and rollback

Stop with the exact reason when the source is missing or contaminated,
attribution is ambiguous for the requested claim, historical material leaks,
the cut is invalid, reset is not repeatable, a fixture or dirty state is
unrecoverable, a transition is unsupported, comparison boundaries drift,
evaluator or holdout is contaminated, oracle authority is absent, residual
results remain ambiguous, or a candidate changes multiple factors.

Canonical reasons:

~~~text
source_not_found
source_contaminated
attribution_ambiguous
historical_leakage
invalid_cut
world_not_reconstructable
reset_not_repeatable
missing_fixture
unsupported_counterfactual
comparison_drift
evaluator_contaminated
holdout_contaminated
oracle_gap
contract_ambiguity
runner_unavailable
access_proof_unavailable_after_start
multiple_factors
insufficient_evidence
~~~

Rollback means: stop fresh actors, discard isolated candidate and reset
workspaces, and leave the live harness unchanged. Preserve sanitized private
source bundles and evaluation evidence by default for diagnosis. Credentials,
secret values, and private tool outputs are never copied into a bundle. If an
indispensable selected raw payload still contains other sensitive material,
require explicit retention authorization before copying it; without that
authorization, omit or scrub it and downgrade or stop when exact provenance can
no longer be supported. Delete any unauthorized sensitive temporary copy during
rollback while retaining non-sensitive diagnostics. A report recommendation
never performs rollback or adoption itself.

## First proof

The first normative pilot uses 5 to 20 real correction charts, at least two
holdout groups, exactly one human-selected factor, baseline plus at most three
candidates, three repeats per harness/chart, hard oracles first, and residual
judgment in both orders. The pilot may emit an `adopt` recommendation, but
application to the live harness is disabled. Rejection or
insufficient_evidence is success when trustworthy.

The first executable pilot uses one Git-backed task with known commit and
dependencies, deterministic tests/state assertions, no indispensable live
service, two identical reset fingerprints, historical suffix absent from actor
input, fresh baseline and candidate runs, state diff, and no historical trace
imitation.

The minimum proof is:

~~~text
five real normative correction charts, at least two frozen holdouts
one exact executable Git-backed chart
one frozen baseline and one factor-local candidate
fresh runs for both arms
a report capable of rejecting the candidate
~~~

No native expansion is admissible until at least five real charts and one fresh
comparison exist and the same missing domain-independent capability blocks at
least three unrelated real charts.

## Anti-platform constraints

Do not add campaigns, epochs, trial registration, lanes, leases, reveal state,
publication state, a global event store, cryptographic custody, recursive
optimizer loops, scalar-only promotion, or a totalized learned world model.
One comparison directory and ordinary content-addressed files are sufficient.
The first useful result is one valid chart and one fresh comparison.
