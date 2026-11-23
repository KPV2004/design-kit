#!/usr/bin/env python3
"""Copy every ```mermaid block from the UX spec into the wireframe's Diagrams page.

Usage: python sync_diagrams.py ux-spec.md wireframes.html

The spec is the single source of truth. Each block's title is the nearest heading above it
(screen-ID brackets removed). The wireframe section between <!-- DIAGRAMS:START --> and
<!-- DIAGRAMS:END --> is replaced entirely.
"""
import html
import re
import sys
from pathlib import Path

START, END = '<!-- DIAGRAMS:START -->', '<!-- DIAGRAMS:END -->'


def extract(spec_text):
    out, heading, block, seen = [], 'Diagram', None, {}
    for line in spec_text.splitlines():
        if block is None:
            m = re.match(r'^#{2,4}\s+(.*)', line)
            if m:
                heading = re.sub(r'\[[a-z][a-z0-9-]*\]\s*', '', m.group(1)).strip(' ·/') or 'Diagram'
            elif line.strip().startswith('```mermaid'):
                block = []
        elif line.strip().startswith('```'):
            title = heading
            seen[title] = seen.get(title, 0) + 1
            if seen[title] > 1:
                title = f'{title} ({seen[title]})'
            out.append((title, '\n'.join(block).strip()))
            block = None
        else:
            block.append(line)
    return out


def main(spec_path, wf_path):
    spec = Path(spec_path).read_text(encoding='utf-8')
    wf_file = Path(wf_path)
    wf = wf_file.read_text(encoding='utf-8')
    if START not in wf or END not in wf:
        sys.exit(f'{wf_path}: markers {START} / {END} not found')
    diagrams = extract(spec)
    if not diagrams:
        print('WARN: no ```mermaid blocks found in spec')
    parts = []
    for t, d in diagrams:
        safe = d.replace('</script', '<\\/script')  # keep the block from closing the script tag
        parts.append(f'<script type="text/plain" class="diagram" data-title="{html.escape(t, quote=True)}">\n{safe}\n</script>')
    body = '\n'.join(parts)
    new = wf.split(START)[0] + START + '\n' + body + '\n' + END + wf.split(END, 1)[1]
    wf_file.write_text(new, encoding='utf-8')
    print(f'Synced {len(diagrams)} diagram(s): ' + ', '.join(t for t, _ in diagrams))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
