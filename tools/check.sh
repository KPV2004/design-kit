#!/usr/bin/env bash
# Everything CI runs, in one command. Run before opening a PR:  ./tools/check.sh
#   --fast   skip the browser tests (no playwright needed)
set -euo pipefail
cd "$(dirname "$0")/.."
FAST=${1:-}
step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }

step "Manifests are valid JSON"
python3 -c "import json; [json.load(open(f)) for f in ('.claude-plugin/plugin.json', '.claude-plugin/marketplace.json')]"

step "Unit tests (parsers, engine version, versions in sync)"
python3 -m unittest discover -s tests -p 'test_scripts.py'

step "examples/procura-design uses the current engine and tools"
diff -r --exclude=__pycache__ skills/design-kit/assets/project/_engine examples/procura-design/_engine
for f in skills/design-kit/scripts/*.py; do diff -q "$f" "examples/procura-design/_tools/$(basename "$f")"; done
echo "in sync (refresh with: cd examples/procura-design && python3 _tools/update_engine.py ../../skills/design-kit)"

step "verify.py on the example project (errors fail the build)"
( cd examples/procura-design && python3 _tools/verify.py . )

if [ "$FAST" != "--fast" ]; then
  step "Browser tests (template + example)"
  python3 tests/test_browser.py
fi

step "Skill zip builds"
./tools/build-skill.sh

printf '\n\033[32mAll checks passed\033[0m\n'
