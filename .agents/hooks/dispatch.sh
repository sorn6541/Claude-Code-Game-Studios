#!/usr/bin/env bash
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$HERE/agy-hook-bridge.sh" ]; then
  exec bash "$HERE/agy-hook-bridge.sh" "$@"
fi
