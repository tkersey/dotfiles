# Hylo portable contracts

## Artifact and store layout

A portable replay campaign is two language-neutral files:

```text
campaign.json
scenarios.jsonl
```

An adapter in any language may interpret those files if it preserves request
visibility, hidden references, environment and effect boundaries, split
membership, oracles, and fingerprints.

The native Ledger source owns operational evidence:

```text
<repo>/.ledger/hylo/events.jsonl
<repo>/.ledger/hylo/events.jsonl.lock
```

Only `ledger --source hylo append` may mutate the event store. The lock sidecar
is coordination state and must be Git-ignored. A custom `--path` must remain
inside the addressed repository.

## Identifiers and fingerprints

Stable identifiers match:

```text
[A-Za-z0-9][A-Za-z0-9._:-]{0,127}
```

Fingerprints are lowercase SHA-256 values:

```text
sha256:<64 lowercase hexadecimal characters>
```

`ledger --source hylo fingerprint` parses one JSON value, rejects duplicate
keys and invalid numbers, recursively sorts object keys, removes insignificant
whitespace, emits normalized JSON scalars, and hashes the canonical UTF-8
bytes. Array order remains significant.

## `hylo-campaign/v1`

```json
{
  "schema": "hylo-campaign/v1",
  "campaign_id": "cmp-example",
  "target": {
    "kind": "skill",
    "id": "example-skill",
    "baseline_fingerprint": "sha256:..."
  },
  "source": {
    "corpus_fingerprint": "sha256:...",
    "session_refs": [
      {
        "kind": "codex_session",
        "ref": "session-id",
        "fingerprint": "sha256:..."
      }
    ],
    "exclusions": ["current_session", "injected_skill_text"]
  },
  "privacy": {
    "mode": "sanitized",
    "redactions": ["secrets", "private_reasoning", "personal_data"],
    "redaction_receipt": {
      "schema": "hylo-redaction-receipt/v1",
      "tool": "seq",
      "version": "v1",
      "source_fingerprint": "sha256:...",
      "output_fingerprint": "sha256:<same as source.corpus_fingerprint>",
      "evidence_refs": ["seq:redaction-receipt"]
    }
  },
  "rubric": {
    "id": "rubric-v1",
    "fingerprint": "sha256:...",
    "dimensions": [
      {
        "id": "correctness",
        "kind": "deterministic",
        "weight": 1.0,
        "critical": true,
        "grader_ref": "test:required-test",
        "grader_fingerprint": "sha256:..."
      }
    ],
    "judge": {
      "kind": "composite",
      "id": "campaign-judge",
      "version": "v1",
      "config_fingerprint": "sha256:..."
    },
    "pass_policy": {
      "minimum_aggregate": 1.0,
      "zero_critical_violations": true
    }
  },
  "replay_policy": {
    "fingerprint": "sha256:...",
    "blind_hidden_reference": true,
    "holdout_blind": true,
    "default_fidelity": "controlled_replay",
    "repeat_count": 1
  },
  "stop_policy": {
    "max_attempts": 100,
    "require_holdout_pass": true,
    "zero_critical_violations": true
  },
  "change_policy": {
    "target_change_authority": "none",
    "publication_authority": "none",
    "allowed_paths": [],
    "require_clean_scope": false
  },
  "scenarios_file": "scenarios.jsonl",
  "scenario_manifest": [
    {
      "scenario_id": "scenario-001",
      "scenario_fingerprint": "sha256:<canonical scenario object>",
      "split": "holdout"
    }
  ]
}
```

Rules:

- Target kind is `skill`, `agent`, `prompt`, `workflow`, or
  `model_configuration`.
- Real-session campaigns have at least one fingerprinted source reference.
- Privacy mode is `sanitized` or `local_full`; both explicitly redact
  `secrets` and `private_reasoning` from persisted evidence. The redaction
  receipt binds raw-source and sanitized-output fingerprints, and its output
  fingerprint equals `source.corpus_fingerprint`. Labels alone are not proof
  of sanitization.
- Rubric dimension IDs are unique, weights are non-negative, and at least one
  weight is positive. Every dimension and the campaign judge freeze declared
  grader identity before replay. A model grader cannot be the sole critical
  authority.
- `minimum_aggregate` is in `[0,1]`.
- Hidden references and holdouts are blind by policy. Repeat and attempt counts
  are positive. Cycle and patience limits are skill-level routing choices, not
  native v1 campaign claims.
- Fidelity is `transcript_only`, `workspace_snapshot`, `controlled_replay`, or
  `synthetic_mutation`.
- Target change authority is `none`, `propose`, or `apply_via_owner`.
- Publication authority is `none` or `commit`; it never authorizes push.
- `apply_via_owner` requires clean scope and one or more unique,
  non-overlapping relative path roots. Commit authority requires
  `apply_via_owner`.
- `scenarios_file` is a non-escaping relative path beside `campaign.json`.
- `scenario_manifest` is non-empty and binds every scenario ID, split, and
  canonical object fingerprint in JSONL order. Campaign validation recomputes
  the file against it, admission rejects unknown or changed scenarios, and no
  attempt may begin until the complete manifest is admitted.

The example is intentionally non-authorizing. An opt-in change campaign uses
`apply_via_owner`, `publication_authority:"commit"`, clean scope, and explicit
relative path roots only after the user grants both authorities.

The `campaign_created` event stores this entire object. Later folding does not
trust a mutable copy on disk.

## `hylo-scenario/v1`

Each non-empty `scenarios.jsonl` line is one object:

```json
{
  "schema": "hylo-scenario/v1",
  "campaign_id": "cmp-example",
  "scenario_id": "scenario-001",
  "split": "holdout",
  "source_refs": [
    {
      "kind": "decision_capsule",
      "ref": "capsule.json",
      "fingerprint": "sha256:..."
    }
  ],
  "source_episode_fingerprint": "sha256:...",
  "request": {
    "message": "User-visible request",
    "visible_context": [],
    "hidden_reference_ref": "local:redacted-reference"
  },
  "environment": {
    "fidelity": "controlled_replay",
    "fingerprint": "sha256:...",
    "repo_revision": "git:0123456789abcdef0123456789abcdef01234567",
    "adapter": {
      "id": "cas-replay",
      "version": "v1",
      "contract_ref": "artifact:adapter-contract",
      "contract_fingerprint": "sha256:..."
    },
    "snapshot": {
      "kind": "git",
      "ref": "git:0123456789abcdef0123456789abcdef01234567",
      "fingerprint": "sha256:..."
    },
    "setup_ref": "artifact:setup-plan",
    "setup_fingerprint": "sha256:...",
    "toolchain": [
      {"id": "zig", "version": "0.16.0"}
    ],
    "fixtures": [],
    "effect_policy": {
      "filesystem": "read_only",
      "allowed_paths": [],
      "network": "deny",
      "network_allowlist": [],
      "external_side_effects": "deny",
      "external_effect_allowlist": []
    },
    "limitations": []
  },
  "replay_policy_fingerprint": "sha256:...",
  "oracles": [
    {
      "id": "required-test",
      "kind": "deterministic",
      "critical": true,
      "observation": "test command exits 0",
      "grader_ref": "test:required-test",
      "grader_fingerprint": "sha256:..."
    }
  ],
  "mutation": null
}
```

Rules:

- Split is `practice`, `holdout`, or `challenge`.
- Source references are non-empty. `source_episode_fingerprint` identifies the
  frozen source episode; the admission event separately fingerprints the
  complete scenario snapshot.
- The request contains visible material only. `hidden_reference_ref` is a
  non-empty `local:` or `artifact:` locator, or a full SHA-256 fingerprint.
- Environment identity includes a versioned adapter contract, immutable
  snapshot locator, setup artifact, toolchain versions, fingerprinted
  fixtures, enforceable filesystem/network/external-effect policy, and
  explicit reconstruction limitations. `workspace_snapshot` and
  `controlled_replay` require a non-empty toolchain. Snapshot kind is `git`,
  `archive`, `container`, `synthetic`, or `transcript`.
- A Git snapshot ref is `git:` plus a full 40- or 64-hex commit object ID, and
  `repo_revision` equals that ref. Moving names such as `HEAD` and branches are
  invalid scenario state.
- The replay-policy fingerprint equals the campaign's frozen value.
- Oracles are non-empty and have unique IDs. Each oracle freezes its declared
  grader ref and fingerprint in scenario syntax before any attempt. A model
  oracle cannot be the sole critical authority.
- A synthetic mutation uses `fidelity:"synthetic_mutation"`, names an earlier
  parent scenario, states its operator, and lists preserved invariants. That
  parent must precede the mutation in the portable JSONL and event lineage.

If `stop_policy.require_holdout_pass` is true, the portable campaign contains
at least one holdout scenario.

## `hylo-event-intent/v1`

Callers submit intent; Ledger supplies storage metadata:

```json
{
  "schema": "hylo-event-intent/v1",
  "campaign_id": "cmp-example",
  "kind": "attempt_recorded",
  "scenario_id": "scenario-001",
  "attempt_id": "attempt-001",
  "grade_id": null,
  "payload": {}
}
```

Allowed kinds, in their legal lineage, are:

```text
campaign_created
scenario_admitted
attempt_recorded
grade_recorded
feedback_recorded
change_recorded
publication_recorded
campaign_closed
```

### Campaign and scenario admission

`campaign_created` is first for its campaign and uses null scenario, attempt,
and grade IDs:

```json
{
  "campaign_fingerprint": "sha256:<canonical campaign object>",
  "campaign": {"schema": "hylo-campaign/v1"}
}
```

`scenario_admitted` supplies top-level `scenario_id`:

```json
{
  "scenario_fingerprint": "sha256:<canonical scenario object>",
  "scenario": {"schema": "hylo-scenario/v1"}
}
```

Ledger recomputes both fingerprints and derives all later policy state from
the embedded immutable snapshots.

### `attempt_recorded`

Top-level scenario and attempt IDs are required; grade ID is null:

```json
{
  "status": "completed",
  "target_fingerprint": "sha256:...",
  "environment_fingerprint": "sha256:...",
  "replay_policy_fingerprint": "sha256:...",
  "origin": "controlled_replay",
  "role": "replay_baseline",
  "blind": true,
  "evidence_refs": ["cas:replay-receipt"],
  "trace_ref": "artifact:attempt-trace",
  "trace_fingerprint": "sha256:...",
  "historical_provenance": null,
  "target_snapshot_revision": "0123456789abcdef0123456789abcdef01234567",
  "target_snapshot_fingerprint": "sha256:...",
  "target_snapshot": {
    "schema": "hylo-target-snapshot/v1",
    "roots": ["codex/skills/example-skill"],
    "entries": [
      {
        "mode": "100644",
        "object_id": "0123456789abcdef0123456789abcdef01234567",
        "object_type": "blob",
        "path": "codex/skills/example-skill/SKILL.md"
      }
    ]
  }
}
```

Status is `completed`, `failed`, or `blocked`. Completed attempts require a
trace reference and fingerprint; other statuses forbid them. Roles bind to
origins:

```text
historical_baseline -> historical
replay_baseline     -> controlled_replay
candidate           -> controlled_replay
mutation            -> synthetic
```

Both baselines use the campaign's baseline target fingerprint. Candidate and
mutation attempts use either that baseline or an already applied target
fingerprint. Controlled and synthetic attempts bind the admitted environment
and replay policy. In commit-authorized campaigns they also embed a canonical
target snapshot whose ordered roots exactly equal the campaign's target roots;
one logical target fingerprint cannot map to two physical snapshots. A replay
baseline names a resolved commit SHA. Candidate and mutation attempts name
`INDEX`; before append, Ledger recomputes both that snapshot and the recorded
staged-diff fingerprint from the addressed repository.

Historical attempts instead set environment and replay-policy fingerprints to
null, omit target snapshots, and supply:

```json
{
  "historical_provenance": {
    "status": "partial",
    "environment_fingerprint": null,
    "repo_revision": null,
    "limitations": ["original workspace unavailable"],
    "evidence_refs": ["session:source"]
  }
}
```

Historical provenance is `exact`, `partial`, or `unavailable`. Non-exact
provenance states its limitations instead of falsely borrowing replay identity.
The campaign's attempt cap is enforced during append.

### `grade_recorded`

Top-level scenario, attempt, and grade IDs are required:

```json
{
  "status": "pass",
  "target_fingerprint": "sha256:...",
  "rubric_fingerprint": "sha256:...",
  "environment_fingerprint": "sha256:...",
  "replay_policy_fingerprint": "sha256:...",
  "blind": true,
  "comparison_eligible": true,
  "aggregate": 0.9,
  "dimensions": [
    {
      "id": "correctness",
      "score": 0.9,
      "weight": 1.0,
      "grader_kind": "deterministic",
      "grader_ref": "test:required-test",
      "grader_fingerprint": "sha256:...",
      "evidence_refs": ["test:required-test"]
    }
  ],
  "oracle_results": [
    {
      "id": "required-test",
      "status": "pass",
      "grader_kind": "deterministic",
      "grader_ref": "test:required-test",
      "grader_fingerprint": "sha256:...",
      "evidence_refs": ["test:required-test"]
    }
  ],
  "critical_violations": [],
  "judge": {
    "kind": "composite",
    "id": "test-runner",
    "version": "v1",
    "config_fingerprint": "sha256:..."
  },
  "evidence_refs": ["trace:attempt-001"]
}
```

Status is `pass`, `fail`, `invalid`, or `incomparable`. For pass/fail, the
dimension set and weights exactly match the frozen rubric. Ledger recomputes
the weighted aggregate and rejects a caller-supplied mismatch. Each dimension
and scenario oracle records its grader kind, identity, fingerprint, and
evidence. Grader kind, ref, and fingerprint must equal the authority already
frozen in campaign or scenario syntax; later declared drift is invalid. These
are consistency checks over attestations, not authentication of the producer.
Deterministic and trace results therefore cite independently inspectable
execution receipts, while human results require human confirmation. Every
scenario oracle appears exactly once in frozen order.

`comparison_eligible:true` additionally requires a completed blind attempt,
pass/fail status, complete fingerprint agreement, and no earlier eligible
grade for that attempt. Candidate and mutation grades additionally require an
eligible like-for-like `replay_baseline` grade whose attempt predates the
candidate attempt for that scenario. Direct comparison freezes environment,
replay policy, rubric, judge kind/ID/version, judge configuration,
per-dimension graders, and oracle graders. A historical attempt is always
diagnostic, even when its reconstructed visibility is marked blind.

Pass and fail labels are derived against the frozen threshold and critical
policy: a pass that misses policy and a fail that already satisfies policy are
both rejected. This prevents manufactured failures from authorizing repairs.

### `feedback_recorded`

Top-level scenario, attempt, and grade IDs identify the grade being explained:

```json
{
  "summary": "The trace violated the required ordering.",
  "next_action": "replay",
  "evidence_refs": ["trace:attempt-001"]
}
```

`next_action` is `replay`, `mutate`, `repair_environment`, `handoff_tune`,
`rebaseline`, `stop`, or `blocked`. Feedback proposes a route; it never rewrites
a grade.

### `change_recorded`

All top-level lineage IDs are null:

```json
{
  "change_id": "change-001",
  "status": "applied",
  "before_target_fingerprint": "sha256:...",
  "after_target_fingerprint": "sha256:...",
  "owner_route": "refine",
  "authority_ref": "user:turn-id",
  "paths": ["codex/skills/example-skill/SKILL.md"],
  "diff_ref": "git-index:HEAD",
  "diff_fingerprint": "sha256:...",
  "motivation_grade_ids": ["grade-replay-001"],
  "validation_refs": ["test:skill-validation"]
}
```

Status is `applied`, `rejected`, or `blocked`. Applied changes require campaign
authority, a before fingerprint equal to the current target, a distinct after
fingerprint that has never named an earlier target epoch, paths inside the
frozen scope, validation evidence, and at least one earlier
comparison-eligible failing practice grade for that before target.
Holdout and challenge grades cannot motivate a repair, so they remain
independent promotion evidence. Once an eligible holdout or challenge grade is
recorded for the current target, no later applied change may use that target as
its base; exposed promotion evidence requires a new campaign.

An applied change is a Git-index observation, not a caller assertion. Stage
only its scoped paths, set `diff_ref:"git-index:HEAD"`, and fingerprint the raw
output of:

```bash
git diff --cached --binary --full-index --no-ext-diff --no-color HEAD --
```

Before append, Ledger recomputes that fingerprint, requires the complete staged
path set to equal `paths`, and rejects tracked or untracked contamination under
any campaign target root. Each candidate or mutation attempt repeats this
check and independently recomputes its `INDEX` target snapshot, so staged drift
requires a fresh change record. The event records the owner-routed
intervention; it does not make the edit.

### `publication_recorded`

All top-level lineage IDs are null:

```json
{
  "publication_id": "publication-001",
  "status": "committed",
  "change_id": "change-001",
  "authority_ref": "user:turn-id",
  "candidate_target_fingerprint": "sha256:...",
  "commit_sha": "0123456789abcdef0123456789abcdef01234567",
  "commit_tree_ref": "git-tree:0123456789abcdef0123456789abcdef01234567",
  "paths": ["codex/skills/example-skill/SKILL.md"],
  "validation_refs": ["test:skill-validation"],
  "promotion_grade_ids": ["grade-holdout-001"]
}
```

Status is `committed` or `blocked`. A committed publication requires explicit
campaign commit authority, the current applied change, exact change paths,
and later comparison-eligible passing candidate or mutation grades for its
target. Every frozen scenario—not a caller-selected subset—has at least
`repeat_count` cited grades after the change. Those IDs must be exactly the
latest eligible cohort for each scenario, and the entire cohort must pass;
older successes cannot hide a newer failure. When the stop policy requires
zero critical violations, no eligible post-change grade for the candidate may
contain one.

Before append, Ledger asks the addressed Git repository to resolve the exact
commit object and tree, then compares the commit's complete changed-path set
with the event paths. It independently projects every campaign target root
from that commit and requires its canonical snapshot fingerprint to equal the
snapshot used by every promotion attempt. A false SHA, tree, path, or target
content claim leaves the store unchanged. This proves the local commit object,
scope, and equality to the graded target; it does not prove branch reachability,
remote push, or generalized improvement.

A blocked publication has no commit or promotion-grade claim.

### `campaign_closed`

All top-level lineage IDs are null. Payload is:

```json
{"reason": "configured budget exhausted"}
```

No later event may target a closed campaign.

## `hylo-event/v1`

Ledger persists one canonical JSON object per line:

```text
schema: hylo-event/v1
sequence
previous_digest
campaign_sequence
previous_campaign_digest
campaign_id
kind
recorded_at_unix
body
body_digest
event_digest
```

`body` contains nullable scenario, attempt, and grade IDs plus the intent
payload. `body_digest` hashes its canonical JSON. `event_digest` binds schema,
global predecessor and sequence, campaign predecessor and sequence, campaign,
kind, timestamp, and body digest. Interleaved campaigns therefore preserve one
global append order and one independent lineage per campaign.

On load, Ledger checks strict schemas, canonical digests, both predecessor
chains, monotonic sequences, and every state-transition law. A failed append
writes no line. The event-store boundary compares the loaded revision again
under its lock, rejects concurrent replacement, and refuses any append whose
result would exceed the next reload cap. Doctor never repairs or truncates
evidence.

## `hylo-progress/v1`

`progress` derives, rather than stores:

```text
campaign status, event count, and campaign chain head
scenario and split counts
attempt status and historical-baseline counts
current-target pass/fail and critical-violation counts by split
target-by-split aggregate and per-dimension means
latest current-target outcome and consecutive passing-repeat count per scenario
current-target, latest-cohort unresolved frontier
grader-stable comparable adjacent cross-target deltas
progress fingerprint bound to the campaign head
```

It does not infer causality, statistical significance, or general capability.
The skill applies those claim rules using sample size, repeats, uncertainty,
split, and environment limitations.

## Native commands

These commands require Ledger `>= 0.6.1`.

```bash
# Probe the source
ledger --source hylo --help

# Canonical fingerprint for a JSON artifact; FILE may be -
ledger --source hylo fingerprint --input FILE

# Validate campaign.json and its scenarios JSONL
ledger --source hylo validate-campaign --campaign campaign.json

# Resolve HEAD or another commit name, then snapshot ordered roots; INDEX is staged state
ledger --source hylo snapshot-target \
  --repo REPO --revision INDEX --input target-roots.json

# Append one validated event intent
ledger --source hylo append --repo REPO --json intent.json

# Validate the complete event store
ledger --source hylo doctor --repo REPO

# Derive progress
ledger --source hylo progress \
  --repo REPO --campaign-id cmp-example --format json

# Print the resolved repo-local store path
ledger --source hylo path --repo REPO
```

`target-roots.json` is:

```json
{
  "schema": "hylo-target-snapshot-request/v1",
  "roots": ["codex/skills/example-skill"]
}
```

The receipt carries `hylo-target-snapshot/v1` syntax plus its canonical
fingerprint. `INDEX` observes staged content without creating a commit; an
input such as `HEAD` is resolved and emitted as the full immutable commit SHA.
Use that resolved SHA—not the moving input name—in scenario and attempt
contracts.

Malformed input, an invalid transition, a false Git publication claim, a
corrupt chain, or a storage failure exits nonzero. The error receipt names the
precise Zig error class. Do not place secrets, capabilities, private reasoning,
or unredacted sensitive material in input files, arguments, or event evidence.
