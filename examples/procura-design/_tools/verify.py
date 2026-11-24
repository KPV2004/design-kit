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

# design-kit version these tools ship with — tools/release.sh keeps it equal to plugin.json and _engine/VERSION
KIT_VERSION = '2.0.0'

errors, warns = [], []
err = errors.append
warn = warns.append

ID = r'[a-z][a-z0-9-]*'


EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u26FF\u2705\u274C\u2728\u2B50]')


def vtuple(v):
    return tuple(int(x) for x in re.findall(r'\d+', v)[:3])


def engine_version_check(folder):
    """Each project holds its own _engine/ copy, which never updates itself — flag stale ones."""
    if not (folder / '_engine').is_dir():
        return
    vf = folder / '_engine' / 'VERSION'
    fix = 'run `python _tools/update_engine.py <path-to-skills/design-kit>`'
    if not vf.exists():
        warn(f'_engine/ has no VERSION stamp (made before design-kit 1.2.1) — it misses later engine fixes; {fix}')
        return
    ev = vf.read_text(encoding='utf-8').strip()
    if vtuple(ev) < vtuple(KIT_VERSION):
        warn(f'_engine/ is {ev} but these tools are {KIT_VERSION} — {fix}')
    elif vtuple(ev) > vtuple(KIT_VERSION):
        warn(f'_tools/ ({KIT_VERSION}) are older than _engine/ ({ev}) — {fix}')


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


def split_cells(line):
    return [c.strip().replace('`', '').strip() for c in line.strip().strip('|').split('|')]


def is_separator(cells):
    return all(c and set(c) <= set('-: ') for c in cells)


def section(text, heading, level='## '):
    """Body under an exact heading line, up to the next heading of the same or higher level."""
    m = re.search(r'^' + re.escape(heading) + r'[ \t]*$', text, re.M)
    if not m:
        return None
    body = text[m.end():]
    stops = ['\n## '] if level == '## ' else ['\n## ', '\n### ']
    for s in stops:
        body = body.split(s, 1)[0]
    return body


def tables(block):
    """Markdown pipe tables in a block → list of (header, rows); header names lower-case, rows as dicts."""
    out, cur = [], []
    for line in block.splitlines() + ['']:
        if line.strip().startswith('|'):
            cur.append(split_cells(line))
            continue
        if cur:
            header = [h.lower() for h in cur[0]]
            body = [c for c in cur[1:] if not is_separator(c)]
            out.append((header, [dict(zip(header, c + [''] * (len(header) - len(c)))) for c in body]))
            cur = []
    return out


def parse_inventory(design):
    if '## 7. Screen inventory' not in design:
        err('design.md: missing "## 7. Screen inventory" section')
        return {}
    sec = design.split('## 7. Screen inventory', 1)[1].split('\n## ', 1)[0]
    rows = {}
    for header, body in tables(sec):
        named = {'id', 'wireframe', 'mockup'} <= set(header)
        for r in body:
            cells = list(r.values())
            sid = r.get('id', '') if named else (cells[0] if cells else '')
            if len(cells) < 5 or not re.fullmatch(ID, sid):
                continue
            if named:
                rows[sid] = {'title': r.get('screen', ''), 'module': r.get('module', ''),
                             'wireframe': '✅' in r['wireframe'], 'mockup': '✅' in r['mockup'],
                             'req': r.get('req id'), 'priority': r.get('priority'), 'status': r.get('status')}
            else:  # header-less / renamed columns: old positional layout
                rows[sid] = {'title': cells[1], 'module': cells[2], 'wireframe': '✅' in cells[3],
                             'mockup': '✅' in cells[4], 'req': None, 'priority': None, 'status': None}
    return rows


# --- Phase 1 UX-gap checks (docs/p1-schema.md): R1 roles, R2 traceability + AC, R3 priority/status, R6 a11y
# All ERROR, including projects made with v2.0.0 that lack the new sections/columns (breaking change, target 3.0.0).
REQ_ID = re.compile(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*')
PRIORITIES = ('MVP', 'P2', 'P3', 'Later')
STATUSES = ('draft', 'review', 'approved', 'changed')
NONE = ('—', 'n/a')
PERM = re.compile(r'✅(?: \(.+\))?|—')
ACTIONS = ('view', 'create', 'edit', 'approve', 'delete')


def multi(value):
    return [v for v in re.split(r'\s*,\s*', value.strip()) if v]


def inventory_checks(inv):
    """R2 Req ID + R3 Priority/Status columns of design.md §7."""
    if not inv:
        return
    sample = next(iter(inv.values()))
    for key, col in (('req', 'Req ID'), ('priority', 'Priority'), ('status', 'Status')):
        if sample[key] is None:
            err(f'design.md §7 inventory has no "{col}" column — add Req ID | Priority | Status after Mockup (see CHANGELOG migration note)')
    for sid, row in sorted(inv.items()):
        req = row['req']
        if req is not None:
            if not req:
                err(f'inventory "{sid}": Req ID is empty — list requirement IDs or write —')
            elif req in NONE:
                if row['module'].lower() != 'system':
                    warn(f'inventory "{sid}": Req ID is — but Module is "{row["module"]}" — only System screens may skip traceability')
            else:
                for r in multi(req):
                    if not REQ_ID.fullmatch(r):
                        err(f'inventory "{sid}": Req ID "{r}" is not a requirement ID like R3 or FR-01')
        if row['priority'] is not None and row['priority'] not in PRIORITIES:
            err(f'inventory "{sid}": Priority "{row["priority"]}" not in {" / ".join(PRIORITIES)}')
        if row['status'] is not None and row['status'] not in STATUSES:
            err(f'inventory "{sid}": Status "{row["status"]}" not in {" / ".join(STATUSES)}')


def need_columns(name, header, cols):
    missing = [c for c in cols if c not in header]
    if missing:
        err(f'spec "{name}" table lacks column(s) {", ".join(missing)}')
    return not missing


def roles_checks(spec, ids_inv):
    """R1: ## Roles & permissions → ### Roles + ### Permission matrix."""
    sec = section(spec, '## Roles & permissions')
    if sec is None:
        err('spec has no "## Roles & permissions" section — add ### Roles and ### Permission matrix (role × screen × action)')
        return
    roles_t = tables(section(sec, '### Roles', '### ') or '')
    matrix_t = tables(section(sec, '### Permission matrix', '### ') or '')
    roles = []
    if not roles_t or not roles_t[0][1]:
        err('spec "Roles & permissions": "### Roles" table is missing or empty')
    elif need_columns('Roles', roles_t[0][0], ('role',)):
        for r in roles_t[0][1]:
            role = r['role']
            if not re.fullmatch(ID, role):
                err(f'spec Roles: role "{role}" must be kebab-case (e.g. buyer, approver)')
            elif role in roles:
                err(f'spec Roles: role "{role}" is declared twice')
            else:
                roles.append(role)
    if not matrix_t or not matrix_t[0][1]:
        err('spec "Roles & permissions": "### Permission matrix" table is missing or empty')
        return
    header, rows = matrix_t[0]
    if not need_columns('Permission matrix', header, ('role', 'screen') + ACTIONS):
        return
    used_roles, used_screens, pairs = set(), set(), set()
    for r in rows:
        rs = multi(r['role'])
        ss = multi(r['screen'])
        for role in rs:
            if role != '*' and role not in roles:
                err(f'spec Permission matrix: role "{role}" is not declared in ### Roles')
        for s in ss:
            if s != '*' and s not in ids_inv:
                err(f'spec Permission matrix: screen "{s}" is not in the design.md inventory')
        if not rs:
            err(f'spec Permission matrix: row for screen "{r["screen"]}" has no Role — use a declared role or *')
        if not ss:
            err(f'spec Permission matrix: row for role "{r["role"]}" has no Screen')
        for a in ACTIONS:
            if not PERM.fullmatch(r[a]):
                err(f'spec Permission matrix [{r["role"]} / {r["screen"]}] {a.title()}: "{r[a]}" — use ✅, ✅ (condition) or —')
        exp_r = set(roles) if '*' in rs else set(rs)
        exp_s = set(ids_inv) if '*' in ss else set(ss)
        used_roles |= exp_r
        used_screens |= exp_s
        if '*' not in rs and '*' not in ss:  # wildcard rows are defaults; explicit rows may refine them
            for p in {(x, y) for x in exp_r for y in exp_s}:
                if p in pairs:
                    warn(f'spec Permission matrix: role "{p[0]}" × screen "{p[1]}" has more than one row — the last one wins')
                pairs.add(p)
    for role in roles:
        if role not in used_roles:
            warn(f'spec Roles: role "{role}" has no row in the Permission matrix')
    for s in sorted(ids_inv - used_screens):
        warn(f'spec Permission matrix: screen "{s}" is not covered by any role')


def ac_checks(spec, inv):
    """R2: ## Acceptance criteria table, every inventory screen covered."""
    sec = section(spec, '## Acceptance criteria')
    if sec is None:
        err('spec has no "## Acceptance criteria" section — add a Given/When/Then table covering every screen')
        return
    t = tables(sec)
    if not t or not t[0][1]:
        err('spec "Acceptance criteria" table has no rows')
        return
    header, rows = t[0]
    if not need_columns('Acceptance criteria', header, ('id', 'screen', 'req id', 'given', 'when', 'then')):
        return
    seen, covered = set(), set()
    for r in rows:
        aid = r['id']
        if not re.fullmatch(r'AC-\d{2,}', aid):
            err(f'spec AC "{aid}": ID must look like AC-01')
        elif aid in seen:
            err(f'spec AC "{aid}" is used twice')
        seen.add(aid)
        screens = multi(r['screen'])
        if not screens:
            err(f'spec AC "{aid}" has no Screen')
        for s in screens:
            if s not in inv:
                err(f'spec AC "{aid}": screen "{s}" is not in the design.md inventory')
            covered.add(s)
        for k in ('given', 'when', 'then'):
            if not r[k]:
                err(f'spec AC "{aid}": {k.title()} is empty')
        req = r['req id']
        if not req:
            err(f'spec AC "{aid}": Req ID is empty — list requirement IDs or write —')
        elif req not in NONE:
            allowed = set()
            known = bool(screens)
            for s in screens:
                inv_req = (inv.get(s) or {}).get('req')
                if inv_req is None:
                    known = False
                elif inv_req not in NONE:
                    allowed.update(multi(inv_req))
            for q in multi(req):
                if not REQ_ID.fullmatch(q):
                    err(f'spec AC "{aid}": Req ID "{q}" is not a requirement ID like R3 or FR-01')
                elif known and q not in allowed:
                    warn(f'spec AC "{aid}": Req ID "{q}" is not listed for {", ".join(screens)} in the inventory')
    for s in sorted(set(inv) - covered):
        err(f'spec has no acceptance criterion for screen "{s}" — add at least one Given/When/Then row')


def a11y_checks(spec, ids_inv):
    """R6: ## Accessibility table, one non-empty row per inventory screen."""
    sec = section(spec, '## Accessibility')
    if sec is None:
        if section(spec, '## Accessibility notes') is not None:
            err('spec still uses "## Accessibility notes" — rename it to "## Accessibility" and add the per-screen table')
        else:
            err('spec has no "## Accessibility" section — add announce / focus / tab order per screen')
        return
    t = tables(sec.split('\n### ', 1)[0])
    if not t or not t[0][1]:
        err('spec "Accessibility" table has no rows')
        return
    header, rows = t[0]
    cols = ('screen', 'announce (aria-live)', 'focus on open', 'focus return', 'tab order')
    if not need_columns('Accessibility', header, cols):
        return
    covered = set()
    for r in rows:
        s = r['screen']
        if s not in ids_inv:
            err(f'spec Accessibility: screen "{s}" is not in the design.md inventory (one screen ID per row)')
        if s in covered:
            warn(f'spec Accessibility: screen "{s}" has more than one row — keep one row per screen')
        covered.add(s)
        for c in cols[1:]:
            if not r[c]:
                err(f'spec Accessibility "{s}": "{c}" is empty — write n/a if it does not apply')
        ann = r[cols[1]]
        if ann and ann != 'n/a':
            for part in ann.split(' · '):
                if not re.match(r'(polite|assertive):', part.strip()):
                    warn(f'spec Accessibility "{s}": announce "{part.strip()[:30]}" should start with polite: or assertive:')
    for s in sorted(ids_inv - covered):
        err(f'spec Accessibility has no row for screen "{s}"')


def p1_checks(inv, spec):
    inventory_checks(inv)
    roles_checks(spec, set(inv))
    ac_checks(spec, inv)
    a11y_checks(spec, set(inv))


# --- Phase 2 checks (docs/p2-schema.md): R8 users & jobs, R9 design-qa.md, R10 notifications, R11 assets,
# R12 analytics events, R13 charts. Every section is optional — absent = not checked (no new breaking change);
# once a section is present its tables are checked and wrong values / unknown screen IDs are ERRORs.
SNAKE = re.compile(r'[a-z][a-z0-9_]*')
EVENT = re.compile(r'[a-z][a-z0-9]*(?:_[a-z0-9]+)+')
VAR = re.compile(r'\{\{\s*([a-z][a-z0-9_]*)\s*\}\}')
CHANNELS = ('email', 'push', 'in-app', 'sms')
NOTIF_TYPES = ('string', 'number', 'money', 'date', 'datetime', 'url')
EVENT_TYPES = ('string', 'integer', 'number', 'boolean', 'datetime', 'string[]')
ENUM = re.compile(r'enum\((.*)\)')
# assumed length of a {{variable}} when checking channel limits (url: the backend adds the link outside the text)
VAR_LEN = {'string': 12, 'number': 6, 'money': 12, 'date': 11, 'datetime': 17, 'url': 0}


def declared_roles(spec):
    sec = section(spec, '## Roles & permissions')
    t = tables(section(sec, '### Roles', '### ') or '') if sec is not None else []
    return {r.get('role', '') for r in t[0][1]} if t else set()


def p2_table(where, block, sub, cols, allow_empty=False):
    """Rows of the first table under `### sub` (or in `block` itself) — None after reporting an ERROR."""
    name = f'{where} {sub[4:]}' if sub else where
    body = block if sub is None else section(block, sub, '### ')
    if body is None:
        err(f'{where}: missing "{sub}" table')
        return None
    t = tables(body)
    if not t:
        err(f'{name}: no table')
        return None
    header, rows = t[0]
    missing = [c for c in cols if c not in header]
    if missing:
        err(f'{name} table lacks column(s) {", ".join(missing)}')
        return None
    if not rows and not allow_empty:
        err(f'{name} table has no rows')
        return None
    return rows


def required(where, row, cols):
    for c in cols:
        if not row.get(c):
            err(f'{where}: "{c}" is empty')


def one_of(where, col, value, allowed):
    if value not in allowed:
        err(f'{where}: {col} "{value}" not in {" / ".join(allowed)}')


def unique_id(where, value, pattern, seen, example):
    if not re.fullmatch(pattern, value):
        err(f'{where}: ID "{value}" must look like {example}')
    elif value in seen:
        err(f'{where}: ID "{value}" is used twice')
    seen.add(value)


def screens_in(where, value, ids, star=True, none=True, single=False):
    """Screen cell → screen IDs; ERROR for unknown IDs and for `*` / `—` where the table forbids them."""
    v = value.strip()
    if not v:
        err(f'{where}: Screen is empty')
        return []
    if v in NONE:
        if not none:
            err(f'{where}: Screen cannot be {v} — name the screen ID')
        return []
    if v == '*':
        if not star:
            err(f'{where}: Screen cannot be * — name the screen ID(s)')
        return sorted(ids)
    out = multi(v)
    if single and len(out) > 1:
        err(f'{where}: one screen ID per row, got "{v}"')
    for s in out:
        if s not in ids:
            err(f'{where}: screen "{s}" is not in the design.md inventory')
    return out


def type_ok(where, typ, types, enums):
    m = ENUM.fullmatch(typ) if enums else None
    if m:
        vals = m.group(1).split('/')
        if not m.group(1) or not all(re.fullmatch(r'[a-z0-9_]+', v) for v in vals):
            err(f'{where}: {typ} — enum values are [a-z0-9_]+ joined by /, none empty')
        elif len(set(vals)) != len(vals):
            err(f'{where}: {typ} repeats a value')
    elif typ not in types:
        err(f'{where}: type "{typ}" — use {" / ".join(types)}' + (' / enum(a/b)' if enums else ''))


def parse_props(where, value, types, optional=False, enums=False):
    """`name: type, name2?: type` → {name: type}; `—` = none."""
    if value in NONE:
        return {}
    if not value:
        err(f'{where}: properties/variables cell is empty — write —')
        return {}
    out = {}
    for item in multi(value):
        m = re.fullmatch(r'([a-z][a-z0-9_]*)(\?)?\s*:\s*(\S.*)', item)
        if not m or (m.group(2) and not optional):
            err(f'{where}: "{item}" must be name: type' + (' (name? for optional)' if optional else ''))
            continue
        name, typ = m.group(1), m.group(3).strip()
        if name in out:
            err(f'{where}: "{name}" is listed twice')
        type_ok(f'{where}: "{name}"', typ, types, enums)
        out[name] = typ
    return out


def users_checks(spec, ids, roles):
    """R8: ## Users & jobs → Personas, Jobs to be done, Journey."""
    sec = section(spec, '## Users & jobs')
    if sec is None:
        return
    w = 'spec Users & jobs'
    personas = set()
    for r in p2_table(w, sec, '### Personas', ('persona', 'role', 'context', 'goals', 'pain points')) or []:
        p = r['persona']
        where = f'{w} persona "{p}"'
        if not re.fullmatch(ID, p):
            err(f'{where}: persona key must be kebab-case (e.g. busy-approver)')
        elif p in personas:
            err(f'{where}: declared twice')
        personas.add(p)
        required(where, r, ('role', 'context', 'goals', 'pain points'))
        for role in multi(r['role']):
            if role not in roles:
                err(f'{where}: role "{role}" is not declared in ### Roles')

    def persona_ref(where, p):
        if not p:
            err(f'{where}: Persona is empty')
        elif p not in personas:
            err(f'{where}: persona "{p}" is not in ### Personas')

    seen = set()
    for r in p2_table(w, sec, '### Jobs to be done', ('id', 'persona', 'when', 'i want to', 'so i can', 'screen')) or []:
        where = f'{w} {r["id"] or "(no ID)"}'
        unique_id(where, r['id'], r'JTBD-\d{2,}', seen, 'JTBD-01')
        persona_ref(where, r['persona'])
        required(where, r, ('when', 'i want to', 'so i can'))
        screens_in(where, r['screen'], ids, none=False)
    for i, r in enumerate(p2_table(w, sec, '### Journey', ('stage', 'persona', 'action', 'screen', 'pain point', 'opportunity')) or [], 1):
        where = f'{w} Journey row {i}'
        required(where, r, ('stage', 'action'))
        persona_ref(where, r['persona'])
        screens_in(where, r['screen'], ids)


def design_qa_checks(folder, design, ids):
    """R9: design-qa.md (optional file) → Pre-handoff checklist + Build review; Tolerances are free text."""
    f = folder / 'design-qa.md'
    if not f.exists():
        return
    text = f.read_text(encoding='utf-8')
    dv, qv = re.search(r'Version:\s*([\d.]+)', design), re.search(r'Version\s*([\d.]+)', text)
    if dv and qv and dv.group(1) != qv.group(1):
        warn(f'version mismatch: design.md {dv.group(1)} vs design-qa.md {qv.group(1)}')
    sec = section(text, '## Pre-handoff checklist')
    if sec is not None:
        seen, open_items = set(), []
        for r in p2_table('design-qa.md Pre-handoff checklist', sec, None, ('id', 'check', 'heuristic', 'result')) or []:
            where = f'design-qa.md {r["id"] or "(no ID)"}'
            unique_id(where, r['id'], r'HC-\d{2,}', seen, 'HC-01')
            required(where, r, ('check', 'heuristic'))
            one_of(where, 'Result', r['result'], ('pass', 'fail', 'n/a', 'todo'))
            if r['result'] in ('fail', 'todo'):
                open_items.append(r['id'])
        if open_items:
            warn(f'design-qa.md checklist: {", ".join(open_items)} still fail/todo — not ready for hand-off')
    sec = section(text, '## Build review')
    if sec is not None:
        cols = ('id', 'screen', 'device', 'theme', 'state', 'property', 'expected', 'actual', 'severity', 'status')
        themes = set(design_theme_names(design)) | {'Default', 'all'}
        seen, unresolved = set(), []
        for r in p2_table('design-qa.md Build review', sec, None, cols, allow_empty=True) or []:
            where = f'design-qa.md {r["id"] or "(no ID)"}'
            unique_id(where, r['id'], r'DQ-\d{2,}', seen, 'DQ-01')
            screens_in(where, r['screen'], ids, star=False, none=False, single=True)
            one_of(where, 'Device', r['device'], ('desktop', 'tablet', 'mobile'))
            one_of(where, 'State', r['state'], ('default', 'empty', 'loading', 'error', 'success', 'permission'))
            one_of(where, 'Property', r['property'], ('layout', 'spacing', 'color', 'typography', 'icon', 'copy',
                                                      'state', 'interaction', 'a11y', 'motion'))
            one_of(where, 'Severity', r['severity'], ('blocker', 'major', 'minor', 'cosmetic'))
            one_of(where, 'Status', r['status'], ('open', 'fixed', 'verified', 'wontfix'))
            required(where, r, ('theme', 'expected', 'actual'))
            if r['theme'] and r['theme'] not in themes:
                warn(f'{where}: theme "{r["theme"]}" is not in design.md §2.9 (or Default / all)')
            if r['severity'] in ('blocker', 'major') and r['status'] in ('open', 'fixed'):
                unresolved.append(r['id'])
        if unresolved:
            warn(f'design-qa.md Build review: {", ".join(unresolved)} blocker/major not verified yet — the round does not pass')


def msg_len(text, variables):
    """Characters a user sees: {{var}} replaced by an assumed length; non-spacing marks (category Mn — Thai
    upper/lower vowels and tone marks) not counted. combining() is wrong here: Thai upper vowels have class 0."""
    import unicodedata
    body = VAR.sub(lambda m: 'x' * VAR_LEN.get(variables.get(m.group(1), 'string'), 12), text)
    return sum(1 for c in body if unicodedata.category(c) != 'Mn')


def notifications_checks(spec, ids, roles, events):
    """R10: ## Notifications → Locales line, triggers, copy per channel × locale, channel limits."""
    sec = section(spec, '## Notifications')
    if sec is None:
        return
    w = 'spec Notifications'
    first = next((l.strip() for l in sec.split('\n### ', 1)[0].splitlines() if l.strip()), '')
    m = re.fullmatch(r'Locales:\s*(.*)', first)
    locales = multi(m.group(1)) if m else []
    if not locales:
        err(f'{w}: no "Locales: th, en" line under the heading')
    triggers, seen = {}, set()
    cols = ('id', 'trigger', 'recipient', 'channels', 'category', 'screen', 'variables')
    for r in p2_table(w, sec, '### Notification triggers', cols) or []:
        nid = r['id']
        where = f'{w} {nid or "(no ID)"}'
        unique_id(where, nid, r'NT-\d{2,}', seen, 'NT-01')
        t = r['trigger']
        if not t:
            err(f'{where}: Trigger is empty')
        elif not EVENT.fullmatch(t):
            warn(f'{where}: trigger "{t}" should be an event name like po_submitted (R12 naming)')
        elif events is not None and t not in events:
            warn(f'{where}: trigger "{t}" is not an event in ## Analytics events')
        if not r['recipient']:
            err(f'{where}: Recipient is empty')
        for who in multi(r['recipient']):
            if who != 'actor' and who not in roles:
                err(f'{where}: recipient "{who}" is not a declared role (or actor)')
        chans = multi(r['channels'])
        if not chans:
            err(f'{where}: Channels is empty')
        for c in chans:
            one_of(where, 'channel', c, CHANNELS)
        one_of(where, 'Category', r['category'], ('transactional', 'marketing'))
        screens_in(where, r['screen'], ids, star=False, single=True)
        triggers[nid] = (set(chans), parse_props(where, r['variables'], NOTIF_TYPES))
    limits = {}
    for r in p2_table(w, sec, '### Channel limits', ('channel', 'field', 'locale', 'max chars')) or []:
        where = f'{w} limit {r["channel"]}/{r["field"]}/{r["locale"]}'
        one_of(where, 'Channel', r['channel'], CHANNELS)
        one_of(where, 'Field', r['field'], ('Subject / Title', 'Body'))
        if r['locale'] != 'all' and r['locale'] not in locales:
            err(f'{where}: locale "{r["locale"]}" is not in Locales (or all)')
        key = (r['channel'], r['field'].lower(), r['locale'])
        if key in limits:
            err(f'{where}: more than one row for this channel × field × locale')
        if not re.fullmatch(r'[1-9]\d*', r['max chars']):
            err(f'{where}: Max chars "{r["max chars"]}" must be a whole number > 0')
            limits.setdefault(key, None)
        else:
            limits[key] = int(r['max chars'])
    have, used, seen = {}, {}, set()
    for r in p2_table(w, sec, '### Notification copy', ('id', 'channel', 'locale', 'subject / title', 'body')) or []:
        nid, ch, loc = r['id'], r['channel'], r['locale']
        where = f'{w} copy {nid}/{ch}/{loc}'
        if nid not in triggers:
            err(f'{where}: ID "{nid}" is not in ### Notification triggers')
            continue
        chans, variables = triggers[nid]
        if ch not in chans:
            err(f'{where}: channel "{ch}" is not in the Channels of {nid}')
        if loc not in locales:
            err(f'{where}: locale "{loc}" is not in Locales')
        if (nid, ch, loc) in seen:
            err(f'{where}: more than one row for this ID × channel × locale')
        seen.add((nid, ch, loc))
        have.setdefault((nid, ch), set()).add(loc)
        subj, body = r['subject / title'], r['body']
        if ch != 'sms' and (not subj or subj in NONE):
            err(f'{where}: Subject / Title is empty')
        if not body or body in NONE:
            err(f'{where}: Body is empty')
        for field, text in (('subject / title', subj), ('body', body)):
            if text in NONE:
                continue
            rest = VAR.sub('', text)
            if '{{' in rest or '{%' in rest:
                err(f'{where}: logic in template — {field} may only use plain {{{{snake_case}}}} variables')
            for v in VAR.findall(text):
                if v not in variables:
                    err(f'{where}: variable "{v}" is not declared in the Variables of {nid}')
                else:
                    used.setdefault((nid, loc), set()).add(v)
            limit = limits.get((ch, field, loc)) or limits.get((ch, field, 'all'))
            if limit and msg_len(text, variables) > limit:
                warn(f'{where}: {field} is about {msg_len(text, variables)} characters — {ch} limit is {limit}')
    for nid, (chans, variables) in sorted(triggers.items()):
        for ch in sorted(chans & set(CHANNELS)):
            missing = [l for l in locales if l not in have.get((nid, ch), set())]
            if missing:
                err(f'{w}: {nid} {ch} has no copy for locale(s) {", ".join(missing)}')
        for loc in locales:
            if any((nid, c) in have and loc in have[(nid, c)] for c in chans):
                unused = sorted(v for v, t in variables.items() if t != 'url' and v not in used.get((nid, loc), set()))
                if unused:
                    warn(f'{w}: {nid} declares {", ".join(unused)} but the {loc} copy never uses it')


def assets_checks(design, ids):
    """R11: design.md ## 9. Assets."""
    sec = section(design, '## 9. Assets')
    if sec is None:
        return
    w = 'design.md §9 Assets'
    seen = set()
    cols = ('asset', 'platform', 'size', 'format', 'screen', 'source', 'status')
    for r in p2_table(w, sec, None, cols) or []:
        a, plat = r['asset'], r['platform']
        where = f'{w} "{a}" ({plat})'
        if not re.fullmatch(ID, a):
            err(f'{where}: asset name must be kebab-case')
        elif (a, plat, r['format']) in seen:
            err(f'{where}: listed twice for the same platform and format')
        seen.add((a, plat, r['format']))
        one_of(where, 'Platform', plat, ('web', 'ios', 'android', 'email', 'all'))
        size_ok = r['size'] == 'vector' or (r['size'] in NONE and r['format'] == 'webmanifest') \
            or all(re.fullmatch(r'\d+x\d+', s) for s in multi(r['size']) or [''])
        if not size_ok:
            err(f'{where}: Size "{r["size"]}" must be vector or WxH in px (e.g. 512x512, comma-separated; — only for webmanifest)')
        one_of(where, 'Format', r['format'], ('svg', 'png', 'ico', 'webp', 'jpg', 'pdf', 'webmanifest', 'xml'))
        if plat == 'email' and r['format'] == 'svg':
            warn(f'{where}: Gmail and Outlook do not show SVG — use png for email')
        screens_in(where, r['screen'], ids, star=False)
        required(where, r, ('source',))
        one_of(where, 'Status', r['status'], ('needed', 'draft', 'review', 'approved'))


def analytics_checks(spec, inv):
    """R12: ## Analytics events → Common properties + Events. Returns the event names (None when absent)."""
    sec = section(spec, '## Analytics events')
    if sec is None:
        return None
    w, ids = 'spec Analytics events', set(inv)
    common = set()
    for r in p2_table(w, sec, '### Common properties', ('property', 'type')) or []:
        p = r['property']
        where = f'{w} common "{p}"'
        if not SNAKE.fullmatch(p) or len(p) > 40:
            err(f'{where}: property must be snake_case, ≤ 40 characters')
        elif p in common:
            err(f'{where}: listed twice')
        common.add(p)
        type_ok(where, r['type'], EVENT_TYPES, True)
    names = set()
    for r in p2_table(w, sec, '### Events', ('event', 'trigger', 'screen', 'source', 'properties', 'req id')) or []:
        e = r['event']
        where = f'{w} "{e}"'
        if not EVENT.fullmatch(e) or len(e) > 40:
            err(f'{where}: event name must be object_action snake_case (e.g. po_submitted), ≤ 40 characters')
        elif e.startswith(('ga_', 'firebase_', 'google_')):
            err(f'{where}: prefixes ga_ / firebase_ / google_ are reserved by analytics tools')
        elif e in names:
            err(f'{where}: listed twice')
        names.add(e)
        required(where, r, ('trigger',))
        star = r['screen'].strip() == '*'
        screens = screens_in(where, r['screen'], ids, none=False)
        one_of(where, 'Source', r['source'], ('client', 'server'))
        props = parse_props(where, r['properties'], EVENT_TYPES, optional=True, enums=True)
        for p in props:
            if len(p) > 40:
                err(f'{where}: property "{p}" is longer than 40 characters')
            if p in common:
                err(f'{where}: property "{p}" repeats a common property')
        if len(set(props) | common) > 25:
            err(f'{where}: {len(set(props) | common)} properties with the common ones — the limit is 25')
        req = r['req id']
        if not req:
            err(f'{where}: Req ID is empty — list requirement IDs or write —')
        elif req not in NONE:
            allowed, known = set(), bool(screens) and not star
            for s in screens:
                inv_req = (inv.get(s) or {}).get('req')
                if inv_req is None:
                    known = False
                elif inv_req not in NONE:
                    allowed.update(multi(inv_req))
            for q in multi(req):
                if not REQ_ID.fullmatch(q):
                    err(f'{where}: Req ID "{q}" is not a requirement ID like R3 or FR-01')
                elif known and q not in allowed:
                    warn(f'{where}: Req ID "{q}" is not listed for {", ".join(screens)} in the inventory')
    return names


def charts_checks(spec, design, ids):
    """R13: ## Charts (optional — apps with charts)."""
    sec = section(spec, '## Charts')
    if sec is None:
        return
    w = 'spec Charts'
    palette = {k for k in design_tokens(design) if k.startswith('chart-')}
    seen = set()
    cols = ('chart', 'screen', 'question', 'type', 'data', 'palette', 'table fallback')
    for r in p2_table(w, sec, None, cols) or []:
        c = r['chart']
        where = f'{w} "{c}"'
        if not re.fullmatch(ID, c):
            err(f'{where}: chart name must be kebab-case')
        elif c in seen:
            err(f'{where}: listed twice')
        seen.add(c)
        screens_in(where, r['screen'], ids, star=False, none=False)
        required(where, r, ('question', 'data', 'palette'))
        one_of(where, 'Type', r['type'], ('bar', 'grouped-bar', 'stacked-bar', 'line', 'area', 'combo', 'donut', 'kpi',
                                               'progress', 'sparkline', 'scatter', 'table'))
        if r['palette'] and r['palette'] not in NONE:
            for t in multi(r['palette']):
                if t not in palette:
                    warn(f'{where}: palette "{t}" is not a chart-* token in design.md §2.6')
        one_of(where, 'Table fallback', r['table fallback'], ('yes', 'no'))
        if r['table fallback'] == 'no':
            warn(f'{where}: no table fallback — screen-reader and colour-blind users cannot read the chart')


# exact Phase 2 headings, keyed by the word a near-miss heading starts with (QA Q-P2-01)
P2_HEADINGS = {
    'spec': {'users': '## Users & jobs', 'notification': '## Notifications', 'analytics': '## Analytics events',
             'chart': '## Charts'},
    'design.md': {'voice': '## 8. Voice & tone', 'asset': '## 9. Assets'},
}


def near_miss_headings(name, text):
    """WARN for a `## ` heading that looks like an optional Phase 2 section but is not spelt exactly — it would not be checked."""
    for line in re.findall(r'^## .*$', text, re.M):
        line = line.rstrip()
        words = re.sub(r'^##\s*[\d.]*\s*', '', line).lower()
        for prefix, exact in P2_HEADINGS[name].items():
            if words.startswith(prefix) and line != exact:
                warn(f'{name}: heading "{line}" is not checked — write it exactly as "{exact}"')


def p2_checks(folder, inv, design, spec):
    near_miss_headings('spec', spec)
    near_miss_headings('design.md', design)
    ids, roles = set(inv), declared_roles(spec)
    users_checks(spec, ids, roles)
    design_qa_checks(folder, design, ids)
    events = analytics_checks(spec, inv)
    notifications_checks(spec, ids, roles, events)
    assets_checks(design, ids)
    charts_checks(spec, design, ids)


def design_tokens(design):
    # §2.9 theme variants repeat token names with different hexes — parse scales only up to that section
    design = design.split('Theme variants', 1)[0]
    t = {k: v.lower() for k, v in re.findall(r'^\|\s*([a-z]+-\d+)\s*\|\s*(#[0-9a-fA-F]{6})\b', design, re.M)}
    for name, a, b, c in re.findall(r'^\|\s*([a-z]+)\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})\s*\|\s*(#[0-9a-fA-F]{6})', design, re.M):
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
    engine_version_check(folder)
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

    # --- component kits: only classes the engine defines (wf-* wireframes, mk-* mock)
    for name, html, css, prefix in (('wireframes', wf, 'wireframe.css', 'wf'), ('mock', mk, 'mockup.css', 'mk')):
        css_path = folder / '_engine' / css
        if not css_path.exists():
            continue
        defined = set(re.findall(r'\.(' + prefix + r'-[a-z0-9-]+)', css_path.read_text(encoding='utf-8')))
        used = set()
        for cls in re.findall(r'class="([^"]*)"', html):
            used.update(c for c in cls.split() if c.startswith(prefix + '-'))
        for c in sorted(used - defined):
            warn(f'{name}: class "{c}" is not part of the {prefix}-* component kit (_engine/{css}) — use a kit component or Tailwind utilities')

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
    if not re.search(r':root\s*\{[^}]*--c-', mk, re.S):
        warn('mock has no static :root --c-* defaults — realtime theming and live design-tool edits need them')

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

    usability_checks(folder, ids_inv)
    p1_checks(inv, spec)
    p2_checks(folder, inv, design, spec)

    # --- version
    dv = re.search(r'Version:\s*([\d.]+)', design)
    sv = re.search(r'Version\s*([\d.]+)', spec)
    if dv and sv and dv.group(1) != sv.group(1):
        warn(f'version mismatch: design.md {dv.group(1)} vs spec {sv.group(1)}')

    browser_checks(files, mk_sections, all_icons)
    return report(len(ids_inv))


# Text contrast of every visible element against the first opaque background behind it.
# Skips disabled controls, annotation markers, inactive states, code blocks and the color swatches
# (they show each color with its own ratio). Shared with tests/test_browser.py.
CONTRAST_JS = """(sel) => {
  const ch = s => s.match(/[\\d.]+/g).map(Number);
  const lum = ([r, g, b]) => [r, g, b].map(c => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; })
                                      .reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const v = ch(getComputedStyle(e).backgroundColor);
                       if (v.length < 4 || v[3] > 0.5) return v; } return [255, 255, 255]; };
  const out = [];
  document.querySelectorAll(sel + ' *').forEach(el => {
    if (!el.offsetParent || el.closest('[disabled], .anno, [data-state]:not(.show), pre, #swatches')) return;
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
    const [a, b] = [lum(ch(getComputedStyle(el).color)), lum(bgOf(el))].sort((x, y) => y - x);
    const r = (a + 0.05) / (b + 0.05);
    if (r < 4.5) out.push(`${el.tagName.toLowerCase()}.${(el.className || '').toString().split(' ').slice(0, 3).join('.')} "${el.textContent.trim().slice(0, 24)}" ${r.toFixed(2)}:1`);
  });
  return [...new Set(out)];
}"""


def usability_checks(folder, ids_inv):
    """usability-test.md: at least 5 tasks, each with screens + a success criterion, screens from the inventory."""
    f = folder / 'usability-test.md'
    if not f.exists():
        warn('no usability-test.md — add the test plan (5 tasks with success criteria) before handing over')
        return
    text = f.read_text(encoding='utf-8')
    tasks = re.split(r'^### ', text.split('## Tasks', 1)[-1].split('\n## ', 1)[0], flags=re.M)[1:]
    if len(tasks) < 5:
        err(f'usability-test.md has {len(tasks)} task(s) — plan at least 5')
    for t in tasks:
        name = t.splitlines()[0].strip()
        if '[' in name and ']' in name and name.startswith('T') and '…' in t:
            warn(f'usability-test.md task "{name}" is still the template placeholder')
            continue
        if not re.search(r'\*\*Success:\*\*\s*\S', t):
            err(f'usability-test.md task "{name}" has no **Success:** criterion')
        screens = re.search(r'\*\*Screens:\*\*(.*)', t)
        ids = re.findall(r'\[(' + ID + r')\]', screens.group(1)) if screens else []
        if not ids:
            err(f'usability-test.md task "{name}" lists no **Screens:** [screen-id]')
        for i in ids:
            if i not in ids_inv:
                err(f'usability-test.md task "{name}" uses screen "{i}" which is not in the design.md inventory')


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
                    .filter(a => !a.dataset.device || a.dataset.device === '{label}')
                    .map(a => [a.textContent.trim(), a.getBoundingClientRect().width > 0 && getComputedStyle(a).visibility !== 'hidden'])
                    .filter(x => !x[1]).map(x => x[0])""")
                if hidden:
                    level(f'mockup "{sid}" ({label}): annotation marker(s) {hidden} not visible')
            pg.close()

        # Text contrast >= 4.5:1 on every mock screen in every theme (desktop width)
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        pg.goto(uri)
        pg.wait_for_timeout(1500)
        themes = pg.evaluate("typeof themes === 'object' ? Object.keys(themes) : ['Default']")
        pg.close()
        for theme in themes:
            pg = b.new_page(viewport={'width': 1440, 'height': 900})
            pg.add_init_script(f"localStorage.setItem('mk-theme', {theme!r})")
            pg.goto(uri)
            pg.wait_for_timeout(1500)
            for sid in mk_sections:
                pg.evaluate(f"showScreen('{sid}')")
                pg.wait_for_timeout(100)
                low = pg.evaluate(CONTRAST_JS, f'[id="{sid}"]')
                if low:
                    more = f' (+{len(low) - 3} more)' if len(low) > 3 else ''
                    err(f'mockup "{sid}" [{theme} theme]: text below 4.5:1 — {"; ".join(low[:3])}{more}')
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
