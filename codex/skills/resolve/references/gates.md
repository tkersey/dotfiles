# Gates

```bash
python3 codex/skills/resolve/tools/acceptance_contract_gate.py acceptance.json
python3 codex/skills/review-adjudication/tools/counterexample_gate.py cex.json
python3 codex/skills/resolve/tools/review_batch_gate.py batch.json
python3 codex/skills/review-compression-compiler/tools/counterexample_basis_gate.py basis.json
python3 codex/skills/resolve/tools/kernel_lint.py kernel.json
python3 codex/skills/resolve/tools/review_potential_gate.py potential.json
python3 codex/skills/resolve/tools/mbkc_gate.py mbkc.json --terminal
```

A failed gate blocks the next mutation/delivery transition.
