# PR Readiness Policy

Default PR mode is `ready`.

Use `draft` only when:

- user explicitly requests draft;
- validation is incomplete/blocked/failing/caveated;
- in-scope tasks remain blocked/deferred/open;
- early visibility is explicitly intended;
- required context is missing and user asks to publish anyway;
- repo policy requires draft.

If work is complete and validation passes, create a ready PR by default.

Do not pass `--draft` unless `pr_readiness.mode: draft`.
