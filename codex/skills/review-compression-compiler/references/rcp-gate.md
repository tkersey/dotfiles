# RCP Gate

Validate packet files with:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py path/to/packet.yml
```

The gate checks for compact packet fields, universalist_check, and rejects unpaid-rent or skipped-universalist add-new-surface packets.
