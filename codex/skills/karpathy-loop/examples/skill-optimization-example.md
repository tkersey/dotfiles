# Skill Optimization Example

Use this when the target is another Claude Skill or a long agent instruction.

```text
Run a Karpathy loop on this Claude Skill.

Target skill:
[paste SKILL.md]

Goal:
Make the skill easier to trigger, more reliable during execution, and more concise while preserving all important behavior.

Test cases:
1. User asks directly for the workflow the skill handles.
2. User asks indirectly for the same workflow.
3. User asks for a related but out-of-scope workflow.
4. User provides incomplete inputs.
5. User asks for an artifact package.

Success checks:
1. Does the description clearly indicate when the skill should trigger?
2. Does the skill avoid triggering for out-of-scope requests?
3. Does the workflow have clear step-by-step execution instructions?
4. Does the skill specify what to do when inputs are missing?
5. Does the final output format match the user’s likely need?
6. Is the skill concise enough to avoid unnecessary context bloat?

Budget:
Run 4 experiments.
```
