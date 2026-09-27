#!/usr/bin/env bash
set -euo pipefail
exec uv run --no-project python3 "$(dirname -- "${BASH_SOURCE[0]}")/zig_cache_drain.py" "$@"
