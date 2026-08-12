#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/web"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run build
cd "$ROOT"
exec python3 -m aion.physics.server "$@"
