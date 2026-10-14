"""Consume the native writer's selected memory layout; never parse Codex config."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class LayoutError(RuntimeError):
    pass


@dataclass(frozen=True)
class MemoryLayout:
    extension: str
    codex_home: Path
    memory_version: str
    memory_root: Path
    extension_root: Path
    notes_dir: Path
    instructions_path: Path
    resources_dir: Path

    def writer_args(self) -> list[str]:
        return ["--codex-home", str(self.codex_home), "--memory-version", self.memory_version]

    def as_dict(self) -> dict[str, str]:
        return {"schema": "memory-note-layout/v1", **{
            key: str(value) for key, value in vars(self).items()
        }}


def memory_note_binary(explicit: str | Path | None = None) -> str:
    selected = explicit or os.environ.get("MEMORY_NOTE_BIN")
    if selected:
        if isinstance(selected, str) and os.sep not in selected:
            command = shutil.which(selected)
            if command:
                return str(Path(command).absolute())
            raise LayoutError(f"memory-note: unavailable: {selected}")
        path = Path(selected).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.absolute())
        raise LayoutError(f"memory-note: unavailable: {path}")
    installed = shutil.which("memory-note")
    if installed:
        return installed
    repo = Path(os.environ.get("SKILLS_ZIG_REPO", str(Path.home() / "workspace/tk/skills-zig")))
    candidate = repo / "zig-out/bin/memory-note"
    if candidate.is_file() and os.access(candidate, os.X_OK):
        return str(candidate.absolute())
    raise LayoutError("memory-note: unavailable; install the supported writer or set MEMORY_NOTE_BIN")


def parse_layout(value: Any, extension: str) -> MemoryLayout:
    if not isinstance(value, dict) or value.get("schema") != "memory-note-layout/v1":
        raise LayoutError("memory-note path: unsupported layout result; upgrade the native writer")
    if value.get("memory_version") not in {"v1", "v2"}:
        raise LayoutError("memory-note path: unsupported memory version")
    fields = ("codex_home", "memory_root", "extension_root", "notes_dir", "instructions_path", "resources_dir")
    paths: dict[str, Path] = {}
    for key in fields:
        raw = value.get(key)
        if not isinstance(raw, str) or not Path(raw).is_absolute() or ".." in Path(raw).parts:
            raise LayoutError(f"memory-note path: invalid {key}")
        paths[key] = Path(raw)
    # Validate the native result's coherence. Selection remains exclusively native.
    expected_root = paths["codex_home"] / ("memories_v2" if value["memory_version"] == "v2" else "memories")
    expected_extension = expected_root / "extensions" / extension
    expected = {
        "memory_root": expected_root,
        "extension_root": expected_extension,
        "notes_dir": expected_extension / "notes",
        "instructions_path": expected_extension / "instructions.md",
        "resources_dir": expected_extension / "resources",
    }
    if any(paths[key] != path for key, path in expected.items()):
        raise LayoutError("memory-note path: inconsistent layout paths")
    return MemoryLayout(extension=extension, memory_version=value["memory_version"], **paths)


def resolve_layout(
    extension: str,
    *,
    codex_home: str | Path | None = None,
    memory_version: str | None = None,
    memory_note_bin: str | Path | None = None,
    cwd: Path | None = None,
) -> MemoryLayout:
    binary = memory_note_binary(memory_note_bin)
    argv = [binary, "path", "--extension", extension, "--format", "json"]
    if codex_home is not None:
        argv.extend(["--codex-home", str(Path(codex_home).expanduser().absolute())])
    if memory_version is not None:
        argv.extend(["--memory-version", memory_version])
    try:
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, check=False)
    except OSError as exc:
        raise LayoutError(f"memory-note path: {exc}") from exc
    if proc.returncode:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise LayoutError(f"memory-note path: {detail or f'exit {proc.returncode}'}")
    try:
        layout = parse_layout(json.loads(proc.stdout), extension)
    except (ValueError, UnicodeDecodeError) as exc:
        raise LayoutError("memory-note path: invalid JSON layout result") from exc
    if codex_home is not None and layout.codex_home != Path(codex_home).expanduser().absolute():
        raise LayoutError("memory-note path: selected a different Codex home")
    if memory_version is not None and layout.memory_version != memory_version:
        raise LayoutError("memory-note path: selected a different memory version")
    return layout


def layout_for(home: Path | MemoryLayout, extension: str = "synesthesia") -> MemoryLayout:
    if isinstance(home, MemoryLayout):
        if home.extension != extension:
            raise LayoutError("memory layout belongs to another extension")
        return home
    return resolve_layout(extension, codex_home=home)


def selected_layout(args: Any, extension: str) -> MemoryLayout:
    existing = getattr(args, "_memory_layout", None)
    if existing is None:
        existing = resolve_layout(
            extension,
            codex_home=getattr(args, "codex_home", None),
            memory_version=getattr(args, "memory_version", None),
            memory_note_bin=getattr(args, "memory_note_bin", None),
            cwd=Path(getattr(args, "repo", None) or ".").expanduser().absolute(),
        )
        args._memory_layout = existing
    return layout_for(existing, extension)


def ensure_no_symlink_components(path: Path) -> None:
    for component in (*reversed(path.absolute().parents), path.absolute()):
        if component.is_symlink():
            raise LayoutError(f"symlink component: {component}")
        if component != path.absolute() and component.exists() and not component.is_dir():
            raise LayoutError(f"not a directory: {component}")


def compiled_documents(layout: MemoryLayout) -> tuple[dict[str, str], list[str]]:
    paths = [layout.memory_root / "memory_summary.md"]
    if layout.memory_version == "v1":
        paths.append(layout.memory_root / "MEMORY.md")
        skills = layout.memory_root / "skills"
        try:
            ensure_no_symlink_components(skills)
            if skills.is_dir():
                paths.extend(sorted(path for path in skills.rglob("*") if path.is_file()))
        except (OSError, LayoutError):
            return {}, [str(skills)]
    documents: dict[str, str] = {}
    unavailable: list[str] = []
    for path in paths:
        try:
            ensure_no_symlink_components(path)
            documents[str(path)] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, LayoutError):
            unavailable.append(str(path))
    return documents, unavailable


def copy_instructions(layout: MemoryLayout, source: Path) -> dict[str, Any]:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise LayoutError(f"source instructions not found: {source}")
    destination = layout.instructions_path
    ensure_no_symlink_components(destination)
    if destination.exists() and not destination.is_file():
        raise LayoutError(f"instructions are not a regular file: {destination}")
    source_bytes = source.read_bytes()
    before = destination.read_bytes() if destination.is_file() else None
    status = "current" if before == source_bytes else "copied"
    if status == "copied":
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        ensure_no_symlink_components(destination)
        fd, temporary = tempfile.mkstemp(prefix=".memory-instructions-", dir=destination.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(source_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, 0o644)
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return {"status": status, "source": str(source), "destination": str(destination),
            "sha256": hashlib.sha256(source_bytes).hexdigest(), "symlink": False,
            "memory_version": layout.memory_version}
