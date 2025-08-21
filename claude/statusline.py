#!/usr/bin/env -S uv run --with rich --quiet
# /// script
# dependencies = ["rich"]
# ///

import json
import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.text import Text

def get_git_info(directory: Path) -> tuple[bool, str, dict]:
    """Returns (is_git_repo, location, status_counts)"""
    try:
        # Get git directory and check if inside work tree
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--git-dir", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "", {}
        
        lines = result.stdout.strip().split("\n")
        git_dir = Path(lines[0]) if lines else Path(".git")
        if not git_dir.is_absolute():
            git_dir = directory / git_dir
        
        # Get current branch or detached state
        result = subprocess.run(
            ["git", "-C", str(directory), "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip()
        
        # If no branch, check if detached and get short hash
        if not branch:
            result = subprocess.run(
                ["git", "-C", str(directory), "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                branch = f"@{result.stdout.strip()}"
            else:
                branch = "detached"
        
        # Check for git operations
        operation = ""
        step = total_steps = 0
        
        # Check for rebase-merge
        rebase_merge_dir = git_dir / "rebase-merge"
        if rebase_merge_dir.exists():
            # Read step numbers
            msgnum_file = rebase_merge_dir / "msgnum"
            end_file = rebase_merge_dir / "end"
            if msgnum_file.exists() and end_file.exists():
                step = int(msgnum_file.read_text().strip())
                total_steps = int(end_file.read_text().strip())
            
            # Check if interactive
            if (rebase_merge_dir / "interactive").exists():
                operation = "rebase-i"
            else:
                operation = "rebase-m"
        
        # Check for rebase-apply
        elif (git_dir / "rebase-apply").exists():
            rebase_apply_dir = git_dir / "rebase-apply"
            next_file = rebase_apply_dir / "next"
            last_file = rebase_apply_dir / "last"
            if next_file.exists() and last_file.exists():
                step = int(next_file.read_text().strip())
                total_steps = int(last_file.read_text().strip())
            
            if (rebase_apply_dir / "rebasing").exists():
                operation = "rebase"
            elif (rebase_apply_dir / "applying").exists():
                operation = "am"
            else:
                operation = "am/rebase"
        
        # Check for other operations
        elif (git_dir / "MERGE_HEAD").exists():
            operation = "merge"
        elif (git_dir / "CHERRY_PICK_HEAD").exists():
            operation = "cherry-pick"
        elif (git_dir / "REVERT_HEAD").exists():
            operation = "revert"
        elif (git_dir / "BISECT_LOG").exists():
            operation = "bisect"
        
        # Get git status porcelain
        result = subprocess.run(
            ["git", "-C", str(directory), "--no-optional-locks", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        stat_lines = result.stdout.splitlines() if result.returncode == 0 else []
        
        # Count different file states (similar to Tide)
        conflicted = sum(1 for line in stat_lines if line.startswith("UU"))
        staged = sum(1 for line in stat_lines if line[0] in "ADMR")
        dirty = sum(1 for line in stat_lines if line[1] in "ADMR")
        untracked = sum(1 for line in stat_lines if line.startswith("??"))
        
        # Get stash count
        result = subprocess.run(
            ["git", "-C", str(directory), "stash", "list"],
            capture_output=True,
            text=True
        )
        stash = len(result.stdout.splitlines()) if result.returncode == 0 else 0
        
        # Get ahead/behind counts
        ahead = behind = 0
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-list", "--count", "--left-right", "@{u}...HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            counts = result.stdout.strip().split("\t")
            if len(counts) == 2:
                behind = int(counts[0]) if counts[0] else 0
                ahead = int(counts[1]) if counts[1] else 0
        
        return True, branch, {
            "conflicted": conflicted,
            "staged": staged,
            "dirty": dirty,
            "untracked": untracked,
            "stash": stash,
            "ahead": ahead,
            "behind": behind,
            "operation": operation,
            "step": step,
            "total_steps": total_steps
        }
    except Exception:
        return False, "", {}

def format_cost(cost: float | None) -> str:
    """Format cost as $X.XX"""
    if cost is None or cost == 0:
        return "$0.00"
    return f"${cost:.2f}"

def main():
    # Read JSON from stdin
    data = json.load(sys.stdin)
    
    # Extract data
    current_dir = Path(data.get("workspace", {}).get("current_dir", "."))
    model_name = data.get("model", {}).get("display_name", "unknown")
    session_cost = data.get("cost", {}).get("total_cost_usd", 0)
    
    # Prepare display values
    short_path = current_dir.name
    cost_display = format_cost(session_cost)
    
    # Build status line
    console = Console(stderr=False, force_terminal=True, legacy_windows=False)
    status = Text()
    
    # Folder
    status.append("📁 ", style="cyan")
    status.append(short_path, style="cyan")
    status.append(" ")
    
    # Git info if available
    is_git, location, git_status = get_git_info(current_dir)
    if is_git:
        status.append("🌿 ", style="yellow")
        
        # Show location (branch or detached)
        if location.startswith("@"):
            # Detached HEAD - show in green like Tide
            status.append(location, style="green")
        else:
            # Branch name
            status.append(location, style="yellow")
        
        # Show operation and progress
        if git_status.get("operation"):
            status.append(f" {git_status['operation']}", style="red")
            if git_status.get("step") and git_status.get("total_steps"):
                status.append(f" {git_status['step']}/{git_status['total_steps']}", style="red")
        
        # Show git status indicators (Tide-style)
        if git_status.get("behind", 0) > 0:
            status.append(f" ⇣{git_status['behind']}", style="cyan")
        if git_status.get("ahead", 0) > 0:
            status.append(f" ⇡{git_status['ahead']}", style="cyan")
        if git_status.get("stash", 0) > 0:
            status.append(f" *{git_status['stash']}", style="yellow")
        if git_status.get("conflicted", 0) > 0:
            status.append(f" ~{git_status['conflicted']}", style="red")
        if git_status.get("staged", 0) > 0:
            status.append(f" +{git_status['staged']}", style="green")
        if git_status.get("dirty", 0) > 0:
            status.append(f" !{git_status['dirty']}", style="red")
        if git_status.get("untracked", 0) > 0:
            status.append(f" ?{git_status['untracked']}", style="blue")
        
        status.append(" ")
    
    # Model
    status.append("🤖 ", style="magenta")
    status.append(model_name, style="magenta")
    status.append(" ")
    
    # Cost
    status.append("💰 ", style="green")
    status.append(cost_display, style="green")
    
    # Print without newline to match original behavior
    console.print(status, end="")

if __name__ == "__main__":
    main()