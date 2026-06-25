# General Fixed-Point Slice

`FPS-v1` is the input and `FPSR-v1` is the result.

The driver does not author the semantic route.

The driver verifies:

```text
current artifact state
current GCR/ASL chain
selected owner/invariant/rows
normal form
boundary
surface budget
proof obligations
stop conditions
```

On a new observation, emit `return_to_frontier`.

See the schemas in `$fixed-point-driver/SKILL.md` and the examples under `assets/`.

## EPG mode

EPG-guided execution uses the same FPS-v1/FPSR-v1 contract with the optional policy binding described in `execution-policy-handoff.md`.
