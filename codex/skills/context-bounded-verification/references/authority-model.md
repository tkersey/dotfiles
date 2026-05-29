# Authority Model

The root agent owns final verification authority. Subagents are read-only evidence authorities with bounded jurisdictions.

## Root-owned decisions

The root must make and record these decisions:

- current workflow objective;
- scope and non-goals;
- tier declaration;
- artifact-state acceptance after every material edit or checkout change;
- whether evidence is current enough to support action;
- final readiness/closure/pass decision;
- implementation authorization checks;
- handoff routing and agenda.

The root may not replace these decisions with a subagent answer, CAS label, reviewer severity, old plan, memory hit, or successful unrelated command.

## Subagent packet rule

Every subagent packet must bind to the root's current state.

```yaml
authority_packet:
  role: context-evidence-authority | context-scope-direction-authority | context-blast-radius-authority | context-closure-authority
  packet_status: accepted | rejected
  artifact_state_id: "..."
  scoped_claim_ids: []
  artifact_state_match: yes | no | unknown
  scope_match: yes | no | unknown
  clearance: clear | veto | unresolved | not-required
  positive_evidence:
    - id: E1
      evidence_ref: "..."
      claim: "..."
  vetoes:
    - id: E2
      class: stale | ungrounded | wrong-objective | out-of-scope | weak-proof | unchecked-blast-radius | handoff-unsafe
      claim: "..."
      evidence_ref: "..."
      required_to_clear: "..."
  reason: "..."
```

The root copies accepted packets into `verification_packet.authority.subagent_packets` in the compact receipt shape expected by the gate:

```yaml
subagent_packets:
  - role: context-evidence-authority
    packet_status: accepted
    artifact_state_match: yes
    scope_match: yes
    clearance: clear | veto | unresolved | not-required
    reason: "..."
```

## Authority roles

### Evidence authority

Owns whether claims are grounded in current artifacts and current evidence. It vetoes memory-only, prior-session-only, reviewer-only, stale, unreachable, or contradicted claims.

### Scope/direction authority

Owns whether the claim advances the current objective and respects non-goals. It vetoes wrong-objective plans, stale instructions, local correctness that broadens the lane, and review pressure that does not belong in the current task.

### Blast-radius authority

Owns whether the inspected surface is enough for the tier. It maps public contract, data, generated artifact, runtime, rollout, rollback, and downstream surfaces. It does not decide final closure.

### Closure authority

Owns whether the proof supports the closure claim at the stated tier. It vetoes unrelated green tests, stale command output, absent negative fixtures for proof-surface changes, and residual risk hidden under a pass claim.

## Veto handling

A veto does not automatically mean the task failed. It means one of these outcomes is required:

- validate-only;
- proof-only;
- no-change;
- defer;
- blocked;
- narrow the scope and rerun proof;
- revise the handoff agenda.

Pass or implementation handoff is forbidden until vetoes are cleared or converted into explicit blockers.
