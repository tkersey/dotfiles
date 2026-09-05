# /// script
# requires-python = ">=3.11"
# dependencies = ["tomlkit==0.13.3"]
# ///
"""Deploy Codex's system baseline and detach/prune the live user configuration."""

from __future__ import annotations

import argparse
from collections.abc import MutableMapping
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
from typing import Any

import tomlkit

MARKER = b"# Managed by tkersey/dotfiles: codex/config.toml\n"
LOCAL_HEADER = b"# Local Codex overrides and installation state. Shared defaults: /etc/codex/config.toml\n"


def same_value(left: Any, right: Any) -> bool:
    """TOML booleans, integers and floats must not compare as the same setting."""
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(map(same_value, left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            same_value(left[key], right[key]) for key in left
        )
    return left == right


def prune_defaults(document: MutableMapping, defaults: dict) -> None:
    """Remove equal leaves only, keeping local-only keys and differing overrides."""
    for key, default in defaults.items():
        if key not in document:
            continue
        value = document[key]
        if isinstance(value, MutableMapping) and isinstance(default, dict):
            was_nonempty = bool(value)
            prune_defaults(value, default)
            if was_nonempty and not value:
                del document[key]
        else:
            plain = value.unwrap() if hasattr(value, "unwrap") else value
            if same_value(plain, default):
                del document[key]


def local_remainder(data: bytes, defaults: dict) -> bytes:
    text = data.decode("utf-8")
    tomllib.loads(text)  # Validate independently before editing a live file.
    document = tomlkit.parse(text)
    prune_defaults(document, defaults)
    result = tomlkit.dumps(document).encode("utf-8")
    tomllib.loads(result.decode("utf-8"))
    return result if result.strip() else LOCAL_HEADER


def snapshot(path: Path) -> tuple[str | None, bytes | None]:
    link = os.readlink(path) if path.is_symlink() else None
    # A dangling symlink is not a fresh installation.
    data = path.read_bytes() if link is not None or path.exists() else None
    return link, data


def private_file(directory: Path, prefix: str, data: bytes) -> Path:
    fd, name = tempfile.mkstemp(dir=directory, prefix=prefix)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return Path(name)  # mkstemp creates mode 0600, regardless of the umask.


def privileged(*args: str | Path) -> str:
    return subprocess.run(
        ["sudo", *(str(arg) for arg in args)],
        check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.strip()


def deploy_system(data: bytes, target: Path, original: tuple) -> None:
    if original[1] == data:
        return
    if not target.parent.exists():
        privileged("install", "-d", "-m", "0755", target.parent)
    with tempfile.TemporaryDirectory(prefix="codex-system-config-") as directory:
        source = private_file(Path(directory), "baseline-", data)
        stage = Path(privileged("mktemp", str(target.parent / ".config.toml.XXXXXX")))
        try:
            privileged("install", "-m", "0644", source, stage)
            if snapshot(target) != original:
                raise RuntimeError("System config changed during installation; left untouched.")
            if original[1] is not None:
                backup = privileged("mktemp", str(target) + ".backup.XXXXXX")
                privileged("install", "-m", "0600", target, backup)
                print(f"System backup: {backup}")
            privileged("mv", "-f", stage, target)
        finally:
            privileged("rm", "-f", stage)
    print(f"Installed system defaults: {target}")


def install_config(source: Path, user: Path, system: Path, *, dry_run: bool = False) -> None:
    baseline = source.read_bytes()
    if not baseline.startswith(MARKER):
        raise RuntimeError("Shared baseline is missing its dotfiles ownership marker.")
    defaults = tomllib.loads(baseline.decode("utf-8"))
    if user.resolve() == source.resolve():
        raise RuntimeError(
            "User config resolves to the reduced repository baseline. Do not migrate "
            "from this file: preserve the live config BEFORE pulling this change. "
            "See codex/CONFIGURATION.md for migration and recovery."
        )
    if user.resolve() == system.resolve():
        raise RuntimeError("User and system config paths must be different.")
    original = snapshot(user)
    if original[0] is not None and original[1].startswith(MARKER):
        raise RuntimeError(
            "User config links to a shared baseline in another checkout. Preserve "
            "the live config BEFORE pulling; see codex/CONFIGURATION.md for recovery."
        )
    system_original = snapshot(system)
    if system_original[0] is not None:
        raise RuntimeError("Refusing to replace a symlink at the system config path.")
    if system_original[1] is not None:
        if not system_original[1].startswith(MARKER):
            raise RuntimeError(
                "Existing system config is not managed by these dotfiles; "
                "review and reconcile it manually before installing."
            )
        tomllib.loads(system_original[1].decode("utf-8"))
    remainder = local_remainder(original[1] or b"", defaults)
    local_changed = original[0] is not None or original[1] != remainder
    if dry_run:
        print(f"System defaults: {system} ({'unchanged' if baseline == system_original[1] else 'install'})")
        print(f"Local config: {user} ({'backup and migrate' if local_changed else 'unchanged'})")
        return
    # Preserve the exact live bytes before either configuration layer changes.
    user.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    stage = None
    try:
        if local_changed:
            if original[1] is not None:
                backup = private_file(user.parent, user.name + ".backup.", original[1])
                print(f"Local backup: {backup}")
            stage = private_file(user.parent, ".config.toml.", remainder)
        if snapshot(user) != original:
            raise RuntimeError("Local config changed during installation; left untouched.")
        # Never remove user defaults before the system baseline is in place.
        deploy_system(baseline, system, system_original)
        if snapshot(user) != original:
            raise RuntimeError(
                "System defaults are installed, but local config changed; "
                "local file left untouched. Close Codex clients and retry."
            )
        if stage is not None:
            os.replace(stage, user)  # Replaces the link itself, never its target.
            print(f"Migrated local config: {user}")
        else:
            print(f"Local config unchanged: {user}")
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="validate and preview without writes or sudo")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("This installer targets Unix Codex installations (macOS/Linux).")
    if os.geteuid() == 0 and not args.dry_run:
        parser.error("Run as your normal user, not with sudo; only system installation requests sudo.")
    user_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    if not user_home.is_absolute():
        parser.error("CODEX_HOME must be an absolute path.")
    try:
        install_config(
            Path(__file__).resolve().with_name("config.toml"),
            user_home / "config.toml", Path("/etc/codex/config.toml"),
            dry_run=args.dry_run,
        )
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"codex-config: {error}\n")


if __name__ == "__main__":
    main()
