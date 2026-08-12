#!/usr/bin/env bash
# Build React UI (if needed) and start the PyTekt Universe dashboard.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB="$ROOT/pytekt/universe/web"

echo "==> PyTekt Universe Dashboard (React)"
if [[ ! -d "$WEB/node_modules" ]]; then
  echo "Installing npm dependencies..."
  (cd "$WEB" && npm install)
fi
echo "Building React app -> pytekt/universe/static/"
(cd "$WEB" && npm run build)
echo "Starting server (default http://127.0.0.1:3857/)"
cd "$ROOT" && python3 -m pytekt.cli universe web "$@"
