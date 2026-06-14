# Audit Queries

Future regression checks:

```bash
seq artifact-search --root ~/.codex/sessions --contains 'review_compression_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'review_distillation_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'resolve_review_wave_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'negative_evidence:' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'scar_tissue_inventory' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'prior_decision_invalidated: yes' --strip-skill-blocks --stats
```
