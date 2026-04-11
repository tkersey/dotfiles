# Ghostty Terminfo for Remote Machines

> **The problem:** You SSH into a server and see `[57414u` garbage when pressing numpad Enter.
> **The solution:** Install Ghostty's terminfo on remote machines.

## Quick Fix

From your Mac (with Ghostty installed):

```bash
infocmp -x xterm-ghostty | ssh user@server 'mkdir -p ~/.terminfo && tic -x -o ~/.terminfo -'
```

Reconnect and special keys will work correctly.

## Shell Function

Add to `~/.zshrc`:

```bash
ghostty_push_terminfo() {
  local host="$1"
  [[ -z "$host" ]] && { echo "Usage: ghostty_push_terminfo <host>" >&2; return 1; }
  infocmp -x xterm-ghostty | ssh "$host" 'mkdir -p ~/.terminfo && tic -x -o ~/.terminfo -'
}
```

Usage:

```bash
ghostty_push_terminfo ubuntu@dev-server.local
ghostty_push_terminfo deploy@prod-web-01
```

## Batch Script

```bash
#!/bin/bash
SERVERS=(
  "ubuntu@dev-server.local"
  "ubuntu@staging.example.com"
  "deploy@prod-web-01"
)

for server in "${SERVERS[@]}"; do
  echo "→ $server"
  if infocmp -x xterm-ghostty | ssh "$server" 'mkdir -p ~/.terminfo && tic -x -o ~/.terminfo -' 2>/dev/null; then
    echo "  ✓ Success"
  else
    echo "  ✗ Failed"
  fi
done
```

## Fallback (No Terminfo Access)

If you can't install terminfo:

```bash
# Force compatible TERM
alias myserver='TERM=xterm-256color ssh user@myserver'

# Or in ~/.ssh/config
Host myserver
    SetEnv TERM=xterm-256color
```

Trade-off: Loses Ghostty-specific features but avoids garbage characters.

## System-Wide Installation

With sudo access:

```bash
infocmp -x xterm-ghostty | ssh user@server 'sudo tic -x -'
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Still seeing `[57414u` | Terminfo not found | Verify `~/.terminfo/x/xterm-ghostty` exists |
| `tic: command not found` | ncurses missing | `sudo apt install ncurses-bin` |
| Works for bash, not vim | App using wrong TERM | Ensure `$TERM=xterm-ghostty` |

### Verify TERM

```bash
echo $TERM  # Should output: xterm-ghostty
```

### Check terminfo

```bash
infocmp xterm-ghostty >/dev/null 2>&1 && echo "Found" || echo "Not found"
```

## Affected Keys

| Key | Without terminfo | With terminfo |
|-----|------------------|---------------|
| Numpad Enter | `[57414u` | Works |
| Numpad numbers | Escape codes | Works |
| Ctrl+Shift+Letter | May not register | Works |
| Function keys (F13+) | Garbage | Works |
