#!/usr/bin/env bash
# Validate cass installation and basic functionality

set -e

echo "=== cass Session Search Validation ==="
echo

# Check cass is installed
if ! command -v cass &> /dev/null; then
    echo "ERROR: cass is not installed or not in PATH"
    echo "FIX: Install cass from https://github.com/your/cass"
    exit 2
fi

echo "✓ cass found: $(which cass)"

# Check cass status
echo
echo "Checking cass status..."
STATUS=$(cass status --json 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "ERROR: cass status failed"
    echo "FIX: Run 'cass doctor' to repair"
    exit 2
fi

# Check if index is fresh
FRESH=$(echo "$STATUS" | jq -r '.index.fresh // false')
if [ "$FRESH" = "true" ]; then
    echo "✓ Index is fresh"
else
    echo "WARNING: Index is stale"
    echo "FIX: Run 'cass index --json'"
fi

# Check conversation count
CONVOS=$(echo "$STATUS" | jq -r '.database.conversations // 0')
echo "✓ Indexed conversations: $CONVOS"

if [ "$CONVOS" -eq 0 ]; then
    echo "WARNING: No conversations indexed"
    echo "FIX: Run 'cass index --full --json' to rebuild index"
fi

# Test basic search (should not panic)
echo
echo "Testing basic search..."
if cass search "*" --json --limit 1 --fields minimal > /dev/null 2>&1; then
    echo "✓ Basic search works"
else
    echo "ERROR: Basic search failed"
    exit 2
fi

# Test aggregation (the most common pitfall)
echo
echo "Testing aggregation..."
if cass search "*" --json --aggregate agent --limit 1 --fields minimal > /dev/null 2>&1; then
    echo "✓ Aggregation works"
else
    echo "ERROR: Aggregation failed"
    exit 2
fi

echo
echo "=== Validation Complete ==="
echo "cass is ready to use"
exit 0
