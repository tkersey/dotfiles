---
name: codebase-doctrine
description: "Compile deep repository evidence into artifact-bound correctness doctrine, authority/law/proof maps, strongest knowledge destinations, and an optional minimal repository-skill portfolio. Use when the user wants both deep codebase understanding and durable doctrine, knowledge routing, or repository-specific skill recommendations. Research discoverable facts before asking; use `$grill-me` only for material user-owned intent choices. Not for quick onboarding, one isolated invariant, ordinary implementation, generic review, or direct skill creation."
metadata:
  version: "2.0.1"
  activation_cost: high
  default_depth: standard
---

# Codebase Doctrine

## Mission

Determine what future maintainers and coding agents must know, decide, reject,
and prove to change a repository safely.

Compile:

```text
authorized intent
-> named search questions
-> artifact-bound evidence
-> closed claim graph
-> current/target authorities, laws, invariants, boundaries, failures, and proof
-> strongest knowledge destinations
-> zero or one root skill plus zero to five focused skill candidates
```

The final doctrine is a canonical synthesis for one pinned repository and intent
state. It is not stronger than current code, executable proof, explicit user
authority, or canonical domain stores such as the negative ledger.

## Activation boundary

Use when the request contains both:

```text
deep repository understanding
+
durable correctness doctrine, knowledge routing, authority/proof maps,
or repository-specific skill recommendations
```

Do not use for:

- quick onboarding or architecture fingerprinting;
- one feature, bug trace, or isolated invariant;
- ordinary implementation or generic review;
- skill brainstorming without repository evidence;
- direct skill creation.

The skill is read-only. Persistence and skill creation require separate explicit
authorization.

## Modes and terminal artifacts

Choose exactly one mode:

| Mode | Purpose | Terminal artifact |
|---|---|---|
| `survey` | Provisional map and exact next questions | `codebase_survey / CBS-v1` |
| `doctrine` | Complete baseline workflow | `codebase_doctrine / CBD-v2` |
| `deep` | Complete baseline plus adaptive specialists | `CBD-v2` with specialist receipts |
| `refresh` | Revalidate an existing doctrine at a new state | `codebase_doctrine_delta / CBDD-v1` plus resulting `CBD-v2` |
| `portfolio` | Reevaluate knowledge destinations and skill candidacy | `codebase_portfolio / CBP-v1` |
| `audit` | Compare current guidance and skills with doctrine | `codebase_doctrine_audit / CBA-v1` |

Do not force a full CBD into survey, portfolio, audit, or delta work.

## Canonical artifacts

```text
doctrine_intent_gate          DIG-v2
codebase_doctrine_intent      CDI-v2
codebase_doctrine_assignment  CBDA-v1
codebase_doctrine_packet      CBDP-v2
codebase_doctrine             CBD-v2
codebase_doctrine_delta       CBDD-v1
codebase_skill_handoff        CBSH-v2
```

DIG plus an optional bounded grill closure deterministically compiles to CDI:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/intent_compile.py \
  gate.yaml \
  [--grill grill.yaml] \
  --output intent.yaml
```

CBD is a closed evidence graph. Every typed reference must resolve.

## Phase 0 — intent before doctrine

### Reconnaissance

Before asking intent questions, inspect enough to distinguish discoverable facts
from user-owned choices:

- repository guidance and existing skills;
- manifests, build/test/release roots;
- major subsystems and cross-cutting flows;
- deployment/distribution shape;
- visible correctness, compatibility, security, performance, and operational priorities.

Create DIG-v2 and validate it:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/intent_gate.py gate.yaml
```

### Mandatory `$grill-me` dispatch

`$grill-me` may clarify only material user-owned choices such as:

```text
target boundary
consumers
current-state versus target-state posture
desired products
correctness priorities
non-goals
proof bar
compatibility or migration posture
persistence
```

Do not ask it for repository facts, laws, implementation design, or skill-file
content.

When DIG-v2 validates with:

```yaml
grill_required: yes
gate:
  doctrine_may_proceed: no
  intent_route:
    route: grill-me
    hard_stop: yes
    next_action: activate_grill_me
```

then Codebase Doctrine must immediately activate `$grill-me` in the same turn,
pass only the validated `codebase_doctrine_grill_handoff`, and hard-stop. Do not
continue repository exploration, synthesize CDI/CBD, ask the questions directly,
or choose defaults. Resume this workflow only after a bound
`grill_decision_packet` returns `plan_allowed: true` and resolves every material
DIG gap.

A grill closure must bind to the original DIG and explicitly resolve every
material gap. `plan_allowed: true` authorizes doctrine inquiry only; it does not
authorize persistence, skill creation, code edits, commit, push, or publication.

### CDI-v2

CDI records:

- target, consumers, posture, products, priorities, non-goals, and proof bar;
- a primary correctness question and primary risk or priority;
- explicitly sourced user invariant hypotheses, if any;
- compatibility, persistence, routing, and portfolio requests;
- assumptions and deferrals.

CDI does **not** declare repository-derived laws before research.

## Artifact state

After CDI locks the target, pin:

```yaml
artifact_state:
  artifact_state_id:
  repository_root:
  repository_name:
  branch:
  head:
  dirty_state:
  tracked_diff_sha256:
  untracked_path_digest:
  scope_path_digest:
  intent_digest:
  scope:
  intent_id:
  captured_at:
```

Every evidence item, proof receipt, worker assignment, and worker packet binds to
this state.

Re-pin before closure. Reject stale evidence after a relevant head, diff, scope,
or intent change.

## Evidence providers

Codebase Doctrine owns analysis and synthesis. It may consume bounded canonical
evidence from:

```text
$seq               query-only session/tool/orchestration evidence
$negative-ledger   query/export-only canonical route evidence
$retrace           bounded replay when consequential rationale is incomplete
$grill-me          user-judgment clarification only
```

These are evidence providers, not competing doctrine owners.

Separate:

```text
fact
inference
recommendation
open question
current observed law
documented intent
explicit user target
proposed law
contradicted or retired doctrine
```

## Workflow

### 1. Fingerprint the repository

Determine repository kind, languages, build/test systems, deployment shape,
dependency direction, subsystems, public contract roots, entrypoints, and local
dialect. Architecture is a hypothesis backed by responsibilities and dependency
direction, not directory names.

### 2. Build the system map

Trace representative flows:

```text
input or trigger
-> parsing or routing
-> orchestration
-> domain transition
-> persistence or integration
-> output or effect
```

Record external boundaries, persistence/configuration roots, feedback loops, and
delays.

### 3. Map authority and state

For important state and evidence, identify who may create, mutate, validate,
certify, publish, transfer, consume, retire, and roll back it.

Prioritize write paths, transitions, certificates, transactions, and rollback
over readers or names.

### 4. Extract the behavioral model

Use the smallest correctness vocabulary that explains carriers, operations,
observations, state classes, transitions, laws, non-laws, forbidden states, and
projections.

Do not turn incidental current behavior into doctrine.

### 5. Extract current and target laws

Every law records:

- doctrine status and normative authority;
- owner;
- accepted observations and counterexamples;
- current evidence and, when applicable, target authority;
- gap statement;
- proof obligations and proof surfaces.

Do not merge an observed law and proposed repair law into one unlabelled row.

### 6. Extract owned invariants and boundaries

An invariant requires owner, source of truth, initialization, preserving
transitions, violating counterexamples, enforcement boundary, exception owner,
and proof.

A boundary requires accepted/rejected inputs, authority before/after, transferred
state or evidence, and proof.

### 7. Perform failure archaeology

Normalize local wounds into recurring law, authority, representation, boundary,
or proof-shape failures.

A negative route may be:

```text
suspected
witnessed
canonical_projection
retired
```

Only a current canonical negative-ledger projection may create durable route
exclusion.

### 8. Map proof

Distinguish:

```text
proof design
executed current proof
historical proof
manual or reviewer proof
```

Executed current proof records command, exit code, result reference, toolchain,
target, artifact state, and verification time.

### 9. Resolve contradictions

Do not average incompatible claims. Resolve them or preserve the contradiction,
stronger evidence, residual uncertainty, and materiality.

### 10. Route durable knowledge

Every durable active claim receives exactly one primary destination:

```text
code
type_or_representation
test_or_property
static_tool_or_linter
CI_gate
AGENTS_or_repository_guidance
ADR_or_reference
negative_ledger
repository_root_skill
focused_skill
retain_in_doctrine
reject
```

Prefer the strongest enforceable destination.

### 11. Design an optional skill portfolio

Portfolio shape:

```text
zero or one root repository skill
zero to five focused skills
```

No skill is required.

Each candidate criterion is an evidence-bearing decision, not a self-attested
boolean. New candidates normally end as `recommended_for_trial`. `accepted`
requires empirical use evidence.

### 12. Test saturation

Stop when additional search is unlikely to change a material doctrine decision.

A `saturated` artifact requires:

- every required lane covered;
- no open route-changing search;
- no unresolved material contradiction;
- every `additional_search_would_change` value is no;
- all durable active claims routed.

Never claim exhaustive understanding.

## Adaptive read-only specialists

Deep mode uses specialists only for unresolved route-changing questions.

Recommended waves:

```text
Wave 1  codebase_cartographer + authority_state_mapper
Wave 2  behavioral_law_miner / failure_forensics_analyst /
        codebase_doctrine_proof_mapper for identified surfaces
Wave 3  doctrine_portfolio_skeptic after draft knowledge routing
Wave 4  search_saturation_auditor after the complete draft
```

Do not launch all workers merely because mode is `deep`.

Every worker receives a CBDA-v1 assignment and returns one CBDP-v2 packet. The
packet gate requires the assignment and enforces artifact state, scope, question,
lane, and update-key authority:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/packet_gate.py packet.yaml \
  --assignment assignment.yaml
```

Workers are read-only, cannot spawn children, and never own final doctrine.

## Root synthesis

The root:

1. validates CDI, artifact state, assignments, and packets;
2. rejects stale, wrong-scope, unsupported, or out-of-authority material;
3. closes evidence and reverse-reference edges;
4. distinguishes current, intended, target, proposed, contradicted, and retired doctrine;
5. resolves or preserves contradictions;
6. routes every durable active claim exactly once;
7. applies evidence-bearing skill candidacy;
8. verifies saturation;
9. emits one mode-appropriate terminal artifact.

Validate CBD-v2:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/doctrine_gate.py \
  doctrine.yaml \
  --require-saturated
```

## Refresh

Generate an identity-level delta between two valid doctrines:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/doctrine_diff.py \
  prior.yaml new.yaml \
  --changed-path src/example.zig \
  --output delta.yaml
```

A delta partitions retained, modified, added, and invalidated IDs; identifies
proof rechecks; and exposes intent drift.

## Persistence

Default output is conversational.

Persist only when requested:

```text
.codebase-doctrine/doctrine.yaml
```

Local-exclude by default unless the user explicitly wants versioned doctrine.

## Skill-creation handoff

Codebase Doctrine recommends; it does not create.

After explicit user authorization, validate CBSH-v2 against its source CBD:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/handoff_gate.py \
  handoff.yaml \
  --doctrine doctrine.yaml
```

Then hand to `$ms`.

## Empirical evolution

After generated skills have real use:

```text
$seq skill-decision-audit
-> $tune
-> $refine
```

Return changed laws or authority to `$codebase-doctrine refresh`. Do not tune from
raw mention counts.

## Validation

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/quick_validate.py
```

## Hard rules

- Read-only.
- Research discoverable facts before asking.
- No material doctrine without valid CDI-v2.
- No repository-derived invariant locked as user intent.
- No silent intent drift.
- Every reference resolves in both directions where specified.
- Every durable active claim has exactly one primary route.
- Writes and transitions outrank reads for authority.
- No law without status, authority, counterexample, evidence, and proof posture.
- No invariant without owner, initialization, transitions, boundary, counterexample, and proof.
- Negative-route exclusions require canonical ledger provenance.
- Skills are optional and require evidence-bearing candidacy.
- No persistence or skill creation without explicit authorization.
- Never claim exhaustive understanding.
