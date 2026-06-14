# Audit Queries

Future regression checks:

```bash
seq artifact-search --root ~/.codex/sessions --contains 'review_compression_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'review_distillation_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'resolve_review_wave_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'negative_route_exclusion_card' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'negative_route_gate' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'negative_evidence_closure_gate' --strip-skill-blocks --stats
```

Success metric:

```text
active_exclusions_changed_route
```

not mere `$negative-ledger` mentions.
