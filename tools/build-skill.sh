#!/usr/bin/env bash
# Build dist/ux-ui-designer.zip for uploading to claude.ai (Customize > Skills > Upload a skill).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist
( cd skills && zip -qr ../dist/ux-ui-designer.zip ux-ui-designer -x '*/__pycache__/*' '*.DS_Store' )
echo "Built dist/ux-ui-designer.zip ($(du -h dist/ux-ui-designer.zip | cut -f1))"
