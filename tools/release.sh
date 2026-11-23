#!/usr/bin/env bash
# Release in two steps, matching the branch + PR workflow:
#
#   ./tools/release.sh prepare 1.3.0   on an up-to-date main: writes 1.3.0 everywhere, dates the
#                                      CHANGELOG "## Unreleased" entry, runs checks, opens a release PR
#   (merge the PR on GitHub)
#   ./tools/release.sh tag 1.3.0       on main after the merge: checks every version says 1.3.0,
#                                      then pushes tag v1.3.0 → the Release workflow builds the zip
#
# Version lives in: .claude-plugin/plugin.json (source of truth), skills/design-kit/assets/project/_engine/VERSION,
# KIT_VERSION in skills/design-kit/scripts/verify.py, the docs site <meta name="dk-version">, and the example
# project's copies of _engine/ and _tools/.
set -euo pipefail
cd "$(dirname "$0")/.."

die() { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
ok()  { printf '\033[32m✓\033[0m %s\n' "$*"; }

CMD=${1:-}; VER=${2:-}
[[ "$CMD" == prepare || "$CMD" == tag ]] || die "usage: tools/release.sh prepare|tag X.Y.Z"
[[ "$VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "version must look like 1.3.0 (no leading v) — got '$VER'"
TAG="v$VER"
CUR=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")

on_fresh_main() {
  git fetch -q origin main --tags
  [[ "$(git branch --show-current)" == main ]] || die "switch to main first (git switch main && git pull)"
  [[ -z "$(git status --porcelain)" ]] || die "working tree has uncommitted changes"
  [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || die "main is not equal to origin/main — run git pull"
}

if [[ "$CMD" == prepare ]]; then
  on_fresh_main
  python3 - "$CUR" "$VER" <<'EOF' || die "$VER must be greater than the current version $CUR"
import sys; t = lambda v: tuple(map(int, v.split('.'))); sys.exit(0 if t(sys.argv[2]) > t(sys.argv[1]) else 1)
EOF
  git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && die "tag $TAG already exists"
  grep -q '^## Unreleased' CHANGELOG.md || die 'CHANGELOG.md needs a "## Unreleased" section describing this release'

  git switch -q -c "release/$VER"
  python3 - "$VER" <<'EOF'
import datetime, json, re, sys
from pathlib import Path
v = sys.argv[1]
def sub(path, pattern, repl, count=1):
    p = Path(path); s = p.read_text(encoding='utf-8')
    s2, n = re.subn(pattern, repl, s, count=count, flags=re.M)
    if n == 0: sys.exit(f'{path}: pattern not found: {pattern}')
    p.write_text(s2, encoding='utf-8')
sub('.claude-plugin/plugin.json', r'"version":\s*"[^"]+"', f'"version": "{v}"')
Path('skills/design-kit/assets/project/_engine/VERSION').write_text(v + '\n')
sub('skills/design-kit/scripts/verify.py', r"^KIT_VERSION = '[^']+'", f"KIT_VERSION = '{v}'")
sub('docs-site/index.html', r'<meta name="dk-version" content="[^"]+">', f'<meta name="dk-version" content="{v}">')
sub('CHANGELOG.md', r'^## Unreleased\s*$', f'## {v} — {datetime.date.today().isoformat()}')
EOF
  ok "version $CUR → $VER written to plugin.json, _engine/VERSION, verify.py, docs site, CHANGELOG"
  ( cd examples/procura-design && python3 _tools/update_engine.py ../../skills/design-kit >/dev/null )
  ok "example project engine refreshed"
  ./tools/check.sh --fast >/dev/null 2>&1 || die "checks failed — run ./tools/check.sh to see why (branch release/$VER left in place)"
  ok "checks passed"
  git add -A
  git commit -q -m "Release $VER"
  git push -q -u origin "release/$VER"
  NOTES=$(python3 - "$VER" <<'EOF'
import re, sys
s = open('CHANGELOG.md', encoding='utf-8').read()
m = re.search(r'^## ' + re.escape(sys.argv[1]) + r'.*?\n(.*?)(?=^## |\Z)', s, re.S | re.M)
print(m.group(1).strip() if m else '')
EOF
)
  PR=$(gh pr create --base main --head "release/$VER" --title "Release $VER" \
       --body "$(printf 'Version bump for **%s**. After merging, run `./tools/release.sh tag %s`.\n\n%s\n' "$VER" "$VER" "$NOTES")")
  ok "release PR: $PR"
  echo "Next: merge it on GitHub, then  git switch main && git pull && ./tools/release.sh tag $VER"
else
  on_fresh_main
  [[ "$CUR" == "$VER" ]] || die "plugin.json on main says $CUR, not $VER — merge the release PR first"
  ENGINE=$(tr -d '[:space:]' < skills/design-kit/assets/project/_engine/VERSION)
  [[ "$ENGINE" == "$VER" ]] || die "_engine/VERSION says $ENGINE, not $VER"
  grep -q "^## $VER " CHANGELOG.md || die "CHANGELOG.md has no '## $VER' entry"
  git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && die "tag $TAG already exists"
  git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1 && die "tag $TAG already exists on origin"
  git tag -a "$TAG" -m "design-kit $VER"
  git push -q origin "$TAG"
  ok "pushed $TAG — the Release workflow builds design-kit.zip and publishes the GitHub Release"
  echo "Watch: gh run list --workflow release.yml --limit 1"
fi
