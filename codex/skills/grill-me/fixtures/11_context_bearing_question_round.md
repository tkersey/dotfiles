# Context-bearing question round

User asks: "grill me on replacing our billing export pipeline."

Expected:
- Emit a compact Question context block before asking questions.
- Include Current frame, Evidence basis, Why now, and What this decides.
- Do not emit Snapshot, grill_decision_packet, plan, spec, implementation steps, or <proposed_plan> while material unknowns remain.
- Ask 1-3 bounded-choice questions with stable snake_case IDs.
- Each question must be understandable from the immediately preceding context.
