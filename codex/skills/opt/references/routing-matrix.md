# $opt Routing Matrix

| User intent | Mode | Governing route | Edit default |
|---|---|---|---|
| “Is this skill well shaped?” | audit | root plus optional read-only modeler | no edit |
| “Optimize this skill” | propose | `$tune` | no edit |
| “Tune from this session” | tune / shadow-diagnose | `$shadow` -> `$tune` | no edit |
| “Fix the skill now” | apply | `$tune` -> complete `REFINE-SKILL-v3` -> `$refine` | explicit authority required |
| “Validate this skill edit” | validate | `$refine validate` | no edit |
| “Prevent that failure again” | regression | `$tune` -> `$refine regression` | explicit authority required |
| “Keep working until improved” | goal-loop | `$cas` + `$opt` | each mutation separately gated |

## Evidence routing

- Current user feedback: use current-turn evidence first; do not claim recurrence.
- One watched session: use `$shadow`; do not inspect raw transcript files unless explicitly authorized.
- Historical sessions: use `$seq` and `$tune`'s evidence hierarchy.
- Worktree changes: inspect only the target skill package and named validation surfaces.
- Supplied brief: preserve its evidence limits and authorized boundary.

## Apply semantics

These words do not by themselves authorize edits:

```text
optimize improve tune harden audit review diagnose make better
```

These normally express edit intent when the target skill is explicit:

```text
edit patch apply update the file change SKILL.md implement the fix
```

Even with edit intent, mutation requires a complete `REFINE-SKILL-v3` handoff. `$refine` is the sole writer.
