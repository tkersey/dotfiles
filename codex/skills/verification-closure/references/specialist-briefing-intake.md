# Specialist briefing intake

When specialist briefings are packet-native:

- prefer direct ingestion over free-form reinterpretation
- preserve `role`, `artifact_state_label`, `scope`, `top_material_signals`, and `unresolved_signals`
- compute `stale` from state-label mismatch
- compute `agreement_pressure` from cross-briefing comparison
- never convert a specialist signal into proof without a supporting check
