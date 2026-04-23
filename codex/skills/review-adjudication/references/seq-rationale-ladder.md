# $seq rationale recovery ladder

Use `$seq` only for rationale recovery, provenance, and artifact-backed why questions.

## When to invoke `$seq`
- The PR why is missing, ambiguous, disputed, or likely to change adjudication.
- A review comment seems odd unless an older plan, memory, or session explains it.
- The user asks what this PR was trying to do.
- A comment may be stale relative to later changes and you need evidence.

## Preferred order
1. `plan-search`
   - Use when you expect explicit plan artifacts or finalized plan blocks.
2. `artifact-search`
   - Use for broad artifact forensics when you need likely rationale evidence but do not know the exact handle yet.
3. `find-session` + `session-prompts`
   - Use when you need the exact prompts, commitments, or decision language from a session.
4. `memory-map`
   - Use to route broad topic lookups across memories.
5. `memory-provenance`
   - Use to answer why a memory exists now or which rollout introduced it.
6. `memory-history`
   - Use when the rationale may have changed across time.

## Evidence ranking
1. Current diff, code, tests, and local artifact state
2. Current-session artifact evidence
3. Prior-session artifact evidence
4. Memory-derived evidence
5. Reviewer intuition without artifact support

## Memory defaults
- `memory_summary.md` for broad navigational recall
- `MEMORY.md` for durable guidance or reusable decisions

## Failure rule
If `$seq` is unavailable or does not yield usable rationale, say so explicitly. Do not fabricate recovered intent.
