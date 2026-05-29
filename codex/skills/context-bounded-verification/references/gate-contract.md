# Context-Bounded Verification Gate Contract

The gate is a structural anti-laundering check for `context-bounded-verification` outputs. It does not prove code correctness. It proves that a readiness, pass/fail, validation, or handoff claim is shaped so weak evidence cannot silently become implementation or closure.

## When the gate is required

Run `tools/context_verification_gate.py` for:

- Tier 2 or Tier 3 work;
- any closure/readiness/pass claim;
- implementation handoff to `accretive-implementer`, `fixed-point-driver`, or another coding workflow;
- review findings promoted into mutations;
- contested evidence, stale plan pressure, or prior-session/memory influence;
- verifier, proof, certificate, source-map, generated-artifact, policy, allowlist, quota, or public-contract changes.

Tier 0/Tier 1 may use the compact note unless the result gates closure or handoff.

## Checker command

```bash
python codex/skills/context-bounded-verification/tools/context_verification_gate.py path/to/packet.md
```

The checker accepts JSON, YAML, or Markdown with a fenced `yaml`/`json` block containing `verification_packet`.

Useful commands:

```bash
python codex/skills/context-bounded-verification/tools/context_verification_gate.py --self-test
python codex/skills/context-bounded-verification/tools/context_verification_gate.py --write-example /tmp/cbv-example.md
python -m py_compile codex/skills/context-bounded-verification/tools/context_verification_gate.py
```

## Gate blocks

The checker fails the packet when it sees any of these patterns:

- `pass` or `pass-with-residual-risk` using stale, superseded, unknown, prior-session, memory-only, or reviewer-only evidence;
- actionability=`implement` or `closure-pass` without current evidence, `artifact_state_match=yes`, and `supports=yes`;
- Tier 2/Tier 3 pass with no executable current proof signal;
- proof/verifier/checker changes without a negative/counterexample check;
- pass while material blast-radius surfaces remain unchecked;
- pass or handoff while direction fit is not `aligned`;
- pass or handoff with unresolved authority packets or vetoes;
- implementation handoff without a current implement-actionable evidence item;
- blocked/defer readiness without concrete blockers;
- handoff allowed with no target, agenda, or `must_not_do` boundaries.

## Gate allows valid blocks

A valid packet may end in `blocked`, `defer`, `validate-only`, `proof-only`, `no-change`, or `pass-with-residual-risk`. The gate is not a pass-only tool. A clean block is a successful context-bounded-verification result when evidence is insufficient or authority is missing.

## Packet version

Current packet version: `CBV-GATE-v1`.

The version is intentionally strict. If the doctrine changes, bump the version and update:

- `SKILL.md` output contract;
- `references/verification-output-contract.md`;
- `tools/context_verification_gate.py`;
- `evals/adversarial-eval-seeds.yaml`;
- README validation examples.
