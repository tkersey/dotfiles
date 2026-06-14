# Gates

Validate packet files:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py path/to/packet.yml
python codex/skills/review-compression-compiler/tools/rdp_gate.py path/to/distillation.yml
python codex/skills/review-compression-compiler/tools/nrec_gate.py path/to/nrec.yml
python codex/skills/review-compression-compiler/tools/route_wave_gate.py path/to/review-wave.route.yml
```

A failed gate blocks mutation or closure.
