# RAC-v1 Authority Chain

Raw review text does not authorize mutation. A review-originated change must be
compiled into `resolve_authority_chain / RAC-v1` before a mutation gate may pass.

Native check:

```bash
resolve-c3 authority-chain check --chain rac.yaml --format json
```

Reference compatibility check:

```bash
python3 codex/skills/resolve/tools/resolve_authority_chain_gate.py rac.yaml
```

Exit codes:

- `0`: valid chain, including legal non-mutation chains.
- `2`: invalid or incomplete chain.
- `3`: unreadable or unsupported input.

The compatibility script emits:

```json
{
  "status": "valid",
  "mutation_allowed": true,
  "missing": [],
  "violations": [],
  "chain_id": "RAC-example",
  "campaign_id": "c3-example"
}
```

Mutation-authorizing chains require current artifact state, a complete review
claim, in-horizon acceptance law, confirmed adjudication, sealed batch,
compression proof links, realization allowance, and agreeing gate fields. Legal
non-mutation chains may set `realization.allowed=false` and
`gate.mutation_allowed=no` only when the adjudication disposition explains the
non-mutation route.
