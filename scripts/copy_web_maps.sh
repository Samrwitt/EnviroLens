#!/usr/bin/env bash
# Copy generated map assets into the Next.js public folder
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/geospatial/maps"
DEST="$ROOT/dashboards/web/public/maps"
mkdir -p "$DEST"
if [[ -d "$SRC" ]]; then
  cp -f "$SRC"/*.png "$SRC"/*.html "$DEST/" 2>/dev/null || true
  echo "Copied map assets to $DEST"
  ls -la "$DEST"
else
  echo "No maps at $SRC — run: python -m geospatial.generate_maps"
fi
