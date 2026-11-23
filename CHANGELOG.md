# Changelog

## Unreleased
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

## 1.2.1 — 2026-11-21
- **Realtime theming**: mock.html ships a static `:root { --c-* }` defaults block; the theme picker only writes its overrides, so switching themes (and live design-tool edits of `:root` variables) restyle the whole app — screens and shell chrome — instantly, no reload.
- Shell chrome (toolbar, notes sidebar, focus rings) is themed through the same variables instead of hardcoded zinc colors.
- A realtime bridge mirrors `--c-*` changes from the shell document into the screen iframe (CSS does not cross the boundary).
- verify.py warns when a mock lacks the `:root` defaults block.

## 1.2.0 — 2026-11-21
- **Wireframes + mock in one pass**: the workflow builds `mock.html` alongside `wireframes.html`, screen by screen, so lo-fi and hi-fi are delivered together.
- **`:mock` screen pairing**: every mock screen id ends with `:mock` (`stock-list:mock` pairs with wireframe `stock-list`); verify.py enforces the 1:1 pairing against the inventory.
- **Theme picker in the mock**: toolbar dropdown with Default / Dark / palette presets (Corporate Blue, Industrial Teal, Neutral Mono) from design.md §2.9 — token overrides applied as CSS variables (opacity utilities keep working), remembered per browser.
- `mockup.html` is now `mock.html` (legacy names still found by verify.py, with a rename warning).

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
