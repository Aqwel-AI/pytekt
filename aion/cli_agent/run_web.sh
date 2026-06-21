#!/usr/bin/env bash
# Build React UI (if needed) and start the Aion Agent web interface.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
UI="$ROOT/aion/cli_agent/web/ui"

echo "==> Aion Agent Web UI (React)"
if [[ ! -d "$UI/node_modules" ]]; then
  echo "Installing npm dependencies..."
  (cd "$UI" && npm install)
fi
echo "Building React app -> aion/cli_agent/web/static/"
(cd "$UI" && npm run build)
echo "Starting server (default http://127.0.0.1:3860/)"
cd "$ROOT" && python3 -m aion.cli agent web "$@"
