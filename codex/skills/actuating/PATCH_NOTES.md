# Patch Notes

Version: `5.2.0`

Restores `$actuating` delivery closure after the v5.1 pre-mutation interlock.

Adds:

- ADD-v1 `actuation_delivery_decision`.
- Post-integration delivery gate and `$ship` tail-call rule.
- `actuation_delivery_gate.py` with decide/check commands.
- Delivery examples and tests.
- Decision-contract route `ACT-SHIP`.

Preserves:

- APMA-v1 pre-mutation authority.
- GCR-v2 self-invalidating stop rule.
- Claim/fencing/resource coverage requirements.
- Serialized `$st` integration.

Critical repair:

```text
proof-complete graph audit != terminal when PR delivery is requested
proof-complete + integrated target branch + ADD-v1 handoff_to_ship -> $ship
```
