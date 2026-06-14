# RCP Gate

A meaningful RCP must include literal `review_compression_packet:` and `packet_version: RCP-v1`.

Validate file packets:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py <packet-file>
```

Gate failure blocks mutation.
