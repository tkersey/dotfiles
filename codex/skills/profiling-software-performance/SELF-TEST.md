# Self-Test — Trigger Phrases

> Phrases the skill SHOULD activate on, and phrases it should NOT. Test after any description change.

## Should activate (positive cases)

- "Can you profile this service and tell me what's slow?"
- "My p99 went from 200ms to 800ms, find out why"
- "Why does this bench run so differently on CI than locally?"
- "Capture a flamegraph for the request handler"
- "Help me set up a performance regression gate for this PR"
- "The archive batch is hitting fsync limits, diagnose"
- "Benchmark FrankenSQLite vs C SQLite fairly on concurrent writers"
- "My Rust binary is using too much RAM, find the leak"
- "Is this workload memory-bandwidth-bound or CPU-bound?"
- "Profile this Python script — it's taking 5 minutes to do 10 seconds of work"
- "btrfs is fragmenting; how do I check and fix that for our DB file?"
- "Scaling-law analysis across batch sizes 1 / 10 / 100 / 1000"
- "Add prompt caching instrumentation to our Claude API calls and measure TTFT"
- "Honest-gate audit on our comparison bench"
- "Generate the hotspot table from this week's profile run"

## Should also activate (adjacent triggers)

- "Why is my container running 20% slower than bare metal?"
- "Too many small files; readdir is slow"
- "p99 is 10× p50, what does that mean?"
- "I have 512GB of RAM free — can I use it to make this faster?"
- "Live-attach profiler to pid 1234 without restarting"

## Should NOT activate (negative cases)

- "Fix the typo in README"
- "Deploy to production"
- "Why does this test fail?"                   (→ general debugging)
- "Set up linting rules"
- "Write a blog post about X"
- "How do I use Kubernetes?"
- "Refactor this function for readability"
- "Add a new API endpoint"
- "Create a new user in the database"

## Partial / boundary cases

These may trigger but should probably defer to a closer skill:

- "My process is hung — why?"                  → `gdb-for-debugging` (state inspection) + this skill (if the hang correlates with profile)
- "Find the data race"                          → `deadlock-finder-and-fixer` (primary) + this skill (profile to isolate)
- "Our Postgres queries are slow"               → `supabase:supabase-postgres-best-practices` (primary) + this skill's DATABASE-PROFILING.md
- "Set up CI for a new project"                 → `gh-actions` (primary) + this skill's CI-REGRESSION-GATES.md

## Test with Haiku

`sw/SKILL.md` warns: a skill that works on Opus may fail on Haiku. After any trigger-description change, run a Haiku-model test:
- Trigger three positive cases
- Trigger three negative cases
- Confirm positive triggers activate, negative don't

If Haiku gets one wrong, the description needs more explicit trigger words.

## Running the self-test

```bash
# Use the writing-skills test-triggers harness:
../sw/scripts/test-triggers.py SELF-TEST.md
# Or manually: ask Claude each phrase in a fresh session and see if the skill loads.
```

## Maintaining this file

When you catch the skill mis-triggering in real use (either activating when it shouldn't, or not activating when it should), add the phrase here with the correct expectation. This file is the skill's test suite.
