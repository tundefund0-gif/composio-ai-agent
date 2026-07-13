#!/usr/bin/env bash
set -e

# ─── Zen Agent — Start Script ────────────────────────────────────
# Usage: ./start.sh
# Or with custom keys: OPENGATE_API_KEY=xxx COMPOSIO_API_KEY=xxx ./start.sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# ─── Configuration ──────────────────────────────────────────────
# These can be overridden via environment variables
export OPENGATE_API_KEY="${OPENGATE_API_KEY:-sk-tiThifcpL4GFv4p64g2raHxUiOwy9Ajm58mQ63rBGzCSkuLYlr9BGFTgeEE20onH}"
export COMPOSIO_API_KEY="${COMPOSIO_API_KEY:-ak_AOwLDMGqjZFztZYfAYgD}"
export OPENGATE_BASE_URL="${OPENGATE_BASE_URL:-https://opencode.ai/zen/v1}"
export OPENGATE_MODEL="${OPENGATE_MODEL:-deepseek-v4-flash-free}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

# ─── Verify keys ───────────────────────────────────────────────
if [ -z "$OPENGATE_API_KEY" ]; then echo "❌ OPENGATE_API_KEY not set"; exit 1; fi
if [ -z "$COMPOSIO_API_KEY" ]; then echo "❌ COMPOSIO_API_KEY not set"; exit 1; fi

echo "🚀 Starting Zen Agent..."
echo "   Model:     $OPENGATE_MODEL"
echo "   Endpoint:  $OPENGATE_BASE_URL"
echo "   Composio:  ${COMPOSIO_API_KEY:0:8}..."
echo "   Port:      $PORT"
echo "   Dashboard: http://localhost:$PORT"
echo ""

# ─── Install deps if missing ────────────────────────────────────
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt -q
fi

# ─── Start server ───────────────────────────────────────────────
exec python3 -m uvicorn server.main:app --host "$HOST" --port 9090 --log-level info
