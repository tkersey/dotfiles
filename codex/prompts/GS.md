---
description: Generate or upgrade a Codex skill bundle (SKILL.md)
argument-hint: "<skill request...>"
---

# Generate Skills (GS)
- **Input:** `$ARGUMENTS` (free-form description of what to turn into a skill). If empty or ambiguous, ask for clarification before writing files.
- **Purpose:** Create or upgrade Codex skills (and Claude-style compatible skills) under `~/.codex/skills/**/SKILL.md`.
- **Hard Requirements (Codex skills spec):**
  - Location: `~/.codex/skills/**/SKILL.md` (recursive). **Only** files named exactly `SKILL.md` count.
  - Discovery: hidden entries and symlinks are skipped; skills are loaded **once at startup**.
  - Format: YAML frontmatter + Markdown body.
    - Required YAML keys:
      - `name`: non-empty, ≤100 chars, one line
      - `description`: non-empty, ≤500 chars, one line
    - Extra YAML keys are allowed (ignored by Codex; useful for Claude-style metadata).
  - Runtime: only `name`, `description`, and file path are injected; the body stays on disk.

- **Process:**
  1. **Search first (reuse > new):**
     - List skills: `find ~/.codex/skills -name SKILL.md -print`
     - Grep by intent/keywords: `rg -n "<keyword>" ~/.codex/skills -S`
  2. **Decide shape (single skill vs pack):**
     - Single skill when it’s one coherent workflow.
     - Skill pack when you have ≥3 sub-workflows that can evolve independently:
       - A gateway skill: `discover-<topic>` (high-level “how to navigate”)
       - A pack index: `~/.codex/skills/<topic>/INDEX.md`
       - Optional per-sub-skill docs: `~/.codex/skills/<topic>/<sub-skill>.md`
  3. **Pick a name + directory (kebab-case):**
     - Single: `~/.codex/skills/<skill-name>/SKILL.md`
     - Gateway: `~/.codex/skills/discover-<topic>/SKILL.md`
     - Keep `name:` equal to the skill name you want users to type (and match in text).
  4. **Write `description` to trigger activation:**
     - One line, ≤500 chars.
     - Include what it does **and when to use it**, with concrete trigger words and synonyms.
       - Pattern: “<verb phrase>; use when <keywords/tasks> are mentioned.”
  5. **Write a terse body (runbook-first):**
     - Sections (keep skimmable):
       - **When to use**
       - **Quick start**
       - **Common commands**
       - **Pitfalls / footguns**
       - **References** (files/links to open, not pasted walls of text)
     - Prefer progressive disclosure: put long material in `INDEX.md`, `references/`, or scripts in `tools/`.
  6. **Optional advanced layout (only if it earns its keep):**
     - `tools/`: runnable helper scripts (node/python/etc.) with pinned deps if needed.
     - `references/`: longer docs, diagrams, RFC notes.
     - `assets/`: fixtures, sample inputs/outputs.
     - “Gateway” pattern examples in this repo:
       - `~/.codex/skills/discover-zig/SKILL.md`
       - `~/.codex/skills/zig/INDEX.md`
     - “Tooling” pattern example:
       - `~/.codex/skills/web-browser/SKILL.md` + `~/.codex/skills/web-browser/tools/`
  7. **Validate (required):**
     - Canonical: restart Codex; invalid skills surface a startup modal listing the broken `SKILL.md` paths.
     - Fast preflight (optional):
       ```bash
       python3 - <<'PY'
       import os
       import pathlib
       import sys
       
       ROOT = pathlib.Path(os.path.expanduser("~/.codex/skills"))
       MAX_NAME = 100
       MAX_DESC = 500
       
       errors: list[str] = []
       
       def walk(dir_path: pathlib.Path) -> None:
         for entry in os.scandir(dir_path):
           name = entry.name
           if name.startswith(".") or entry.is_symlink():
             continue
           path = pathlib.Path(entry.path)
           if entry.is_dir(follow_symlinks=False):
             walk(path)
             continue
           if not entry.is_file(follow_symlinks=False) or name != "SKILL.md":
             continue
           lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
           if not lines or lines[0].strip() != "---":
             errors.append(f"{path}: missing frontmatter start '---'")
             continue
           try:
             end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
           except StopIteration:
             errors.append(f"{path}: missing frontmatter end '---'")
             continue
           fm = lines[1:end]
           skill_name = None
           skill_desc = None
           for line in fm:
             if line.startswith("name:") and skill_name is None:
               skill_name = line.split(":", 1)[1].strip()
             if line.startswith("description:") and skill_desc is None:
               skill_desc = line.split(":", 1)[1].strip()
           if not skill_name:
             errors.append(f"{path}: missing/empty 'name'")
           elif len(skill_name) > MAX_NAME:
             errors.append(f"{path}: 'name' too long ({len(skill_name)} > {MAX_NAME})")
           if not skill_desc:
             errors.append(f"{path}: missing/empty 'description'")
           elif len(skill_desc) > MAX_DESC:
             errors.append(f"{path}: 'description' too long ({len(skill_desc)} > {MAX_DESC})")
       
       if ROOT.exists():
         walk(ROOT)
       
       if errors:
         print("\\n".join(errors))
         sys.exit(1)
       print("OK: skills frontmatter looks valid")
       PY
       ```

- **`SKILL.md` template (copy/paste)**
  ````markdown
  ---
  name: your-skill-name
  description: One-line summary; use when <keywords/tasks> are mentioned (<=500 chars).
  ---

  # <Skill Title>
  ## When to use
  - ...

  ## Quick start
  ```bash
  # ...
  ```

  ## Common commands
  - ...

  ## Pitfalls / gotchas
  - ...

  ## References
  - `~/.codex/skills/<...>/...`
  ````

- **Deliverable:** A valid `SKILL.md` (and any optional `INDEX.md`/tools) added/updated under `~/.codex/skills`, plus a short note telling users how to invoke or load deeper docs.
- **Optional (bd):** If skill work is non-trivial, you may track it with a bead and store final Closure Notes in `notes` capturing learnings and validation steps.
