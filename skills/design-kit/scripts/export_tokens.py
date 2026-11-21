#!/usr/bin/env python3
"""Export color tokens from design.md for developers.

Usage: python export_tokens.py <design.md> <out_dir>

Writes:
  tokens.css          CSS custom properties (--color-brand-600, --bg-page ...)
                      plus a [data-theme="dark"] block when §2.4 has a Dark column
  tailwind.config.js  theme.extend.colors with the same names as design.md
  tokens.json         flat {name: hex} map for any other stack, plus the §2.4 dark
                      values and the §2.8 platform mapping (e.g. Flutter constants)
"""
import json
import re
import sys
from pathlib import Path


def parse(design):
    # §2.9 theme variants repeat token names with different hexes — scales come only from above that section
    design = design.split('Theme variants', 1)[0]
    scales = {}
    for name, step, hexv in re.findall(r'\|\s*([a-z]+)-(\d+)\s*\|\s*(#[0-9a-fA-F]{6})\b', design):
        scales.setdefault(name, {})[int(step)] = hexv.lower()
    for name, a, b, c in re.findall(r'\|\s*([a-z]+)\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})', design):
        scales.setdefault(name, {}).update({50: a.lower(), 600: b.lower(), 700: c.lower()})
    usage, dark = {}, {}
    sec = design.split('Usage tokens', 1)
    if len(sec) == 2:
        block = sec[1].split('\n#', 1)[0]
        dark_col = None
        for line in block.splitlines():
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if not cells or not cells[0]:
                continue
            if cells[0].lower() == 'token':
                dark_col = next((i for i, c in enumerate(cells) if c.lower() == 'dark'), None)
                continue
            if len(cells) < 2 or set(cells[0]) <= {'-'}:
                continue
            if re.fullmatch(r'[a-z][a-z-]+|#[0-9a-fA-F]{6}|[a-z]+(?:-\d+)?', cells[1]):
                usage[cells[0]] = cells[1]
                if dark_col is not None and len(cells) > dark_col and cells[dark_col] and not set(cells[dark_col]) <= {'-'}:
                    dark[cells[0]] = cells[dark_col]
    return {k: dict(sorted(v.items())) for k, v in scales.items()}, usage, dark


def platform_mapping(design):
    """§2.8 rows: | Token | Web class | Platform name | Hex | — for non-web stacks."""
    sec = design.split('Platform mapping', 1)
    if len(sec) == 2:
        out = {}
        for line in sec[1].split('\n#', 1)[0].splitlines():
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) >= 4 and cells[0].lower() != 'token' and not set(cells[0]) <= {'-'} \
                    and all(cells[:4]) and re.fullmatch(r'[a-z][\w-]*( \(dark\))?', cells[0]):
                out[cells[0]] = {'web': cells[1], 'platform': cells[2], 'hex': cells[3]}
        return out
    return {}


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
    scales, usage, dark = parse(design)
    platform = platform_mapping(design)
    if not scales:
        sys.exit('No color tokens found in design.md')

    def css_ref(val):
        """value → CSS (var(--) for scale refs, hex otherwise); None when unresolvable."""
        ref = re.fullmatch(r'([a-z]+)-(\d+)', val)
        if ref and ref.group(1) in scales:
            return f'var(--color-{val})'
        return resolve(val, scales)

    css = [':root {']
    for name, steps in scales.items():
        css += [f'  --color-{name}-{s}: {h};' for s, h in steps.items()]
    for tok, val in usage.items():
        r = css_ref(val)
        if r:
            css.append(f'  --{tok}: {r};')
    css.append('}')
    if dark:
        css.append('/* attach data-theme="dark" to <html> (or your theme class) */')
        css.append('[data-theme="dark"] {')
        for tok, val in dark.items():
            r = css_ref(val)
            if r:
                css.append(f'  --{tok}: {r};')
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
    if dark:
        flat['dark'] = {t: resolve(v, scales) for t, v in dark.items() if resolve(v, scales)}
    if platform:
        flat['platform'] = platform
    (out / 'tokens.json').write_text(json.dumps(flat, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    extra = [k for k, v in (('dark tokens', dark), ('platform mappings', platform)) if v]
    print(f'Exported {len(flat)} tokens'
          + (f' + {", ".join(extra)}' if extra else '')
          + f' → tokens.css, tailwind.config.js, tokens.json in {out}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
