# Review Result Contract

Normalize every review run:

```yaml
review_result:
  clean:
  backend_class:
  target_fingerprint:
  tool_completed:
  base_ref:
  base_sha:
  head_sha:
  invocation:
  raw_output_ref:
  findings: []
```

A clean review requires successful completion, reliable parse, zero substantive findings/comments/notes, and matching pinned backend/base/head/fingerprint.
