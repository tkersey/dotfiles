# Canonical Markers and Formats

## Kernel markers
```markdown
<!-- TRIANGULATED_KERNEL_START vX.Y -->
...kernel content...
<!-- TRIANGULATED_KERNEL_END vX.Y -->
```

## Quote bank entry (minimal)
```markdown
## §42 — Source Title, Page 12
> "Verbatim quote..."
— Source: CORPUS.md, Source Title, Page 12
Tags: conception, disclosure, testing
```

## Operator card (minimum fields)
```markdown
### Operator Name

**Definition**: One sentence.
**When-to-Use Triggers**:
- ...
**Failure Modes**:
- ...
**Prompt Module**:
~~~text
[OPERATOR: name]
Steps...
~~~
**Canonical tag**: operator-tag
**Quote-bank anchors**: §12, §33
```

## Delta block (for Track B)
```json
{
  "operation": "ADD",
  "section": "hypothesis_slate",
  "target_id": null,
  "payload": { "name": "H1", "claim": "...", "mechanism": "..." },
  "rationale": "why"
}
```

