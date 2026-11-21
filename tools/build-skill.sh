#!/usr/bin/env bash
# Build dist/design-kit.zip for uploading to claude.ai (Customize > Skills > Upload a skill).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist
( cd skills && zip -qr ../dist/design-kit.zip design-kit -x '*/__pycache__/*' '*.DS_Store' )
echo "Built dist/design-kit.zip ($(du -h dist/design-kit.zip | cut -f1))"
