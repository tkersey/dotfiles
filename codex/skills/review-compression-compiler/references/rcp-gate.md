# RCP Gate

Validate packet files with:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py path/to/packet.yml
python codex/skills/review-compression-compiler/tools/route_wave_gate.py path/to/review-wave.route.yml
```

The RCP gate checks compact packet fields, universalist_check, falsification, route_wave_ref, and rent.

The route-wave gate checks that route receipts, RCP packets, universalist checks, and implementation handoff permission are present.
