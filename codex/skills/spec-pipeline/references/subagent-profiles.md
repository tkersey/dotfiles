# Subagent Profiles

Preferred agents:

```text
spec_evidence_synthesizer
spec_decision_auditor
spec_invariant_challenger
spec_governance_auditor
spec_retro_miner
```

Use the smallest profile that provides independent value.

Packet value:

- positive: changes a decision, proof, risk, or handoff;
- neutral: valid but no material delta;
- negative: stale, malformed, wrong-scope, unsupported, or timeout.

No passing handoff with open workers.
