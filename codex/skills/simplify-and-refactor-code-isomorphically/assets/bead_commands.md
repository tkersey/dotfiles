# Beads (br) cheat commands — refactor workflow

> `br` is the local issue tracker. Use it to turn this pass's candidates and
> rejections into trackable beads so the work survives session boundaries.

## Create a bead per candidate

```bash
br create \
  --title "ISO-014 — collapse parse_header across tcp/tls" \
  --label refactor --label pass-1 \
  --body-file refactor/artifacts/<run-id>/cards/ISO-014.md
```

## Link beads to commits

```bash
br link <bead-id> --commit <sha>
```

## Close a bead after merge

```bash
br close <bead-id> --reason shipped --commit <sha>
```

## Close a bead as rejected (keep the reason!)

```bash
br close <bead-id> --reason rejected --body-file refactor/artifacts/<run-id>/rejections/ISO-014.md
```

## Find this pass's beads

```bash
br list --label refactor --label pass-1 --status any
```

## Export a pass summary to paste into the PR

```bash
br list --label refactor --label pass-1 --status any --format markdown > /tmp/pass-1-summary.md
```

## Bead patterns for horror-story prevention

- One bead per candidate — never "cleanup sweep" beads.
- If a candidate turns out to span multiple levers, close the parent, create
  one child bead per lever, and link them all to the original.
- Rejected candidates are NOT failures — they are investigated and documented.
  Close with `--reason rejected`, never delete.
