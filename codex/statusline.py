"""A Codex statusline provider using newline-delimited MCP over stdio."""

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


URI = "ui://workspace-statusline/footer"
TOOL = {
    "name": "statusline",
    "title": "Git workspace",
    "description": "Show the Codex version, model and reasoning level, directory, Git status, and weekly allowance.",
    "inputSchema": {"type": "object", "properties": {}},
    "_meta": {
        "openai/ui": {"entrypoints": [{"type": "statusline", "resourceUri": URI}]}
    },
}


def git_status(cwd):
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", cwd, "status", "--porcelain=v2",
             "--branch", "-z", "--untracked-files=all", "--ignore-submodules=none"],
            capture_output=True, timeout=5, check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    branch = revision = ""
    staged = unstaged = untracked = conflicts = 0
    records = iter(result.stdout.split(b"\0"))
    for record in records:
        if record.startswith(b"# branch.head "):
            branch = record[14:].decode(errors="replace")
        elif record.startswith(b"# branch.oid "):
            revision = record[13:21].decode(errors="replace")
        elif record.startswith((b"1 ", b"2 ")):
            staged += record[2:3] != b"."
            unstaged += record[3:4] != b"."
            if record.startswith(b"2 "):
                next(records, None)  # A rename includes a second NUL-delimited path.
        elif record.startswith(b"? "):
            untracked += 1
        elif record.startswith(b"u "):
            conflicts += 1

    if branch == "(detached)":
        branch = f"detached@{revision}"
    counts = [(staged, "staged"), (unstaged, "unstaged"),
              (untracked, "untracked"), (conflicts, "conflicted")]
    changes = ", ".join(f"{count} {label}" for count, label in counts if count)
    return branch, changes or "clean"


# Keep filesystem work outside the one-second MCP read deadline. Only the
# result for the displayed directory may appear in its footer.
executor = ThreadPoolExecutor(max_workers=1)
git_future = None
git_cwd = None
last_status = None
next_refresh = 0.0


def current_git(cwd):
    global git_future, git_cwd, last_status, next_refresh
    if git_future is not None and git_future.done():
        last_status = git_future.result()
        git_future = None
        next_refresh = time.monotonic() + 2
    if git_future is None and (cwd != git_cwd or time.monotonic() >= next_refresh):
        if cwd != git_cwd:
            last_status = None
        git_cwd = cwd
        git_future = executor.submit(git_status, cwd)
    return last_status if cwd == git_cwd else None


def weekly_remaining(account):
    limits = account.get("rate_limits") or []
    for limit in limits:
        if len(limits) > 1 and limit.get("limit_id") != "codex":
            continue
        for key in ("primary_limit", "secondary_limit"):
            window = limit.get(key) or {}
            if window.get("window_minutes") == 7 * 24 * 60:
                return remaining(window.get("used_percent"))
    return None


def remaining(used):
    if isinstance(used, (int, float)):
        return round(max(0, min(100, 100 - used)))
    return None


def render(state):
    """Render the snapshot with Git status from its working directory."""
    thread = state.get("thread") or {}
    model = thread.get("model") or {}
    cwd = (thread.get("workspace") or {}).get("cwd")
    week_left = weekly_remaining(state.get("account") or {})
    children = []

    def add(value, color, width=40):
        if value:
            label = " ".join(str(value).split())
            if len(label) > width:
                label = label[:width - 1] + "…"
            children.append({"type": "text", "props": {"color": color}, "children": [label]})

    add((state.get("app") or {}).get("cli_version"), "status-metadata")
    add(" ".join(filter(None, [model.get("display_name"), model.get("reasoning_level")])), "status-model")
    if cwd:
        directory = Path(cwd)
        if directory.is_relative_to(Path.home()):
            directory = Path("~") / directory.relative_to(Path.home())
        label = str(directory)
        add(label if len(label) <= 48 else "…" + label[-47:], "status-path", 48)
        if status := current_git(cwd):
            branch, changes = status
            add(branch, "status-branch")
            add(changes, "status-state", 80)
    if week_left is not None:
        add(f"week {week_left}% left", "status-limit")
    if not children:
        return None
    return {"type": "row", "props": {"gap": 2, "wrap": "wrap"}, "children": children}


def respond(method, params):
    if method == "initialize":
        return {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": {"name": "workspace-statusline", "version": "1.0"},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [TOOL]}
    if method == "tools/call":
        if params.get("name") != TOOL["name"]:
            raise ValueError("Unknown tool name")
        return {
            "content": [{"type": "text", "text": f"The statusline resource is {URI}."}]
        }
    if method == "resources/list":
        return {
            "resources": [
                {"name": "footer", "uri": URI, "mimeType": "application/json"}
            ]
        }
    if method == "resources/templates/list":
        return {"resourceTemplates": []}
    if method == "resources/read":
        if params.get("uri") != URI:
            raise ValueError("Unknown resource URI")
        state = params.get("_meta", {}).get("com.openai/codex-statusline-state", {})
        return {
            "contents": [
                {
                    "uri": URI,
                    "mimeType": "application/json",
                    "text": json.dumps(render(state), ensure_ascii=False),
                }
            ]
        }
    raise KeyError(method)


def main():
    for line in sys.stdin.buffer:
        reply = {"jsonrpc": "2.0", "id": None}
        try:
            request = json.loads(line)
            if not isinstance(request, dict) or not isinstance(
                request.get("method"), str
            ):
                reply["error"] = {"code": -32600, "message": "Invalid request"}
            elif "id" not in request:
                continue
            else:
                reply["id"] = request["id"]
                reply["result"] = respond(request["method"], request.get("params", {}))
        except json.JSONDecodeError:
            reply["error"] = {"code": -32700, "message": "Parse error"}
        except KeyError:
            reply["error"] = {"code": -32601, "message": "Method not found"}
        except (TypeError, ValueError, AttributeError):
            reply["error"] = {"code": -32602, "message": "Invalid parameters"}
        print(json.dumps(reply), flush=True)


if __name__ == "__main__":
    main()
