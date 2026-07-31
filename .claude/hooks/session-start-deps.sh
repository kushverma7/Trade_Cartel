#!/bin/bash
# Reinstall the Python stack the backtest/ package needs.
#
# Why this exists: the container is rebuilt for every session, so pip
# installs from a previous session are gone while the repo itself
# persists in git. Without this, backtest/ imports fail on a fresh
# session and the first thing anyone does is reinstall by hand.
#
# Idempotent: pip skips anything already satisfied.
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

if [ -f requirements.txt ]; then
    python3 -m pip install --quiet --disable-pip-version-check \
        -r requirements.txt 2>&1 | tail -3 || true
fi

# Node deps for the MCP servers. The tradingview-mcp package ships its
# entry point WITHOUT a shebang, so `npx tradingview-mcp` runs it under sh
# and dies with "import: not found" - which is why that MCP never loaded in
# any session. .mcp.json therefore invokes node directly against a locally
# installed copy, and this keeps that copy present.
if [ -f package.json ] && [ ! -d node_modules/tradingview-mcp ]; then
    npm install --silent --no-audit --no-fund 2>&1 | tail -2 || true
fi

# backtest/ is imported as a package from the repo root
echo 'export PYTHONPATH="${CLAUDE_PROJECT_DIR:-.}:${PYTHONPATH:-}"' \
    >> "${CLAUDE_ENV_FILE:-/dev/null}" 2>/dev/null || true

exit 0
