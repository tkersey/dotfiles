# Audit Queries

Future regression check:

```bash
seq artifact-search --root ~/.codex/sessions \
  --contains 'review_compression_packet' \
  --strip-skill-blocks \
  --stats \
  --format jsonl
```

Useful companion searches:

```bash
seq artifact-search --root ~/.codex/sessions --contains 'RCP-v1' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'rent_status: unpaid' --strip-skill-blocks --stats
seq artifact-search --root ~/.codex/sessions --contains 'checkpoint_after_local_proof' --strip-skill-blocks --stats
```

A meaningful `$review-compression-compiler` use should produce `review_compression_packet`, not only normal-form prose.
