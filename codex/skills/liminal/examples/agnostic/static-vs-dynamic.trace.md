# Static versus Dynamic Delimited Control Trace

This trace is a language-neutral witness scaffold. It is intended to make the extra delimiter in `shift/reset` visible before translating the example into a concrete host language.

## Shared context

Let `E[x] = 1 + x`.

## Static control: `shift/reset`

```text
reset E[shift k . BODY]
-> reset((lambda k. BODY) (lambda x. reset E[x]))
```

Captured continuation:

```text
k_static = lambda x. reset(1 + x)
```

The resumed continuation is re-delimited. If `BODY` resumes `k_static` and that resumed computation performs another capture, the capture sees the reinstated `reset` boundary.

## Dynamic control: `control/prompt`

```text
prompt E[control k . BODY]
-> prompt((lambda k. BODY) (lambda x. E[x]))
```

Captured continuation:

```text
k_dynamic = lambda x. 1 + x
```

The resumed continuation is not wrapped in the same extra delimiter. If `BODY` resumes `k_dynamic` and that resumed computation performs another capture, the dynamic boundary story differs.

## Witness obligation

For a full answer, instantiate `BODY` with either:

1. a nested-resume expression where a later capture observes the reinstated delimiter, or
2. a BFS-style traversal where the traversal order depends on static versus dynamic extent.

Source anchors: `[DC-AC-1990]`, `[DC-DYN-2005]`, `[DC-STC-2004]`.
