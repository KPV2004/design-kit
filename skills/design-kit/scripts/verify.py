#!/usr/bin/env python3
"""Check that design.md, wireframes, mockup and UX spec agree with each other.

Usage: python verify.py <folder>   (folder holds design.md, ux-spec.md, wireframes.html, mockup.html, _engine/)

Exit code 1 if any ERROR. WARN lines are worth fixing but don't block delivery.
Browser checks (JS errors, annotation visibility) run only if playwright is installed.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sync_diagrams import extract as extract_diagrams  # noqa: E402

errors, warns = [], []
err = errors.append
warn = warns.append

ID = r'[a-z][a-z0-9-]*'


EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u26FF\u2705\u274C\u2728\u2B50]')


def structure_checks(folder, raw):
    """AI-readability structure: engine files present, SCREENS line, per-screen markers."""
    for name, engine in (('wf', 'wireframe'), ('mk', 'mockup')):
        html = raw[name]
        for ext in ('js', 'css'):
            ref = f'_engine/{engine}.{ext}'
            if ref in html and not (folder / ref).exists():
                err(f'{ref} is referenced but missing — copy _engine/ from the skill')
        if '_engine/' not in html:
            warn(f'{name}: engine is inline (old format) — migrate to content + _engine/ structure')
            continue
        tag = 'template' if name == 'wf' else 'section class="screen"'
        order = re.findall(r'<' + tag + r' id="([^"]+)"', re.sub(r'<!--.*?-->', '', html, flags=re.S))
        toc = re.search(r'SCREENS \(in order\):\s*(.+)', html)
        if not toc:
            err(f'{name}: missing "SCREENS (in order): …" line in the header comment')
        else:
            listed = [x.strip() for x in toc.group(1).split('·') if x.strip()]
            if listed != order:
                err(f'{name}: SCREENS line {listed} ≠ actual screen order {order}')
        if name == 'wf':
            for sid, attrs, body in re.findall(r'<template id="([^"]+)"([^>]*)>(.*?)</template>', html, re.S):
                dev = (re.search(r'data-device="([^"]+)"', attrs) or [None, 'desktop'])[1]
                frames = set(re.findall(r'\bframe-(desktop|tablet|mobile)\b', body))
                if not frames:
                    err(f'wireframe "{sid}": no .frame-desktop / .frame-tablet / .frame-mobile')
                elif dev == 'responsive' and not {'desktop', 'mobile'} <= frames:
                    err(f'wireframe "{sid}" is responsive but lacks a {"desktop" if "desktop" not in frames else "mobile"} frame')
                elif dev in ('desktop', 'mobile') and frames != {dev}:
                    warn(f'wireframe "{sid}": data-device="{dev}" but has frames {sorted(frames)}')
        for sid in order:
            if f'SCREEN: {sid} ' not in html or f'/SCREEN: {sid} ' not in html:
                err(f'{name}: screen "{sid}" is not wrapped in SCREEN / /SCREEN markers')


def icon_map_from_design(design):
    sec = design.split('## 6.', 1)
    if len(sec) < 2:
        return {}
    block = sec[1].split('\n## ', 1)[0]
    return dict(re.findall(r'^\|\s*([a-z][a-z0-9-]*)\s*\|\s*([a-z][a-z0-9-]*:[a-z0-9-]+)\s*\|', block, re.M))


def mockup_icons(html):
    m = re.search(r'const icons\s*=\s*\{(.*?)\};', html, re.S)
    if not m:
        return None
    return {k.strip("'"): v for k, v in re.findall(r"([a-z][\w-]*|'[^']+')\s*:\s*'([a-z][a-z0-9-]*:[a-z0-9-]+)'", m.group(1))}


def html_unescape(t):
    import html
    return html.unescape(t)


def find(folder, *patterns):
    for pattern in patterns:
        hits = sorted(folder.glob(pattern))
        if hits:
            return hits[0]
    return None


def parse_inventory(design):
    if '## 7. Screen inventory' not in design:
        err('design.md: missing "## 7. Screen inventory" section')
        return {}
    sec = design.split('## 7. Screen inventory', 1)[1].split('\n## ', 1)[0]
    rows = {}
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 5 and re.fullmatch(ID, cells[0]) and cells[0] != 'id':
            rows[cells[0]] = {'title': cells[1], 'wireframe': '✅' in cells[3], 'mockup': '✅' in cells[4]}
    return rows


def design_tokens(design):
    # §2.9 theme variants repeat token names with different hexes — parse scales only up to that section
    design = design.split('Theme variants', 1)[0]
    t = {k: v.lower() for k, v in re.findall(r'\|\s*([a-z]+-\d+)\s*\|\s*(#[0-9a-fA-F]{6})\b', design)}
    for name, a, b, c in re.findall(r'\|\s*([a-z]+)\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})', design):
        t.update({f'{name}-50': a.lower(), f'{name}-600': b.lower(), f'{name}-700': c.lower()})
    return t


def mockup_tokens(html):
    m = re.search(r'const tokens\s*=\s*\{(.*?)\n\s*\};', html, re.S)
    if not m:
        return None
    out = {}
    for name, body in re.findall(r'(\w+)\s*:\s*\{([^}]*)\}', m.group(1)):
        for k, v in re.findall(r"(\d+)\s*:\s*['\"](#[0-9a-fA-F]{6})['\"]", body):
            out[f'{name}-{k}'] = v.lower()
    return out


def mockup_usage(html):
    m = re.search(r'const usageTokens\s*=\s*\{(.*?)\n\s*\};', html, re.S)
    if not m:
        return None
    return {k: v.lower() for k, v in re.findall(r"'([a-z][a-z-]+)'\s*:\s*'(#[0-9a-fA-F]{6})'", m.group(1))}


def mockup_themes(html):
    m = re.search(r'const themes\s*=\s*\{(.*?)\n\s*\};', html, re.S)
    if not m:
        return None
    out = {}
    for name, blk in re.findall(r"'([^']+)'\s*:\s*\{([^{}]*)\}", m.group(1)):
        out[name] = {k: v.lower() for k, v in re.findall(r"'([a-z][a-z0-9-]*)'\s*:\s*'(#[0-9a-fA-F]{6})'", blk)}
    if re.search(r"'Default'\s*:\s*null", m.group(1)):
        out.setdefault('Default', {})
    return out


def design_usage(design):
    """§2.4 rows → {token: value-ref-or-hex} (first value column, Light or Value)."""
    sec = design.split('Usage tokens', 1)
    if len(sec) != 2:
        return {}
    out = {}
    for line in sec[1].split('\n#', 1)[0].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells or not cells[0] or cells[0].lower() == 'token' or set(cells[0]) <= {'-'}:
            continue
        if len(cells) >= 2:
            out[cells[0]] = cells[1]
    return out


def design_theme_names(design):
    sec = design.split('Theme variants', 1)
    if len(sec) != 2:
        return {}
    names = {}
    for line in sec[1].split('\n#', 1)[0].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[0] not in ('Theme',) and not set(cells[0]) <= {'-'} and cells[0]:
            names.setdefault(cells[0], {})[cells[1]] = cells[2]
    return names


def resolve_ref(val, tokens_map):
    if val.startswith('#'):
        return val.lower()
    if val == 'white':
        return '#ffffff'
    m = re.fullmatch(r'([a-z]+)-(\d+)', val)
    if m:
        return tokens_map.get(val.lower())
    return None


def main(folder):
    folder = Path(folder)
    files = {
        'design': folder / 'design.md',
        'wf': find(folder, 'wireframes.html', '*-wireframes.html'),
        'mk': find(folder, 'mock.html', '*:mock.html', 'mockup.html', '*-mockup.html'),
        'spec': find(folder, 'ux-spec.md', '*-ux-spec.md'),
    }
    for k, f in files.items():
        if not f or not f.exists():
            err(f'missing file: {k}')
    if errors:
        return report()

    strip = lambda h: re.sub(r'<!--.*?-->', '', h, flags=re.S)  # ignore commented-out examples
    raw = {k: files[k].read_text(encoding='utf-8') for k in ('wf', 'mk')}
    structure_checks(folder, raw)
    design = files['design'].read_text(encoding='utf-8')
    wf = strip(files['wf'].read_text(encoding='utf-8'))
    mk = strip(files['mk'].read_text(encoding='utf-8'))
    spec = files['spec'].read_text(encoding='utf-8')

    inv = parse_inventory(design)
    ids_inv = set(inv)
    ids_wf = set(re.findall(r'<template id="([^"]+)"', wf))
    mk_sections = dict(re.findall(r'<section class="screen[^"]*" id="([^"]+)"([^>]*)>', mk))
    for i in sorted(i for i in mk_sections if not i.endswith(':mock')):
        err(f'mock screen id "{i}" must end with ":mock" — it pairs with wireframe screen "{i}"')
    ids_mk = {i[:-5] for i in mk_sections if i.endswith(':mock')} - {'design-system'}
    ids_spec = set()
    for line in spec.splitlines():
        if line.startswith('### '):
            ids_spec.update(re.findall(r'\[(' + ID + r')\]', line))

    # --- inventory vs files
    for i in sorted(ids_inv - ids_wf):
        err(f'wireframe missing for screen "{i}"')
    for i in sorted(ids_wf - ids_inv):
        err(f'wireframe "{i}" not in design.md inventory')
    for i in sorted(ids_inv - ids_spec):
        err(f'spec has no "### [{i}]" heading')
    for i in sorted(ids_spec - ids_inv):
        err(f'spec screen "{i}" not in inventory')
    for i, row in sorted(inv.items()):
        if row['mockup'] and i not in ids_mk:
            err(f'inventory says Mockup ✅ for "{i}" but mock has no "{i}:mock" screen')
        if not row['mockup'] and i in ids_mk:
            warn(f'mock has "{i}:mock" but inventory Mockup column is not ✅')
    for i in sorted(ids_mk - ids_inv):
        err(f'mock screen "{i}:mock" not in inventory')

    # --- responsive duplication
    header = design[:600].lower()
    is_native = 'native' in header or ('mobile' in header and 'web' not in header)
    for i in sorted(ids_inv):
        if i.startswith('m-') and i[2:] in ids_inv and not is_native:
            err(f'"{i}" duplicates "{i[2:]}" — responsive web must use one screen ID with a mobile frame/viewport, not an m-* copy')

    # --- links
    for name, html, ids in (('wireframes', wf, ids_wf), ('mockup', mk, set(mk_sections))):
        for t in sorted(set(re.findall(r"showScreen\('([^']+)'\)", html)) - ids - {'id'}):
            err(f'{name}: showScreen("{t}") points to a screen that does not exist')

    # --- notes vs markers (static)
    for sid, attrs in mk_sections.items():
        body = mk.split(f'id="{sid}"', 1)[1].split('</section>', 1)[0]
        markers = len(re.findall(r'class="anno"', body))
        notes_m = re.search(r'data-notes="([^"]*)"', attrs)
        notes = [n for n in (notes_m.group(1).split('|') if notes_m else []) if n.strip()]
        if markers != len(notes):
            err(f'mockup "{sid}": {markers} annotation markers but {len(notes)} data-notes entries')

    # --- tokens
    dt, mt = design_tokens(design), mockup_tokens(mk)
    if mt is None:
        err('mock: no `const tokens = {...}` block')
    else:
        for k, v in sorted(dt.items()):
            if mt.get(k) != v:
                err(f'token {k}: design.md {v} ≠ mock {mt.get(k)}')
    if re.search(r'(?:bg|text|border|ring|fill|stroke)-\[#', mk):
        err('mock uses raw hex classes like bg-[#...] — use token classes')

    # --- usage tokens (theme-engine defaults) + theme variants
    mu = mockup_usage(mk)
    du = design_usage(design)
    if mu is None:
        warn('mock has no `const usageTokens` block — the theme picker needs defaults from design.md §2.4')
    else:
        for k, ref in sorted(du.items()):
            expect = resolve_ref(ref, dt)
            if expect and mu.get(k) != expect:
                err(f'usage token {k}: design.md {ref} → {expect} ≠ mock {mu.get(k)}')
    th = mockup_themes(mk)
    dth = design_theme_names(design)
    if th is None:
        warn('mock has no `const themes` block — add theme variants (design.md §2.9) for the theme picker')
    else:
        known = set(dt) | set(du)
        for name, ov in sorted(th.items()):
            if name != 'Default' and name not in dth:
                warn(f'theme "{name}" is not documented in design.md §2.9 Theme variants')
            for k in ov:
                if k not in known:
                    warn(f'theme "{name}" overrides unknown token "{k}"')
        for name in sorted(set(dth) - set(th)):
            warn(f'design.md §2.9 theme "{name}" is missing from the mock theme picker')
    if files['mk'].name not in ('mock.html',) and not files['mk'].name.endswith(':mock.html'):
        warn(f"{files['mk'].name}: rename the mock file to mock.html (v1.2 convention)")

    # --- icons
    icon_map = icon_map_from_design(design)
    mk_icons = mockup_icons(mk)
    screens_html = ''.join(mk.split(f'id="{sid}"', 1)[1].split('</section>', 1)[0] for sid in mk_sections)
    used = set(re.findall(r'<iconify-icon[^>]*\sicon="([^"]+)"', screens_html))
    emoji = sorted(set(EMOJI.findall(screens_html)))
    if emoji:
        err(f'mockup screens use emoji as icons: {" ".join(emoji)} — use icons from the design.md icon map')
    if not icon_map:
        warn('design.md §6 has no icon map table (| purpose | prefix:name |)')
    else:
        if mk_icons is not None and mk_icons != icon_map:
            diff = sorted(set(icon_map.items()) ^ set(mk_icons.items()))
            err(f'icon map differs between design.md and mockup `const icons`: {diff[:6]}')
        for n in sorted(used - set(icon_map.values())):
            err(f'mockup uses icon "{n}" which is not in the design.md icon map')
        prefixes = {n.split(':')[0].replace('material-symbols-light', 'material-symbols') for n in icon_map.values()}
        if len(prefixes) > 1:
            err(f'icon map mixes sets {sorted(prefixes)} — use one set')
        if prefixes == {'lucide'}:
            warn('icon set is Lucide — the default of most AI builders; fine only if the existing stack uses it')
    all_icons = sorted(set(icon_map.values()) | used)

    # --- dev diagrams
    spec_dg = extract_diagrams(spec)
    raw_wf = files['wf'].read_text(encoding='utf-8')
    wf_dg = [(html_unescape(t), d.replace('<\\/script', '</script').strip())
             for t, d in re.findall(r'<script type="text/plain" class="diagram" data-title="([^"]*)">\n?(.*?)</script>', raw_wf, re.S)]
    if [(t, d.strip()) for t, d in spec_dg] != wf_dg:
        err('wireframe Diagrams page is out of sync with the spec — run scripts/sync_diagrams.py')
    kinds = ' '.join(d.split('\n', 1)[0] for _, d in spec_dg)
    if 'flowchart' not in kinds:
        err('spec has no user flow diagram (```mermaid flowchart)')
    if 'erDiagram' not in kinds:
        warn('spec has no ER diagram — needed whenever screens show or save data')
    if 'sequenceDiagram' not in kinds:
        warn('spec has no sequence diagram for the main actions')
    if re.search(r'status|สถานะ', spec, re.I) and 'stateDiagram' not in kinds:
        warn('spec mentions statuses but has no stateDiagram-v2')

    # --- spec must stand alone: these sections exist and have rows
    for heading in ('## States', '## Fields & validation', '## Interactions & behavior',
                    '## Copy deck', '## API contract'):
        if heading not in spec:
            warn(f'spec has no "{heading[3:]}" section — the spec must stand alone from app code')
            continue
        block = spec.split(heading, 1)[1].split('\n## ', 1)[0]
        rows = [l for l in block.splitlines() if l.strip().startswith('|')]
        if len(rows) < 3:
            warn(f'spec "{heading}" table has no data rows — every data screen needs one')

    # --- dark mode & platform mapping (design.md header promises)
    header = design[:600].lower()
    if re.search(r'dark mode:\s*(yes|true|light \+ dark|light\+dark)', header):
        sec = design.split('Usage tokens', 1)
        if len(sec) == 2 and not re.search(r'^\|\s*token\s*\|.*\bdark\b', sec[1].split('\n#', 1)[0], re.M | re.I):
            warn('design.md says Dark mode: yes but §2.4 usage tokens have no Dark column — devs cannot build the dark theme from the spec')
    if re.search(r'stack:\s*(flutter|react native|native)', header) and 'Platform mapping' not in design:
        warn('design.md stack is non-web but §2.8 platform mapping is missing — tokens/ alone cannot be pasted into Flutter/native code')

    # --- version
    dv = re.search(r'Version:\s*([\d.]+)', design)
    sv = re.search(r'Version\s*([\d.]+)', spec)
    if dv and sv and dv.group(1) != sv.group(1):
        warn(f'version mismatch: design.md {dv.group(1)} vs spec {sv.group(1)}')

    browser_checks(files, mk_sections, all_icons)
    return report(len(ids_inv))


def browser_checks(files, mk_sections, all_icons=()):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        warn('playwright not installed — skipped JS-error and annotation-visibility checks')
        return
    with sync_playwright() as p:
        b = p.chromium.launch()
        for key in ('wf', 'mk'):
            pg = b.new_page(viewport={'width': 1440, 'height': 900})
            js = []
            pg.on('pageerror', lambda e, js=js: js.append(str(e)))
            pg.goto(files[key].resolve().as_uri())
            pg.wait_for_timeout(2500)
            for e in js:
                err(f'{files[key].name}: JS error: {e}')
            pg.close()
        # Every icon name must exist in its set
        if all_icons:
            pg = b.new_page()
            pg.goto(files['mk'].resolve().as_uri() + '?frame=1')
            pg.wait_for_timeout(1500)
            missing = pg.evaluate("""async (names) => {
                if (!customElements.get('iconify-icon')) return ['(iconify-icon did not load)'];
                const box = document.createElement('div'); document.body.appendChild(box);
                box.innerHTML = names.map(n => `<iconify-icon noobserver icon="${n}"></iconify-icon>`).join('');
                await new Promise(r => setTimeout(r, 4000));
                return [...box.children].filter(e => !e.shadowRoot?.querySelector('svg')).map(e => e.getAttribute('icon'));
            }""", all_icons)
            for n in missing:
                err(f'icon "{n}" does not exist (check the exact name in the icon set)')
            pg.close()

        # Mermaid syntax of every diagram on the wireframe Diagrams page
        pg = b.new_page()
        pg.goto(files['wf'].resolve().as_uri())
        pg.wait_for_timeout(2500)
        bad = pg.evaluate("""async () => {
            if (!window.mermaid) return [['(all)', 'Mermaid did not load']];
            const out = [];
            for (const s of document.querySelectorAll('script.diagram')) {
                try { await mermaid.parse(s.textContent.trim()); } catch (e) { out.push([s.dataset.title, String(e.message || e).split('\\n')[0]]); }
            }
            return out;
        }""")
        for title, msg in bad:
            err(f'diagram "{title}": Mermaid syntax error — {msg}')
        pg.close()

        # Annotation visibility inside the mockup's frame mode
        uri = files['mk'].resolve().as_uri() + '?frame=1'
        for width, label, level in ((1440, 'desktop', err), (390, 'mobile', warn)):
            pg = b.new_page(viewport={'width': width, 'height': 900})
            pg.goto(uri)
            pg.wait_for_timeout(2000)
            for sid, attrs in mk_sections.items():
                if label == 'desktop' and 'data-device="mobile"' in attrs:
                    continue
                pg.evaluate(f"showScreen('{sid}')")
                pg.wait_for_timeout(100)
                hidden = pg.evaluate(f"""() => [...document.querySelectorAll('[id="{sid}"] .anno')]
                    .filter(a => !a.closest('[data-state]:not(.show)'))
                    .map(a => [a.textContent.trim(), a.getBoundingClientRect().width > 0 && getComputedStyle(a).visibility !== 'hidden'])
                    .filter(x => !x[1]).map(x => x[0])""")
                if hidden:
                    level(f'mockup "{sid}" ({label}): annotation marker(s) {hidden} not visible')
            pg.close()
        b.close()


def report(n=None):
    for e in errors:
        print('ERROR', e)
    for w in warns:
        print('WARN ', w)
    print(f'\n{len(errors)} error(s), {len(warns)} warning(s)' + (f' — {n} screens in inventory' if n else ''))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
