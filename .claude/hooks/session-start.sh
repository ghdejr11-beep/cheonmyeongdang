#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

echo "Installing root npm dependencies..."
(cd "$ROOT" && npm install --no-audit --no-fund)

echo "Installing tax server npm dependencies..."
(cd "$ROOT/departments/tax/server" && npm install --no-audit --no-fund)

echo "Session start hook completed."
