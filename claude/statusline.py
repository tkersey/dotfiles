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

def get_git_info(directory: Path) -> tuple[bool, str, bool, int]:
    """Returns (is_git_repo, branch_name, is_clean, unpushed_count)"""
    try:
        # Check if it's a git repo
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return False, "", False, 0
        
        # Get current branch
        result = subprocess.run(
            ["git", "-C", str(directory), "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip() if result.returncode == 0 else "detached"
        
        # Check if repo is clean
        diff_result = subprocess.run(
            ["git", "-C", str(directory), "diff", "--quiet"],
            capture_output=True
        )
        staged_result = subprocess.run(
            ["git", "-C", str(directory), "diff", "--cached", "--quiet"],
            capture_output=True
        )
        is_clean = diff_result.returncode == 0 and staged_result.returncode == 0
        
        # Get unpushed commits count (only if clean)
        unpushed_count = 0
        if is_clean:
            result = subprocess.run(
                ["git", "-C", str(directory), "rev-list", "--count", "@{u}..HEAD"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                try:
                    unpushed_count = int(result.stdout.strip())
                except ValueError:
                    unpushed_count = 0
        
        return True, branch, is_clean, unpushed_count
    except Exception:
        return False, "", False, 0

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
    console = Console(stderr=False)
    status = Text()
    
    # Folder
    status.append("📁 ", style="cyan")
    status.append(short_path, style="cyan")
    status.append(" ")
    
    # Git info if available
    is_git, branch, is_clean, unpushed = get_git_info(current_dir)
    if is_git:
        status.append("🌿 ", style="yellow")
        status.append(branch, style="yellow")
        status.append(" ")
        
        if is_clean:
            status.append("✓", style="green")
            if unpushed > 0:
                status.append(f" +{unpushed}", style="blue")
        else:
            status.append("●", style="red")
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