#!/usr/bin/env python3
"""Codex-only account switching helper for the accts skill."""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from typing import Any


VERSION = "0.1.0"
STATE_VERSION = 1
SECRET_KEY_FRAGMENTS = (
    "access_token",
    "refresh_token",
    "id_token",
    "auth_token",
    "api_key",
    "password",
    "secret",
    "bearer",
)
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@+-]*$")


class AcctsError(RuntimeError):
    pass


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def eprint(*parts: object) -> None:
    print(*parts, file=sys.stderr)


def expand_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def accts_home() -> Path:
    return expand_path(os.environ.get("ACCTS_HOME", "~/.local/share/accts"))


def codex_home_default() -> Path:
    return expand_path(os.environ.get("CODEX_HOME", "~/.codex"))


def default_config_path() -> Path:
    env = os.environ.get("ACCTS_CONFIG")
    if env:
        return expand_path(env)
    if os.environ.get("ACCTS_HOME"):
        return accts_home() / "accts.toml"
    return codex_home_default() / "accts.toml"


def check_account_name(name: str) -> str:
    if not NAME_RE.match(name):
        raise AcctsError(f"invalid account name {name!r}; use letters, numbers, dot, dash, underscore, @, or +")
    return name


def validate_rel_path(value: str, *, field: str) -> Path:
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        raise AcctsError(f"{field} must be a relative path inside the accts vault")
    return rel


def reject_secret_toml_keys(obj: Any, prefix: str = "") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in SECRET_KEY_FRAGMENTS):
                where = f"{prefix}.{key}" if prefix else str(key)
                raise AcctsError(f"TOML key {where!r} looks secret-bearing; keep OAuth material only in auth.json vault files")
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            reject_secret_toml_keys(value, child_prefix)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            reject_secret_toml_keys(value, f"{prefix}[{index}]")


def read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    reject_secret_toml_keys(data)
    return data


def write_file_atomic(path: Path, data: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
        os.chmod(path, mode)
    finally:
        if tmp.exists():
            tmp.unlink()


def write_json_atomic(path: Path, data: dict[str, Any], *, mode: int = 0o600) -> None:
    encoded = json.dumps(data, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    write_file_atomic(path, encoded, mode=mode)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_copy_file(src: Path, dst: Path, *, mode: int = 0o600) -> None:
    if not src.exists():
        raise AcctsError(f"missing auth file: {src}")
    write_file_atomic(dst, src.read_bytes(), mode=mode)


class Runtime:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = read_toml(config_path)
        settings = self.config.get("settings", {})
        if settings and not isinstance(settings, dict):
            raise AcctsError("[settings] must be a table")
        self.codex_home = expand_path(str(settings.get("codex_home", codex_home_default())))
        base = accts_home()
        self.vault_dir = expand_path(str(settings.get("vault_dir", base / "vault")))
        self.state_dir = expand_path(str(settings.get("state_dir", base / "state")))
        self.cas_cwd = expand_path(str(settings.get("cas_cwd", Path.cwd())))
        self.auth_file = self.codex_home / "auth.json"
        self.state_file = self.state_dir / "state.json"

    def raw_accounts(self) -> dict[str, dict[str, Any]]:
        accounts = self.config.get("accounts", {})
        if accounts is None:
            return {}
        if not isinstance(accounts, dict):
            raise AcctsError("[accounts] must be a table")
        out: dict[str, dict[str, Any]] = {}
        for name, meta in accounts.items():
            check_account_name(name)
            if meta is None:
                meta = {}
            if not isinstance(meta, dict):
                raise AcctsError(f"[accounts.{name}] must be a table")
            out[name] = dict(meta)
        return out

    def state(self) -> dict[str, Any]:
        state = read_json(self.state_file, {})
        if not state:
            state = {"version": STATE_VERSION, "accounts": {}, "turn_use_ledger": []}
        state.setdefault("version", STATE_VERSION)
        state.setdefault("accounts", {})
        state.setdefault("turn_use_ledger", [])
        return state

    def save_state(self, state: dict[str, Any]) -> None:
        state["version"] = STATE_VERSION
        write_json_atomic(self.state_file, state)

    def vault_rel_for(self, name: str, meta: dict[str, Any] | None = None) -> Path:
        check_account_name(name)
        meta = meta or {}
        vault = meta.get("vault")
        if vault:
            return validate_rel_path(str(vault), field=f"accounts.{name}.vault")
        return Path(name) / "auth.json"

    def vault_auth_file(self, name: str, meta: dict[str, Any] | None = None) -> Path:
        return self.vault_dir / self.vault_rel_for(name, meta)

    def account_map(self) -> dict[str, dict[str, Any]]:
        accounts = self.raw_accounts()
        state = self.state()
        for name, meta in list(state.get("accounts", {}).items()):
            if NAME_RE.match(name) and name not in accounts:
                accounts[name] = dict(meta)
        if self.vault_dir.exists():
            for child in self.vault_dir.iterdir():
                if child.is_dir() and NAME_RE.match(child.name) and child.name not in accounts:
                    accounts[child.name] = {}
        for name, meta in accounts.items():
            meta.setdefault("enabled", True)
            meta.setdefault("reset_participates", True)
            meta.setdefault("label", name)
        return accounts

    def active_account(self) -> str | None:
        current_hash = sha256_file(self.auth_file)
        if not current_hash:
            return None
        for name, meta in self.account_map().items():
            vault_hash = sha256_file(self.vault_auth_file(name, meta))
            if vault_hash and vault_hash == current_hash:
                return name
        state_active = self.state().get("active_account")
        if isinstance(state_active, str):
            return state_active
        return None

    def eligible_reset_accounts(self) -> list[str]:
        names: list[str] = []
        for name, meta in sorted(self.account_map().items()):
            if meta.get("enabled", True) is False:
                continue
            if meta.get("reset_participates", True) is False:
                continue
            if self.vault_auth_file(name, meta).exists():
                names.append(name)
        return names


def runtime_from_args(args: argparse.Namespace) -> Runtime:
    return Runtime(expand_path(args.config))


def template_config() -> str:
    return """# accts stores only metadata here. Keep OAuth tokens only in auth.json vault files.
[settings]
# codex_home = "~/.codex"
# vault_dir = "~/.local/share/accts/vault"
# state_dir = "~/.local/share/accts/state"
# cas_cwd = "/path/to/repo"

[accounts.personal]
label = "Personal"
enabled = true
reset_participates = true
vault = "personal/auth.json"

[accounts.work]
label = "Work"
enabled = true
reset_participates = true
vault = "work/auth.json"
"""


def cmd_init(args: argparse.Namespace) -> int:
    path = expand_path(args.config)
    if args.dry_run:
        print(f"would initialize {path}")
        print(template_config())
        return 0
    if path.exists() and not args.force:
        raise AcctsError(f"{path} already exists; pass --force to overwrite")
    write_file_atomic(path, template_config().encode("utf-8"), mode=0o600)
    print(f"initialized {path}")
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    name = check_account_name(args.name)
    accounts = rt.account_map()
    meta = accounts.get(name, {})
    state = rt.state()
    dst = rt.vault_auth_file(name, meta)
    safe_copy_file(rt.auth_file, dst)
    account_state = dict(state.get("accounts", {}).get(name, {}))
    account_state.update(
        {
            "label": args.label or meta.get("label", name),
            "email": args.email or meta.get("email"),
            "vault": str(rt.vault_rel_for(name, meta)),
            "auth_sha256": sha256_file(dst),
            "last_backup_at": utc_now(),
        }
    )
    state.setdefault("accounts", {})[name] = account_state
    rt.save_state(state)
    print(f"backed up {name}")
    return 0


def backup_current(rt: Runtime) -> None:
    if not rt.auth_file.exists():
        return
    timestamp = utc_now().replace(":", "").replace("-", "")
    dst = rt.vault_dir / "backups" / f"current-{timestamp}.auth.json"
    safe_copy_file(rt.auth_file, dst)


def activate_account(rt: Runtime, name: str, *, backup: bool = False, source: str = "cli") -> None:
    name = check_account_name(name)
    accounts = rt.account_map()
    meta = accounts.get(name, {})
    src = rt.vault_auth_file(name, meta)
    if not src.exists():
        raise AcctsError(f"no vaulted auth.json for account {name!r}; run backup first")
    if backup:
        backup_current(rt)
    safe_copy_file(src, rt.auth_file)
    state = rt.state()
    now = utc_now()
    state["active_account"] = name
    state["active_auth_sha256"] = sha256_file(rt.auth_file)
    state["last_activated_at"] = now
    state["last_activation_source"] = source
    if state.get("pending_account") == name:
        state.pop("pending_account", None)
        state.pop("pending_queued_at", None)
    account_state = dict(state.get("accounts", {}).get(name, {}))
    account_state.update(
        {
            "label": meta.get("label", account_state.get("label", name)),
            "email": meta.get("email", account_state.get("email")),
            "vault": str(rt.vault_rel_for(name, meta)),
            "auth_sha256": sha256_file(src),
            "last_activated_at": now,
        }
    )
    state.setdefault("accounts", {})[name] = account_state
    rt.save_state(state)


def cmd_activate(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    activate_account(rt, args.name, backup=args.backup_current, source="cli")
    print(f"activated {args.name}")
    return 0


def status_payload(rt: Runtime) -> dict[str, Any]:
    accounts = rt.account_map()
    current_hash = sha256_file(rt.auth_file)
    active = rt.active_account()
    account_rows = []
    for name, meta in sorted(accounts.items()):
        vault_file = rt.vault_auth_file(name, meta)
        vault_hash = sha256_file(vault_file)
        account_rows.append(
            {
                "name": name,
                "label": meta.get("label", name),
                "enabled": meta.get("enabled", True) is not False,
                "reset_participates": meta.get("reset_participates", True) is not False,
                "vaulted": vault_file.exists(),
                "active": bool(vault_hash and current_hash and vault_hash == current_hash),
                "vault_sha256": vault_hash,
            }
        )
    state = rt.state()
    return {
        "active_account": active,
        "auth_present": rt.auth_file.exists(),
        "auth_sha256": current_hash,
        "pending_account": state.get("pending_account"),
        "reset_cycle": state.get("reset_cycle"),
        "accounts": account_rows,
    }


def cmd_status(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    payload = status_payload(rt)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    active = payload["active_account"] or "unknown"
    pending = payload["pending_account"] or "none"
    print(f"active: {active}")
    print(f"pending: {pending}")
    for row in payload["accounts"]:
        mark = "*" if row["active"] else " "
        vaulted = "vaulted" if row["vaulted"] else "missing"
        print(f"{mark} {row['name']}: {vaulted}")
    return 0


def cmd_ls(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    rows = status_payload(rt)["accounts"]
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    for row in rows:
        mark = "*" if row["active"] else " "
        enabled = "enabled" if row["enabled"] else "disabled"
        vaulted = "vaulted" if row["vaulted"] else "missing"
        print(f"{mark} {row['name']}\t{enabled}\t{vaulted}")
    return 0


def queue_account(rt: Runtime, name: str) -> None:
    name = check_account_name(name)
    meta = rt.account_map().get(name, {})
    if not rt.vault_auth_file(name, meta).exists():
        raise AcctsError(f"no vaulted auth.json for account {name!r}; run backup first")
    state = rt.state()
    state["pending_account"] = name
    state["pending_queued_at"] = utc_now()
    rt.save_state(state)


def cmd_queue(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    queue_account(rt, args.name)
    print(f"queued {args.name}")
    return 0


def reset_cycle_next(state: dict[str, Any]) -> str | None:
    cycle = state.get("reset_cycle")
    if not isinstance(cycle, dict) or cycle.get("complete"):
        return None
    accounts = cycle.get("accounts", [])
    touched = set(cycle.get("touched", []))
    for name in accounts:
        if name not in touched:
            return name
    return None


def cmd_next(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    state = rt.state()
    name = state.get("pending_account") or reset_cycle_next(state)
    if not name:
        eligible = rt.eligible_reset_accounts()
        name = eligible[0] if eligible else None
    if args.json:
        print(json.dumps({"next_account": name}, indent=2, sort_keys=True))
    else:
        print(name or "none")
    return 0


def advance_reset_cycle(rt: Runtime, state: dict[str, Any], just_used: str | None) -> str | None:
    cycle = state.get("reset_cycle")
    if not isinstance(cycle, dict) or cycle.get("complete"):
        return None
    accounts = cycle.get("accounts", [])
    if just_used in accounts:
        touched = list(dict.fromkeys(cycle.get("touched", []) + [just_used]))
        cycle["touched"] = touched
        cycle["last_touched_at"] = utc_now()
    next_name = reset_cycle_next(state)
    if next_name:
        state["pending_account"] = next_name
        state["pending_queued_at"] = utc_now()
        return next_name
    cycle["complete"] = True
    cycle["completed_at"] = utc_now()
    state.pop("pending_account", None)
    state.pop("pending_queued_at", None)
    return None


def run_cas_status(rt: Runtime) -> dict[str, Any]:
    commands = [
        ["cas", "account", "status", "--cwd", str(rt.cas_cwd), "--json", "--usage", "--hooks", "off"],
        [
            str(expand_path(os.environ.get("SKILLS_ZIG_REPO", "/Users/tk/workspace/tk/skills-zig")) / "zig-out/bin/cas_account"),
            "status",
            "--cwd",
            str(rt.cas_cwd),
            "--json",
            "--usage",
            "--hooks",
            "off",
        ],
    ]
    errors: list[str] = []
    for command in commands:
        try:
            proc = subprocess.run(command, check=False, text=True, capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"{command[0]}: {exc}")
            continue
        if proc.returncode == 0:
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError as exc:
                errors.append(f"{command[0]}: invalid JSON: {exc}")
                continue
        errors.append(f"{command[0]}: exit {proc.returncode}: {proc.stderr.strip()[:200]}")
    raise AcctsError("unable to read CAS account status; " + "; ".join(errors))


def reset_value_from_table(obj: dict[str, Any]) -> str | None:
    reset_names = {"resetsat", "resets_at", "resetat", "reset_at", "windowresetat", "window_reset_at"}
    for key, value in obj.items():
        lowered = str(key).replace("-", "_").lower()
        compact = lowered.replace("_", "")
        if lowered in reset_names or compact in reset_names:
            if isinstance(value, str) and value:
                return value
            if isinstance(value, (int, float)):
                return str(value)
    return None


def search_reset_key(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            if any(word in lowered for word in ("secondary", "weekly", "week")):
                if isinstance(value, dict):
                    direct = reset_value_from_table(value)
                    if direct:
                        return direct
                found = search_reset_key(value)
                if found:
                    return found
        duration = obj.get("windowDurationMins") or obj.get("window_duration_mins")
        if isinstance(duration, (int, float)) and duration >= 10080:
            found = reset_value_from_table(obj)
            if found:
                return found
        for value in obj.values():
            found = search_reset_key(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = search_reset_key(value)
            if found:
                return found
    return None


def reset_key_from_status(data: dict[str, Any]) -> str:
    value = search_reset_key(data)
    if not value:
        raise AcctsError("CAS status did not expose a weekly/secondary reset timestamp")
    return value


def load_status_fixture(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    with expand_path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AcctsError("CAS fixture must contain a JSON object")
    return data


def cmd_reset_status(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    cas_data = load_status_fixture(args.fixture)
    cas_error = None
    if cas_data is None and not args.state_only:
        try:
            cas_data = run_cas_status(rt)
        except AcctsError as exc:
            cas_error = str(exc)
    payload = {"reset_cycle": rt.state().get("reset_cycle"), "cas_error": cas_error}
    if cas_data is not None:
        payload["cas_reset_key"] = reset_key_from_status(cas_data)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"cycle: {payload['reset_cycle'] or 'none'}")
        if "cas_reset_key" in payload:
            print(f"cas_reset_key: {payload['cas_reset_key']}")
        if cas_error:
            print(f"cas_error: {cas_error}")
    return 0 if not cas_error else 1


def cmd_reset_start(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    state = rt.state()
    if state.get("reset_cycle") and not args.force:
        raise AcctsError("reset cycle already exists; pass --force to replace it")
    if args.resets_at:
        reset_key = args.resets_at
    else:
        fixture = load_status_fixture(args.fixture)
        reset_key = reset_key_from_status(fixture or run_cas_status(rt))
    accounts = rt.eligible_reset_accounts()
    if not accounts:
        raise AcctsError("no vaulted enabled accounts participate in reset rotation")
    cycle = {
        "key": reset_key,
        "resets_at": reset_key,
        "accounts": accounts,
        "touched": [],
        "complete": False,
        "started_at": utc_now(),
    }
    state["reset_cycle"] = cycle
    state["pending_account"] = accounts[0]
    state["pending_queued_at"] = utc_now()
    rt.save_state(state)
    print(f"started reset cycle {reset_key}; queued {accounts[0]}")
    return 0


def cmd_reset_advance(args: argparse.Namespace) -> int:
    rt = runtime_from_args(args)
    state = rt.state()
    account = args.account or rt.active_account()
    next_name = advance_reset_cycle(rt, state, account)
    rt.save_state(state)
    if next_name:
        print(f"queued {next_name}")
    else:
        print("reset cycle complete")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local Codex auth accounts with a non-secret TOML config.")
    parser.add_argument("--config", default=str(default_config_path()), help="Path to accts.toml")
    parser.add_argument("--version", action="version", version=f"accts {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Create a metadata-only TOML config template")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("backup", help="Back up the current ~/.codex/auth.json into the accts vault")
    p.add_argument("name")
    p.add_argument("--label")
    p.add_argument("--email")
    p.set_defaults(func=cmd_backup)

    p = sub.add_parser("activate", help="Restore a vaulted account into ~/.codex/auth.json")
    p.add_argument("name")
    p.add_argument("--backup-current", action="store_true")
    p.set_defaults(func=cmd_activate)

    p = sub.add_parser("queue", help="Record the account to activate manually next")
    p.add_argument("name")
    p.set_defaults(func=cmd_queue)

    p = sub.add_parser("status", help="Show active, pending, and vaulted accounts")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("ls", help="List configured and vaulted accounts")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_ls)

    p = sub.add_parser("next", help="Print the account currently pending or next in reset rotation")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_next)

    reset = sub.add_parser("reset-cycle", help="Manage weekly reset rotation through all Codex accounts")
    reset_sub = reset.add_subparsers(dest="reset_command", required=True)
    p = reset_sub.add_parser("status", help="Show reset-cycle state and CAS reset key")
    p.add_argument("--json", action="store_true")
    p.add_argument("--fixture", help=argparse.SUPPRESS)
    p.add_argument("--state-only", action="store_true", help="Do not call CAS; show local state only")
    p.set_defaults(func=cmd_reset_status)
    p = reset_sub.add_parser("start", help="Start a reset cycle and queue the first untouched account")
    p.add_argument("--force", action="store_true")
    p.add_argument("--fixture", help=argparse.SUPPRESS)
    p.add_argument("--resets-at", help="Explicit reset timestamp, mainly for offline testing")
    p.set_defaults(func=cmd_reset_start)
    p = reset_sub.add_parser("advance", help="Mark one account used and queue the next untouched account")
    p.add_argument("--account")
    p.set_defaults(func=cmd_reset_advance)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except AcctsError as exc:
        eprint(f"accts: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
