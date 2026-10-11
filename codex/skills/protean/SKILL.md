---
name: protean
description: >-
  Author, compile, execute, inspect, and reuse computations with Protean, Horos,
  and native Kronos. Use for general typed programs, explicit effects and retained
  continuations, or constructing a reusable tool from admitted components. Not
  limited to the adaptive agent's precompiled tool catalog.
metadata:
  version: "1.0.0"
---

# Protean computations

Turn the requested behavior into an executable computation, run it, and return
its actual result. Horos (formerly Boundary) owns checked construction and
compilation; Kronos (formerly World) executes the program; Protean (formerly
Agent) supplies reusable agent constructions and native environmental capabilities.
This is a skill for the **coding agent**, not instructions to launch another model.

Prefer an adequate existing command or admitted program. Use this ecosystem when
its typed composition, explicit effects, retained execution, or reusable program
artifact materially helps the task. Do not require a framework for simple work.

## Choose the right construction route

| Need | Route |
| --- | --- |
| A new algorithm, control structure, type, or procedure outside the frozen tool catalog | Author Zig using the actual Horos/Protean APIs; emit an ordinary program and execute it with native Kronos. |
| A pure procedure expressible by components already admitted to a Protean task | Use that task's real `tool_build` and `tool_run` interface. |
| Model reasoning, interactive work, or existing native capabilities | Use the actual Protean authored/native host path, including `addNativeSystem` when building an application. |

The component route is a subset, not the general programming interface. Do not
force every computation into its current tables, predicates, or input schemas.
Conversely, general authoring does not make arbitrary native code a Kronos
program: the relevant algorithm and control must be lowered into the actual
Horos program representation, not computed by an emitter or a host callback.
Pure computation needs no model, provider credential, or SQLite task host unless
its actual execution path requires that host's persistence or interaction.

## Resolve the real interface before writing code

Read [the native workflow](references/native-workflow.md) when selecting a build,
execution, or tool-construction path. Resolve the current checkout, accepted
source/dependency identities, compiler pin, public exports, and build help. Use
`$zig` for version-specific language/build work and `$universalist` for a live
semantic boundary decision; neither requires a new planning artifact.

Use the names and paths the selected revisions actually export. A repository
rename does not imply that its source/API rename has landed. Do not resurrect
retired JavaScript runtimes, invent compatibility aliases, or hand-edit package
hashes. Do not assume a proposed skills-zig computation CLI exists: consult its
actual installed help and published contract before invoking one.

## Derive the computation, not a staged answer

Establish inputs, output relationships, important distinctions, failure behavior,
and necessary effects. Derive the smallest adequate representation and operations
together. For a join, distinguish missing evidence from disagreement; for a
traversal, account for every required input rather than accepting a plausible
partial result. Parameterize incidental values so the program works on another
compatible input. Do not embed the expected answer or perform the requested
analysis in fixture decoding.

For general authoring, use existing typed construction, functions, recursion,
iteration, branching, handlers, and ownership facilities where the actual API
supports them. Introduce a missing ordinary computation in the caller's code,
not a new interpreter or a complete goal disguised as a primitive. Use Protean
constructions when they provide needed semantics; direct Horos authoring plus
Kronos is sufficient for a pure program. Missing expressiveness is a concrete
implementation question, not evidence that the frozen component catalog is the
limit of the entire system.

Keep external work behind declared effects and explicitly authorized handlers.
Writing a program does not authorize filesystem access, network calls, publication,
credential discovery, or a model call. Compiling/running Zig build code is a real
local execution action, not a sandbox supplied by Horos admission. Use the
existing authorized workspace/isolation boundary; do not execute untrusted build
code merely because its output will be checked.

## Compile once; execute the actual program

Use the selected public build/authoring path. Compilation produces the canonical
program and its real interfaces. The build host runs emitters; a cross-compiled
target is not a build-time generator. Zig is an authoring/build dependency, not a
requirement to execute an already compiled program through a prebuilt native host.

Run the exact admitted image and compatible input through Kronos. Preserve the
three separate claims: structurally admitted, authorized to execute, and correct
for the requested task. A digest identifies bytes; a successful link is not a
proof of natural-language intent. Use independent expected relationships and an
informative alternate input where useful. Do not add a permanent suite for every
scratch computation or claim checks that were not executed.

For the component route, discover the actual catalog and contracts, submit the
complete supported recipe, inspect real diagnostics, and use the returned exact
program/input references. `tool_build` and `tool_run` are model actions in the
adaptive application; they are **not automatically shell commands or public
JSON-RPC methods**. A shell-capable coding agent must use an actual available
native API/command path, not fabricate provider messages to gain access to them.

On rejection, repair the first causal defect while preserving the requirement.
Do not weaken authority checks, fabricate bindings, or substitute a scripted
answer. An unavailable interface must be reported accurately; useful independent
authoring work can continue without pretending execution succeeded.

## Effects, continuation, and recovery

Observe Kronos's real outcome. Completed, failed, cancelled, yielded, and requested
work are distinct. A request is not permission to execute it. Serve only an
admitted effect, or return the actual pending request and checkpoint to its caller.
Do not coerce suspension or missing capability into success.

Use the existing Prepared/Resident or invocation owner appropriate to the host.
Bind replies to the exact outstanding request and schema. Preserve the original
program, state, resource and occurrence identities across suspension and recovery.
A saved continuation is not a transcript summary. Acquired external responses are
reused through their real owner; unknown delivery remains unknown, not a blind
retry. Checkpoint copying does not establish distributed custody.

## No arbitrary limits or extra machinery

Do not introduce arbitrary call, work, control, skill, retry, tool-build/run,
spending, or elapsed-time quotas, nor replace them with a huge sentinel number.
Keep accounting separate from permission to continue. Use runtime quanta for
responsive scheduling/cancellation, not as a cumulative stopping allowance.
Actual provider constraints, checked arithmetic, available resources and required
authorization remain real. An encountered capacity boundary must identify its
actual cause; do not call a guessed ceiling a physical limit.

An older selected build may still enforce limits. Do not bypass them, reset
counters, split a task to replenish them, or claim they have been removed. Explain
the blocking owner and make an authorized correction when it belongs to the task.
Do not propagate those old limits into new code or this skill's defaults.

Keep one computation and one executor. No JavaScript/Python production counterpart,
second adaptive loop, recipe interpreter, scheduler, model hidden inside a builder,
per-program skill generator, quota service, or evidence warehouse. A future CLI
is a thin native caller of existing owners, not a new execution semantics.

## Deliver usable work

Return the source or admitted composition, exact program/interface identity,
a concise invocation using the **verified available** interface, actual result
or pending state, and consequential limitations. Reuse the same program on new
inputs without synthesis when its contract permits. Retain only artifacts needed
for use, authorized recovery, or requested delivery; do not publish private
captures or opaque reasoning. Temporary investigations stay out of the codebase.

For explicitly authorized inference, use the user's selected default—currently
Astra at medium—and make purposeful switch tests return to it promptly. Resolve
the approved concrete model ID from current configuration; do not override a
caller-selected profile or add an LLM to deterministic work.
