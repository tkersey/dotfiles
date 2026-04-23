# Closure gates

A readiness decision is blocked by any unresolved material gate in these classes:
- `material_soundness`
- `critical_invariants`
- `material_foot_guns`
- `material_complexity_hazards`
- `briefing_agreement` when the conflict is material and unbounded
- `external_blockers`

When multiple gates remain, surface the single highest open gate in `Reopen Trigger` and route the narrowest next move.
