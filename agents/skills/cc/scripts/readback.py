"""Admit or hold one native Claude Code review session from its own evidence.

usage:
  uv run --no-project python -I readback.py standard EVENTS SESSION_ID MODEL TARGET LEVEL OUT
      [--reference-patch PATCH] [--followup EVENTS]...
  uv run --no-project python -I readback.py custom   EVENTS SESSION_ID MODEL PROMPT_FILE OUT

EVENTS is captured `--output-format stream-json --verbose` stdout. MODEL is the
full selected model ID. TARGET is the target passed to /review (`<base>..HEAD`),
or "-" when none was passed. Custom delivery is checked in the session transcript
under $CLAUDE_CONFIG_DIR (default ~/.claude)/projects/*/SESSION_ID.jsonl.

Each stream's first init must report Claude Code 2.1.287 or newer, tools within
the launch inventory, permissionMode dontAsk, and no MCP servers; these and the
loaded plugins are reported under runtime. The standard recipe must carry a
forked-command- parent_tool_use_id, the runtime's marker of a prompt-started
forked command; it does not name which command resolved.

The standard read gate recognizes direct Bash `git diff` calls against TARGET
and bounded `;`/`&&` chains, not arbitrary shell programs. Shell success proves
only the final && group's completion; earlier semicolon groups remain unknown.
A request needs a later completed tool_result with the same tool ID; in the
original stream it must come from the forked /review thread after its recipe.

With --reference-patch, the helper compares observed output with a complete UTF-8
patch supplied by the caller; it never runs Git. The caller must establish that
the reference was captured successfully under an enforced read-only boundary
for the same frozen subject. A target read that precedes `;` counts as patch
delivery only when its output contains the whole reference at line boundaries,
allowing omission of one final newline. The target command's completion remains
unknown. Patch markers alone never count. A reference also yields delivery: per
file, how many distinctive changed lines appear in any tool result of the
original or follow-up streams, each up to its first result. It reports text
presence, never a hold. Optional same-session follow-up streams can supply a
missing observation while retaining the original result and every supplemental
result separately. Reference provenance, Git subject, recovery
authorization, reassessment, and coverage remain with the caller.
Without a successful read, other Bash command requests are retained as
other_bash_requests without inferring which programs they executed. The hold
names the same-session follow-up remedy only when no other hold remains, since
follow-ups add reads and clear nothing else; a bad --reference-patch argument is
not such a hold. persisted_output records output transport independently of
target completion and reference matching.
Non-human result origins and terminal counts are diagnosed separately. Ambiguous
multi-result streams retain their ordered result events under results, with no
singular result selected. Launch settings cannot repair a rejected prior stream.
Native result text and permission denials are preserved without interpreting a
verdict or deciding whether an optional denied call mattered. OUT receives the
evidence and problems; exit 0 only when the required checks pass.
"""

import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path

LEVEL = re.compile(r"`(\w+) effort\b")
HEX = re.compile(r"[0-9a-f]{7,40}\Z")
REFERENCE_TARGET = re.compile(r"[0-9a-f]{7,40}(?:\.\.HEAD)?\Z")
EXIT_CODE = re.compile(r"\A\s*Exit code(?:\s*:\s*|\s+)(\d+)(?:\s|$)", re.IGNORECASE)
PATCH_TEXT = re.compile(r"^diff --git ", re.MULTILINE)
SUMMARY_DIFF = re.compile(r"--(?:stat|shortstat|numstat|name-only|name-status)(?:=\S*)?")
PATCH_OPTION = re.compile(r"-p|-u|--patch\S*|-U\S*|--unified\S*")
COMPANION_GIT = {"rev-parse", "merge-base", "ls-files", "check-ignore"}
FIND_ACTIONS = {"-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprint0", "-fprintf",
                "-fls", "-printf"}
# Prompt-started forked-command messages reach stream-json from 2.1.287 (headless docs).
MIN_VERSION = (2, 1, 287)
FORKED = "forked-command-"
# Launch inventories as init reports them; init names the Agent tool `Task`.
INVENTORY = {"standard": {"Read", "Grep", "Glob", "Bash", "Agent", "Task"},
             "custom": {"Read", "Grep", "Glob", "Bash", "StructuredOutput"}}
DISTINCTIVE = 12
READ_PREFIX = re.compile(r"\s*\d+[\t→]")
GREP_PREFIX = re.compile(r"(?=(:[0-9]+:|-[0-9]+-))")
# The Grep tool omits the path when it searches one file (observed: about half of real Grep lines).
BARE_PREFIX = re.compile(r"[0-9]+[:-]")
GIT_ESCAPE = re.compile(rb'\\([0-3][0-7]{2}|[abfnrtv\\"])')
GIT_ESCAPES = dict(zip(b'abfnrtv\\"', b'\a\b\f\n\r\t\v\\"'))


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "".join(part["text"] for part in content
                   if isinstance(part, dict) and part.get("type") == "text"
                   and isinstance(part.get("text"), str))


def parts_of(event: dict) -> list[dict]:
    message = event.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return [part for part in content if isinstance(part, dict)] if isinstance(content, list) else []


def load_events(path: Path, problems: list[str], label="events") -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        problems.append(f"cannot read {label}: {exc}")
        return []
    events = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except (ValueError, RecursionError) as exc:
            problems.append(f"{label} line {number}: invalid JSON ({exc})")
            continue
        if not isinstance(event, dict):
            problems.append(f"{label} line {number}: expected an object")
        else:
            events.append(event)
    return events


def common(events: list[dict], sid: str, model: str, problems: list[str]) -> dict:
    inits = [e for e in events if e.get("type") == "system" and e.get("subtype") == "init"]
    results = [e for e in events if e.get("type") == "result"]
    # Only an absent or human origin identifies the requested turn; the runtime has other kinds.
    origins = [r["origin"] for r in results if r.get("origin") is not None
               and not (isinstance(r["origin"], dict) and r["origin"].get("kind") == "human")]
    if origins:
        problems.append("unexpected non-human result origin: " + json.dumps(origins, ensure_ascii=False)
                        + "; inspect the trigger before applying caller recovery; "
                          "launch settings do not repair this stream")
    if len(inits) != 1:
        problems.append(f"expected one init event, found {len(inits)}")
    if inits:
        init = inits[0]
        if init.get("session_id") != sid:
            problems.append(f"init session {init.get('session_id')} is not {sid}")
        if init.get("model") != model:
            problems.append(f"init model {init.get('model')} is not {model}")
    if not results:
        problems.append("no result event: not terminal")
        return {}
    if len(results) != 1:
        problems.append(f"expected one terminal result, found {len(results)}")
    if any(e.get("session_id", sid) != sid for e in events):
        problems.append("events mix sessions")
    for index, result in enumerate(results, 1):
        prefix = f"result {index}: " if len(results) > 1 else ""
        if result.get("session_id") != sid:
            problems.append(f"{prefix}result session {result.get('session_id')} is not {sid}")
        if result.get("subtype") != "success" or result.get("is_error", False) is not False:
            problems.append(f"{prefix}result is {result.get('subtype')} (is_error={result.get('is_error')})")
        usage = result.get("modelUsage")
        used = sorted(usage) if isinstance(usage, dict) else []
        if used != [model]:
            problems.append(f"{prefix}models used {used}, expected only {model}")
        if not isinstance(result.get("permission_denials", []), list):
            problems.append(f"{prefix}permission_denials is not an array")
    if len(results) > 1:
        return {"result": None, "results": results,
                "permission_denials": [denial for result in results
                                      if isinstance(result.get("permission_denials"), list)
                                      for denial in result["permission_denials"]]}
    return results[0]


def result_evidence(result: dict) -> dict:
    return {"result": result.get("result"), "permission_denials": result.get("permission_denials", []),
            **{key: result[key] for key in ("origin", "results") if key in result}}


def launch_runtime(events: list[dict], kind: str, problems: list[str]) -> dict:
    """Check the runtime-authored launch facts in the stream's first init."""
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    if init is None:
        return {}
    version, tools = init.get("claude_code_version"), init.get("tools")
    parsed = (tuple(map(int, version.split("."))) if isinstance(version, str)
              and re.fullmatch(r"\d+\.\d+\.\d+", version) else None)
    if parsed is None or parsed < MIN_VERSION:
        problems.append(f"init claude_code_version {version!r} is not 2.1.287 or newer")
    if (not isinstance(tools, list) or not all(isinstance(tool, str) for tool in tools)
            or not set(tools) <= INVENTORY[kind]):
        problems.append(f"init tools {tools!r} exceed the {kind} launch inventory")
    if init.get("permissionMode") != "dontAsk":
        problems.append(f"init permissionMode {init.get('permissionMode')!r} is not dontAsk")
    if init.get("mcp_servers") != []:
        problems.append(f"init mcp_servers {init.get('mcp_servers')!r} is not empty")
    return {"claude_code_version": version, "tools": tools, "permission_mode": init.get("permissionMode"),
            "mcp_servers": init.get("mcp_servers"), "plugins": init.get("plugins")}


def git_path(text: str) -> str:
    """Decode Git's C-quoted pathname bytes without changing unquoted whitespace."""
    if text.startswith('"') and text.endswith('"'):
        try:
            quoted = text[1:-1].encode("utf-8")
        except UnicodeEncodeError:  # lone surrogates from tool output are not Git's quoting
            return text
        raw = GIT_ESCAPE.sub(lambda m: bytes([int(m[1], 8) if len(m[1]) == 3 else GIT_ESCAPES[m[1][0]]]), quoted)
        return raw.decode("utf-8", errors="surrogateescape")
    return text


def patch_files(reference: str) -> list[dict]:
    """Keep sections distinct until their canonical a/b paths are resolved."""
    files, current, in_hunk = [], None, False
    for line in reference.split("\n"):
        if line.startswith("diff --git "):
            names = line[len("diff --git "):]
            middle = len(names) // 2
            old, new = git_path(names[:middle]), git_path(names[middle + 1:])
            # Unchanged names have equally long rendered fields, even when quoted;
            # diff.noprefix renders them identically. Renames/copies resolve below;
            # splitting on ' b/' loses valid names, and ---/+++ lines cannot tell a
            # noprefix a/ or b/ folder from a prefix.
            symmetric = names[middle:middle + 1] == " "
            path = (old[2:] if symmetric and old.startswith("a/") and new == "b/" + old[2:]
                    else old if symmetric and old == new else None)
            current = {"path": path, "lines": [], "aliases": {path} if path is not None else set(),
                       "header": line}
            files.append(current)
            in_hunk = False
        elif current is not None:
            if line.startswith("@@"):
                in_hunk = True
            elif not in_hunk and line.startswith(("rename from ", "rename to ", "copy from ", "copy to ")):
                _, side, name = line.split(" ", 2)
                name = git_path(name)
                current["aliases"].add(name)
                if side == "to":
                    current["path"] = name
            elif in_hunk and line[:1] in ("+", "-") and sum(not char.isspace() for char in line[1:]) >= DISTINCTIVE:
                current["lines"].append(line[1:].rstrip())
    return files


def output_text(line: str, paths: set[str]) -> tuple[str, ...]:
    """Remove one display prefix; ambiguous grep boundaries stay unnormalized."""
    read = READ_PREFIX.match(line)
    if read:
        return line, line[read.end():]
    candidates = [(match.start(), match.start() + len(match[1]))
                  for match in GREP_PREFIX.finditer(line) if match.start()]
    known = [(start, end) for start, end in candidates if git_path(line[:start]) in paths]
    if known:
        return (line, line[known[0][1]:]) if len(known) == 1 else (line,)
    bare = BARE_PREFIX.match(line)
    if bare:
        return line, line[bare.end():]
    return (line, line[candidates[0][1]:]) if len(candidates) == 1 else (line,)


def delivery(reference: str, streams: list[list[dict]]) -> dict:
    """Count distinctive changed reference lines whose text appears in any tool result.

    Text presence is not attention or reasoning, and identical text elsewhere also
    matches. Read line numbers, grep match/context prefixes (with or without a path)
    and diff markers are removed.
    """
    sections = patch_files(reference)
    files = {}
    for section in sections:
        if section["path"] is not None:
            # Type changes can produce multiple sections for the same real file.
            files.setdefault(section["path"], []).extend(section["lines"])
    paths = {name for section in sections for name in section["aliases"]}
    paths.update("./" + name for name in tuple(paths))
    for stream in streams:
        init = next((event for event in stream if event.get("type") == "system" and event.get("subtype") == "init"), {})
        cwd = init.get("cwd")
        if isinstance(cwd, str):
            paths.update(cwd.rstrip("/") + "/" + name for section in sections for name in section["aliases"])
    seen = set()
    for event in (event for stream in streams for event in stream):
        for part in parts_of(event):
            if part.get("type") == "tool_result":
                for line in text_of(part.get("content")).split("\n"):
                    for text in output_text(line, paths):
                        seen.update((text.rstrip(), text[1:].rstrip() if text[:1] in "+- " else text.rstrip()))
    measured = [{"path": name, "lines": len(lines), "delivered": sum(line in seen for line in lines)}
                for name, lines in files.items() if lines]
    unparsed = [section["header"] for section in sections if section["path"] is None]
    return {"distinctive_min_chars": DISTINCTIVE, "lines": sum(f["lines"] for f in measured),
            "delivered": sum(f["delivered"] for f in measured), "files": measured,
            "unmeasured": [name for name, lines in files.items() if not lines],
            **({"unparsed_headers": unparsed} if unparsed else {})}


def pieces(command: str) -> tuple[list[list[str]], list[str]] | None:
    """Split unquoted `;`/`&&` operators before decoding each argument list."""
    if any(token in command for token in ("\n", "\r", "`", "$", "#")):
        return None
    raw, operators = [], []
    start = index = 0
    quote = None
    while index < len(command):
        char = command[index]
        if quote:
            if char == quote:
                quote = None
            elif char == "\\" and quote == '"':
                index += 1
        elif char in "'\"":
            quote = char
        elif char == "\\":
            index += 1
        elif char == ";" or command.startswith("&&", index):
            operator = ";" if char == ";" else "&&"
            raw.append(command[start:index])
            operators.append(operator)
            index += len(operator)
            start = index
            continue
        elif char in "()<>|&":
            return None
        index += 1
    if quote:
        return None
    raw.append(command[start:])
    try:
        commands = [shlex.split(part) for part in raw]
    except ValueError:
        return None
    return (commands, operators) if all(commands) else None


def companion_read(words: list[str]) -> bool:
    """Recognize companion reads; their output never authenticates a target read."""
    if words[:2] == ["git", "--no-pager"]:
        words = words[:1] + words[2:]
    if words[:1] == ["git"] and len(words) > 1:
        subcommand, args = words[1], words[2:]
        if subcommand == "status":
            return not any(a == "--verbose" or (a.startswith("-") and not a.startswith("--") and "v" in a)
                           for a in args)
        if subcommand == "diff":
            options = args[:args.index("--")] if "--" in args else args
            if options == ["HEAD"]:
                return True
            return (any(SUMMARY_DIFF.fullmatch(a) for a in options)
                    and not any(PATCH_OPTION.fullmatch(a) for a in options))
        return subcommand in COMPANION_GIT
    if words[:1] == ["ls"] or words == ["pwd"]:
        return True
    return words[:1] == ["find"] and not any(word in FIND_ACTIONS for word in words[1:])


def diff_read(command: str, target: str) -> tuple[str, bool, bool] | None:
    """Classify a Bash command as a patch read of TARGET without executing it.

    Return shape, whether shell success establishes a target read's success,
    and whether exit 1 has the direct diff's --exit-code meaning. In a chain,
    only the final && group is established by a successful aggregate result.
    """
    parsed = pieces(command)
    if not parsed:
        return None
    commands, operators = parsed
    target_reads = [direct_diff(piece, target) for piece in commands]
    if not any(target_reads):
        return None
    if not operators:
        words = commands[0]
        options = words[:words.index("--")] if "--" in words else words
        return "direct", True, "--exit-code" in options
    if not all(read or companion_read(piece) for read, piece in zip(target_reads, commands)):
        return None
    final_group = max((index + 1 for index, op in enumerate(operators) if op == ";"), default=0)
    return "chain", any(target_reads[final_group:]), False


def direct_diff(words: list[str], target: str) -> bool:
    """Recognize a direct patch read with a base operand.

    Summary-only modes and unknown options are excluded, so they cannot
    silently substitute other output. Path-limited reads are observations; the
    caller judges overall coverage.
    """
    if words[:2] == ["git", "--no-pager"]:
        words = words[:1] + words[2:]
    if words[:2] != ["git", "diff"]:
        return False
    args = words[2:]
    if "--" in args:
        args = args[:args.index("--")]
    # These flags change presentation but still produce the patch. Keep the
    # grammar small: unknown options cannot silently substitute other output.
    options = {"--exit-code", "--no-color", "--color=never", "--no-ext-diff", "--no-textconv",
               "--patch", "-p", "--unified", "-U"}
    operands = [word for word in args if word not in options
                and not re.fullmatch(r"(?:--unified=|-U)[0-9]+", word)]
    if len(operands) == 1:
        operands = re.split(r"\.{2,3}", operands[0])
        if len(operands) == 1:
            # The caller freezes a clean working tree at HEAD before dispatch.
            operands.append("HEAD")
    if len(operands) != 2:
        return False
    base, head = operands
    return bool(HEX.fullmatch(base) and target.startswith(base) and head == "HEAD")


def tool_result_status(part: dict, event: dict, difference_exit: bool) -> tuple[bool, str]:
    """Use native tool_result errors, plus explicit Bash completion metadata.

    Bash commonly reports failures as `is_error` with an `Exit code N` prefix.
    An omitted is_error means success in the tool-result protocol. Exit 1 from
    --exit-code is a successful diff observation only when patch text exists.
    """
    if not isinstance(part.get("content"), (str, list)):
        return False, "malformed tool_result content"
    failed = part.get("is_error", False)
    if not isinstance(failed, bool):
        return False, "malformed tool_result is_error"
    content = text_of(part.get("content"))
    if re.search(r"^Command running in background\b", content, re.MULTILINE):
        return False, "Bash returned a background launch acknowledgment"
    match = EXIT_CODE.match(content)
    codes = [int(match.group(1))] if match else []
    details = event.get("tool_use_result")
    if details is not None:
        if not isinstance(details, dict):
            return False, "malformed Bash result metadata"
        if details.get("interrupted") or details.get("backgroundTaskId") or details.get("background_task_id"):
            return False, "Bash result is interrupted or still in the background"
    # A tool_result can carry an explicit exit code itself; Claude transcript
    # metadata sometimes supplies it alongside stdout/stderr instead.
    for source in (part, details or {}):
        for key in ("exit_code", "exitCode"):
            if key in source:
                code = source[key]
                if not isinstance(code, int) or isinstance(code, bool):
                    return False, "malformed Bash exit code"
                codes.append(code)
    if len(set(codes)) > 1:
        return False, "conflicting Bash exit codes"
    code = codes[0] if codes else None
    if code == 1 and difference_exit and PATCH_TEXT.search(content):
        return True, "git diff --exit-code returned a patch (exit 1)"
    if failed or code not in (None, 0):
        return False, f"Bash tool_result failed (is_error={failed}, exit_code={code})"
    return True, "completed correlated Bash tool_result"


def load_reference_patch(path: Path, target: str, problems: list[str]) -> tuple[dict, str | None]:
    evidence = {"path": str(path)}
    if not REFERENCE_TARGET.fullmatch(target):
        problems.append(f"cannot compare reference patch for target {target!r}; expected <base>..HEAD")
        return evidence, None
    try:
        raw = path.read_bytes()
        evidence["sha256"] = hashlib.sha256(raw).hexdigest()
        patch = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        problems.append(f"cannot read reference patch: {exc}")
        return evidence, None
    evidence["patch_text"] = bool(PATCH_TEXT.search(patch))
    if not evidence["patch_text"]:
        problems.append("reference patch contains no patch text")
        return evidence, None
    return evidence, patch


def reference_observed(content: str, reference: str | None) -> bool:
    patch = reference.removesuffix("\n") if reference else ""
    return bool(patch) and re.search(r"(?:\A|\n)" + re.escape(patch) + r"(?=\n|\Z)", content) is not None


def standard(events: list[dict], target: str, level: str, problems: list[str], followups=(),
             reference: str | None = None) -> dict:
    terminal = next((i for i, e in enumerate(events) if e.get("type") == "result"), len(events))
    session = events[:terminal]
    # Reads and delivery stop at each stream's first result, which is the response being judged.
    sessions = [session] + [stream[:next((i for i, e in enumerate(stream) if e.get("type") == "result"), len(stream))]
                            for stream in followups]
    start = next((i for i, e in enumerate(session) if e.get("type") == "user" and isinstance(e.get("message"), dict)
                  and "Review target:" in text_of(e["message"].get("content"))), None)
    carrier = session[start] if start is not None else None
    recipe = text_of(carrier["message"].get("content")) if carrier else None
    evidence = {"diff_reads": []}
    if recipe is None:
        problems.append("no expanded /review recipe in the session")
    else:
        fork = carrier.get("parent_tool_use_id")
        evidence["recipe_parent_tool_use_id"] = fork
        if not (isinstance(fork, str) and fork.startswith(FORKED)):
            problems.append(f"recipe parent_tool_use_id {fork!r} does not mark a prompt-started forked command")
        observed = LEVEL.search(recipe)
        observed_level = observed.group(1) if observed else None
        evidence.update(observed_level=observed_level, recipe_header=recipe.split("\n\n", 2)[:2])
        if observed_level != level:
            problems.append(f"recipe ran at {observed_level} effort, bound level is {level}")
        if target != "-" and f"Review target: `{target}`" not in recipe:
            problems.append(f"recipe target is not {target}")
    if target != "-":
        requests = [(source, i, p) for source, stream in enumerate(sessions)
                    for i, e in enumerate(stream) if e.get("type") == "assistant"
                    for p in parts_of(e) if p.get("type") == "tool_use"]
        others = []
        for source, index, request in requests:
            inputs = request.get("input")
            command = inputs.get("command") if isinstance(inputs, dict) else None
            observation = diff_read(command, target) if request.get("name") == "Bash" and isinstance(command, str) else None
            if observation is None:
                if request.get("name") == "Bash" and isinstance(command, str):
                    others.append({"tool_use_id": request.get("id"), "command": command,
                                   **({"followup": source} if source else {})})
                continue
            shape, completion_bound, difference_exit = observation
            tool_id = request.get("id")
            read = {"tool_use_id": tool_id, "command": command, "shape": shape, "ok": False}
            if not completion_bound:
                read["completion_status"] = "unknown"
            if source:
                read["followup"] = source
            evidence["diff_reads"].append(read)
            # A verifier subagent's or an earlier read does not reach the forked reviewer.
            if source == 0 and (carrier is None or index <= start or sessions[0][index].get("parent_tool_use_id")
                                != carrier.get("parent_tool_use_id")):
                read["reason"] = "not requested by the forked /review thread after its recipe"
                continue
            if inputs.get("run_in_background"):
                read["reason"] = "background request does not establish completed diff observation"
                continue
            if not isinstance(tool_id, str) or not tool_id or sum(p.get("id") == tool_id for _, _, p in requests) != 1:
                read["reason"] = "missing or duplicate tool_use ID"
                continue
            matches = [(i, p, e) for i, e in enumerate(sessions[source]) if e.get("type") == "user"
                       for p in parts_of(e) if p.get("type") == "tool_result" and p.get("tool_use_id") == tool_id]
            if len(matches) != 1 or matches[0][0] <= index:
                read["reason"] = "no unique later correlated tool_result"
                continue
            _, part, event = matches[0]
            read["ok"], read["reason"] = tool_result_status(part, event, difference_exit)
            details = event.get("tool_use_result")
            if ((isinstance(details, dict) and details.get("persistedOutputPath"))
                    or text_of(part.get("content")).startswith("<persisted-output>")):
                read["persisted_output"] = True
            if read["ok"] and not completion_bound:
                if reference_observed(text_of(part.get("content")), reference):
                    read.update(reference_matched=True, reason="target diff precedes a semicolon; completion remains "
                                "unknown, but the observed output contains the whole caller-supplied reference patch")
                else:
                    read.update(ok=False, unverified=True,
                                reason="target diff precedes a semicolon; its completion status is unavailable")
        if not any(read["ok"] for read in evidence["diff_reads"]):
            # Follow-ups only add reads, so every hold recorded before this one survives them.
            remedy = ("other holds remain that a --followup cannot clear; do not resume for this read alone, "
                      "and apply the caller's existing recovery rules" if problems else
                      "resume the same session with the bound launch settings, complete a direct foreground "
                      "target diff read and dependent reassessment, then pass the separate stream with --followup")
            if any(read.get("unverified") for read in evidence["diff_reads"]):
                problems.append(f"no successful correlated `git diff` read against {target}: the recognized read "
                                "precedes a `;`, so its completion is unverified; "
                                + ("" if problems or reference is not None
                                   else "supply an authenticated --reference-patch, or ") + remedy)
            elif evidence["diff_reads"]:
                problems.append(f"no successful correlated `git diff` read against {target}: every recognized "
                                f"read failed or lacks a unique later result (see diff_reads); {remedy}")
            elif others:
                problems.append(f"no successful correlated `git diff` read against {target}: "
                                "other Bash requests did not establish a target patch read (see other_bash_requests); "
                                f"{remedy}")
            else:
                problems.append(f"no successful correlated `git diff` read against {target}: "
                                f"no recognized target diff request was found; {remedy}")
            evidence["other_bash_requests"] = others
    if reference is not None:
        evidence["delivery"] = delivery(reference, sessions)
    return evidence


def transcript_path(sid: str) -> Path | None:
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    matches = sorted(root.glob(f"*/{sid}.jsonl"))
    return matches[0] if len(matches) == 1 else None


def custom(result: dict, sid: str, prompt: bytes, problems: list[str]) -> dict:
    evidence = {"prompt_sha256": hashlib.sha256(prompt).hexdigest()}
    try:
        path = transcript_path(sid)
    except (OSError, ValueError) as exc:
        path = None
        problems.append(f"cannot locate transcript: {exc}")
    if path is None:
        problems.append(f"no unique transcript for {sid}")
    else:
        evidence["transcript"] = str(path)
        records = load_events(path, problems, "transcript")
        sessions = [r["sessionId"] for r in records if "sessionId" in r]
        if not sessions or any(session != sid for session in sessions):
            problems.append("transcript mixes sessions or has no session identity")
        first = next((r for r in records if r.get("type") == "user" and not r.get("isMeta")), None)
        message = first.get("message") if first else None
        delivered = text_of(message.get("content")) if isinstance(message, dict) else None
        if delivered is None or delivered.encode() != prompt:
            problems.append("first transcript message is not the exact prompt: delivery unverified")
    output = result.get("structured_output")
    if not isinstance(output, dict):
        problems.append("no structured_output object from a unique terminal result")
    evidence["structured_output"] = output
    return evidence


def main() -> None:
    kind, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else (None, [])
    followup_paths, reference_path = [], None
    flags = list(zip(args[6::2], args[7::2])) if kind == "standard" and len(args) >= 6 and len(args) % 2 == 0 else None
    if (flags is not None and all(flag in ("--followup", "--reference-patch") for flag, _ in flags)
            and sum(flag == "--reference-patch" for flag, _ in flags) <= 1):
        events_path, sid, model, target, level, out = args[:6]
        followup_paths = [value for flag, value in flags if flag == "--followup"]
        reference_path = next((value for flag, value in flags if flag == "--reference-patch"), None)
    elif kind == "custom" and len(args) == 5:
        events_path, sid, model, prompt_path, out = args
    else:
        sys.exit(__doc__)
    problems: list[str] = []
    events = load_events(Path(events_path), problems)
    result = common(events, sid, model, problems)
    report = {"kind": kind, "session_id": sid, "model": model,
              "runtime": launch_runtime(events, kind, problems), **result_evidence(result)}
    if kind == "standard":
        if not isinstance(result.get("result"), str) or not result["result"].strip():
            problems.append("no nonempty native result text from a unique terminal result")
        reference, argument = None, []
        if reference_path is not None:
            report["reference_patch"], reference = load_reference_patch(Path(reference_path), target, argument)
        followups = []
        for path in followup_paths:
            issues = []
            stream = load_events(Path(path), issues, "follow-up events")
            supplemental = common(stream, sid, model, issues)
            runtime = launch_runtime(stream, "standard", issues)
            if not isinstance(supplemental.get("result"), str) or not supplemental["result"].strip():
                issues.append("no nonempty follow-up result text from a unique terminal result")
            problems.extend(f"follow-up {len(followups) + 1}: {issue}" for issue in issues)
            followups.append(stream)
            report.setdefault("followups", []).append({"events": path, "runtime": runtime,
                                                       **result_evidence(supplemental)})
        report.update(standard(events, target, level, problems, followups, reference))
        problems.extend(argument)
    else:
        try:
            prompt = Path(prompt_path).read_bytes()
        except OSError as exc:
            prompt = b""
            problems.append(f"cannot read prompt: {exc}")
        report.update(custom(result, sid, prompt, problems))
    report.update(ok=not problems, problems=problems)
    Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", errors="backslashreplace")
    if problems:
        sys.exit("hold: " + "; ".join(problems))


if __name__ == "__main__":
    main()
