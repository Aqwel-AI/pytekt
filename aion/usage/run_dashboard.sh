#!/usr/bin/env bash
# Build React UI (if needed) and start the Aion usage dashboard.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB="$ROOT/aion/usage/web"

echo "==> Aion Usage Dashboard (React)"
if [[ ! -d "$WEB/node_modules" ]]; then
  echo "Installing npm dependencies..."
  (cd "$WEB" && npm install)
fi
echo "Building React app -> aion/usage/static/"
(cd "$WEB" && npm run build)
echo "Starting server (default http://127.0.0.1:3847/)"
cd "$ROOT" && python3 -m aion.cli usage "$@"
