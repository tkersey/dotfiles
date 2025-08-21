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
    """Returns (is_git_repo, branch_name, status_counts)"""
    try:
        # Check if it's a git repo
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "", {}
        
        # Get current branch
        result = subprocess.run(
            ["git", "-C", str(directory), "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip() if result.returncode == 0 else "detached"
        
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
            "behind": behind
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
    is_git, branch, git_status = get_git_info(current_dir)
    if is_git:
        status.append("🌿 ", style="yellow")
        status.append(branch, style="yellow")
        
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