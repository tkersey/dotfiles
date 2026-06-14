# Audit Queries

Future regression checks:

```bash
seq artifact-search --root ~/.codex/sessions --contains 'review_compression_packet' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'universalist_check' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'decision: use-universalist' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'rent_status: unpaid' --strip-skill-blocks --stats
```

A meaningful compiler use should produce both `review_compression_packet` and `universalist_check`.
