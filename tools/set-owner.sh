#!/usr/bin/env bash
# One-time setup after forking/creating the repo:
#   ./tools/set-owner.sh <github-user> "<Your Name>"
# Replaces YOUR_GITHUB_USER and YOUR_NAME in the manifests, READMEs and LICENSE.
set -euo pipefail
[ $# -eq 2 ] || { echo 'usage: ./tools/set-owner.sh <github-user> "<Your Name>"'; exit 1; }
cd "$(dirname "$0")/.."
FILES=(.claude-plugin/plugin.json .claude-plugin/marketplace.json README.md README.th.md LICENSE)
python3 - "$1" "$2" "${FILES[@]}" << 'PY'
import sys, pathlib
user, name, *files = sys.argv[1:]
for f in files:
    p = pathlib.Path(f); s = p.read_text(encoding='utf-8')
    p.write_text(s.replace('YOUR_GITHUB_USER', user).replace('YOUR_NAME', name), encoding='utf-8')
    print('updated', f)
PY
grep -rn "YOUR_GITHUB_USER\|YOUR_NAME" "${FILES[@]}" && echo "placeholders left above" || echo "done — no placeholders left"
