# Coordinator Subtree Protocol

Use this protocol whenever `fixed-point-driver` enables read-only specialist subagents.

## Topology

- Root spawns exactly one direct child: `fp_coordinator`.
- `fp_coordinator` spawns specialist children such as:
  - `fp_evidence`
  - `fp_invariants`
  - `fp_hazards`
  - `fp_complexity`
  - `fp_verification`
- Specialists never target `/root`.
- Root never directly targets specialist children.

## Allowed tool flow

1. Root `spawn_agent(task_name=\"fp_coordinator\", ...)`
2. `fp_coordinator` `spawn_agent(...)` for specialist auditors
3. Specialists return exactly one `SPECIALIST_PACKET` each to `fp_coordinator`
4. `fp_coordinator` synthesizes one `COORDINATOR_PACKET`
5. `fp_coordinator` `send_message(target=\"/root\", message=<COORDINATOR_PACKET>)`
6. Root `wait_agent(...)` only as a mailbox/status wakeup
7. Root integrates the coordinator result and then `close_agent(target=\"fp_coordinator\")`

## Packet shapes

### `SPECIALIST_PACKET`

```text
<SPECIALIST_PACKET role="..." artifact_state_label="..." status="ok|blocked|transport-invalid">
scope: ...
top_material_signals: ...
unresolved_signals: ...
agreement_pressure: ...
Routing Call: ...
</SPECIALIST_PACKET>
```

### `COORDINATOR_PACKET`

```text
<COORDINATOR_PACKET artifact_state_label="..." status="ok|blocked|transport-invalid">
scope: ...
synthesized_signals: ...
unresolved_signals: ...
briefing_agreement: aligned|mixed|conflicting
Routing Call: ...
</COORDINATOR_PACKET>
```

## Fail-closed rules

- If root-visible output references descendant specialist paths such as `/root/fp_coordinator/fp_*`, the run is transport-blocked.
- If root-visible coordinator output contains `Echo:`, `<hook_prompt`, `<subagent_notification>`, or raw outer inter-agent JSON, the run is transport-blocked.
- Root may receive at most one clean `COORDINATOR_PACKET` per run.
- If any of the above fail, do not claim the workaround is fixed; report `blocked` with transport evidence.
