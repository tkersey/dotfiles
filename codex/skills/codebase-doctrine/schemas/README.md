# Codebase Doctrine schemas

The JSON Schemas provide structural validation and editor support.

Relational validation is intentionally performed by the skill-local tools:

```bash
uv run --with pyyaml python codex/skills/codebase-doctrine/tools/intent_gate.py ...
uv run --with pyyaml python codex/skills/codebase-doctrine/tools/doctrine_gate.py ...
uv run --with pyyaml python codex/skills/codebase-doctrine/tools/packet_gate.py ...
uv run --with pyyaml python codex/skills/codebase-doctrine/tools/handoff_gate.py ...
uv run --with pyyaml python codex/skills/codebase-doctrine/tools/mode_gate.py ...
```

The relational gates check graph closure, artifact-state equality, reverse evidence
links, doctrine status, proof receipts, negative-ledger authority, skill
candidacy evidence, saturation, assignment authority, and handoff provenance.
