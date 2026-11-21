# Changelog

## 1.2.0 — 2026-11-21
- **Wireframes + mock in one pass**: the workflow builds `mock.html` alongside `wireframes.html`, screen by screen, so lo-fi and hi-fi are delivered together.
- **`:mock` screen pairing**: every mock screen id ends with `:mock` (`stock-list:mock` pairs with wireframe `stock-list`); verify.py enforces the 1:1 pairing against the inventory.
- **Theme picker in the mock**: toolbar dropdown with Default / Dark / palette presets (Corporate Blue, Industrial Teal, Neutral Mono) from design.md §2.9 — token overrides applied as CSS variables (opacity utilities keep working), remembered per browser.
- `mockup.html` is now `mock.html` (legacy names still found by verify.py, with a rename warning).

## 1.1.0 — 2026-11-21
- **English by default**: design.md, ux-spec.md, wireframe/mockup copy, sample data and the review-tool chrome are English unless the app's UI language says otherwise; localized apps record every locale's exact strings in the spec's **copy deck**. Feedback markers are now Fix / Add / Remove / Question (older Thai exports still parse).
- **The spec must stand alone**: ux-spec.md carries a per-screen state matrix, a behavior list (autofocus, keyboard type, save success/failure navigation, optimistic updates, auto-save), an interactions table, the copy deck, and fields & validation with exact error text — never details that live only in a wireframe annotation.
- **Dark mode**: design.md §2.4 usage tokens gain a Dark column (plus dark contrast checks); `tokens/` exports dark values (`[data-theme="dark"]` in tokens.css, `dark` object in tokens.json).
- **Non-web stacks**: design.md §2.8 platform mapping (token → the app's actual constant → hex, e.g. `brand-600 → AppColors.greenDark → 0xFF263B34` for Flutter), exported into tokens.json.
- **verify.py** warns on empty spec tables, a missing Dark column when dark mode is declared, and a missing platform mapping when the stack is Flutter/native.

## 1.0.0 — 2026-11-20
First public release.
- Project folder output: design.md, ux-spec.md, wireframes.html, mockup.html, `_engine/`, `_tools/`, tokens, AGENTS.md
- Wireframes: every screen, Desktop / Tablet / Mobile filter, zoom & pan, pinned review comments with markdown export, Diagrams page
- Mockup: review shell with device preview, state switcher, notes sidebar, design-system page (swatches, contrast, icons)
- Dev diagrams in the spec (user flow, ER, state, sequence) synced into the wireframe
- Color system with computed contrast, icon guidance against the "AI look", Thai-specific typography rules
- `verify.py` consistency checks across all files
