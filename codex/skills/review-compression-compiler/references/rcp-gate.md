# RCP Gate

Validate packet files with:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py path/to/packet.yml
```

The gate checks for the compact packet fields and rejects unpaid-rent add-new-surface packets.

Passing this script is not proof of correctness; failing it blocks implementation handoff.
