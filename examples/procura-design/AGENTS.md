# Procura — Design project · AI guide

> Read this first. It tells you what each file is, which parts you may edit, and how to check your work.
> Version: 1.0 (must equal design.md) · Device model: Responsive web · Icon set: Phosphor `ph:` · Language: English by default (UI copy follows the app's locales — see the spec's copy deck)

## Files

| File | Role | Edit? |
|---|---|---|
| `design.md` | **Source of truth** — colors (light + dark), typography, components, icon map (§6), screen inventory (§7), changelog | Yes |
| `ux-spec.md` | **Source of truth for behavior** — per-screen behavior, state matrix, fields + exact error text, interactions, copy deck, **all diagrams** (Mermaid), API contract. Must stand alone: a dev implements from it without reopening app code. Never leave a detail only in an annotation. | Yes |
| `wireframes.html` | Low-fi screens as `<template>` blocks + diagrams copied from the spec | Screens only |
| `mock.html` | Hi-fi screens as `<section id="<id>:mock">` blocks + `tokens` / `usageTokens` / `themes` / `icons` config | Config + screens only |
| `_engine/` | Toolbar, zoom, comments, device frames — shared code | **Never** |
| `_tools/` | `verify.py`, `sync_diagrams.py`, `export_tokens.py` | Never |
| `tokens/` | Generated from design.md for developers | Never by hand — regenerate |
| `usability-test.md` | Test plan for the prototype: goals, participants, 5 tasks with screens + success criteria, measures, results | Yes |
| `feedback/` | Exported review comments (`*-wireframe-feedback.md`) | Read, then archive |

## How the files connect

- **Screen ID** (kebab-case, e.g. `po-list`) is the shared key: design.md §7 row → `<template id>` in wireframes → `<section id="po-list:mock">` in mock (every mock id ends with `:mock`) → `### [po-list]` in ux-spec.
- Each screen block is wrapped in markers, so you can find or replace one screen without reading the rest:
  `<!-- ════════ SCREEN: po-list ════════ -->` … `<!-- ════════ /SCREEN: po-list ════════ -->`
- The `SCREENS (in order): …` line at the top of wireframes.html and mockup.html lists every screen — update it when adding/removing screens.
- Colors: design.md §2 → `const tokens` + `const usageTokens` in mock.html → `tokens/`. Theme variants: design.md §2.9 → `const themes` (theme picker in the mock toolbar). Icons: design.md §6 → `const icons` in mock.html.
- Diagrams: written only in ux-spec.md; `sync_diagrams.py` copies them into wireframes.html between `DIAGRAMS:START/END`.

## Editing rules

1. Change design.md / ux-spec.md first, then the screens that depend on them.
2. One change → every affected file:

   | Change | Also update |
   |---|---|
   | Color / font token | mock `tokens`, theme overrides if §2.9 touches it, re-export `tokens/` |
   | Icon | design.md §6 + mock `icons` + every usage |
   | New / removed screen | design.md §7, wireframes, ux-spec (screens + user flow + states row), mock (`<id>:mock`) if on main flow, both `SCREENS` lines, every `showScreen()` link |
   | Layout | wireframe + mock + spec layout/notes |
   | Theme variant | design.md §2.9 + mock `themes` (brand-700 AA with white text; brand-600 ≥ 4.5:1 on white — verify checks every theme) |
   | Field / validation | spec fields table + copy deck + ER + API contract + screens |
   | Status / transition | design.md status mapping + state diagram + badges in screens |
   | Behavior / interaction | spec interactions table + state matrix (+ screens if a state variant is visible) |
   | New / removed / renamed screen on a tested flow | usability-test.md task **Screens:** lists |
   | Dark-mode token | design.md §2.4 Dark column + contrast checks + mockup `tokens` + re-export `tokens/` |
3. Edit inside the screen markers with targeted replacements; don't reformat untouched screens.
4. Components: wireframes compose from the `wf-*` kit (toolbar → Components), the mock from the `mk-*` kit (gallery on `design-system:mock`). Don't invent new `wf-*`/`mk-*` names — verify.py warns.
5. Mock: screen ids end with `:mock`; theme-aware classes (`bg-surface`, `bg-page`, `text-body`, `text-muted`, `border-input`) for surfaces that must follow the theme; token classes only (`bg-brand-600`); icons only from `icons`; no emoji; `data-notes` count = `.anno` markers (a marker on a desktop- or mobile-only element gets `data-device="desktop|mobile"`); reviewer hints in `data-hint`; widgets use ARIA roles (`role=tablist/tab`, `aria-haspopup=menu`, `role=switch`) and dialogs open with `openDialog('id')` — the engine adds the keyboard behavior.
6. Responsive web: one screen ID whose template holds `.frame-desktop` / `.frame-tablet` (only if the layout differs) / `.frame-mobile` — never `m-*` copies.
7. Bump the version in design.md, ux-spec.md, `WF.version` (wireframes.html) and this file; add a changelog row.

## Commands (run from this folder)

```bash
python _tools/sync_diagrams.py ux-spec.md wireframes.html   # after any diagram change
python _tools/export_tokens.py design.md tokens/            # after any color change
python _tools/verify.py .                                   # always, before finishing — fix every ERROR
python _tools/update_engine.py <path-to-skills/design-kit>  # when verify says _engine/ is out of date
```

## Applying review feedback

Files in `feedback/` (or pasted text starting with `# Wireframe feedback —`) list comments by `## [screen-id]` with device, nearby text and position. Locate each element, apply the change across all affected files, answer every **Question** item (older Thai exports label them **คำถาม**), skip items marked ✅, then move the file to `feedback/done/`.
