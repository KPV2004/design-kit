#!/usr/bin/env python3
"""Export design tokens from design.md for developers.

Usage: python export_tokens.py <design.md> <out_dir>

Reads colors (§2) and, when present, the §4 motion / breakpoint / z-index tables.

Writes:
  tokens.css          CSS custom properties (--color-brand-600, --bg-page ...)
                      plus a [data-theme="dark"] block when §2.4 has a Dark column,
                      --duration-* / --ease-* (0ms under prefers-reduced-motion),
                      --breakpoint-* and --z-*
  tailwind.config.js  theme.extend.colors with the same names as design.md, plus
                      theme.screens, extend.transitionDuration,
                      extend.transitionTimingFunction and extend.zIndex
  tokens.json         flat {name: hex} map for any other stack, plus the §2.4 dark
                      values, the §2.8 platform mapping (e.g. Flutter constants) and
                      "motion" {duration: {name: ms}, easing: {name: css}},
                      "breakpoints" {name: px}, "zIndex" {name: int}
"""
import json
import re
import sys
from pathlib import Path


def parse(design):
    # §2.9 theme variants repeat token names with different hexes — scales come only from above that section
    design = design.split('Theme variants', 1)[0]
    scales = {}
    for name, step, hexv in re.findall(r'^\|\s*([a-z]+)-(\d+)\s*\|\s*(#[0-9a-fA-F]{6})\b', design, re.M):
        scales.setdefault(name, {})[int(step)] = hexv.lower()
    for name, a, b, c in re.findall(r'^\|\s*([a-z]+)\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})', design, re.M):
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


TIME = re.compile(r'(\d+(?:\.\d+)?)\s*(ms|s)')
EASING = re.compile(r'cubic-bezier\(\s*-?[\d.]+\s*(?:,\s*-?[\d.]+\s*){3}\)|linear|ease(?:-in|-out|-in-out)?'
                    r'|steps\(\s*\d+\s*(?:,\s*[a-z-]+\s*)?\)')
NAME = re.compile(r'[a-z][a-z0-9-]*')


# §4 sub-headings, matched on the whole heading text (case-insensitive) after an optional
# section number — "### 4.1 Motion tokens" yes; "## 4. Spacing, …, motion" or "### Motion notes" no.
SECTION_NAMES = {
    'motion': ('motion tokens', 'motion'),
    'breakpoints': ('breakpoints',),
    'z-index': ('z-index (layers)', 'z-index', 'z-index tokens', 'layers'),
}


def section_rows(design, key):
    """(token, value) rows of the `| Token | … |` table under each `###` heading named SECTION_NAMES[key]."""
    names = '|'.join(re.escape(n) for n in SECTION_NAMES[key])
    heading = re.compile(r'^###[ \t]+(?:\d+(?:\.\d+)*\.?[ \t]+)?(?:' + names + r')[ \t]*#*[ \t]*$', re.M | re.I)
    rows = []
    for m in heading.finditer(design):
        in_table = False
        for line in design[m.end():].split('\n#', 1)[0].splitlines():
            if not line.lstrip().startswith('|'):
                if in_table:
                    break  # only the first Token table under the heading
                continue
            cells = [c.strip().strip('`') for c in line.strip().strip('|').split('|')]
            if not in_table:
                in_table = cells[0].lower() == 'token'
                if not in_table:
                    break  # first table is not a token table — read nothing
                continue
            if set(cells[0]) <= {'-', ':'} or len(cells) < 2:
                continue
            rows.append((cells[0], cells[1]))
    return rows


def layout_tokens(design):
    """§4.1 motion, §4.2 breakpoints, §4.3 z-index → (tokens, skipped rows as messages)."""
    motion, bps, z, skipped = {'duration': {}, 'easing': {}}, {}, {}, []
    for tok, val in section_rows(design, 'motion'):
        t, e = TIME.fullmatch(val), EASING.fullmatch(val)
        if NAME.fullmatch(tok) and t:
            ms = float(t.group(1)) * (1000 if t.group(2) == 's' else 1)
            motion['duration'][tok.removeprefix('duration-')] = int(ms) if ms.is_integer() else ms
        elif NAME.fullmatch(tok) and e:
            motion['easing'][tok.removeprefix('ease-')] = re.sub(r'\s*,\s*', ', ', val)
        else:
            skipped.append(f'motion {tok!r} = {val!r}')
    for tok, val in section_rows(design, 'breakpoints'):
        m = re.fullmatch(r'(\d+)\s*(?:px)?', val)
        if NAME.fullmatch(tok) and m:
            bps[tok.removeprefix('breakpoint-')] = int(m.group(1))
        else:
            skipped.append(f'breakpoint {tok!r} = {val!r}')
    for tok, val in section_rows(design, 'z-index'):
        if NAME.fullmatch(tok) and re.fullmatch(r'-?\d+', val):
            z[tok.removeprefix('z-')] = int(val)
        else:
            skipped.append(f'z-index {tok!r} = {val!r}')
    if list(bps.values()) != sorted(bps.values()):
        skipped.append('breakpoints are not ascending — mobile-first min-widths must grow')
    bps = dict(sorted(bps.items(), key=lambda kv: kv[1]))
    if not motion['duration'] and not motion['easing']:
        motion = {}
    return {'motion': motion, 'breakpoints': bps, 'zIndex': z}, skipped


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
    layout, skipped = layout_tokens(design)
    motion, bps, zidx = layout['motion'], layout['breakpoints'], layout['zIndex']
    if not scales:
        sys.exit('No color tokens found in design.md')
    for msg in skipped:
        print(f'WARN skipped {msg} — see design.md §4 value formats', file=sys.stderr)

    def ms(v):
        return f'{v}ms'

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
    if motion or bps or zidx:
        css.append(':root {')
        css += [f'  --duration-{n}: {ms(v)};' for n, v in motion.get('duration', {}).items()]
        css += [f'  --ease-{n}: {v};' for n, v in motion.get('easing', {}).items()]
        if bps:
            css.append('  /* custom properties do not work inside @media — use for JS (matchMedia) or container math */')
        css += [f'  --breakpoint-{n}: {v}px;' for n, v in bps.items()]
        css += [f'  --z-{n}: {v};' for n, v in zidx.items()]
        css.append('}')
    if motion.get('duration'):
        css.append('@media (prefers-reduced-motion: reduce) {')
        css.append('  :root {')
        css += [f'    --duration-{n}: 0ms;' for n in motion['duration']]
        css.append('  }')
        css.append('}')
    (out / 'tokens.css').write_text('\n'.join(css) + '\n', encoding='utf-8')

    colors = {n: {str(s): h for s, h in st.items()} for n, st in scales.items()}

    def js_obj(d, ind):
        return json.dumps(d, indent=ind)[:-1] + ' ' * (ind - 2) + '}'

    extend = [f'      colors: {js_obj(colors, 8)},\n']
    if motion.get('duration'):
        extend.append(f'      transitionDuration: {js_obj({n: ms(v) for n, v in motion["duration"].items()}, 8)},\n')
    if motion.get('easing'):
        extend.append(f'      transitionTimingFunction: {js_obj(motion["easing"], 8)},\n')
    if zidx:
        extend.append(f'      zIndex: {js_obj({n: str(v) for n, v in zidx.items()}, 8)},\n')
    screens = (f'    // design.md §4.2 replaces Tailwind\'s default screens\n'
               f'    screens: {js_obj({n: f"{v}px" for n, v in bps.items()}, 6)},\n') if bps else ''
    (out / 'tailwind.config.js').write_text(
        '/** Generated from design.md — edit design.md, then re-run export_tokens.py */\n'
        'module.exports = {\n  theme: {\n' + screens + '    extend: {\n'
        "      fontFamily: { sans: ['\"IBM Plex Sans Thai\"', 'Tahoma', 'system-ui', 'sans-serif'] },\n"
        + ''.join(extend) +
        '    },\n  },\n};\n', encoding='utf-8')

    flat = {f'{n}-{s}': h for n, st in scales.items() for s, h in st.items()}
    flat.update({t: resolve(v, scales) for t, v in usage.items() if resolve(v, scales)})
    if dark:
        flat['dark'] = {t: resolve(v, scales) for t, v in dark.items() if resolve(v, scales)}
    if platform:
        flat['platform'] = platform
    flat.update({k: v for k, v in layout.items() if v})
    (out / 'tokens.json').write_text(json.dumps(flat, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    extra = [k for k, v in (('dark tokens', dark), ('platform mappings', platform), ('motion', motion),
                            ('breakpoints', bps), ('z-index', zidx)) if v]
    print(f'Exported {len(flat)} tokens'
          + (f' + {", ".join(extra)}' if extra else '')
          + f' → tokens.css, tailwind.config.js, tokens.json in {out}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
