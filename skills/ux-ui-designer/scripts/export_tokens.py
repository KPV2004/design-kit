#!/usr/bin/env python3
"""Export color tokens from design.md for developers.

Usage: python export_tokens.py <design.md> <out_dir>

Writes:
  tokens.css          CSS custom properties (--color-brand-600, --bg-page ...)
  tailwind.config.js  theme.extend.colors with the same names as design.md
  tokens.json         flat {name: hex} map for any other stack
"""
import json
import re
import sys
from pathlib import Path


def parse(design):
    scales = {}
    for name, step, hexv in re.findall(r'\|\s*([a-z]+)-(\d+)\s*\|\s*(#[0-9a-fA-F]{6})\b', design):
        scales.setdefault(name, {})[int(step)] = hexv.lower()
    for name, a, b, c in re.findall(r'\|\s*([a-z]+)\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})', design):
        scales.setdefault(name, {}).update({50: a.lower(), 600: b.lower(), 700: c.lower()})
    usage = {}
    sec = design.split('Usage tokens', 1)
    if len(sec) == 2:
        block = sec[1].split('\n#', 1)[0]
        for tok, val in re.findall(r'\|\s*([a-z][a-z-]+)\s*\|\s*([a-z]+(?:-\d+)?|#[0-9a-fA-F]{6})\s*\|', block):
            if tok != 'token':
                usage[tok] = val
    return {k: dict(sorted(v.items())) for k, v in scales.items()}, usage


def resolve(val, scales):
    if val.startswith('#'):
        return val
    if val in ('white', 'black'):
        return '#ffffff' if val == 'white' else '#000000'
    m = re.fullmatch(r'([a-z]+)-(\d+)', val)
    if m and int(m.group(2)) in scales.get(m.group(1), {}):
        return scales[m.group(1)][int(m.group(2))]
    return None


def main(design_path, out_dir):
    design = Path(design_path).read_text(encoding='utf-8')
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scales, usage = parse(design)
    if not scales:
        sys.exit('No color tokens found in design.md')

    css = [':root {']
    for name, steps in scales.items():
        css += [f'  --color-{name}-{s}: {h};' for s, h in steps.items()]
    for tok, val in usage.items():
        ref = re.fullmatch(r'([a-z]+)-(\d+)', val)
        if ref and ref.group(1) in scales:
            css.append(f'  --{tok}: var(--color-{val});')
        elif resolve(val, scales):
            css.append(f'  --{tok}: {resolve(val, scales)};')
    css.append('}')
    (out / 'tokens.css').write_text('\n'.join(css) + '\n', encoding='utf-8')

    colors = {n: {str(s): h for s, h in st.items()} for n, st in scales.items()}
    (out / 'tailwind.config.js').write_text(
        '/** Generated from design.md — edit design.md, then re-run export_tokens.py */\n'
        'module.exports = {\n  theme: {\n    extend: {\n'
        "      fontFamily: { sans: ['\"IBM Plex Sans Thai\"', 'Tahoma', 'system-ui', 'sans-serif'] },\n"
        f'      colors: {json.dumps(colors, indent=8)[:-1]}      }},\n'
        '    },\n  },\n};\n', encoding='utf-8')

    flat = {f'{n}-{s}': h for n, st in scales.items() for s, h in st.items()}
    flat.update({t: resolve(v, scales) for t, v in usage.items() if resolve(v, scales)})
    (out / 'tokens.json').write_text(json.dumps(flat, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Exported {len(flat)} tokens → tokens.css, tailwind.config.js, tokens.json in {out}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
