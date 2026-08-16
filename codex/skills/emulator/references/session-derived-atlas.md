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
  source/<chart-id>/source-map.yaml
  actors/
  worlds/
  harnesses/baseline/
  harnesses/candidates/<candidate-id>/
  runs/<run-group-id>/
  reports/<run-group-id>/
  datasets/
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

seq find-session \
  --prompt <bounded-text> \
  --root "${CODEX_HOME:-$HOME/.codex}/sessions" \
  --format json
~~~

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
    path_sha256:
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
surface, and hard-oracle interpretation. Without that evidence the chart stays
diagnostic. Proven recurring evaluator patterns may later be reused without
per-chart review only when the chart cites the reviewed pattern and its
applicability evidence. For holdout, that reviewer must not participate in
factor selection or candidate authoring. If no independent reviewer is
available, freeze the factor, factor-owner declaration, candidate budget,
runtime policy, and every other candidate-affecting human choice before the
review; after seeing the correction the reviewer may accept or reject the chart
but may not change those choices. Otherwise the chart remains diagnostic.

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
    kind: git_worktree
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
    filesystem: read_only | isolated_write | declared_roots
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

Run the forbidden-ref and excerpt scan over every byte in the complete
actor-readable inventory, including harness, memory, tool fixtures, and mounted
roots. Any unscannable or unsanitized readable asset is excluded or makes the
run `status: invalid_environment` with `status_reason: historical_leakage`.

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
least two root-session identity fingerprints, and contains every root session
covered by the human attestation. `<digest>` is SHA-256 of those exact bytes.
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
Retried or near-duplicate sessions without a shared stable external-task or
human-attested duplicate-cluster descriptor are ineligible for holdout.

- discovery is visible for failure mining, mechanism hypotheses, and chart
  design;
- development is visible for bounded candidate and evaluator iteration;
- holdout is frozen before candidate generation and hidden from the author,
  optimizer prompt, candidate worktree, and development reports.

Compile and validate holdout charts in a fresh context that terminates before
candidate optimization starts. Candidate authoring and optimization use a
separate fresh context that receives discovery/development material only; prior
model context that saw holdout contents is not an admissible optimizer. Freeze
all chart, evaluator, and partition fingerprints before that handoff.

Do not rely on prompts or same-user file modes to hide holdout material from an
optimizer with filesystem tools. Run optimization in a workspace where holdout
roots are not mounted/readable, and bind an optimizer-readable inventory plus
access-proof ref and fingerprint in the pre-candidate policy asset. Missing or
mismatched optimizer access evidence contaminates the holdout.

Use holdout only after candidate fingerprints freeze. An active holdout never
enters training data. When deliberately consumed, retire it from holdout and
replace it with an untouched group before another optimization cycle.

Retirement never edits the fingerprinted chart or an earlier root in place.
Write a content-addressed `holdout-retirement/v1` marker naming the group,
chart fingerprints, consumption purpose, and prior root fingerprint. Maintain
immutable content-addressed index snapshots under
`holdout-retirements/snapshots/<digest-hex>.json`; each is the ordered set of
all marker refs and fingerprints. A mutable `holdout-retirements/current.json`
pointer may identify the latest snapshot but is outside prior closures. The
next root binds the current immutable snapshot and each effective marker through
`partition_policy` and recursive closure. When finalizing any root and before
its first run or report, copy its complete exact closure under
`roots/<root-digest-hex>/`, preserving relative paths and bytes (or
using immutable digest-addressed assets with an exact path map). Reports cite
that archived root, and subordinate refs resolve from the archived root
directory rather than the live atlas root. Later roots never mutate an archived
root or any asset it references.

When no retirement index exists, the first selecting root with a holdout
creates both an immutable empty snapshot and `current.json`; otherwise it
preserves and binds the existing current snapshot. The pointer is mandatory
even when there are no retirements. A root without holdout charts may omit both.

Before every selecting run, acquire the retirement-index update lock, resolve
the current pointer, and require its target snapshot fingerprint to equal the
root's bound snapshot. While still holding that lock, acquire the group locks
and create the reservation described below; release it only after those bytes
are durably present. A stale
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
{"current_pointer_fingerprint":"sha256:<hex>","current_pointer_ref":"holdout-retirements/current.json","resolved_snapshot_fingerprint":"sha256:<hex>","resolved_snapshot_ref":"holdout-retirements/snapshots/<digest-hex>.json","root_contract_fingerprint":"sha256:<hex>","root_snapshot_fingerprint":"sha256:<hex>","run_group_id":"<run-group-id>","schema":"partition-validation/v1","storage_domain_id":"sha256:<hex>"}
~~~

The writer fingerprints the exact current-pointer bytes, resolves that pointer,
and requires the resolved ref/fingerprint to equal the root-bound snapshot
before emitting the artifact. `resolved_snapshot_fingerprint`,
`root_snapshot_fingerprint`, and the EER `partition_snapshot_fingerprint` are
identical. Store it
at `runs/<run-group-id>/partition-validation.json`; runs and EER bind that ref
and exact fingerprint. This runtime proof is distinct from the static
`partition-claim-validation/v1` asset.

Once per comparison cycle and before its first actor sees a holdout, atomically
create an exclusive
`holdout-use/v1` reservation. For compare mode it names the optimization cycle,
full frozen candidate set, groups, chart fingerprints, all per-candidate
comparison IDs, arms, and repeats; each pair keeps its own EER and run group
under that one cycle reservation. Later arms/repeats in that cycle validate and
reuse the exact reservation and matching group locks; they do not create them
again. Holdout use outside compare mode is unsupported. Bind the reservation
ref and fingerprint in every affected run. Any existing or incomplete
reservation makes the group unavailable outside the named cycle and fails
closed. On completion, create a content-addressed `holdout-retirement/v1`
marker referencing the reservation, consumed groups, chart fingerprints,
purpose, and prior root; incorporate that marker in the next immutable
snapshot. Prefer discovery/development for standalone examples; do not spend a
holdout casually.

Constrain every path-derived identifier as specified by the contract profile
before use, and prove each resolved destination remains under its owner root
before create, replace, or removal. Derive the
cross-atlas holdout key as SHA-256 of the exact UTF-8 tuple
`"emulator-holdout/v1" NUL source_identity_fingerprint` for every individual
source identity in the group. Before reading any message, tool, attachment, or
other semantic source byte, use only physical discovery metadata to derive the
source identities, then atomically publish the applicable exposure claim or
holdout reservation described below. If identity cannot be derived without a
semantic read, stop rather than exposing it before a claim. Before chart
compilation, resolve one authoritative private, writable
`storage_domain_root`. Use the canonical resolved
`${CODEX_HOME:-$HOME/.codex}` when writable; a caller may instead explicitly
supply one shared private root for the entire corpus and comparison cycle. The
atlas lives at
`<storage_domain_root>/emulators/<atlas-id>`. Freeze the resolved storage-domain
path and
`storage_domain_id = SHA-256("emulator-storage-domain/v1" NUL canonical-realpath-UTF-8)`
in the root before any partition claim or candidate generation. Claims,
reservations, validations, runs, and reports bind that ID. Within the selected
domain, derive the only valid
`holdout_lock_root` as `<storage_domain_root>/emulator-holdout-locks`; neither
path may vary per atlas or later phase. The root contract repeats both resolved
paths and the domain ID, and validation rejects any other relationship. Claims
are authoritative only against claims with the same domain ID. A caller-supplied
noncanonical domain is diagnostic/development-only because exposure in another
domain cannot be excluded; it cannot support holdout, harness selection,
promotion, or `adopt`. The
canonical lock is `<holdout_lock_root>/<hex>.lock`, so corpus membership or a
local group rename cannot give the same source group a second identity. Acquire
multiple keys in sorted digest order with an atomic create-new operation that
fails if the key already exists; never use check-then-create. The lock record
binds the final root fingerprint, reservation fingerprint, pre-candidate policy
fingerprint, and cycle identity. An existing lock is reusable only when all
those fields exactly match the current cycle reservation; otherwise acquisition
fails. If acquisition fails before any actor exposure, remove only locks and
the unexposed reservation created by that same attempt; after exposure, any
incomplete lock or reservation remains fail-closed for human resolution.
After successful acquisition, copy each lock's exact bytes into the run group's
atlas-relative `runs/<run-group-id>/holdout-locks/<hex>.lock` and bind only
those snapshots as EER/run refs. The atlas-relative lock-validation artifact
maps each snapshot fingerprint to its canonical absolute lock path and domain
ID; canonical paths are evaluator-only runtime facts, not report refs.

Before any semantic source read, acquire the exclusive global
`<holdout_lock_root>/.partition-freeze.lock`, validate the complete sorted
identity-key set, stage all new claims, then publish them before releasing the
lock. Create or validate
`<holdout_lock_root>/<hex>.partition.json` for every individual source identity.
Its file contains exactly the RFC 8785 canonical UTF-8 bytes of:

~~~json
{"exposure_status":"holdout_unexposed","partition":"holdout","schema":"emulator-partition-claim/v1","source_group_fingerprint":"sha256:<hex>","source_identity_fingerprint":"sha256:<hex>","storage_domain_id":"sha256:<hex>"}
~~~

For discovery or development, `partition` is that exact value and
`exposure_status` is respectively `discovery_exposed` or
`development_exposed`; no other fields or values are admitted. The filename's
holdout-key hex and both fingerprint fields must agree with the claimed
identity, group, and storage domain. Claims are finalized before compilation
and before the pre-candidate policy, which then binds their fingerprints;
claims never point back to that policy. The atlas copies each canonical claim's
exact bytes to the atlas-relative
`partitions/claims/<holdout-key>.partition.json` and binds those snapshot refs
and fingerprints in the pre-candidate policy and root closure. It then creates
an atlas-relative `partition-claim-validation/v1` asset mapping every snapshot
to its canonical holdout key, global claim location, storage-domain ID, and
identical fingerprint. The validation asset is evaluator-only and is bound by
the final root, runs, and EER; external absolute claim paths are runtime facts,
not closure refs. Its RFC 8785 payload is exactly
`{"claims":[{"canonical_claim_path":"<absolute-path>","holdout_key":"<hex>","snapshot_fingerprint":"sha256:<hex>","snapshot_ref":"partitions/claims/<hex>.partition.json"}],"schema":"partition-claim-validation/v1","storage_domain_id":"sha256:<hex>"}`
with claims sorted by `holdout_key`; no other fields are admitted. An existing
byte-identical compatible claim is reused. An existing claim for
another partition, or any prior
discovery/development exposure when the new claim is holdout, is
`holdout_contaminated`. Record every partition exposure before the compiler,
author, actor, or optimizer can read that group; claims are not deferred until
partition freeze or execution. If any key is
incompatible before exposure, remove only staged or published claims created by
that attempt while still holding the global lock; compatible pre-existing
claims are never removed. Bind only atlas-relative claim snapshots in the
pre-candidate policy, final root closure, runs, and EER, plus their
atlas-relative validation artifact.

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

Before candidate generation, write and fingerprint an evaluator-only
pre-candidate policy asset containing the selecting chart commitments,
partition snapshot, model/runtime configuration, repeat counts, randomness
matching, improvement threshold, protected dimensions, and candidate budget.
Do not expose that asset, its holdout fields, or its evaluator criteria to the
optimizer. Candidate generation receives a separate redacted optimizer policy
containing the selected factor, exact factor-owner paths and runtime keys,
runtime constraints, budget, and only discovery/development inputs. Before
candidate generation, require those shared fields to equal the pre-candidate
policy exactly. The final root binds both exact refs and
fingerprints; candidate manifests cannot rewrite either snapshot.

Manifest every behavior-bearing root:

~~~json
{
  "schema": "emulator-harness-manifest/v1",
  "harness_id": "baseline-or-candidate-id",
  "factor": "question_policy",
  "roots": [
    {"path": "AGENTS.md", "mode": "100644", "sha256": "..."},
    {"path": "skills/example/SKILL.md", "mode": "100644", "sha256": "..."}
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
Every root `path` is normalized, relative, nonempty, non-escaping, and unique.
Source symlinks are resolved exactly once while capturing the frozen source
harness; dangling links and loops are invalid. A separately fingerprinted,
evaluator-only `harness-capture-provenance/v1` asset binds every source link
path, raw target, and final resolved source path and is included in the root
closure and the corresponding baseline/candidate root entry. That provenance
validates capture but is excluded from harness
identity and factor-delta comparison, so equivalent captures in different
worktrees have the same behavior fingerprint. The staged bundle
then contains only regular, non-symlink files at the logical root paths, with
the resolved bytes and executable modes bound by the manifest. No materialized
bundle symlink may resolve back into the live harness. Absolute logical paths,
`..`, and duplicate normalized paths are invalid.
The final resolved source of every symlink must remain inside one frozen
`target.harness_roots` entry; otherwise capture stops. Legitimate external
content must first be declared as another harness root—there is no implicit
host-path allowlist.

Candidate metadata:

~~~yaml
candidate:
  candidate_id:
  baseline_harness_fingerprint:  # harness subject only
  candidate_harness_fingerprint: # harness subject only
  factor:
  factor_delta_validation_ref:
  factor_delta_validation_fingerprint:
  hypothesis:
  changed_paths: []
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

The pre-candidate policy enumerates the exact behavior-bearing paths and runtime
configuration keys owned by the selected factor. After candidate freeze, one
factor-delta validation asset per candidate computes that candidate's complete
baseline/candidate manifest diff, requires at least one change, and requires
every changed path or runtime key to be in that predeclared owner set. The
matching `candidate_harnesses` root entry, candidate metadata, and pairwise EER
bind the same ref and fingerprint. A missing, incomplete, mismatched, or
out-of-factor delta is `multiple_factors` and cannot be recommended; one
candidate's validation never covers another candidate.

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
deterministic chart: one arm run after two identical reset proofs
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

Return adopt, reject, or insufficient_evidence. Adopt requires:

1. complete baseline and candidate arms are environment-valid for every required chart and repeat;
2. every required chart comparison is determinate, with no required run or
   comparison classified `ambiguous`;
3. no new candidate `hard_fail` of any kind;
4. no protected regression;
5. at least one targeted untouched holdout improvement;
6. any residual preference is order-stable;
7. the exact frozen candidate fingerprint was evaluated;
8. stochastic evidence satisfies the repeat count and improvement rule frozen
   in the root before candidate generation; arms use matched seeds/schedules
   when controllable, and uncontrolled nondeterminism that cannot meet that
   predetermined rule yields `insufficient_evidence`.

Promotion is only an evidence strength: it means these conditions and every
included chart's realized claim eligibility support a separately authorized
adoption decision. A chart contributes no stronger claim than the weaker of its
declared class, maximum supported claim, and the authority actually proved by
that run. It never mutates
the live harness. Ties, unsupported required charts, evaluator disagreement,
access-proof gaps, or inadequate holdout coverage yield insufficient_evidence.
Apply one total precedence rule: `reject` when any candidate introduces a
`hard_fail`, protected regression, or contracted non-hard regression beyond the
frozen tolerance. Otherwise return `adopt` only when every adoption condition
above holds. All remaining cases, including missing/invalid arms, ties,
unsupported coverage, disagreement, and inadequate stochastic evidence, are
`insufficient_evidence`. Exactly one disposition is emitted.

Record paired_replay_delta, observed_association, regression, or
insufficient_evidence as the evidence relation, separately from the adoption
recommendation. Do not claim a causal mechanism from an uncontrolled comparison.

## 11. Export

Emit chart-aware EER-v1 and runs.jsonl as specified in eer-v1.md. `compare`
additionally emits one comparison.json per baseline/candidate pair; standalone
`run` omits comparison artifacts and uses an independent run-group directory.
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
purpose by ref and fingerprint. Missing or mismatched retirement evidence keeps
the row ineligible.

Do not export a historical recovery as chosen unless separately re-executed or
objectively validated.

Trajectory rows require fresh executable runs, a valid reset fingerprint,
complete observable transition trace, hard-oracle results, no evaluator leakage,
and permitted data handling. Historical trajectories are not training
trajectories by default.

Curriculum rows may record family, difficulty, tools, prerequisites, failure
cluster, fidelity, and supported claim. Every export retains chart and authority
provenance.

Counterexample rows require a fresh environment-valid mutation run, exact
mutation assignment, a reproducible minimized failing artifact, evaluator
evidence, and a chart that is not active holdout. Bind the external generator
when one exists; finite built-in enumeration instead derives case identity from
the chart fingerprint, ordered dimension assignment, and shrink strategy. A
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
multiple_factors
insufficient_evidence
~~~

Rollback means: stop fresh actors, discard isolated candidate and reset
workspaces, and leave the live harness unchanged. Preserve private source
bundles and evaluation evidence by default for diagnosis; delete material only
with explicit authorization. A report recommendation never performs rollback or
adoption itself.

## First proof

The first normative pilot uses 5 to 20 real correction charts, at least two
holdout groups, exactly one human-selected factor, baseline plus at most three
candidates, three repeats per harness/chart, hard oracles first, and residual
judgment in both orders. Adoption is disabled. Rejection or
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
