---
name: codebase-doctrine
description: "Learn how a repository actually works, extract the laws and ownership boundaries that make it correct, route durable knowledge to code/tests/tooling/docs/ledger/skills, and design the smallest repository-specific correctness-skill portfolio. Use for codebase learning plus doctrine design, repository correctness atlas, authority maps, failure archaeology, proof maps, skill candidacy, search saturation, or explicit deep read-only subagent exploration. Not for a quick architecture summary, one isolated invariant, direct skill creation, or implementation."
metadata:
  version: "1.0.1"
  activation_cost: high
  default_depth: standard
---

# Codebase Doctrine

## Mission

Build a trustworthy model of a repository and determine what future agents must know, decide, reject, and prove to change it safely.

```text
Learn the system.
Find its authorities and laws.
Study how it fails.
Map how correctness is proved.
Route each durable lesson to its proper enforcement surface.
Create skills only for recurring judgment.
```

This is a self-contained workflow. It owns adapted architecture, archaeology, systems, invariant, algebraic, boundary, forensic, proof, routing, and saturation methods.

It does **not** invoke or compile outputs from existing public skills. Those skills remain available for narrower or deeper standalone work.

## Canonical artifact

Produce one root artifact:

```text
codebase_doctrine / CBD-v1
```

Default persisted location when requested:

```text
.codebase-doctrine/doctrine.yaml
```

Subagent packets are evidence inputs, never competing truth sources.

## Use / do not use

Use when the user wants both:

```text
deep repository understanding
+ durable correctness doctrine or repository-specific skill recommendations
```

Do not use for:

- quick architecture fingerprint;
- onboarding summary only;
- one feature/bug trace;
- one invariant design;
- immediate skill creation;
- repository implementation;
- generic review;
- skill brainstorming without codebase evidence.

## Modes

```text
survey      fast provisional map; no committed portfolio
doctrine    complete default workflow
deep        complete workflow with read-only specialists
refresh     revalidate an existing CBD-v1 at a new artifact state
portfolio   reevaluate routing and skill candidacy from an existing doctrine
audit       compare existing repository guidance/skills with current doctrine
```

## Inputs

Resolve mode, scope, depth, focus, repository skill namespace, evidence lanes, subagent policy, and persistence.

Defaults: `doctrine`, whole repository, standard depth, Git history enabled, optional safe runtime/`$seq`/negative-ledger evidence, deep-mode subagents, and no persistence.

## Artifact-state pin

Before searching:

```yaml
artifact_state:
  artifact_state_id:
  repository_root:
  repository_name:
  branch:
  head:
  dirty_state:
  scope:
  captured_at:
```

Every evidence item and worker packet binds to it.

Reject stale packets after a relevant head or scope change.

## Evidence and search discipline

Every claim derives from `codebase_evidence`:

```yaml
codebase_evidence:
  evidence_id:
  lane:
  question_id:
  observation:
  evidence_ref:
  artifact_state_id:
  scope:
  confidence:
  supports_claim_ids: []
  contradicts_claim_ids: []
```

Lanes:

```text
guidance
static structure
symbols/references
behavior/tests
authority/mutation
history/forensics
runtime
agent history
negative evidence
```

Search is question-driven:

```yaml
search_question:
  question_id:
  question:
  why_it_matters:
  lanes: []
  search_methods: []
  evidence_found: []
  model_change:
  status:
```

Use the best available mechanism: docs, exact search, structural/AST search, symbol references, dependency/call graphs, tests/fixtures, Git history, runtime evidence, `$seq`, and negative-ledger records.

Do not use every mechanism mechanically.

See [exploration-method.md](references/exploration-method.md) and [evidence-model.md](references/evidence-model.md).

## Workflow

### 1. Fingerprint the repository

Determine repository kind, languages, build/test systems, deployment shape, dominant/secondary architectures, dependency direction, subsystems, entry points, public contract roots, and repository dialect.

Architecture names must be evidence-backed and may vary by subsystem.

See [repository-fingerprint.md](references/repository-fingerprint.md).

### 2. Build the system map

Trace representative flows:

```text
input/trigger
-> parsing/routing
-> orchestration
-> domain transition
-> persistence/integration
-> output/effect
```

Record components, connections, external boundaries, persistence/config roots, feedback loops, and delays.

Use clear/complicated/complex/chaotic classification only when it changes the search or intervention method.

### 3. Map authority and state

Find who may create, mutate, certify, publish, transfer, consume, and retire state.

Prioritize write paths and transitions over read references.

Identify shadow owners, late validation, and ambiguous authority transfer.

See [authority-model.md](references/authority-model.md).

### 4. Extract the behavioral model

Capture only correctness-relevant:

```text
carriers
operations
observations
state classes
transitions
laws
non-laws
forbidden states/transitions
interpreters/projections
```

Use tests and observable behavior to distinguish laws from implementation accidents.

See [behavioral-model.md](references/behavioral-model.md).

### 5. Extract owned invariants

Require:

```text
statement
owner
source of truth
initialization
preserving transitions
counterexample
enforcement boundary
exception owner
proof surface
```

Reject or downgrade candidates missing those elements.

See [invariant-method.md](references/invariant-method.md).

### 6. Perform failure archaeology

Search bug fixes, reverts, recurring review findings, regressions, hot symbols, duplicate checks, fallback growth, failed routes, and negative evidence.

Normalize:

```text
local failure
-> recurring family
-> violated law/authority rule
-> wrong boundary, representation, or proof shape
```

A family named only after a file/function/comment remains provisional.

See [failure-forensics.md](references/failure-forensics.md).

### 7. Map proof

For each law/invariant, map structural enforcement, static checks, tests, properties, state machines, integration proof, runtime witnesses, and CI.

Detect law gaps, wound-specific test growth, duplicate fixtures, and tests with unclear claim coverage.

See [proof-mapping.md](references/proof-mapping.md).

### 8. Resolve contradictions

Record conflicting claims and evidence.

Prefer stronger/current evidence, but preserve residual uncertainty.

Do not silently merge incompatible worker conclusions.

### 9. Route knowledge

Every durable finding gets one primary destination:

```text
code
type/representation
test/property
static tool/linter
CI gate
AGENTS/repository guidance
ADR/reference
negative ledger
repository root skill
focused skill
retain in doctrine
reject
```

Prefer the strongest enforceable destination.

Use skills only for recurring judgment and route selection.

See [knowledge-routing.md](references/knowledge-routing.md).

### 10. Design the skill portfolio

Default:

```text
one thin root repository skill
zero to five focused skills
```

Do not mirror the directory tree.

Each focused skill must pass:

```text
recurring trigger
consequential decision
stable governing law
independent activation
standalone workflow
observable success/failure
not better as code/test/tooling/docs
```

Keep rejected candidates and reasons.

See [skill-candidacy.md](references/skill-candidacy.md).

### 11. Test search saturation

Stop when more search is unlikely to change:

```text
repository fingerprint
authority map
governing laws
proof map
knowledge routes
skill portfolio
```

Output one of:

```text
saturated
targeted_search_required
blocked
```

Never claim exhaustive understanding.

See [saturation.md](references/saturation.md).

## Read-only specialists

Use in deep mode or when explicitly requested:

```text
codebase_cartographer
authority_state_mapper
behavioral_law_miner
failure_forensics_analyst
codebase_doctrine_proof_mapper
doctrine_portfolio_skeptic
search_saturation_auditor
```

The proof worker uses the workflow-scoped identity
`codebase_doctrine_proof_mapper`. Do not alias it to the general
`proof_surface_mapper`; agent names are global registry identities.

All workers:

- are read-only;
- use the same artifact state;
- cite concrete evidence;
- separate facts and inferences;
- return exactly one CBDP-v1 packet;
- do not edit code or create skill files.

Validate:

```bash
python3 codex/skills/codebase-doctrine/tools/packet_gate.py packet.yaml
```

See [specialist-packets.md](references/specialist-packets.md).

## Root synthesis

1. Validate packets.
2. Reject stale, wrong-scope, acknowledgement-only, and unsupported packets.
3. De-duplicate facts.
4. Normalize terms.
5. Resolve or preserve contradictions.
6. Re-check high-impact claims in root.
7. Route knowledge before proposing skills.
8. Apply the skill candidacy gate.
9. Challenge stopping in deep mode.
10. Emit one CBD-v1.

## CBD-v1

CBD-v1 contains artifact/request identity, search and evidence ledgers, repository/system/authority/behavior maps, laws, invariants, boundaries, failure and negative-route families, proof, contradictions, open questions, knowledge routes, root/focused/rejected skill designs, saturation, confidence, and next actions.

Validate:

```bash
python3 codex/skills/codebase-doctrine/tools/doctrine_gate.py doctrine.yaml
```

See [doctrine-schema.md](references/doctrine-schema.md).

## Persistence

Default output is conversational.

Persist only when requested.

When persisting, use:

```text
.codebase-doctrine/doctrine.yaml
```

Local-exclude by default unless the user explicitly wants versioned doctrine.

Do not silently create repository files.

## Skill-creation handoff

This workflow recommends designs only.

It does not create skills.

An accepted handoff uses `CBSH-v1` and binds doctrine ID, candidate ID, governing laws, triggers, non-triggers, decisions, prohibited routes, required artifacts, success/failure signals, protected doctrine IDs, package boundary, and validation.

Use `$ms` only after explicit follow-up authorization.

## Empirical evolution

After repository skills are used:

```text
$seq skill-decision-audit
-> $tune
-> $refine
```

Evaluate trigger quality, actual decision influence, clause compliance, outcome association, ceremonial use, missed activation, and doctrine drift.

Do not tune from raw mention counts.

## Output

Report artifact state, mode/scope, saturation, architecture, flows, authorities, laws, invariants, failure families, proof posture, knowledge destinations, root/focused/rejected skill designs, evidence coverage, contradictions, open questions, confidence, and next actions.

## Hard rules

- Read-only; do not invoke existing specialist skills.
- Evidence and explicit questions precede doctrine.
- Writes/transitions outrank reads for authority.
- No law from naming; no invariant without owner, counterexample, transition, boundary, and proof.
- Route knowledge before skills.
- One root skill, at most five accepted focused skills, all candidacy-gated.
- Validate worker packets; never claim exhaustive understanding.
- No persistence or skill creation without explicit authorization.
