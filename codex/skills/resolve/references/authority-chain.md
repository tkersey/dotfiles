# RAC-v1 Authority Chain

Raw review text does not authorize mutation. A review-originated change must be
compiled into `resolve_authority_chain / RAC-v1` before a mutation gate may pass.

Native check:

```bash
resolve-c3 authority-chain check --chain rac.yaml --format json
```

Native mutation gate:

```bash
resolve-c3 mutation-gate --chain rac.yaml --format json
```

Reference compatibility check:

```bash
python3 codex/skills/resolve/tools/resolve_authority_chain_gate.py rac.yaml
```

Reference mutation gate:

```bash
python3 codex/skills/resolve/tools/resolve_mutation_gate.py --chain rac.yaml
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

The mutation gate exits `0` only when mutation is allowed, `2` when a RAC
artifact was evaluated but mutation is blocked, and `3` when input could not be
evaluated. Blocked workflows may only adjudicate the claim, seal or repair the
batch, compile or repair CEB/MBK/RC, rebase AC, create a follow-up, reject the
finding, or block.

Mutation-authorizing chains require current artifact state, a complete review
claim, in-horizon acceptance law, confirmed adjudication, sealed batch,
compression proof links, realization allowance, and agreeing gate fields. Legal
non-mutation chains may set `realization.allowed=false` and
`gate.mutation_allowed=no` only when the adjudication disposition explains the
non-mutation route.
