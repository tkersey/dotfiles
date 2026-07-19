# Implementation reference

## What this skill wraps

Apple's `fm` CLI is preinstalled with macOS 27 and is intended for terminal use and automation. The wrapper uses the CLI directly rather than linking the Foundation Models framework or creating an application.

The noninteractive response form used by this skill is equivalent to:

```text
/usr/bin/fm respond --model system|pcc --no-stream [options] --text=<prompt>
```

Supported convenience options in `scripts/fmctl.sh` include:

- instructions: `--instructions`
- images: repeatable `--image`
- guided generation: `--schema`
- existing session history: `--load-transcript`
- deterministic sampling request: `--greedy`

Use `scripts/fmctl.sh raw respond --help` on the target Mac as the source of truth for the installed OS build.

## Why the pseudo-terminal exists

Some local agent shells do not give child commands a controlling terminal. The Private Cloud Compute access path used by `fm` may require a controlling terminal with a nonzero size. The wrapper therefore launches `fm` through Apple's `/usr/bin/script`, sets the child terminal to 24 rows by 80 columns, and keeps standard input open until the process exits.

The fixed shell program is:

```sh
stty rows 24 cols 80; exec "$@"
```

All executable paths, options, prompts, and file paths are passed positionally through `"$@"`. User-controlled content is never inserted into the shell program itself.

## Why `--no-stream` and `--text=` are used

The pseudo-terminal makes `fm` believe it is connected to an interactive terminal. `--no-stream` requests a stable final response rather than terminal-oriented incremental rendering.

Using one argument in the form `--text=<prompt>` ensures a prompt beginning with an option-looking string such as `--model pcc` remains prompt data rather than becoming another CLI option.

## Product boundary

A skill supplies a repeatable workflow and may include scripts, but it does not grant access to the user's computer by itself. The host agent must already be running locally with terminal permission. A skill installed only in a cloud or mobile session cannot execute the Mac's `/usr/bin/fm`.

## Operational limitations

- The real `fm` executable is available only on the relevant macOS release.
- PCC is remote processing and may have usage limits.
- The CLI's available flags can change with OS seeds or updates; inspect local help when an option fails.
- The `fm` CLI should be treated as a generation engine, not as a tool-calling runtime. Keep file or system actions in the parent agent and validate generated data first.
- Transcript files are accepted only when already produced in a format understood by the installed `fm`; this skill does not synthesize that format.

## Sources used for this implementation

- Apple Developer, “Build AI-powered scripts with the fm CLI and Python SDK,” WWDC26.
- Guilherme Rambo, `insidegui/TwoMillionKit`, especially `FMToolLanguageModel.swift` and its PTY invocation strategy.
