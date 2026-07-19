---
name: fm
description: Invokes Apple's macOS 27 fm command-line tool from a local Mac to use the on-device system model or Private Cloud Compute, including instructions, image prompts, schema-constrained JSON, and noninteractive automation. Use when the user asks to run Apple Foundation Models through fm, compare system versus pcc, generate structured output, or automate fm without Swift or an app.
---

# `fm`

Use Apple's installed `fm` command-line tool directly. Do not create an Xcode project, Swift package, Mac app, daemon, MCP server, or network service for this workflow.

## Execution boundary

1. Run commands only in a shell that is local to the user's Mac.
2. Before the first invocation in a thread, run:

   ```bash
   scripts/fmctl.sh check
   ```

3. If the check reports a non-macOS environment or a missing `/usr/bin/fm`, stop and state the exact prerequisite. Never substitute another model while claiming its output came from `fm`.
4. Use `scripts/fmctl.sh respond` for agent-driven, noninteractive requests. Do not launch `fm chat` from an unattended shell.
5. The wrapper creates a sized pseudo-terminal for compatibility with Private Cloud Compute, while passing user content as argument values rather than interpolating it into shell code.

## Model routing

- Use `system` by default. It is the on-device model and is the preferred choice for local or sensitive content.
- Use `pcc` only when the user explicitly asks for Private Cloud Compute, PCC, Apple's cloud model, or otherwise clearly requests remote model processing.
- State which model produced the result.
- Do not send credentials, private keys, tokens, or other secrets to `pcc` unless the user explicitly directs that exact disclosure.

## Basic invocation

Pass short prompts with `--prompt`:

```bash
scripts/fmctl.sh respond \
  --model system \
  --prompt 'Summarize the following text in three sentences.'
```

For long, multiline, or untrusted prompt content, write it to a temporary file and use `--prompt-file`:

```bash
prompt_file="$(mktemp)"
trap 'rm -f "$prompt_file"' EXIT
cat >"$prompt_file" <<'PROMPT'
<complete prompt here>
PROMPT
scripts/fmctl.sh respond --model system --prompt-file "$prompt_file"
```

Never concatenate user text into a shell command string and never use `eval`.

## Instructions, images, and schemas

Add session-style instructions with `--instructions` or `--instructions-file`:

```bash
scripts/fmctl.sh respond \
  --model pcc \
  --instructions 'Return a direct, technically precise answer.' \
  --prompt 'Explain this design tradeoff.'
```

Image paths may be repeated:

```bash
scripts/fmctl.sh respond \
  --model pcc \
  --image '/absolute/path/screenshot.png' \
  --prompt 'Identify the application shown and explain the evidence.'
```

For structured output, create or provide a schema and pass it with `--schema`:

```bash
schema_file="$(mktemp)"
trap 'rm -f "$schema_file"' EXIT
scripts/fmctl.sh schema object \
  --name Result \
  --string summary \
  --string risks --array >"$schema_file"

scripts/fmctl.sh respond \
  --model system \
  --schema "$schema_file" \
  --prompt 'Analyze the proposed change.'
```

Validate model-generated JSON before using it to rename, move, overwrite, or delete files. Treat paths and commands returned by the model as untrusted data.

## Advanced options

- `--greedy` requests greedy sampling.
- `--transcript FILE` passes an existing `fm` transcript to `--load-transcript`. Do not invent the transcript format.
- `scripts/fmctl.sh raw ...` exposes noninteractive `fm` subcommands and future options. Use it only with argument arrays and quoted values.
- For current local help, run `scripts/fmctl.sh raw respond --help`.

Read [references/implementation.md](references/implementation.md) when diagnosing CLI compatibility, PTY behavior, or option changes.

## Result handling

- On success, return the `fm` output with a brief label identifying `system` or `pcc`.
- For schema-constrained output, preserve the JSON exactly unless the user asks for a formatted interpretation.
- On failure, report the exit status and sanitized error output. Do not echo secrets or the full prompt merely to diagnose a failure.
- Do not claim that the `fm` CLI itself performed tool calling. Keep any external actions in the parent agent and validate model output before acting.
