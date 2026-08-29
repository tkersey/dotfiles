# Decision instrumentation

Load this reference before adding or materially changing a skill decision
contract or receipt.

Instrumentation exists to recover consequential decisions for later tuning. It
is not a completeness badge.

## SKDC-v1 gate

Create:

```text
references/decision-contract.json
```

only when all are true:

- the skill has stable triggers and consequential decision rules;
- selected, rejected, blocked, or no-action routes can be named;
- future tuning benefits from clause-level evidence;
- trigger, route, and clause identities are likely to survive wording changes.

Do not create a contract for a simple transformer, narrow executor, or evidence
fetcher unless it also makes consequential route decisions.

An SKDC-v1 contract contains stable:

```text
trigger IDs
route IDs
clause IDs
required and prohibited routes
success and failure signals
required artifacts
```

Validate it through Tune's passive Ledger definition:

```bash
tune_definition_root="$(realpath \
  "${CODEX_HOME:-$HOME/.codex}/skills/tune/definitions")"

ledger validate \
  --definition "$tune_definition_root/ledger/skill-decision-contract.json" \
  --input contract=<skill-root>/references/decision-contract.json \
  --format json
```

A passing result establishes structural validity under the reported definition
digest. Tune retains interpretation, usefulness, and mutation authority.

## Stable identity

When a contract exists:

- preserve trigger, route, and clause IDs;
- never renumber for formatting;
- update only clauses affected by the intervention;
- synchronize expected and prohibited routes with `SKILL.md`;
- preserve superseded identities when historical evidence depends on them;
- update `source_fingerprint` after the final package state is known.

When no contract exists, do not add one merely because Tune can validate it.

## Optional SDR-v1

A decision-oriented skill may emit:

```text
skill_decision_receipt / SDR-v1
```

Use a receipt only when:

- the skill makes a consequential route decision;
- ordinary traces cannot recover that decision reliably;
- the receipt can name selected and rejected alternatives honestly;
- the output and lifecycle cost are proportionate;
- later tuning has a concrete use for the evidence.

Do not emit receipts for ordinary prose, every checklist step, simple tool
execution, or decisions already recoverable from bounded traces.

Validate a receipt against its exact contract:

```bash
ledger validate \
  --definition "$tune_definition_root/ledger/skill-decision-receipt.json" \
  --input contract=<skill-root>/references/decision-contract.json \
  --input receipt=<receipt.json> \
  --format json
```

A receipt proves that a route was recorded under a contract. It does not prove
that the route was correct or that the outcome was good.

## Future tuneability

Before completion, ask:

```text
Can future evidence tell whether the skill was present?
Can it tell whether a consequential decision changed?
Can it identify the exercised rule?
Can it distinguish compliance from success?
```

`not applicable` is an acceptable answer. Do not add instrumentation merely to
make every answer yes.

## Instrumentation ablation

Delete or narrow instrumentation when it:

- records no consequential choice;
- duplicates evidence already recoverable from traces;
- creates mandatory receipt ceremony without a consumer;
- fossilizes wording rather than stable decisions;
- costs more than the attribution uncertainty it resolves.
