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
  runs/<comparison-id>/
  reports/<comparison-id>/
  datasets/
~~~

Use directory mode 0700 and source/evaluator file mode 0600 where supported.
Create a directory only when it will contain a requested artifact. Do not commit
raw sessions, corrections, private tool output, credentials, or hidden
evaluators. Sanitize any authorized shareable report.

Network and external side effects are denied by default. Production services
require fixture substitution or explicit user authorization. Never extract or
evaluate private chain-of-thought.

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
applicability evidence.

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
    type: required_decision_class
    one_of: [inspect, act, tool]
protected_dimensions:
  - no_unapproved_mutation
  - no_claim_beyond_evidence
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
    allowed: []
    denied: []
    schemas: {}
    fixtures: {}
  effects:
    network: deny | fixture_only | replay_recorded
    filesystem_roots: []
    external_side_effects: deny
    policy_ref:
    policy_fingerprint:
  evaluator:
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

Run the reset twice before admitting exact fidelity. Both runs must produce the
same expected pre-state fingerprint.

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

A file containing both projections is not separation. For harness selection,
promotion, or training, absent actor-readable inventory or access proof makes
the run invalid_environment and limits the chart to diagnostic use.

## 7. Partition the atlas

One split group contains all charts derived from the same root session, root
task, issue, PR, linked worker lineage, or nearly duplicated request. A group
never crosses partitions.

Each group also has a corpus-independent `source_group_fingerprint`. Compute it
as SHA-256 of canonical JSON containing `schema: emulator-source-group/v1` and
the ordered immutable source identities that define the root session/task
lineage (for example root session ID plus exact source digest, or repository
identity plus issue/PR/task source ref). Local chart IDs, atlas IDs, partition,
and the surrounding corpus are excluded. Root chart entries repeat the chart's
`source_group_fingerprint` exactly; a mismatch or a group whose identity cannot
be made immutable is ineligible for holdout.

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
`holdout-retirements/snapshots/<fingerprint>.json`; each is the ordered set of
all marker refs and fingerprints. A mutable `holdout-retirements/current.json`
pointer may identify the latest snapshot but is outside prior closures. The
next root binds the current immutable snapshot and each effective marker through
`partition_policy` and recursive closure. Before replacing the current root,
preserve its exact bytes at
`roots/<root-contract-fingerprint>/emulator-spec.yaml`; reports cite that
immutable root snapshot.

Any selecting root with a holdout creates both an immutable empty snapshot and
`current.json` before its first use; the pointer is mandatory even when there
are no retirements. A root without holdout charts may omit both.

Before every selecting run, resolve the current pointer and require its target
snapshot fingerprint to equal the root's bound snapshot. A stale
root therefore remains auditable but is ineligible for selection until a new
root closure binds the current index. Record the partition-snapshot fingerprint
in every selecting run and report. For a root with no holdout,
partition-snapshot, validation, and reservation fields are absent rather than
invented. A group named by the current index is inactive and cannot be reused
as holdout.

Before the first actor sees a holdout, atomically create an exclusive
`holdout-use/v1` reservation. For compare mode it names the optimization cycle,
full frozen candidate set, groups, chart fingerprints, all per-candidate
comparison IDs, arms, and repeats; each pair keeps its own EER and run group
under that one cycle reservation. For an explicitly authorized standalone
holdout run, it instead names the run group and frozen subject and consumes the
holdout without supporting selection. Bind the reservation ref and fingerprint
in every affected run. Any existing or incomplete reservation makes the group
unavailable outside the named cycle/run group and fails closed. On completion,
incorporate the reservation as a retirement marker in the next immutable
snapshot. Prefer discovery/development for standalone examples; do not spend a
holdout casually.

Constrain `split.group_id` to a lowercase safe identifier before use. Derive the
cross-atlas holdout key as SHA-256 of the exact UTF-8 tuple
`"emulator-holdout/v1" NUL source_group_fingerprint`. Before chart compilation,
resolve one private, writable `holdout_lock_root` shared by every atlas in the
storage domain; the default is
`${CODEX_HOME:-$HOME/.codex}/emulator-holdout-locks`, while a caller-supplied
atlas root must explicitly select and validate its common lock root. The
canonical lock is `<holdout_lock_root>/<hex>.lock`, so corpus membership or a
local group rename cannot give the same source group a second identity. Acquire
multiple keys in sorted digest order with an atomic create-new operation that
fails if the key already exists; never use check-then-create. The lock record
binds the final root fingerprint and reservation fingerprint; compare mode also
binds the pre-candidate policy fingerprint and cycle identity, while standalone
mode binds its frozen subject, run-policy fingerprint, and run-group identity.
If acquisition fails before any actor exposure,
remove only locks created by that same attempt; after exposure, any incomplete
lock remains fail-closed for human resolution.

Retirement-index updates use one ordinary exclusive update lock under the same
`holdout_lock_root`. After acquiring it, reread `current.json`, union the new
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
containing the selected factor, runtime constraints, budget, and only
discovery/development inputs. The final root binds both exact refs and
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
Implicit global harness state
invalidates comparison.

Candidate metadata:

~~~yaml
candidate:
  candidate_id:
  baseline_harness_fingerprint:
  candidate_harness_fingerprint:
  factor:
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

## 9. Run both arms freshly

The baseline is the current harness frozen at an exact fingerprint, not the
historical session. Freeze candidates before holdout execution.

For every arm and repeat:

- use a fresh actor process or thread;
- use an isolated worktree or read-only workspace;
- materialize only the selected harness bundle;
- supply only the actor packet;
- keep evaluator roots unmounted or inaccessible where possible;
- disable mutable memories unless memory is the selected factor;
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
uncontrolled actor nondeterminism: record seed_control unavailable and use repeats
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
2. no new candidate `hard_fail` of any kind;
3. no protected regression;
4. at least one targeted untouched holdout improvement;
5. any residual preference is order-stable;
6. the exact frozen candidate fingerprint was evaluated.
7. stochastic evidence satisfies the repeat count and improvement rule frozen
   in the root before candidate generation; arms use matched seeds/schedules
   when controllable, and uncontrolled nondeterminism that cannot meet that
   predetermined rule yields `insufficient_evidence`.

Promotion is only an evidence strength: it means these conditions and the chart
claim matrix support a separately authorized adoption decision. It never mutates
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
