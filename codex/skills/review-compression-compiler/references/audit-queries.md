# Audit Queries

Future regression checks:

```bash
seq artifact-search --root ~/.codex/sessions --contains 'review_compression_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'resolve_review_wave_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'Resolve route artifact:' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'universalist_check' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'prior_decision_invalidated: yes' --strip-skill-blocks --stats
```

A meaningful compiler use should produce both `review_compression_packet` and a route-wave publication.
