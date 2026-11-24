# Changelog

## Unreleased
Target version: 3.0.0 (breaking — not released yet).

### Breaking
Projects made with 2.0.0 fail `verify.py` until they add the hand-off tables (the user chose ERROR, not WARN).
- design.md §7 inventory needs `Req ID`, `Priority` (`MVP` · `P2` · `P3` · `Later`) and `Status` (`draft` · `review` · `approved` · `changed`) columns, filled on every row. Columns are now read by name, not position.
- ux-spec.md needs `## Roles & permissions` (`### Roles` + `### Permission matrix`), `## Acceptance criteria` (≥ 1 row per inventory screen) and `## Accessibility` as a per-screen table — `## Accessibility notes` no longer counts.

### Migrating a 2.0.0 project
1. Copy the new `scripts/*.py` into the project's `_tools/` (or run `update_engine.py`), then run `verify.py` to list what is missing.
2. design.md: add `Req ID | Priority | Status` to §7 after Mockup; rename §4 to "Spacing, radius, elevation, motion, layers" and add §4.1–4.3 from the template; add §5.1 Component mapping.
3. ux-spec.md: add `## Roles & permissions` after User flow, `## Acceptance criteria` after Screens, `## Formats & locale` after Copy deck; replace `## Accessibility notes` with `## Accessibility` (table + `### Global`), moving the old bullets.
4. Re-export tokens, verify to 0 errors, bump the design version (minor) with a changelog row. `examples/procura-design` 1.1 shows the result.

### Added
- **Hand-off tables** in the templates and `references/handoff-tables.md`: roles & permission matrix, acceptance criteria (Given / When / Then), inventory Req ID / Priority / Status, component mapping (design.md §5.1: `mk-*` → code component, kit ARIA states → props), formats & locale (date, time, timezone, number, currency, plural; CLDR patterns, Thai era).
- **Accessibility beyond contrast** in `references/states-and-accessibility.md` and the spec's per-screen table: aria-live announcements, focus on open / focus return, tab order, WCAG 2.2 target size and focus-not-obscured, 200% zoom / reflow, dynamic type, error summaries.
- **Motion, breakpoint and z-index tokens** (design.md §4.1–4.3) exported to `tokens/`; spec layout rules name breakpoints (`md`, `lg`).

## 2.0.0 — 2026-11-23

### Breaking
Projects that passed `verify.py` before may now fail it.
- `verify.py` errors on any text below 4.5:1 on any mock screen in any theme (it used to check none). The old **Industrial Teal** preset fails: its `brand-600` `#0d9488` is 3.74:1 on white — update §2.9 and `const themes` to `#0f766e` / `#115e59` / `#134e4a`.
- `verify.py` warns when `usability-test.md` is missing and errors when it has fewer than 5 tasks, a task without `**Success:**`, or screens not in the inventory.

### Added
- **Keyboard behavior in the mock engine** (WAI-ARIA patterns, wired by role): tabs with ←/→/Home/End and `aria-controls` panels; `openDialog('id')` / `closeDialog('id')` with focus moved in, Tab trapped, Esc to close and focus returned; menu buttons (`aria-haspopup=menu`) with ↑/↓/Home/End/Esc; `role=switch`; single-select chips (`data-select="single"`). The component gallery demonstrates each, and browser tests cover them.
- **`usability-test.md`** deliverable: goals, participants + screener, setup, five tasks (scenario, screens, success, watch-for), measures (success, time, errors, SEQ, SUS), severity scale, results table. Workflow step 9 in SKILL.md; Procura example included.
- **Device-specific markers**: `<span class="anno" data-device="desktop">` — the visibility check skips them at other widths (no more warnings for desktop-only elements).
- Color presets in `references/color-system.md` now list a `brand-600` that is ≥ 4.5:1 on white (Teal `#0f766e`, Green `#15803d`, Orange `#c2410c`) with its ratio.

### Tooling
- **CI**: every PR runs `./tools/check.sh` — unit tests for the scripts, `verify.py` on `examples/procura-design`, browser tests on the template and the example (no JS errors, the State switcher shows exactly one variant, text ≥ 4.5:1 in every theme at desktop and mobile widths) and the zip build. The tests fail on each bug fixed in 1.2.1.
- **`examples/procura-design`**: a full design project (purchase-order approval, 5 screens) made with the skill — the CI fixture and the docs site's live demo.
- **Engine version stamp**: `_engine/VERSION`; `verify.py` warns when a project's engine is older than its tools or unstamped. New `_tools/update_engine.py` refreshes `_engine/` and `_tools/` from the installed skill without touching design files.
- **`tools/release.sh prepare|tag X.Y.Z`**: writes the version everywhere it lives, dates the changelog, opens the release PR, and tags only when `main` carries that version. The Release workflow now reacts only to `vX.Y.Z` tags and also checks `_engine/VERSION`.
- **Docs site redesign**: live demo, install tabs (keyboard accessible), copy buttons, mobile section nav, dark mode, changelog rendered from `CHANGELOG.md`, version read from one meta tag.

### Fixed
- The contrast check (tests and verify) skipped anything inside a `.hidden` class, including `hidden md:block` tables that are visible on desktop.

## 1.2.1 — 2026-11-23
- **Wireframe component kit**: ~35 grayscale `wf-*` blocks (text, buttons + states, form controls incl. check/radio/toggle/chips, table, badges, stats, charts, list, top bar, sidebar, tabs, breadcrumb, pagination, stepper, mobile app/tab bar, modal, bottom sheet, menu, banner, toast, skeleton, empty). Error states use dashed borders + a mark, never color alone.
- **Components page** in the wireframe toolbar (`#components`): live demo + copyable markup for every block.
- **Mock component kit**: themeable `mk-*` components driven by the `--c-*` tokens — buttons (variants, sizes, disabled, `aria-busy` loading, icon), fields (`aria-invalid` error, disabled, help), select/textarea, checkbox/radio/switch, chips, card, table, badges, stat, avatar, progress, side nav, tabs, breadcrumb, pagination, dialog, menu, alerts, toast, tooltip, skeleton, empty. 40px targets (44px on coarse pointers), `prefers-reduced-motion` respected.
- **AA in dark themes**: the engine flags dark themes (`.theme-dark`) and swaps 700-on-50 tinted text (below 4.5:1 on dark tints) for body text, keeping the hue in the dot/bar.
- Inactive `data-state` variants are hidden with `!important`, so kit components that set their own `display` (mk-empty, mk-alert) never leak into other states.
- **Component gallery** on `design-system:mock`, rendered by the engine with icons from the project's `icons` map.
- Templates use the kits; the example `list` wireframe shows sidebar, top bar, table, badges and pagination.
- verify.py warns on `wf-*` / `mk-*` classes not defined by the kits.
- Fix: the example `list` wireframe's `data-notes` broke on unescaped quotes, losing note 2.
- Fix: `export_tokens.py` and `verify.py` read a §2.4 row like `| bg-page | neutral-50 | #020617 |` as a token row, overwriting `neutral-50` with the dark hex in tokens/ and verify (regexes now anchored to the row start).
- Fix: the mock's State → Error option never showed error variants (sent `Error`, screens use `data-state="error"`).

## 1.1.0 — 2026-11-21
- **English by default**: design.md, ux-spec.md, wireframe/mock copy, sample data and the review-tool chrome are English unless the app's UI language says otherwise; localized apps record every locale's exact strings in the spec's **copy deck**. Feedback markers are now Fix / Add / Remove / Question (older Thai exports still parse).
- **The spec must stand alone**: ux-spec.md carries a per-screen state matrix, a behavior list (autofocus, keyboard type, save success/failure navigation, optimistic updates, auto-save), an interactions table, the copy deck, and fields & validation with exact error text — never details that live only in a wireframe annotation.
- **Wireframes + mock in one pass**: the workflow builds `mock.html` alongside `wireframes.html`, screen by screen, so lo-fi and hi-fi are delivered together.
- **`:mock` screen pairing**: every mock screen id ends with `:mock` and pairs 1:1 with the wireframe screen; verify.py enforces the pairing against the inventory.
- **Realtime theme picker in the mock**: toolbar dropdown with Default / Dark / palette presets (Corporate Blue, Industrial Teal, Neutral Mono) from design.md §2.9 — token overrides applied as CSS variables, choice remembered per browser; static `:root` defaults make theme switches and live design-tool edits restyle the whole app (screens + shell chrome) instantly, and a realtime bridge mirrors `--c-*` changes into the screen iframe.
- **Dark mode**: design.md §2.4 usage tokens gain a Dark column (plus dark contrast checks); `tokens/` exports dark values.
- **Non-web stacks**: design.md §2.8 platform mapping (token → the app's actual constant → hex, e.g. Flutter `AppColors`), exported into tokens.json.
- `mockup.html` is now `mock.html` (legacy names still found by verify.py, with a rename warning).
- **verify.py** warns on empty spec tables, a missing Dark column, missing platform mapping, `:mock` pairing, usage-token/theme drift, and missing `:root` defaults.

## 1.0.0 — 2026-11-20
First public release.
- Project folder output: design.md, ux-spec.md, wireframes.html, mockup.html, `_engine/`, `_tools/`, tokens, AGENTS.md
- Wireframes: every screen, Desktop / Tablet / Mobile filter, zoom & pan, pinned review comments with markdown export, Diagrams page
- Mockup: review shell with device preview, state switcher, notes sidebar, design-system page (swatches, contrast, icons)
- Dev diagrams in the spec (user flow, ER, state, sequence) synced into the wireframe
- Color system with computed contrast, icon guidance against the "AI look", Thai-specific typography rules
- `verify.py` consistency checks across all files
