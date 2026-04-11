#!/usr/bin/env python3
"""Generate a starter architecture report from codebase analysis.

Usage: ./scaffold-report.py [project_path] [output_file]

Performs quick analysis and generates a markdown template pre-filled
with discovered information about the codebase.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_cmd(cmd: str, cwd: str = ".") -> str:
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def count_lines(path: str, extensions: list[str]) -> int:
    """Count lines of code for given extensions."""
    total = 0
    for ext in extensions:
        output = run_cmd(f"find . -name '*{ext}' -exec wc -l {{}} + 2>/dev/null | tail -1", path)
        if output:
            parts = output.split()
            if parts and parts[0].isdigit():
                total += int(parts[0])
    return total


def detect_language(path: str) -> tuple[str, list[str]]:
    """Detect primary language from files present."""
    checks = [
        ("Cargo.toml", "Rust", [".rs"]),
        ("package.json", "TypeScript/JavaScript", [".ts", ".tsx", ".js", ".jsx"]),
        ("go.mod", "Go", [".go"]),
        ("pyproject.toml", "Python", [".py"]),
        ("requirements.txt", "Python", [".py"]),
        ("Gemfile", "Ruby", [".rb"]),
    ]
    for marker, lang, exts in checks:
        if (Path(path) / marker).exists():
            return lang, exts
    return "Unknown", []


def find_entry_points(path: str, lang: str) -> list[str]:
    """Find likely entry points based on language."""
    entries = []
    if lang == "Rust":
        output = run_cmd('rg -l "fn main" --type rust 2>/dev/null', path)
        entries = output.split("\n") if output else []
    elif lang == "Go":
        output = run_cmd('rg -l "func main" --type go 2>/dev/null', path)
        entries = output.split("\n") if output else []
    elif "Python" in lang:
        output = run_cmd('rg -l "if __name__" --type py 2>/dev/null', path)
        entries = output.split("\n") if output else []
    return [e for e in entries if e][:5]


def find_key_types(path: str, lang: str) -> list[str]:
    """Find major type definitions."""
    types = []
    if lang == "Rust":
        output = run_cmd('rg "^pub struct " --type rust -l 2>/dev/null | head -5', path)
        types = output.split("\n") if output else []
    elif lang == "Go":
        output = run_cmd('rg "^type .* struct" --type go -l 2>/dev/null | head -5', path)
        types = output.split("\n") if output else []
    return [t for t in types if t]


def get_dependencies(path: str, lang: str) -> list[str]:
    """Extract top dependencies."""
    deps = []
    if lang == "Rust":
        output = run_cmd('grep "^[a-z]" Cargo.toml 2>/dev/null | head -10', path)
        for line in output.split("\n"):
            if "=" in line:
                deps.append(line.split("=")[0].strip())
    elif "TypeScript" in lang or "JavaScript" in lang:
        output = run_cmd('jq -r ".dependencies | keys[]" package.json 2>/dev/null | head -10', path)
        deps = output.split("\n") if output else []
    return [d for d in deps if d][:5]


def generate_report(path: str, output_file: str | None = None):
    """Generate the report scaffold."""
    path = os.path.abspath(path)
    project_name = os.path.basename(path)

    lang, exts = detect_language(path)
    loc = count_lines(path, exts) if exts else 0
    entries = find_entry_points(path, lang)
    types = find_key_types(path, lang)
    deps = get_dependencies(path, lang)

    report = f"""# {project_name} - Technical Architecture Report

## Executive Summary

**{project_name}** is a [CLI tool / web service / library] that [main purpose]. Built with {lang}.

**Key Statistics:**
- ~{loc:,} lines of code
- Language: {lang}
- Key dependencies: {", ".join(deps[:5]) if deps else "[analyze Cargo.toml/package.json]"}

---

## Entry Points

| Entry | Location | Purpose |
|-------|----------|---------|
"""
    for entry in entries[:5]:
        report += f"| Main | `{entry}` | [describe] |\n"
    if not entries:
        report += "| [entry] | `src/main.*` | [describe] |\n"

    report += """
---

## Key Types

| Type | Location | Purpose |
|------|----------|---------|
"""
    for t in types[:5]:
        report += f"| [TypeName] | `{t}` | [describe] |\n"
    if not types:
        report += "| [TypeName] | `src/model.*` | [describe] |\n"

    report += """
---

## Data Flow

```
[Input Source]
     |
     v
[Entry Point] --> parses/validates
     |
     v
[Handler/Controller] --> orchestrates
     |
     v
[Core Domain Logic] --> business rules
     |
     v
[Storage/External] --> persists/calls
     |
     v
[Output/Response]
```

**Happy Path Description:**
1. User invokes [command/endpoint]
2. [Entry] parses input and creates [Type]
3. [Handler] calls [Core] which processes...
4. Result is [stored/returned/displayed]

---

## External Dependencies

| Dependency | Purpose | Critical? |
|------------|---------|-----------|
"""
    for dep in deps[:5]:
        report += f"| {dep} | [purpose] | Yes/No |\n"
    if not deps:
        report += "| [dep] | [purpose] | Yes/No |\n"

    report += """
---

## Configuration

| Source | Location/Example | Priority |
|--------|------------------|----------|
| Environment var | `APP_*` | 1 (highest) |
| Config file | `~/.config/{project}/config.toml` | 2 |
| CLI flag | `--flag` | 3 |
| Default | Hardcoded | 4 (lowest) |

---

## Test Infrastructure

| Type | Location | Count |
|------|----------|-------|
| Unit tests | `src/**/*_test.*` | ~[N] |
| Integration | `tests/integration/` | ~[N] |
| E2E | `tests/e2e/` | ~[N] |

**Running Tests:**
```bash
# [language-specific test command]
```

---

## Notes & Gotchas

- [Any non-obvious behavior]
- [Known limitations]
- [Areas needing improvement]

---

*Generated: {datetime.now().strftime("%Y-%m-%d")}*
*Status: DRAFT - requires human review and completion*
"""

    if output_file:
        with open(output_file, "w") as f:
            f.write(report)
        print(f"Report scaffold written to: {output_file}")
    else:
        print(report)


if __name__ == "__main__":
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output = sys.argv[2] if len(sys.argv) > 2 else None
    generate_report(project_path, output)
