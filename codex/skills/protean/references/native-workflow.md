# Native computation workflow

This reference separates available interfaces from a proposed convenience CLI.
The inspected Protean source was `6f4c6f48b9edec6ec597d0b6ad62cbdf8a09a43d`:
repository URLs used the new names while source still used `agent`, `boundary`,
`world`, and `adaptive-agent`. Resolve the consuming project's actual pins and
exports; these historical spellings are inspection leads, not a fallback stack.
Kronos references below are mutable documentation locations, not dependency pins.

## 1. General authored computation: the broad route

Use the ordinary construction API, not `tool_build`'s finite component vocabulary.
The current public Protean entrypoints include `system`, `Context`, and `compile`;
Horos also provides direct authoring and source/data interfaces. Discover actual
signatures and a nearby current example before writing a definition.

For an application requiring Protean's native effects/task host, the public build
helper accepts caller-owned definition, types and environment paths. Adapt the
existing downstream recipe; do not copy the whole adaptive application merely to
calculate a pure result. Its inspected call shape was:

```zig
_ = agent_build.addNativeSystem(b, dependency, .{
    .name = "my-computation",
    .application = .{ .source = .{
        .definition = b.path("definition.zig"),
        .types = b.path("types.zig"),
    } },
    .environment = b.path("environment.zig"),
});
```

This is the build-helper **call shape**, not a complete runnable project. Resolve
`dependency` and `agent_build` with the actual selected package names. Implement
the exports and handler contracts required by the selected native emitter/host;
inspect `tools/native/emit.zig`, `build_native.zig`, and the retained downstream
consumer rather than inventing their interfaces. `.application.emitted` reuses an
exact image/assets/types tuple instead of regenerating it.

For pure code with no task-host requirement, use Horos compilation and Kronos's
public native module directly. The inspected exports were `Session`, `Prepared`,
`Resident`, and `invocation`. `Session.initImage(allocator, image, arguments)`
admits an image/input; the corresponding prepared/resident interfaces expose the
managed lifecycle. Inspect their current contracts for drive, outcome, output
publication, cancellation and release. Never build a second interpreter around
a JSON workflow to avoid learning the native API.

The existing build graph or a small caller-owned Zig consumer is the usable path
today. Such a consumer may encode input and observe outcomes; the computation
itself belongs in the emitted program. Do not promote a disposable driver into a
maintained application/framework merely to execute one computation.

## 2. Existing adaptive application

Use this route when an adaptive model is genuinely part of the requested work.
At the inspected snapshot, these were documented native commands, run from the
Protean checkout with exact Zig `0.17.0` and its approved source inputs:

```sh
zig run tools/native/dependencies.zig -- setup \
  conformance/agent4/dependencies.lock.json \
  conformance/agent4/native-dependencies.lock.json \
  .agent4-native/inputs "$(command -v zig)"
zig build adaptive-agent -Doptimize=safe
./zig-out/bin/adaptive-agent describe-build
./zig-out/bin/adaptive-agent --help
```

Do not run this block against renamed paths blindly. Read the selected README
and build help first; use its native replacements where naming has changed.
Do not restore deleted setup scripts or require the optional JS/WASM package.

The configured executable exposes `validate`, `run`, and
`serve --transport stdio`. Its native host uses newline-framed JSON-RPC and
advertises application schemas. Use current help/discovery for the actual
arguments and methods. An approved configuration, inference authorization and
explicit credential binding are required for provider calls. No secret search,
implicit model call, or alternate agent implementation is part of this skill.

The existing downstream build witness resides at
`test/consumers/adaptive/build.zig` in the inspected snapshot. It demonstrates the
public helper and authenticated native sources; it is not a requirement that
all new computations duplicate that example.

## 3. Approved-component construction inside an adaptive task

Read the actual loaded `tool-construction` catalog. `tool_build` accepts a
`proposal_json` string containing `instances`, `bindings`, and `entry` in the
current recipe grammar. It returns a program reference and actual contracts or
structured rejection. `tool_run` accepts `tool_ref` and `input_ref` and invokes
that program through native Kronos. References resolve within their admitted task
and policy; they are not arbitrary paths, global handles, or execution grants.

The initial generated-tool domain is pure computation over admitted values.
An external effect, new primitive, or new schema requires general authoring or a
real capability change; it cannot be invented as another recipe key. A complete
fixed solution renamed as a component does not establish new composition.

Those action names are not sufficient to call them from a coding-agent shell.
Use an actually exposed native interface or integrate the public native owners.
Do not send `{"method":"tool_build"}` to stdio without a discovered method,
forge an acquired model response, or route deterministic computation through a
paid adaptive task simply because a direct command has not been added yet.

## 4. A future skills-zig interface

No new CLI is implemented or required by this skill. Prefer a published native
computation interface when one exists; its installed help is authoritative.
A useful implementation would provide build, inspect, run, and continuation
operations around the existing owners. It must keep source compilation separate
from running a precompiled program and return typed terminal or suspended outcomes.

The CLI must not recreate Protean's model/task loop, Kronos's evaluator, Horos's
compiler/linker, their codecs, or a durable store. General authoring must remain
possible outside the adaptive component catalog. Effect requests use existing
explicit handlers or are returned to the caller; there is no implicit shell or
network authority. No arbitrary cumulative quota is introduced.

skills-zig currently supplies separate native CLIs, not an umbrella command, and
uses Homebrew/tap delivery for shipped binaries. A new command is a separate
implementation/release task, not a file hidden in this skill. A local development
binary is not an installed release. Until then, use Sections 1–3 and state any
missing convenience interface accurately.

## Source owners

- [Protean public architecture and native build](https://github.com/tkersey/protean/blob/6f4c6f48b9edec6ec597d0b6ad62cbdf8a09a43d/README.md)
- [Native downstream build call](https://github.com/tkersey/protean/blob/6f4c6f48b9edec6ec597d0b6ad62cbdf8a09a43d/test/consumers/adaptive/build.zig)
- [Original runtime construction skill](https://github.com/tkersey/protean/blob/6f4c6f48b9edec6ec597d0b6ad62cbdf8a09a43d/examples/adaptive-agent/skills/tool-construction/SKILL.md)
- [Kronos public native exports](https://github.com/tkersey/kronos/blob/main/src/root.zig) and [session owner](https://github.com/tkersey/kronos/blob/main/src/interpreter_v2/stable_session.zig)
- [Kronos execution/embedding distinction](https://github.com/tkersey/kronos/blob/main/README.md)
- [skills-zig CLI and distribution conventions](https://github.com/tkersey/skills-zig/blob/main/README.md)

These links locate implementation owners; they do not install dependencies,
authorize builds or effects, or prove that the current checkout matches them.
