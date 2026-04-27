# Reading Flame Graphs — The Canonical Skill

> Flame graphs are the single most common perf artifact. They look simple. They are not. This reference turns a wall of boxes into a decision.

Canonical source: Brendan Gregg — https://www.brendangregg.com/flamegraphs.html

## Contents

1. [Axis mechanics (what the picture actually means)](#axis-mechanics-what-the-picture-actually-means)
2. [Shapes and their meanings](#shapes-and-their-meanings)
3. [The four things you look for first](#the-four-things-you-look-for-first)
4. [Differential flame graphs](#differential-flame-graphs)
5. [Off-CPU flame graphs](#off-cpu-flame-graphs)
6. [Icicle graphs and speedscope](#icicle-graphs-and-speedscope)
7. [Color conventions](#color-conventions)
8. [Common misreadings](#common-misreadings)
9. [The interactive viewer keyboard cheat sheet](#the-interactive-viewer-keyboard-cheat-sheet)
10. [Per-language flame gotchas](#per-language-flame-gotchas)
11. [Structured exercises](#structured-exercises)

---

## Axis mechanics (what the picture actually means)

- **Y-axis**: call-stack depth. Bottom = earliest caller. Top = currently running function (the leaf).
- **X-axis**: proportion of samples that ended in that frame. NOT time along the X. A wide bar means that stack captured a lot of samples, i.e., that code was on CPU a lot.
- **X-axis is sorted alphabetically by default**, not chronologically. You cannot read "first this happened, then that" across the X.
- **One sample = one stack = one vertical line** of the flame. A dense region at depth 10 just means many samples were 10-deep there.
- **Width is proportional to aggregate time on CPU** (or aggregate samples, if sampling at fixed rate).

If you remember one rule: **widest box = hottest function.**

If you remember two: **wide box at the top (leaf) = directly doing work. Wide box at the bottom (root) = its callee is hot, not it.**

---

## Shapes and their meanings

### The plateau (wide, flat leaf)

```
      ┌──────────────┐
      │ hot_function │  ← widest at the top, wide shelf
      ├──────────────┤
      │    caller    │
      └──────────────┘
```

**Meaning**: hot_function is directly burning CPU. Inline, micro-optimize, algorithmically replace.

### The tall, narrow tower

```
      ┌┐
      ││ leaf_42       ← thin at top
      ├┤
      │caller_41       ← thin at every level
      ├┤
      ...             ← deep
      ├┤
      └┘  root
```

**Meaning**: deep call stack but not a lot of time. This is fine unless you see the SAME tower appear many times (in which case the TOTAL width across copies is the signal).

### The staircase (recursion)

```
  ┌──────┐
  │ f    │
  ├──────┼──────┐
  │ f    │ f    │
  ├──────┼──────┼──────┐
  │ f    │ f    │ f    │
  └──────┴──────┴──────┘
```

**Meaning**: recursive function; total width across all `f` boxes = total time in `f`. If it's deep AND wide, consider tail-calling or iterative rewrite.

### The broad flat base

```
┌──────────────────────────────────────────────┐
│  tokio::runtime::worker::run                 │
├────┬────┬────┬────┬────┬────┬────┬────┬──────┤
│... │... │... │... │... │... │... │... │ ...  │
└────┴────┴────┴────┴────┴────┴────┴────┴──────┘
```

**Meaning**: runtime / dispatcher on bottom, many different work items on top. Width of the base is total CPU; widths of the top-level children tell you which task types dominated.

Look at the second layer, not the base. The base will always be wide on an async runtime.

### The "where's my function?" missing bar

You look for `hot_function` expected to be hot; it's not visible.

**Possible reasons**:
1. **Inlined** by the compiler — the leaf you see is actually your function, labeled as the caller
2. **Stripped symbols** — the frame is `??`
3. **Not actually hot** — your belief about the hot path was wrong (apply `◊ Paradox-Hunt`)
4. **Different binary / profile** — you profiled a release build without symbols

Fix by: rebuild with `[profile.release-perf] debug = "line-tables-only"` (Rust), `-fno-omit-frame-pointer -g` (C/C++), and re-run.

### The spiky-top (sampling noise)

Many narrow bars at the leaves, no clear dominant.

**Possible reasons**:
1. **Workload is diverse** — nothing is actually dominant; profile-guided optimization won't help much; consider algorithmic changes
2. **Sampling rate too low** — raise `--freq=997` (perf) or `samply`'s sampling rate
3. **Wrong sampling axis** — maybe you should be looking at alloc, not CPU

### The "everything is one call"

Single wide bar across the whole flame, no detail.

**Possible reasons**:
1. **Symbols missing** — everything is `unknown` under one name
2. **LTO fused everything** — `lto="fat"` can merge cross-crate into one symbol
3. **You're profiling the wrong process** — check `pgrep`

---

## The four things you look for first

Do these in order. Stop when you have a target.

### 1. Widest top-level bars (after the runtime base)

Ignore the event-loop / scheduler at the very bottom. Look at the **widest bars one level up**. Those are your application's top-of-stack hot functions.

### 2. Wide bars at medium depth (5-10 frames in)

These are "fat middle" patterns — a function spending a lot of time in its own body (not in a single hot callee). Candidates for algorithmic rewrite.

### 3. Patterns that appear multiple places

If `alloc::raw_vec::RawVec::reserve` is wide in 4 different towers, you have a **cross-cutting** allocation problem. Often fixed with a single upstream change (pre-size, `with_capacity`).

### 4. Known-suspicious frames

| Language | Suspicious frame | What it means |
|----------|------------------|---------------|
| Rust | `alloc::raw_vec::RawVec::reserve_for_push` | Vec growth; pre-size |
| Rust | `core::ptr::drop_in_place` | Destruction cost; consider arena |
| Rust | `hashbrown::raw::RawTable::find_insert_slot` | Hash cost; try `ahash`/`FxHash` |
| Rust | `<String as ...>::to_string` | Allocation; `&str` / `Cow` |
| Rust | `core::iter::adapters::*` chain | Iterator overhead; check for `.collect::<Vec<_>>()` |
| Go | `runtime.mallocgc` | GC pressure; `sync.Pool`, pre-allocate |
| Go | `runtime.convT*` | `interface{}` boxing; generics |
| Go | `runtime.gcAssist*` | GC assist; lower allocation rate |
| Node | `Compiled Code: *` | JIT; usually fine |
| Node | `V8::CompileFunction` | Dynamic compilation; cache |
| Node | `v8::internal::*::Add` | Map/Set / hash work |
| Python | `PyEval_EvalFrameDefault` | Interpreter overhead; vectorize |
| Python | `numpy.core._multiarray_umath.*` | Good news — you're in C |
| C++ | `operator new` | Allocation; pool / arena |
| C++ | `std::__atomic_*` | Atomics in hot path; maybe lock-free hash |
| Any | `memmove` / `memcpy` | Large copy; move, zero-copy, mmap |

---

## Differential flame graphs

When comparing "before" and "after":

```bash
# Collapse both stacks to the same format
perf script -i perf.data.before | stackcollapse-perf.pl > before.folded
perf script -i perf.data.after  | stackcollapse-perf.pl > after.folded

# Differential (red = slower, blue = faster)
difffolded.pl before.folded after.folded | flamegraph.pl --title "Diff" > diff.svg
```

Read the result:
- **Red bars** = got wider (slower after change)
- **Blue bars** = got narrower (faster after change)
- **White** = unchanged
- The total sum of reds should approximately equal the total sum of blues in a zero-sum optimization

**Watch for**: a "win" that's actually moved cost elsewhere. Blue in `serialize::json` + red in `serialize::msgpack` of similar width = you reorganized, didn't optimize.

### `samply` compare

```
samply load before.json after.json
```

In Firefox Profiler, use the "Compare" tab to see frame-by-frame delta with built-in widgets.

---

## Off-CPU flame graphs

The on-CPU flame only shows time burning CPU. It hides:
- blocked on I/O
- blocked on a mutex
- blocked on a semaphore
- blocked on page fault (rare but possible)
- yielding / sleeping (scheduler chose not to run)

### How to generate

```bash
# Linux + BCC
sudo offcputime-bpfcc -p $PID 30 > offcpu.stacks
flamegraph.pl --color=io --title="Off-CPU (30s)" --countname=us < offcpu.stacks > offcpu.svg

# Canonical reference
# https://www.brendangregg.com/FlameGraphs/offcpuflamegraphs.html
```

### How to read

The **top frame is the function that called the blocking syscall/wait**:
- `futex_wait` → lock contention (find which lock)
- `io_schedule` → disk I/O (then `biosnoop` for which file)
- `epoll_wait` / `poll` → event loop idle — mostly GOOD (app is waiting for work)
- `schedule` alone → preemption / yield
- `page_fault` → working set > RAM

The Y-axis below the top frame is your application code that called it. That's where the fix lives.

### When to reach for off-CPU

Any time on-CPU says "it's not burning CPU" but wall-clock says "it's slow." `Off-CPU` usually reveals I/O or lock as the actual cause.

---

## Icicle graphs and speedscope

**Icicle** is the same data, flipped: root at the top, leaves at the bottom. Sometimes easier to scan because your eye starts at the entry point.

**Speedscope** (https://www.speedscope.app/) renders `.cpuprofile` (V8), `.folded` (Brendan Gregg), `pprof`, `trace event` (Chrome), and more. Three views:
- Time-order (chronological, useful for one-shot scripts)
- Left-heavy (similar to icicle, sorted)
- Sandwich (caller + callee side-by-side for a selected frame)

**Firefox Profiler** (https://profiler.firefox.com/) is samply's default viewer. Has:
- Call tree (tree view, sortable by total / self time)
- Flame graph (traditional)
- Stack chart (timeline view — this is useful for periodic events)
- Marker chart (for instrumented spans)

---

## Color conventions

Default `flamegraph.pl` uses hue by function name (stable across runs, so diffs look right):
- Warm hues (red/orange/yellow) = user code
- Cool hues = system / kernel (when merged)

With `--color=io`, the scheme is:
- Red = user application
- Orange = user syscall / library
- Yellow = Java-like runtime
- Green = C++
- Aqua = JIT-compiled
- Blue = kernel

For differential, hues become red (slower) / blue (faster) — overrides the default scheme.

`samply` / Firefox Profiler has a similar but richer palette with category tags you can filter by.

---

## Common misreadings

| Misreading | What's really true |
|-----------|--------------------|
| "This is the slowest function" (tall, narrow) | It's the deepest stack; slowest = widest, not tallest |
| "The X axis is time" | X axis is aggregate sample count, NOT time |
| "This wide bar at the bottom is the problem" | The bottom is the caller (e.g., `main`, event loop). Look at the leaf. |
| "I don't see `my_fn`, so it's not called" | It was inlined. Check compiler output or disable inlining for profile-builds |
| "The flame changed between runs, therefore the code did" | Sampling variance changes bars run-to-run; aggregate ≥ 30s before concluding |
| "100% CPU in the flame = app is CPU-bound" | Only the sampled process is shown; system-wide contention is invisible here |
| "Idle time missing" | On-CPU flame hides waits. For waits, off-CPU flame |
| "Red is bad" in a normal (non-diff) flame | Red is just a hue in the default palette, not a severity |

---

## The interactive viewer keyboard cheat sheet

### Firefox Profiler / `samply` output

- `/` — search function name
- `Ctrl+F` — same
- Click a bar — filter call tree to that stack
- Double-click a bar — zoom to that subtree
- `Esc` — clear zoom
- Timeline drag — restrict to a time window (crucial for "show me just this 500ms spike")
- Marker track — toggles instrumented spans and GC events

### Speedscope

- `1 / 2 / 3` — switch between Time Order / Left Heavy / Sandwich
- `/` — search
- Click — zoom on function
- `Esc` — unzoom

### `flamegraph.pl` SVG (open in browser)

- Click a bar — zoom to subtree
- "Reset zoom" — button in corner
- "Search" — find function names matching a regex

---

## Per-language flame gotchas

### Rust

- `lto = "thin"` is fine for profiling. `lto = "fat"` can merge cross-crate into inscrutable single frames.
- `panic = "abort"` skips unwind tables → backtraces on panic disappear from the flame; use `panic = "unwind"` for profile builds.
- Release default `opt-level=3` inlines aggressively. `[profile.release-perf] opt-level = 3, debug = "line-tables-only"` keeps the flame readable without losing speed.
- `samply` gives you Firefox Profiler UI with much better zoom/search than `flamegraph.pl` SVGs.
- `cargo flamegraph` uses `perf` under the hood on Linux, `dtrace` on macOS (limited; prefer `samply`).

### Go

- Goroutines: `pprof` flame shows on-CPU stacks per goroutine; `go tool trace` shows scheduler / GC timeline.
- Go's `runtime.*` frames are numerous; `focus` the viewer on non-runtime frames to clarify.
- `pprof -focus <regex>` filters the flame to stacks matching your regex.

### Node / TypeScript

- `--prof` + `--prof-process` gives V8 tick flame; poor symbol resolution compared to `clinic flame` or `0x`.
- `clinic flame` uses `0x` and adds instrumentation heuristics. Recommended default.
- JIT frames (`Compiled Code: *`) are opaque; search for names of your top-level functions.

### Python

- `py-spy record` generates a flame compatible with `flamegraph.pl`. Default sampling rate is 100 Hz; raise with `--rate 250` for short scripts.
- `scalene` shows CPU AND memory AND Python-vs-native split — richer than a pure flame.
- `viztracer` shows a chronological timeline (not a flame). Good for "where did my request spend its 200ms?"

### C/C++

- `perf record -g --call-graph dwarf` is canonical but DWARF-based unwinding is slow/large. Prefer `--call-graph fp` with frame pointers forced on.
- Hot inlined functions in release builds can vanish; a "wide bar at a higher frame" often represents a chain of inlined callees.
- Use `addr2line` to resolve raw addresses if symbols are partial.

---

## Structured exercises

Learn to read flames faster by practicing on known-good artifacts. This skill's `tests/artifacts/perf/` is one source; public flames are another.

### Exercise 1: Identify the hottest top-level function

1. Open the most recent flamegraph for the benchmark under investigation.
2. Ignore the bottom 3 frames (runtime).
3. Find the widest 4th-level frame.
4. Record its name and the proportion (eyeball "is it 40%? 10%?").
5. Cross-check against `span_summary.json` top row. They should agree within 20%.

If they disagree, one of them is measuring something the other isn't (sampling vs spans). Reconcile.

### Exercise 2: Spot an allocation pattern

1. Open any recent flame.
2. Ctrl-F for `RawVec::reserve`, `Box::new`, `alloc::alloc`.
3. Note the aggregate width (sum across all matches).
4. If > 15% of the flame, allocation is a hotspot; plan an alloc-axis profile (heaptrack, DHAT).

### Exercise 3: Prove a hypothesis

1. Pick a hypothesis from hypothesis.md that says "the bottleneck is X."
2. Ctrl-F for `X` in the flame.
3. Measure the aggregate width (a range of bars, summed).
4. If the width doesn't match the hypothesis (too small to matter or way bigger than expected), the hypothesis was wrong; mark it `rejects` with the flame artifact as evidence.

### Exercise 4: Flame diff

1. Run the baseline bench, save flame A.
2. Apply one optimization.
3. Run again, save flame B.
4. Generate `diff.svg` (see §Differential flame graphs).
5. Find the largest red bar. That's a new cost introduced by the change.
6. Find the largest blue bar. That's what the change actually optimized.
7. If the blue is smaller than the red, the optimization regressed; roll back.

---

## Flame-graph checklist (pre-profile)

- [ ] Frame pointers present (`-C force-frame-pointers=yes` or `-fno-omit-frame-pointer`)
- [ ] Symbols present (`debug = "line-tables-only"` minimum)
- [ ] Build profile is NOT size-optimized (`opt-level != "z"`)
- [ ] Workload duration ≥ 30s (enough samples for stable widths)
- [ ] Sampling frequency ≥ 99 Hz (`perf record -F 997` or `samply` default 1000 Hz)
- [ ] Only one sampler running
- [ ] Fingerprint captured alongside the `.svg` / `.json`

If any unchecked, the flame is advisory at best.
