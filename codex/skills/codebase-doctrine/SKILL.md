---
name: codebase-doctrine
description: "Learn how a repository works, clarify the intended doctrine target with `$grill-me` only when material user judgments remain, extract correctness laws and authority boundaries, route durable knowledge to code/tests/tooling/docs/ledger/skills, and design the smallest repository-specific skill portfolio. Use for codebase doctrine, correctness atlas, authority maps, failure archaeology, proof maps, doctrine scope clarification, skill candidacy, saturation, refresh, or audit. Not for quick onboarding, one isolated invariant, direct skill creation, or implementation."
metadata:
  version: "1.1.0"
  activation_cost: high
  default_depth: standard
---

# Codebase Doctrine

## Mission

Build a trustworthy model of a repository and determine what future agents must know, decide, reject, and prove to change it safely.

```text
Clarify what doctrine is being produced and for whom.
Learn the system.
Find its authorities and laws.
Study how it fails.
Map how correctness is proved.
Route each durable lesson to its strongest enforcement surface.
Create skills only for recurring judgment.
```

This is a self-contained repository-analysis workflow. It owns adapted architecture, archaeology, systems, invariant, behavioral-law, boundary, forensic, proof, routing, and saturation methods.

It does not invoke or compile outputs from existing specialist skills.

Narrow exception:

```text
$grill-me may clarify user-owned doctrine intent.
```

`$grill-me` does not perform repository analysis, supply codebase evidence, choose laws, or design the skill portfolio.

## Canonical artifacts

```text
doctrine_intent_gate / DIG-v1
codebase_doctrine_intent / CDI-v1
codebase_doctrine / CBD-v1
```

Default persisted location when requested:

```text
.codebase-doctrine/doctrine.yaml
```

Subagent packets and the grill packet are inputs. CBD-v1 is the sole doctrine authority.

## Use / do not use

Use when the user wants both:

```text
deep repository understanding
+ durable correctness doctrine or repository-specific skill recommendations
```

Do not use for:

- quick architecture fingerprint;
- onboarding summary only;
- one feature or bug trace;
- one isolated invariant design;
- immediate skill creation;
- repository implementation;
- generic review;
- skill brainstorming without codebase evidence.

## Modes

```text
survey      provisional map and exact next questions; no committed portfolio
doctrine    complete default workflow
deep        complete workflow with read-only specialists
refresh     revalidate an existing CBD-v1 and CDI-v1 at a new artifact state
portfolio   reevaluate knowledge routing and skill candidacy
audit       compare current guidance/skills with doctrine
```

`survey` may proceed with a provisional intent when the user only wants reconnaissance.

`doctrine`, `deep`, and material `portfolio` work require an allowed CDI-v1.

`refresh` may reuse the prior CDI-v1 unless research shows intent drift.

## Inputs

Resolve mode, repository, provisional scope, depth, focus, intended consumers, desired products, doctrine posture, proof bar, skill namespace, evidence lanes, history/runtime/agent/negative-evidence policy, subagent policy, and persistence.

Defaults:

```text
mode = doctrine
scope = whole coherent repository
posture = descriptive plus gap analysis
consumer = future maintainers and coding agents
desired products = correctness atlas + knowledge routing + skill candidates
history = yes
runtime/seq/negative-ledger = when available and safe
subagents = deep mode or explicit request
persistence = none
```

Defaults are allowed only when their consequence is low and explicit in CDI-v1.

## Phase 0 — Doctrine Intent Gate

Before full exploration, pin repository root/name, branch, head, dirty state, and capture time, then run a shallow reconnaissance over guidance, manifests, build/test roots, architecture docs, major subsystems, deployment shape, and existing repository skills.

Its purpose is to remove discoverable facts from the question queue—not to perform the doctrine analysis early.

Classify intake items as:

```text
researched fact
low-consequence explicit default
material user judgment
unavailable fact
```

### DIG-v1

Create `doctrine_intent_gate / DIG-v1` with the provisional artifact state, researched facts, explicit user request, defaults, material judgment gaps, grill decision, handoff/direct candidate, reason, and proceed gate.

Validate:

```bash
python3 codex/skills/codebase-doctrine/tools/intent_gate.py gate.yaml
```

See [doctrine-intent-gate.md](references/doctrine-intent-gate.md).

### When `$grill-me` is required

Invoke `$grill-me` only when an unresolved user judgment could materially change:

```text
target boundary
current-state versus desired-state posture
intended consumers or owners
desired products
correctness/risk priorities
non-goals
proof bar
persistence/versioning
```

Typical triggers include unrelated products in one monorepo, ambiguous subsystem versus cross-cutting scope, descriptive versus prescriptive doctrine, atlas-only versus skill-portfolio output, conflicting correctness priorities, or materially different evidence bars.

Skip it when the user already answered the choice, the answer is discoverable, a low-consequence default is safe, mode is provisional survey, or refresh can reuse a still-valid CDI-v1.

### Handoff and closure

Pass `$grill-me` a bounded `CDGH-v1` containing researched facts, working target, only material judgment gaps, allowed lanes, forbidden discoverable-fact questions, and CDI projection fields.

`$grill-me` uses its normal research-first bounded-question workflow and emits its standard `grill_decision_packet`.

Pause doctrine analysis while material questions remain. Proceed only when:

```text
grill_decision_packet.plan_allowed = true
```

This authorizes doctrine investigation only—not implementation, persistence, or skill creation.

See [grill-me-handoff.md](references/grill-me-handoff.md).

### CDI-v1

Project the explicit request, accepted grill packet, or prior doctrine intent into `codebase_doctrine_intent / CDI-v1`.

CDI-v1 locks source/provenance, repository boundary, included/excluded subsystems, cross-cutting flows, consumers, posture, desired products, primary invariant, correctness priorities, non-goals, proof/compatibility/persistence postures, portfolio/routing requests, assumptions, deferrals, and `doctrine_allowed`.

Validate:

```bash
python3 codex/skills/codebase-doctrine/tools/intent_gate.py intent.yaml
```

Do not continue material doctrine work when `doctrine_allowed: no`.

## Final artifact-state pin

After CDI-v1 locks the target boundary:

```yaml
artifact_state:
  artifact_state_id:
  repository_root:
  repository_name:
  branch:
  head:
  dirty_state:
  scope:
  intent_id:
  captured_at:
```

Every evidence item and worker packet binds to this state.

Reject stale packets after a relevant head, scope, or intent change.

## Evidence and search discipline

Every claim derives from `codebase_evidence` bound to the final artifact state and a named search question.

Evidence lanes:

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

Use docs, exact/structural/symbol search, dependency/call graphs, tests/fixtures, Git history, runtime evidence, `$seq`, and negative-ledger records according to the question. Separate observed facts, inferences, contradictions, and recommendations.

Do not use every mechanism mechanically.

See [exploration-method.md](references/exploration-method.md) and [evidence-model.md](references/evidence-model.md).

## Workflow

### 1. Fingerprint the repository

Determine kind, languages, build/test systems, deployment shape, dominant/secondary architectures, dependency direction, subsystems, entry points, public contract roots, and repository dialect.

Architecture must be evidence-backed and may vary by subsystem.

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

Use clear/complicated/complex/chaotic classification only when it changes the inquiry method.

### 3. Map authority and state

Find who may create, mutate, certify, publish, transfer, consume, and retire state.

Prioritize writes and transitions over reads.

Identify shadow owners, late validation, public bypasses, and ambiguous authority transfer.

See [authority-model.md](references/authority-model.md).

### 4. Extract the behavioral model

Capture only correctness-relevant carriers, operations, observations, state classes, transitions, laws, non-laws, forbidden states/transitions, and interpreters/projections.

Use tests and observable behavior to distinguish laws from implementation accidents.

See [behavioral-model.md](references/behavioral-model.md).

### 5. Extract owned invariants

Require statement, owner, source of truth, initialization, preserving transitions, counterexample, enforcement boundary, exception owner, and proof surface.

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

See [failure-forensics.md](references/failure-forensics.md).

### 7. Map proof

Map each law/invariant to structural enforcement, static checks, tests, properties, state machines, integration proof, runtime witnesses, and CI.

Detect law gaps, wound-specific test growth, duplicate fixtures, and unclear claim coverage.

See [proof-mapping.md](references/proof-mapping.md).

### 8. Resolve contradictions and intent drift

Record conflicting claims and evidence. Prefer stronger/current evidence while preserving residual uncertainty.

Reopen the intent gate only when research reveals a material user-owned mismatch, such as:

```text
several unrelated products inside the selected boundary
current and desired doctrine conflict
the intended audience changes the route
requested products become mutually incompatible
proof bar is infeasible for the selected scope
```

Allow at most:

```text
one intake grill cycle
one optional research-triggered scope-reopen cycle
```

Do not silently redefine target, posture, consumers, outputs, non-goals, or proof bar.

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

Prefer the strongest enforceable destination. Use skills only for recurring judgment and route selection.

See [knowledge-routing.md](references/knowledge-routing.md).

### 10. Design the skill portfolio

Default:

```text
one thin root repository skill
zero to five focused skills
```

Do not mirror the directory tree.

Each focused candidate must have a recurring trigger, consequential decision, stable law, independent activation, standalone workflow, observable success/failure, and no stronger code/test/tooling/docs destination.

Keep rejected candidates and reasons.

See [skill-candidacy.md](references/skill-candidacy.md).

### 11. Test search saturation

Stop when more search is unlikely to change the fingerprint, authority map, laws, proof map, knowledge routes, or skill portfolio.

Verdicts:

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

The workflow-scoped proof worker is `codebase_doctrine_proof_mapper`, not the general `proof_surface_mapper`.

All workers are read-only, share the final artifact state scoped by CDI-v1, cite evidence, separate facts/inferences, return one CBDP-v1 packet, and do not edit code or create skill files.

Validate:

```bash
python3 codex/skills/codebase-doctrine/tools/packet_gate.py packet.yaml
```

See [specialist-packets.md](references/specialist-packets.md).

## Root synthesis

1. Validate intent, artifact state, and packets.
2. Reject stale, wrong-scope, acknowledgement-only, and unsupported packets.
3. De-duplicate facts and normalize terms.
4. Resolve or preserve contradictions.
5. Re-check high-impact claims in root.
6. Verify no unapproved intent drift occurred.
7. Route knowledge before proposing skills.
8. Apply the skill candidacy gate.
9. Challenge stopping in deep mode.
10. Emit one CBD-v1.

## CBD-v1

CBD-v1 contains CDI-v1 intent, artifact/request identity, search/evidence ledgers, repository/system/authority/behavior maps, laws, invariants, boundaries, failure and negative-route families, proof, contradictions, open questions, knowledge routes, root/focused/rejected skill designs, saturation, confidence, and next actions.

Validate:

```bash
python3 codex/skills/codebase-doctrine/tools/doctrine_gate.py \
  --require-intent doctrine.yaml
```

See [doctrine-schema.md](references/doctrine-schema.md).

## Persistence

Default output is conversational.

Persist only when requested.

When persisting, use `.codebase-doctrine/doctrine.yaml` and local-exclude by default unless the user wants versioned doctrine.

Do not silently create repository files.

## Skill-creation handoff

This workflow recommends designs only; it does not create skills.

An accepted CBSH-v1 binds doctrine/intent/artifact IDs, candidate, governing laws, triggers, non-triggers, decisions, prohibited routes, artifacts, success/failure signals, protected doctrine IDs, package boundary, and validation.

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

Report intent source and boundary, artifact state, mode/scope, saturation, architecture, flows, authorities, laws, invariants, failure families, proof posture, knowledge destinations, root/focused/rejected skill designs, evidence coverage, contradictions, open/deferred questions, confidence, and next actions.

## Hard rules

- Read-only.
- `$grill-me` is the only public-skill invocation exception and owns only user-judgment clarification.
- Research discoverable facts before asking the user.
- No material doctrine without allowed CDI-v1.
- No silent intent drift.
- Evidence and explicit questions precede doctrine.
- Writes/transitions outrank reads for authority.
- No law from naming; no invariant without owner, counterexample, transition, boundary, and proof.
- Route knowledge before skills.
- One root skill and at most five accepted focused skills.
- Validate worker packets; never claim exhaustive understanding.
- No persistence or skill creation without explicit authorization.
