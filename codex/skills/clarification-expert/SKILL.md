---
name: clarification-expert
description: Clarify ambiguous requests by researching first, then asking only judgment calls; stop before implementation.
---

# Clarification Expert

## When to use
- The request is ambiguous, under-specified, or missing success criteria.
- The user asks to “build a system”, “optimize”, “make it better”, or “how do I”.
- Requirements conflict, or trade-offs are implicit.

## Quick start
1. Research first; don’t ask for discoverable facts.
2. Maintain a running snapshot (facts, decisions, open questions).
3. Ask only judgment calls: prefer 1 question, never exceed 3 per batch (use `request_user_input` if available; otherwise note it is unavailable and use the Human input block).
4. Incorporate answers and repeat until no open questions remain.
5. Generate verbose beads, then stop (no implementation).

## Asking questions (tool-aware)
- Maintain an ordered queue of open questions.
- Ask questions in batches: prefer 1; use up to 3 only when the questions are independent (no ordering dependency).
- If a tool named `request_user_input` is available, use it (do not render the fallback Human input block).
- Otherwise, add a one-line note that the tool is unavailable, then render the fallback Human input block (below).
- After receiving answers, update the Snapshot and refresh the open-question queue:
  - remove answered questions
  - append newly discovered open questions (including follow-ups triggered by the answers)
  - continue looping until the queue is empty

### Loop pseudocode
```text
open_questions := initial judgment calls (ordered)
answered_ids := set()

while open_questions not empty:
  batch := take_next(open_questions, max=3, prefer=1)

  if tool_exists("request_user_input"):
    tool_args := { questions: batch_to_tool_questions(batch) }
    raw := call request_user_input(tool_args)
    resp := parse_json(raw)
    answers_by_id := resp.answers
  else:
    note "request_user_input not available; using fallback"
    render fallback numbered block for batch
    answers_by_id := extract answers from user reply

  for q in batch:
    a := answers_by_id[q.id].answers (may be missing/empty)
    if a missing/empty and q still required:
      keep q in open_questions (re-ask; rephrase; same id)
    else:
      remove q from open_questions
      answered_ids.add(q.id)
      update Snapshot with facts/decisions from a

  followups := derive_followups(answers_by_id, Snapshot) using rules below
  enqueue followups:
    - if a follow-up blocks other questions, prepend it
    - otherwise append it
    - dedupe by id against open_questions and answered_ids
```

### Follow-up derivation rules
Only create a follow-up when it is a judgment call required to proceed. Apply these rules in order:

- If an answer expands scope ("also", "while you’re at it", "and then"), add: "Is this in scope for this request?" with options include/exclude.
- If an answer introduces a dependency ("depends on", "only if", "unless"), add: "Which condition should we assume?" (options if you can name them; otherwise free-form).
- If an answer reveals competing priorities (speed vs safety, UX vs consistency, etc.), add: "Which should we prioritize?" with 2-3 explicit choices.
- If an answer contains a user_note with multiple distinct requirements, split into multiple follow-up questions (but keep each question single-sentence).
- If a follow-up would ask for a discoverable fact, do not ask it; instead, treat it as a research action and update Snapshot Facts after inspecting the repo.

Follow-up hygiene:
- Assign each follow-up a stable snake_case `id` derived from intent (not position), and keep the same id if you later re-ask it.
- Choose `header` <= 12 chars (tight noun/verb), and keep the `question` single-sentence.
- Prefer options when the space of answers is small; omit options for genuinely free-form prompts.

## `request_user_input` (preferred)
When available, ask questions via a tool call with up to 3 questions.

### Call shape
- Provide `questions: [...]` with 1-3 items.
- Each item must include:
  - `id`: stable snake_case identifier (used to map answers)
  - `header`: short UI label (12 chars or fewer)
  - `question`: single-sentence prompt
  - `options` (optional): 2-3 mutually exclusive choices
    - put the recommended option first and suffix its label with "(Recommended)"
    - only include an "Other" option if you explicitly want a free-form option
    - if the question is free-form, omit `options` entirely
- If you need to re-ask the same conceptual question (rephrased), keep the same `id`.

Example:
```json
{
  "questions": [
    {
      "id": "deploy_target",
      "header": "Deploy",
      "question": "Where should this ship first?",
      "options": [
        { "label": "Staging (Recommended)", "description": "Validate safely before production." },
        { "label": "Production", "description": "Ship directly to end users." }
      ]
    }
  ]
}
```

### Response shape
The tool returns a JSON payload with an `answers` map keyed by question id:
```json
{
  "answers": {
    "deploy_target": { "answers": ["Staging (Recommended)", "user_note: please also update the docs"] }
  }
}
```
In some runtimes this arrives as a JSON-serialized string in the tool output content; parse it as JSON before reading `answers`.

### Answer handling
- Treat each `answers[<id>].answers` as user-provided strings.
- In the TUI flow:
  - option questions typically return the selected option label, plus an optional `user_note: ...`
  - free-form questions return only the note (and may be empty if the user submits nothing)
- If the question used options and you suffixed the recommended option label with ` (Recommended)`, the selected label may include that suffix; strip it when interpreting intent.
- If an entry starts with `user_note:`, treat it as free-form context and mine it for facts/decisions/follow-ups.
- If an answer is missing/empty for a question you still need, keep it in the queue and re-ask (possibly rephrased or with options).

## Snapshot template
```
Snapshot
- Facts:
- Decisions:
- Open questions:
```

## Human input block (fallback)
If `request_user_input` is not available, add a one-line note that it is unavailable, then use this exact heading and numbered list:
```
CLARIFICATION EXPERT: HUMAN INPUT REQUIRED
1. ...
2. ...
3. ...
```

## Guardrails
- Never ask what the code can reveal; inspect the repo first.
- Keep questions minimal and sequential.
- After bead creation, hard-stop.

## Deliverable format
- Snapshot.
- Ask for answers (use `request_user_input` if available; otherwise use the Human input block).
- One-line Insights/Next Steps.

## Activation cues
- "clarify"
- "ambiguous"
- "build a system"
- "make it better"
- "optimize this"
- "how do I"
- "unclear goal"
- "conflicting requirements"
