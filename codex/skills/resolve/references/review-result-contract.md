# Review Result Contract

Every review backend must normalize into this shape:

```yaml
review_result:
  clean: true|false
  backend_class: cas-lane | native-cli | cas-native-fallback
  target_fingerprint: string|null
  tool_completed: true|false
  exit_status: integer|null
  base_ref: string
  base_sha: string
  head_sha: string
  invocation: string
  sandbox_mode: string|null
  raw_output_ref: string
  findings:
    - id:
      file:
      line_range:
      severity:
      body:
      suggested_fix:
```

## Clean review rule

A review run is clean only when:

- tool completed successfully;
- output explicitly indicates no findings/comments, or parser proves an empty finding list under documented format;
- no inline comments, requested changes, warnings, or substantive notes exist;
- backend class matches current streak pins or starts a new streak;
- target fingerprint matches when supplied or starts a new streak;
- base ref, base SHA, and `HEAD` SHA match current streak pins or start a new streak.

## Not clean

Treat as not clean:

- tool failure;
- missing or ambiguous output;
- partial output;
- transport failure;
- parser failure;
- review comments hidden in unparsed output;
- unexpected base;
- different `HEAD`.

## Streak pinning

When `clean_review_streak == 0`, the next clean review can establish:

```yaml
streak_base_ref:
streak_base_sha:
streak_head_sha:
streak_review_backend:
streak_target_fingerprint:
```

Subsequent clean reviews must match pins. Otherwise reset and start a new streak only after the next clean review.
