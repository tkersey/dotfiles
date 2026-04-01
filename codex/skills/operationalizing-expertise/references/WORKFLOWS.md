# Workflows (Full Steps)

## Track A: Static Distillation (corpus -> kernel)

1) Corpus assembly
- Normalize transcripts and split into stable segments.
- Establish an anchor scheme (e.g., §1..§N) and keep it immutable.

2) Quote bank
- Extract high-signal quotes with tags.
- Enforce sequential anchors and minimum counts.

3) Multi-model distillation
- Run 3 models on the same sources (GPT/Opus/Gemini).
- Store raw responses verbatim for provenance.

4) Triangulated kernel
- Keep only consensus items.
- Include output contract (what the system must produce).

5) Operator library
- Convert operators into prompt modules.
- Require triggers + failure modes + anchors.

6) Validation
- Run structure checks and anchor validation.
- Fail fast in CI.

## Track B: Orchestrated Artifact Loop (kickoff -> deltas -> artifact)

1) Join-key contract
- Example: `RS-YYYYMMDD-topic` or `<bead-id>`.
- Use the same ID for mail thread, artifact filename, and session handle.

2) Kickoff prompts
- Embed kernel and operator cards.
- Assign roles to agents (hypothesis, test design, critique, synthesis).

3) Delta capture
- Require structured deltas in agent outputs.
- Normalize invalid fields rather than discarding everything.

4) Deterministic merge + lint
- Merge deltas into a structured artifact.
- Lint for missing third-alternative, missing anchors, or invalid sections.

5) Persistence + indexes
- Store session artifacts per thread_id.
- Maintain cross-session indexes for search and replay.

6) (Optional) Memory loop
- Extract only high-confidence rules.
- Store provenance + human review notes.

