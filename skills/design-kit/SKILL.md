---
name: design-kit
description: Design UX/UI for a whole app or feature and deliver an AI-readable design project folder — design.md (colors, typography, icons, components), wireframes of every screen with zoom, pinned review comments and a Diagrams page, dev diagrams (user flow, ER, state, sequence, API contract), a clickable HTML + Tailwind mockup with device preview, a UX spec, design tokens, and an AGENTS.md guide — kept in sync when the design changes. Use whenever the user asks to design, mock up, wireframe, plan screens, choose colors, icons or a theme, write design.md, lay out a page, form, report, dashboard, or mobile app — ERP/back-office, web, or mobile — even if they only say "ออกแบบหน้าจอ", "ทำ wireframe", "ทำ mockup", "เลือกสี", "ทำ design.md", "วาง layout", "UX/UI", ask to change an existing design ("แก้หน้า...", "เปลี่ยนสี...", "เพิ่มหน้า..."), or paste wireframe feedback ("Wireframe feedback — ...").
---

# Design Kit

Turn an app or feature idea into a complete, consistent design project a developer (or another AI) can pick up — and keep it consistent as it changes.

## Environment

This skill runs in claude.ai and in Claude Code. Resolve these once at the start:

| | claude.ai | Claude Code |
|---|---|---|
| `<skill>` (this skill's folder) | the path this SKILL.md was read from | the path this SKILL.md was read from |
| `<out>` (where projects go) | `/mnt/user-data/outputs` | the current working directory, or the path the user names |
| User uploads | `/mnt/user-data/uploads` (read-only — copy before editing) | files in the working directory |
| Deliver | zip the folder and present the zip + design.md with `present_files` | leave the folder in place; tell the user the path and to open `wireframes.html` |

Requirements for the scripts: Python 3.9+. Browser checks in `verify.py` (JS errors, icon names, Mermaid syntax, annotation visibility) need `playwright` with Chromium; without it they're skipped with a warning — in Claude Code, suggest `pip install playwright && playwright install chromium` once.

## The project folder

Every design is delivered as one folder, built from `assets/project/`:

```
<app>-design/
├── AGENTS.md          AI entry point: file roles, what may be edited, commands   (CLAUDE.md imports it)
├── design.md          source of truth: colors, typography, icons (§6), components, screen inventory (§7), changelog
├── ux-spec.md         behavior, validation + exact error text, ALL diagrams (Mermaid), API contract, risks
├── wireframes.html    content only: WF config + diagrams (generated) + one <template> per screen
├── mockup.html        content only: tokens + icons config + one <section> per screen
├── _engine/           shared review UI (toolbar, zoom, comments, device frames) — never edited per project
├── _tools/            verify.py · sync_diagrams.py · export_tokens.py (copied from this skill's scripts/)
├── tokens/            tokens.css · tailwind.config.js · tokens.json (generated)
└── feedback/          exported review comments
```

Why this shape: content files hold only what changes per project, so an AI editing a screen reads a few hundred lines instead of thousands of lines of engine code; every screen sits between `<!-- ════════ SCREEN: id ════════ -->` / `<!-- ════════ /SCREEN: id ════════ -->` markers and is listed in a `SCREENS (in order): …` header line, so one screen can be found and replaced in isolation; AGENTS.md tells any future AI session (including Claude Code opened on this folder) the rules without re-reading this skill.

The **screen ID** (kebab-case, e.g. `po-list`) is the shared key: design.md §7 row → `<template id>` → `<section id>` → spec heading `### [po-list]`. None of this is production code.

## First: is there existing work?

Check the conversation, the uploads / working directory for an existing design.md, wireframes, mockup, spec, or a project zip.

- **Found** → **Updating an existing design**. Reuse tokens, icons, and IDs; never start over.
- **A "Wireframe feedback — …" export** → **Applying wireframe feedback**.
- **Old format** (single-file HTML with inline engine, `*-wireframes.html` names, no AGENTS.md) → offer to migrate as part of the change: create the folder from `assets/project/`, move each screen's markup into the new content files with markers, keep IDs and content unchanged, then verify.

## Workflow (new design)

### 1. Understand before drawing

Extract: **who** (role, frequency, device), **job to be done**, **data** (fields, volume), **context** (internal / public web / native mobile; existing system), **constraints** (permissions, approvals, language), **brand** (logo, colors, product name, or a mood).

Ask only what would change the design — at most 3 questions in one message. Otherwise record assumptions in design.md §0.

### 2. Read the references

| Need | Read |
|---|---|
| ERP, back-office, reports, admin, dashboards | `references/enterprise-patterns.md` |
| Customer-facing web app | `references/web-app-patterns.md` |
| Mobile app | `references/mobile-patterns.md` |
| **Always** — palette, contrast, status colors | `references/color-system.md` |
| **Always** — icon set, anti-"AI look" rules, icon map | `references/iconography.md` |
| **Always** — states, accessibility, Thai text | `references/states-and-accessibility.md` |
| **Always** — ER, state, sequence, API contract | `references/dev-diagrams.md` |

### 3. Decide the device model

- **Responsive web**: one ID per screen. Wireframe templates hold `.frame-desktop` (1280) and `.frame-mobile` (390), plus `.frame-tablet` (768) whenever the layout changes meaningfully at tablet width (sidebar collapses, table becomes cards, two columns become one) — skip it when tablet is just a wider mobile. The mockup builds one screen with Tailwind breakpoints, checked with the Tablet/Mobile toggles. **Never `m-*` copies** — two copies drift apart.
- **Native mobile app**: `data-device="mobile"`; `m-` prefix only if a separate web admin exists.
- **Desktop-only internal tool**: design for 1366px+, note it in design.md.

### 4. Screen inventory and flow

List **every** screen, grouped by module. Checklist so the boring ones aren't forgotten:

- Auth: login, forgot/reset password, first-time setup
- Each module: list/search, detail, create, edit, delete confirm, approval
- Shared: home/dashboard, notifications, profile, settings, users & roles
- System: empty first-use, 403, 404, error/maintenance, session expired
- Dialogs/bottom sheets with real content (own ID) · Mobile: onboarding, offline

Write the user flow as Mermaid `flowchart` with **screen IDs as node IDs**, including failure paths. It goes in ux-spec.md `## User flow`.

### 5. Checkpoint (apps with more than ~8 screens)

Before building screens, send: the inventory (grouped, with IDs), the flow, the device model, the palette (brand 600 hex + preset + why), the icon set (+ why), and any invented product name. Ask to confirm or correct, and end the turn. Redoing 15+ screens built on a wrong assumption costs far more than one message. Small, clear features (≤ 8 screens) skip this and list assumptions instead.

### 6. Create the folder and write design.md

```bash
cp -r <skill>/assets/project <out>/<app>-design
mkdir -p <out>/<app>-design/_tools && cp <skill>/scripts/*.py <out>/<app>-design/_tools/
```

Fill design.md: full color scales per `color-system.md` with **computed contrast ratios** (fix failing pairs before moving on); typography, spacing, components with states; **§6 icon set + icon map** per `iconography.md` (one set chosen for the users — e.g. Fluent for people who live in Office/Dynamics AX, Phosphor or Tabler elsewhere, not Lucide by default); §7 inventory; changelog 1.0. Fill AGENTS.md header (app, version, device model, icon set).

### 7. Wireframe every screen (`wireframes.html`)

- Replace the example screens with one marked `<template>` block per inventory screen — all of them — in inventory order; update the `SCREENS (in order)` line.
- Set `WF = { app, version }`. Grayscale `wf-*` classes only. Attributes: `data-title`, `data-module`, `data-device`, `data-notes` (one per `.anno`, `|`-separated). Frames get `data-label` ("Desktop 1280", "Mobile 390").
- Wire primary buttons with `showScreen('id')`. Don't touch the DIAGRAMS block — it's generated.
- The engine already provides: **device filter** (ทั้งหมด / Desktop / Tablet / Mobile, key `D`, remembered per browser; screens without that device show a notice), overview grid, **zoom** (−/+, พอดีจอ, 100%, Ctrl/⌘+scroll or pinch at the cursor, keys `+ - 0 1`), **Space+drag pan**, 💬 pinned comments, Diagrams page with zoom, feedback export.

### 8. Build the mockup (`mockup.html`)

- Paste design.md's scales into `const tokens` and the icon map into `const icons`.
- One marked `<section class="screen">` per screen on the primary flow plus one example of each pattern; keep `design-system` last; update the `SCREENS` line and the inventory Mockup column.
- Token classes only (`bg-brand-600`); icons only as `<iconify-icon icon="…">` from the map; **no emoji**; icon + label for important actions.
- `data-notes` explains each `.anno` marker (shown in the sidebar); reviewer instructions go in `data-hint`, never inside the screen. Markers must be visible at desktop width.
- `data-state` variants (empty / loading / error) on data screens. Realistic Thai data (names, codes, THB with separators, dd/MM/yyyy); hard cases visible (long names, many rows, a validation error).
- Check responsive screens with the Mobile toggle.

### 9. Write the UX spec (`ux-spec.md`)

Fill the skeleton: Summary · Assumptions · User flow · Screens (`### [id]`, several IDs may share a heading) · States · Fields & validation (exact error text — developers copy it verbatim) · Interactions · **Dev diagrams** (ER, one state diagram per status-bearing entity, one sequence per main action, integration if other systems) · **API contract** · Accessibility · Risks. Every diagram is a ```mermaid block so it renders inline in GitHub/Obsidian/VS Code. Names of statuses, endpoints and fields must match across diagrams, fields table, and API contract.

### 10. Sync, export, verify

```bash
cd <out>/<app>-design
python _tools/sync_diagrams.py ux-spec.md wireframes.html
python _tools/export_tokens.py design.md tokens/
python _tools/verify.py .
```

`verify.py` checks structure (engine present, SCREENS lines, screen markers), inventory ↔ wireframes ↔ spec ↔ mockup coverage, `m-*` duplicates, broken `showScreen` links, notes vs markers, tokens and icon map in sync, raw hex classes, emoji, unknown/mixed/non-existent icons, diagram sync + Mermaid syntax + required diagram types, versions, JS errors, annotation visibility. **Fix every ERROR**; fix warnings or state why not.

### 11. Deliver

claude.ai: zip the folder (`cd <out> && zip -r <app>-design.zip <app>-design`) and present the zip plus `design.md`; tell the user to unzip and open `wireframes.html` / `mockup.html` from the folder — the HTML files need `_engine/` next to them. Claude Code: give the folder path. In chat, keep it short: **implementation risks first**, then key decisions, screen count by module, open questions, one next step.

## Applying wireframe feedback

The export looks like:

```
# Wireframe feedback — Auth — v1.0
## [login] เข้าสู่ระบบ
1. **แก้ไข** · desktop · ใกล้ "เข้าสู่ระบบ" · ตำแหน่ง (50%, 61%) — ปุ่มควรอยู่ชิดขวา
2. **คำถาม** — ทำไมไม่มี LINE login
## Diagram: Data model (ER)
1. **เพิ่ม** — USER ต้องมี phone
```

1. **Load** the project (conversation or uploaded zip/files). Without it, ask for it.
2. **Locate** each item: screen marker `SCREEN: id` + device + `ใกล้ "…"` text + position %. Skip ✅ items.
3. **Triage** in one short list: planned change per item, conflicts (with each other or design principles — propose an alternative), questions. Ambiguous items → ask. If all clear, proceed.
4. **Apply** each through **Updating an existing design** — a wireframe comment usually changes the mockup and spec too.
5. **Answer** every **คำถาม** item. Save the export into `feedback/done/`.
6. **Report** a table: item → done / changed differently (why) / needs answer; list files changed; remind the user to click "ลบรายการที่เสร็จแล้ว" in the wireframe (comments live in their browser).

## Updating an existing design

Every change updates **all affected files in place**:

| Change | design.md | wireframes | mockup | ux-spec | generated |
|---|---|---|---|---|---|
| Color / font token | ✏️ + contrast | — | ✏️ `tokens` | if status colors | re-export tokens |
| Icon set / icon | ✏️ §6 map | if shown | ✏️ `icons` + usages | — | — |
| New screen | ✏️ §7 | ✏️ block + SCREENS line | ✏️ if main flow | ✏️ section + flow | re-sync diagrams |
| Remove screen | ✏️ §7 | ✏️ block, line, links | ✏️ block, line, links | ✏️ section + flow | re-sync diagrams |
| Layout change | — | ✏️ | ✏️ | ✏️ layout/notes | — |
| Field / validation | — | if visible | if visible | ✏️ fields + ER + API | re-sync diagrams |
| Status / transition | ✏️ status mapping | badges | badges | ✏️ state diagram | re-sync diagrams |
| New component | ✏️ components | where used | where used | if behavior | — |

1. **Load** current files; on claude.ai copy uploads into `<out>` first (uploads are read-only).
2. **Edit inside screen markers** with targeted str_replace; never regenerate approved screens; keep IDs stable; fix links to removed screens.
3. **Version**: bump design.md (minor for tweaks, major for palette/restructure), add a changelog row naming changed screens, and update the version in ux-spec.md, `WF.version`, and AGENTS.md. Prefix changed screens' `data-notes` with "(แก้ไข vX.Y)" for one round.
4. **Run** sync / export as needed, then `verify.py`; fix all errors.
5. **Report** changes per file and knock-on changes the user didn't ask for (e.g. "เปลี่ยน brand เป็นสีส้ม ปุ่ม primary ต้องใช้ brand-700 เพราะ 600 ตัดกับตัวอักษรขาวไม่ผ่าน AA"). On claude.ai, re-zip and present.

Alternatives go in as extra screens (`po-list-opt-b`), not new files; remove the losing option once chosen.

## Design principles

When options conflict, the earlier one wins.

1. **Task speed over decoration** — especially for tools used all day.
2. **Prevent errors before reporting them** — pickers over free text, sensible defaults, disabled actions explain why.
3. **Make state visible** — where am I, what's selected, is it saved, did it work.
4. **Irreversible actions need friction** — confirmation naming the object and consequence.
5. **Consistency with what users already know** — match the existing system when fitting into it.
6. **Hierarchy through layout and weight, not color** — color is for status and the one primary action per view.
