---
name: design-kit
description: Design UX/UI for an app or feature and deliver an AI-readable design project — design.md (colors light + dark, typography, icons, components), wireframes of every screen (zoom, pinned comments, diagrams page) built together with a clickable HTML + Tailwind mock (theme picker), dev diagrams (user flow, ER, state, sequence, API contract), a stand-alone UX spec (states, exact error text, interactions, copy deck), design tokens with platform mapping, and an AGENTS.md guide — English by default, kept in sync on change. Use whenever the user asks to design, mock up, wireframe, plan screens, choose colors, icons or a theme, write design.md, lay out a page, form, report, dashboard, or mobile app — ERP/back-office, web, or mobile — even if they only say "ออกแบบหน้าจอ", "ทำ wireframe", "ทำ mockup", "เลือกสี", "ทำ design.md", "วาง layout", "UX/UI", ask to change an existing design ("แก้หน้า...", "เปลี่ยนสี...", "เพิ่มหน้า..."), or paste wireframe feedback ("Wireframe feedback — ...").
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
├── usability-test.md  test plan for the prototype: 5 tasks with screens + success criteria, measures, results
├── wireframes.html    content only: WF config + diagrams (generated) + one <template> per screen
├── mock.html          content only: tokens + usageTokens + themes + icons config + one <section id="id:mock"> per screen
├── _engine/           shared review UI (toolbar, zoom, comments, device frames) — never edited per project
├── _tools/            verify.py · sync_diagrams.py · export_tokens.py (copied from this skill's scripts/)
├── tokens/            tokens.css · tailwind.config.js · tokens.json (generated)
└── feedback/          exported review comments
```

Why this shape: content files hold only what changes per project, so an AI editing a screen reads a few hundred lines instead of thousands of lines of engine code; every screen sits between `<!-- ════════ SCREEN: id ════════ -->` / `<!-- ════════ /SCREEN: id ════════ -->` markers and is listed in a `SCREENS (in order): …` header line, so one screen can be found and replaced in isolation; AGENTS.md tells any future AI session (including Claude Code opened on this folder) the rules without re-reading this skill.

The **screen ID** (kebab-case, e.g. `po-list`) is the shared key: design.md §7 row → `<template id>` → `<section id="po-list:mock">` in the mock (every mock id ends with `:mock`) → spec heading `### [po-list]`. None of this is production code.

## Language

Deliverables default to **English**: design.md, ux-spec.md, wireframe/mock copy, error text, diagrams, sample data, review-tool chrome. Match the app's real UI language instead when the app is already localized (e.g. a Thai-only app keeps Thai screen copy) — and when it ships several locales, record every locale's exact strings in the spec's **copy deck**. The user can override the default; their explicit choice wins.

## The spec must stand alone

The test for ux-spec.md: **a developer implements from it without reopening app code**. Anything they must know — validation rules and exact error text, endpoints and payloads, per-screen states, focus/keyboard behavior, what Save does on success and failure, dark theme values, breakpoint rules — goes in the spec's tables. A wireframe annotation is a pointer to a spec row, never the only place a requirement lives. When designing against an existing codebase, mine the code first (validators, theme, API client, l10n files) and paste the facts verbatim into the spec.

## First: is there existing work?

Check the conversation, the uploads / working directory for an existing design.md, wireframes, mock, spec, or a project zip.

- **Found** → **Updating an existing design**. Reuse tokens, icons, and IDs; never start over.
- **A "Wireframe feedback — …" export** → **Applying wireframe feedback**.
- **Stale engine** — `verify.py` warns that `_engine/` is older than the tools (or has no VERSION stamp) → run `python _tools/update_engine.py <skill>` from the project folder (copy `update_engine.py` from `<skill>/scripts/` first if the project predates it), then verify. It never touches content files.
- **Old format** (single-file HTML with inline engine, `*-wireframes.html` names, no AGENTS.md) → offer to migrate as part of the change: create the folder from `assets/project/`, move each screen's markup into the new content files with markers, keep IDs and content unchanged, then verify.

## Workflow (new design)

### 1. Understand before drawing

Extract: **who** (role, frequency, device), **job to be done**, **data** (fields, volume), **context** (internal / public web / native mobile; existing system), **constraints** (permissions, approvals, language), **brand** (logo, colors, product name, or a mood), **stack** (Tailwind web / Flutter / React Native — decides whether design.md needs the §2.8 platform mapping), and whether the app has or plans a **dark theme**. For an existing app, also note where the code keeps error strings, validators, endpoints and locales — the spec will quote them.

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
| **Always** — roles & permissions, acceptance criteria, inventory Req ID / Priority / Status, component mapping, formats & locale | `references/handoff-tables.md` |

### 3. Decide the device model

- **Responsive web**: one ID per screen. Wireframe templates hold `.frame-desktop` (1280) and `.frame-mobile` (390), plus `.frame-tablet` (768) whenever the layout changes meaningfully at tablet width (sidebar collapses, table becomes cards, two columns become one) — skip it when tablet is just a wider mobile. The mock builds one screen with Tailwind breakpoints, checked with the Tablet/Mobile toggles. **Never `m-*` copies** — two copies drift apart.
- **Native mobile app**: `data-device="mobile"`; `m-` prefix only if a separate web admin exists.
- **Desktop-only internal tool**: design for 1366px+, note it in design.md.

### 4. Screen inventory and flow

List **every** screen, grouped by module. Checklist so the boring ones aren't forgotten:

- Auth: login, forgot/reset password, first-time setup
- Each module: list/search, detail, create, edit, delete confirm, approval
- Shared: home/dashboard, notifications, profile, settings, users & roles
- System: empty first-use, 403, 404, error/maintenance, session expired
- Dialogs/bottom sheets with real content (own ID) · Mobile: onboarding, offline

Give each screen its **Req ID** (from the requirements doc), **Priority** (`MVP` · `P2` · `P3` · `Later`) and **Status** (`draft` · `review` · `approved` · `changed`) — see `handoff-tables.md` §1. List the **roles** from the requirements; they become the permission matrix.

Write the user flow as Mermaid `flowchart` with **screen IDs as node IDs**, including failure paths. It goes in ux-spec.md `## User flow`.

### 5. Checkpoint (apps with more than ~8 screens)

Before building screens, send: the inventory (grouped, with IDs, Req ID and Priority), the roles, the flow, the device model, the palette (brand 600 hex + preset + why), the icon set (+ why), and any invented product name. Ask to confirm or correct, and end the turn. Redoing 15+ screens built on a wrong assumption costs far more than one message. Small, clear features (≤ 8 screens) skip this and list assumptions instead.

### 6. Create the folder and write design.md

```bash
cp -r <skill>/assets/project <out>/<app>-design
mkdir -p <out>/<app>-design/_tools && cp <skill>/scripts/*.py <out>/<app>-design/_tools/
```

Fill design.md: full color scales per `color-system.md` with **computed contrast ratios** (fix failing pairs before moving on); **§2.4 usage tokens with a Dark column whenever the app has or will ship dark mode** — for an existing app, copy the real dark values from its theme code rather than inventing them; **§2.8 platform mapping whenever the stack isn't web** (token → the app's actual constant → hex, e.g. `brand-600 → AppColors.greenDark → 0xFF263B34`, so a Flutter dev never converts hex by hand); typography, spacing; **§4.1–4.3 motion, breakpoint and z-index tokens** (keep the table formats — `export_tokens.py` reads them); components with states plus **§5.1 component mapping** (`mk-*` → code component, `TBD` until the stack is chosen; `handoff-tables.md` §4); **§6 icon set + icon map** per `iconography.md` (one set chosen for the users — e.g. Fluent for people who live in Office/Dynamics AX, Phosphor or Tabler elsewhere, not Lucide by default); §7 inventory with Req ID / Priority / Status; changelog 1.0. Fill AGENTS.md header (app, version, device model, icon set, language).

### 7. Wireframe AND mock every screen (`wireframes.html` + `mock.html`)

Build both files in the same pass — for each inventory screen, write the wireframe template, then immediately its mock section — so the delivery is reviewable lo-fi and hi-fi together.

- Wireframes: replace the example screens with one marked `<template>` block per inventory screen in inventory order; update the wireframe's `SCREENS (in order)` line. Set `WF = { app, version }`. Grayscale `wf-*` classes only — compose from the **wireframe component kit** (topbar, sidebar, table, badge, tabs, stepper, modal, bottom sheet, empty/skeleton states…; full list in the file header, live gallery with copyable markup under the toolbar's **Components** page); never invent new `wf-*` names. Attributes: `data-title`, `data-module`, `data-device`, `data-notes` (one per `.anno`, `|`-separated); frames get `data-label` ("Desktop 1280", "Tablet 768", "Mobile 390"). Wire primary buttons with `showScreen('id')`. Don't touch the DIAGRAMS block — it's generated.
- Mock: one marked `<section class="screen" id="<id>:mock">` per screen on the primary flow plus one example of each pattern; keep `design-system:mock` last; update the mock's `SCREENS` line and the inventory Mockup column. **Every mock id ends with `:mock`**, pairing it with the wireframe screen of the same base id; navigation uses `showScreen('id:mock')`.
- Mock config: design.md's scales into `const tokens`, §2.4 resolved into `const usageTokens`, §2.9 variants into `const themes` (Default plus Dark and any palette presets — keep `brand-700` dark enough that white text on it stays AA in every theme), and the §6 icon map into `const icons`.
- Mock components: use the **`mk-*` kit** (`mk-btn mk-btn-primary`, `mk-field`/`mk-input` with `aria-invalid`, `mk-table`, `mk-badge-success`, `mk-tabs`, `mk-alert-danger`, `mk-modal`, `mk-skeleton`, `mk-empty`…) — it already carries hover/focus/disabled/loading/error states, 40px (44px on touch) targets, reduced-motion handling and AA-safe dark variants. The gallery on `design-system:mock` shows every component with copyable markup. Tailwind stays for layout and spacing; hand-roll only what the kit lacks, and add it to design.md §5.
- Mock classes: theme-aware surfaces (`bg-surface`, `bg-page`, `text-body`, `text-muted`, `border-input`, `border-default`) so themes actually restyle the screens; token classes only (`bg-brand-600`); icons only as `<iconify-icon icon="…">` from the map; **no emoji**; icon + label for important actions. Interactive widgets carry ARIA roles (`role=tablist/tab`, `aria-haspopup=menu` + `role=menu`, `role=switch`) and dialogs open with `openDialog('id')` — the engine supplies the keyboard behavior (arrow keys, focus trap, Esc), so the mock is keyboard-testable.
- `data-notes` explains each `.anno` marker (shown in the sidebar); a marker on an element that exists only at one width gets `data-device="desktop"` or `"mobile"`; reviewer instructions go in `data-hint`, never inside the screen. Markers must be visible at desktop width.
- `data-state` variants (empty / loading / error) on data screens. Realistic sample data in the deliverable language (English by default; for localized apps show the app's real locales — names, codes, THB with separators, dd/MM/yyyy); hard cases visible (long names, many rows, a validation error).
- Check responsive screens with the Mobile toggle; check every theme with the Theme dropdown.
- The engines already provide: device filter, overview grid, zoom/pan, 💬 pinned comments (wireframes), device preview, state switcher, **theme picker** (mock toolbar — Default / Dark / presets from §2.9, remembered per browser), notes sidebar, feedback export.

### 8. Write the UX spec (`ux-spec.md`)

Fill the skeleton — it is the file a front-end dev lives in, so it must stand alone (see *The spec must stand alone* above): Summary · Assumptions · User flow · **Roles & permissions** (`### Roles` + `### Permission matrix`, `Role | Screen | View | Create | Edit | Approve | Delete`) · Screens (`### [id]`, several IDs may share a heading — each with **Layout incl. every breakpoint rule** and a **Behavior** list: autofocus, keyboard type, what Save success/failure does — pop vs navigate — optimistic updates, auto-save) · **Acceptance criteria** (`ID | Screen | Req ID | Given | When | Then`, ≥ 1 row per inventory screen) · **States matrix** (every data screen gets a row; empty/loading/error/success/permission; "n/a" beats silence) · **Fields & validation** (exact error text, copied from the app's code when it exists — developers paste it verbatim) · **Interactions & behavior** table (triggers → outcomes, incl. quirks like auto-save or read-only modes) · **Copy deck** (every UI string per locale — EN/TH columns for localized apps) · **Formats & locale** (date / time / datetime / timezone / number / currency / plural patterns per locale) · **Dev diagrams** (ER, one state diagram per status-bearing entity, one sequence per main action, integration if other systems) · **API contract** (method, path, used-by screen, request body, response, errors — from the real API client, never invented) · **Accessibility** (one row per inventory screen: `Screen | Announce (aria-live) | Focus on open | Focus return | Tab order`, then `### Global` rules — `states-and-accessibility.md`) · Risks. Layout rules name the §4.2 breakpoints (`md`, `lg`), not raw px. Every diagram is a ```mermaid block so it renders inline in GitHub/Obsidian/VS Code. Names of statuses, endpoints and fields must match across diagrams, fields table, copy deck, and API contract.

### 9. Plan the usability test (`usability-test.md`)

Fill the template: goals tied to the spec's success metric and design.md §0 assumptions, participants (5 per user group) with a screener, setup (device matching the device model, starting screen), **five tasks** from warm-up to hardest — each a goal in the user's words (never name the button), the `**Screens:** [id] → [id]` it touches, an observable `**Success:**` end state, and what to watch for; include one task that hits a validation error and recovers with the spec's exact error text. Keep the measures table (success, time, errors, SEQ, SUS) and an empty results table. `verify.py` checks there are ≥ 5 tasks, each with screens from the inventory and a success criterion.

### 10. Sync, export, verify

```bash
cd <out>/<app>-design
python _tools/sync_diagrams.py ux-spec.md wireframes.html
python _tools/export_tokens.py design.md tokens/
python _tools/verify.py .
```

`verify.py` checks structure (engine present, SCREENS lines, screen markers), inventory ↔ wireframes ↔ spec ↔ mock coverage (`:mock` id pairing), `m-*` duplicates, unknown `wf-*` / `mk-*` classes (not in the component kits), broken `showScreen` links, notes vs markers, tokens, usage tokens and theme variants in sync with design.md, raw hex classes, emoji, unknown/mixed/non-existent icons, diagram sync + Mermaid syntax + required diagram types, versions, empty spec tables (states, fields, interactions, copy deck, API contract), inventory Req ID / Priority / Status values, roles & permission matrix (declared roles, inventory screens, cell values), acceptance criteria (format, unique IDs, every screen covered), accessibility table (every screen, no empty cells), usability-test tasks (≥ 5, screens from the inventory, success criteria), text contrast ≥ 4.5:1 on every mock screen in every theme, dark-mode/platform-mapping presence when the header promises them, JS errors, annotation visibility. **Fix every ERROR**; fix warnings or state why not.

### 11. Deliver

claude.ai: zip the folder (`cd <out> && zip -r <app>-design.zip <app>-design`) and present the zip plus `design.md`; tell the user to unzip and open `wireframes.html` / `mock.html` from the folder — the HTML files need `_engine/` next to them. Claude Code: give the folder path. In chat, keep it short: **implementation risks first**, then key decisions, screen count by module, open questions, one next step.

## Applying wireframe feedback

The export looks like:

```
# Wireframe feedback — Auth — v1.0
> Exported 21/11/2026 09:14 · 2 open items · file wireframes.html
## [login] Sign in
1. **Fix** · desktop · near "Sign in" · position (50%, 61%) — the button should sit flush right
2. **Question** — why is there no LINE login?
## Diagram: Data model (ER)
1. **Add** — USER needs a phone field
```

Exports made by older, Thai-language engines use the same shape with `**แก้ไข**` (Fix), `**เพิ่ม**` (Add), `**ลบออก**` (Remove), `**คำถาม**` (Question) — treat them identically.

1. **Load** the project (conversation or uploaded zip/files). Without it, ask for it.
2. **Locate** each item: screen marker `SCREEN: id` + device + `near "…"` text + position %. Skip ✅ items.
3. **Triage** in one short list: planned change per item, conflicts (with each other or design principles — propose an alternative), questions. Ambiguous items → ask. If all clear, proceed.
4. **Apply** each through **Updating an existing design** — a wireframe comment usually changes the mock and spec too. Feedback can also target mock screens: item markers `## [<id>:mock]` map to the same screen.
5. **Answer** every **Question** item. Save the export into `feedback/done/`.
6. **Report** a table: item → done / changed differently (why) / needs answer; list files changed; remind the user to click "Clear done items" in the wireframe (comments live in their browser).

## Migrating a v2.0.0 project

From 3.0 (unreleased), `verify.py` errors on projects that lack the hand-off tables. To bring a v2.0.0 project up to date (keep every ID and screen unchanged):

1. Copy the new `scripts/*.py` into `_tools/` (or run `update_engine.py`), then run `verify.py` to list what is missing.
2. design.md §7: add columns `Req ID | Priority | Status` after Mockup; fill every row (`—` Req ID only for system screens). Rename §4 to `Spacing, radius, elevation, motion, layers` and add §4.1–4.3 from the template; add §5.1 Component mapping.
3. ux-spec.md: add `## Roles & permissions` after User flow, `## Acceptance criteria` after Screens, `## Formats & locale` after Copy deck, and replace `## Accessibility notes` with `## Accessibility` (table + `### Global`) — move the old bullets into the table rows or `### Global`.
4. Re-export tokens, verify to 0 errors, bump the design version (minor) with a changelog row "Hand-off tables added".

## Updating an existing design

Every change updates **all affected files in place**:

| Change | design.md | wireframes | mock | ux-spec | generated |
|---|---|---|---|---|---|
| Color / font token | ✏️ + contrast | — | ✏️ `tokens` (+ §2.9 if it breaks a theme) | if status colors | re-export tokens |
| Dark-mode value | ✏️ §2.4 Dark + §2.7 | — | ✏️ `tokens` | — | re-export tokens |
| Theme variant | ✏️ §2.9 | — | ✏️ `themes` | — | — |
| Icon set / icon | ✏️ §6 map | if shown | ✏️ `icons` + usages | — | — |
| New screen | ✏️ §7 | ✏️ block + SCREENS line | ✏️ `<id>:mock` if main flow | ✏️ section + flow + states row | re-sync diagrams |
| Remove screen | ✏️ §7 | ✏️ block, line, links | ✏️ block, line, links | ✏️ section + flow + states row | re-sync diagrams |
| Layout change | — | ✏️ | ✏️ | ✏️ layout/notes (breakpoints into the spec, not annotations) | — |
| Field / validation | — | if visible | if visible | ✏️ fields + copy deck + ER + API | re-sync diagrams |
| Behavior / interaction | — | if visible | if visible | ✏️ interactions table + state matrix | — |
| UI string | — | if visible | if visible | ✏️ copy deck | — |
| Status / transition | ✏️ status mapping | badges | badges | ✏️ state diagram | re-sync diagrams |
| Role / permission | — | if visible | disabled/hidden states | ✏️ roles + permission matrix + States Permission column + AC | — |
| Requirement change | ✏️ §7 Req ID / Priority | — | — | ✏️ acceptance criteria | — |
| Edit to an approved screen | ✏️ §7 Status → `changed` | — | — | — | — |
| Motion / breakpoint / layer token | ✏️ §4.1–4.3 | — | if used | layout rules if a breakpoint is renamed | re-export tokens |
| Component library / stack | ✏️ §5.1 mapping | — | — | — | — |
| Date / number format | — | sample data | sample data | ✏️ formats & locale | — |
| New component | ✏️ components | where used | where used | if behavior | — |

When the change is to an **existing app's design**, open the code that owns the facts before editing the spec: validators and error strings, the API client (endpoints, payloads), theme files (light/dark), l10n files (real EN/TH strings). Quote them verbatim in the spec — paraphrasing sends the dev back to the code anyway.

1. **Load** current files; on claude.ai copy uploads into `<out>` first (uploads are read-only).
2. **Edit inside screen markers** with targeted str_replace; never regenerate approved screens; keep IDs stable; fix links to removed screens.
3. **Version**: bump design.md (minor for tweaks, major for palette/restructure), add a changelog row naming changed screens, and update the version in ux-spec.md, `WF.version`, and AGENTS.md. Prefix changed screens' `data-notes` with "(changed vX.Y)" for one round.
4. **Run** sync / export as needed, then `verify.py`; fix all errors.
5. **Report** changes per file and knock-on changes the user didn't ask for (e.g. "brand switched to orange, so primary buttons use brand-700 — brand-600 with white text fails AA"). On claude.ai, re-zip and present.

Alternatives go in as extra screens (`po-list-opt-b`), not new files; remove the losing option once chosen.

## Design principles

When options conflict, the earlier one wins.

1. **Task speed over decoration** — especially for tools used all day.
2. **Prevent errors before reporting them** — pickers over free text, sensible defaults, disabled actions explain why.
3. **Make state visible** — where am I, what's selected, is it saved, did it work.
4. **Irreversible actions need friction** — confirmation naming the object and consequence.
5. **Consistency with what users already know** — match the existing system when fitting into it.
6. **Hierarchy through layout and weight, not color** — color is for status and the one primary action per view.
7. **Spec over annotation** — if a developer must know it, it's in ux-spec.md's tables; annotations only point there.
