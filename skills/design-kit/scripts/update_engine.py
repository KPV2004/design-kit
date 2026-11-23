#!/usr/bin/env python3
"""Refresh a design project's _engine/ and _tools/ from the installed design-kit skill.

Usage: python _tools/update_engine.py [path-to-skills/design-kit]   (run from the project folder)

Each project keeps its own copy of the review engine and tools, so fixes in a newer
design-kit never reach it on their own. This copies the skill's assets/project/_engine/
and scripts/ over the project's copies. Content files (design.md, ux-spec.md,
wireframes.html, mock.html, tokens/, feedback/) are never touched.

Without a path it looks in the usual install locations (Claude Code skills folder,
plugin cache, ~/.agents/skills).
"""
import shutil
import sys
from pathlib import Path

CANDIDATES = [
    '~/.claude/skills/design-kit',
    '~/.agents/skills/design-kit',
    '~/.claude/plugins/marketplaces/design-kit/skills/design-kit',
]


def is_skill(p):
    return (p / 'SKILL.md').exists() and (p / 'assets' / 'project' / '_engine').is_dir()


def find_skill(arg):
    if arg:
        p = Path(arg).expanduser().resolve()
        return p if is_skill(p) else None
    hits = [Path(c).expanduser() for c in CANDIDATES]
    hits += sorted(Path('~/.claude/plugins/cache').expanduser().glob('*/design-kit/*/skills/design-kit'))
    found = [p for p in hits if is_skill(p)]
    return max(found, key=lambda p: version(p / 'assets' / 'project' / '_engine')) if found else None


def version(engine_dir):
    f = engine_dir / 'VERSION'
    return tuple(int(x) for x in f.read_text().strip().split('.')) if f.exists() else (0,)


def main(arg=None):
    project = Path.cwd()
    if not (project / 'design.md').exists() or not (project / '_engine').exists():
        sys.exit('Run this from a design project folder (one that has design.md and _engine/).')
    skill = find_skill(arg)
    if not skill:
        sys.exit('design-kit skill not found — pass its path, e.g. python _tools/update_engine.py ~/.claude/skills/design-kit')
    old = (project / '_engine' / 'VERSION')
    old_v = old.read_text().strip() if old.exists() else 'unversioned'
    new_v = (skill / 'assets' / 'project' / '_engine' / 'VERSION').read_text().strip()
    shutil.copytree(skill / 'assets' / 'project' / '_engine', project / '_engine', dirs_exist_ok=True)
    (project / '_tools').mkdir(exist_ok=True)
    for f in (skill / 'scripts').glob('*.py'):
        shutil.copy2(f, project / '_tools' / f.name)
    print(f'_engine/ and _tools/ updated: {old_v} → {new_v} (from {skill})')
    print('Next: python _tools/verify.py .')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
