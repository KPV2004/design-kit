# [App name] — Design System

> Version: 1.0 · Updated: [yyyy-MM-dd] · Product type: [Enterprise / Web app / Native mobile / Mixed] · Device model: [Responsive web / Native mobile / Desktop-only] · Stack: [Tailwind web / Flutter / React Native / …] · Dark mode: [no / yes — light + dark]
> Source of truth for colors, typography, spacing, and components. The wireframes, mockup, and UX spec must use the names defined here.

## 0. Assumptions
List anything not confirmed by the user (brand, product name, login method...). Mark each as confirmed once the user agrees.

## Changelog
| Version | Date | Change |
|---|---|---|
| 1.0 | [date] | Initial design system |

## 1. Design principles
3–5 principles specific to this app (e.g. "Prefer picking over typing — use dropdowns/scan wherever possible").

## 2. Colors

### 2.1 Brand scale
| Token | Hex | Usage |
|---|---|---|
| brand-50 | | Selected row, soft background |
| brand-100 | | Hover on soft background |
| brand-200 | | |
| brand-300 | | |
| brand-400 | | Primary in dark mode |
| brand-500 | | |
| brand-600 | | Primary button, links, active tab |
| brand-700 | | Primary hover/pressed |
| brand-800 | | |
| brand-900 | | Headings on brand-tinted areas |

### 2.2 Neutral scale
(same 10-step table: page bg, borders, muted text, body text, headings)

### 2.3 Semantic colors
| Token | 50 (bg) | 600 (main) | 700 (text) | Usage |
|---|---|---|---|---|
| danger | | | | Errors, destructive actions |
| success | | | | Completed, approved |
| warning | | | | Pending, attention |
| info | | | | Informational, posted |

### 2.4 Usage tokens
If design.md says **Dark mode: yes** (or the existing app has a dark theme — mine it from its theme code), every usage token needs a dark value; re-check dark pairs in §2.7. Don't ship a light-only spec for an app that ships dark.

| Token | Light | Dark | Where |
|---|---|---|---|
| bg-page | neutral-50 | neutral-950 | App background |
| bg-surface | white | neutral-900 | Cards, tables, modals |
| text-body | neutral-800 | neutral-100 | Main text |
| text-muted | neutral-500 | neutral-400 | Helper text, captions |
| border-default | neutral-200 | neutral-800 | Dividers |
| border-input | neutral-300 | neutral-600 | Input borders |
| focus-ring | brand-500 | brand-400 | Keyboard focus |

### 2.5 Status mapping
| Status | Badge | Label |
|---|---|---|

### 2.6 Chart palette
chart-1 … chart-8 with hex.

### 2.7 Contrast checks
| Pair | Ratio | Pass |
|---|---|---|
| text-body on bg-page | | AA |
| white on brand-600 | | AA |
| text-muted on bg-surface | | AA |
| text-body dark on bg-page dark (dark mode only) | | AA |
| white on brand-400 (dark-mode primary) | | AA |

### 2.8 Platform mapping (non-web stacks)
Required when the stack isn't web (Flutter, React Native…): map each token to the constant the app already uses — `tokens/` alone can't be pasted into Flutter, and a dev shouldn't have to convert hex by hand. Keep the names the app actually uses.

| Token | Web class | Platform name | Hex |
|---|---|---|---|
| brand-600 | bg-brand-600 | AppColors.greenDark | 0xFF263B34 |
| brand-400 | bg-brand-400 | AppColors.greenPrimary | 0xFF… |
| bg-page (dark) | dark:bg-neutral-950 | AppColors.dark.background | 0xFF… |

### 2.9 Theme variants (mock theme picker)
Named looks the reviewer can switch between in mock.html. Each row overrides one token. Rules: keep `brand-700` dark enough that white text on it stays AA in every theme, and `brand-600` ≥ 4.5:1 on white — it is the link and selected-tab color; Dark reuses the scale with dark surfaces instead of inventing new hues.

| Theme | Token | Value |
|---|---|---|
| Dark | bg-page | neutral-950 |
| Dark | bg-surface | neutral-900 |
| Dark | text-body | neutral-100 |
| Dark | text-muted | neutral-400 |
| Dark | border-default | neutral-700 |
| Dark | border-input | neutral-600 |
| Dark | focus-ring | brand-400 |
| Dark | brand-600 | brand-400 |
| Dark | brand-50 | neutral-800 |
| Corporate Blue | brand-600 | #2563eb |
| Corporate Blue | brand-700 | #1d4ed8 |
| Corporate Blue | brand-800 | #1e40af |
| Industrial Teal | brand-600 | #0f766e |
| Industrial Teal | brand-700 | #115e59 |
| Industrial Teal | brand-800 | #134e4a |
| Neutral Mono | brand-600 | #52525b |
| Neutral Mono | brand-700 | #3f3f46 |
| Neutral Mono | brand-800 | #27272a |

## 3. Typography
| Token | Size / line-height | Weight | Usage |
|---|---|---|---|
| display | 30 / 1.4 | 700 | Page hero (web/mobile only) |
| h1 | 24 / 1.5 | 600 | Page title |
| h2 | 18 / 1.5 | 600 | Section title |
| body | 14–16 / 1.65 | 400 | Text (16 on mobile) |
| small | 12 / 1.6 | 400 | Captions, table meta |
| mono | 13 | 400 | Codes, amounts (tabular-nums) |

Font: [choose per app — e.g. IBM Plex Sans Thai for Thai UIs, Inter elsewhere]; fallback Tahoma, system-ui. Thai needs line-height ≥ 1.6.

## 4. Spacing, radius, elevation, motion, layers
- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48
- Radius: sm 4 · md 6 · lg 8 · xl 12 · full
- Shadow: sm (cards), md (dropdowns), lg (modals)
- Layout: container width, sidebar width, grid columns (breakpoints in §4.2)

The three tables below are exported by `export_tokens.py` to `tokens/` — keep the column order, one token per row, and the value formats shown. Rows with another value format are skipped with a warning.

### 4.1 Motion tokens
Durations in `ms` (or `s`); easings as `cubic-bezier(x1, y1, x2, y2)`, `linear`, `ease`, `ease-in`, `ease-out`, `ease-in-out` or `steps(n)`. Name durations `duration-*` and easings `ease-*`. Under `prefers-reduced-motion: reduce` every duration exports as `0ms` — never put essential information in an animation.
| Token | Value | Usage |
|---|---|---|
| duration-fast | 120ms | Hover, focus ring, toggles |
| duration-base | 200ms | Dropdowns, tabs, toasts in |
| duration-slow | 320ms | Dialogs, drawers, page-level transitions |
| ease-standard | cubic-bezier(0.2, 0, 0, 1) | Moves and resizes on screen |
| ease-enter | cubic-bezier(0, 0, 0.2, 1) | Elements entering (decelerate) |
| ease-exit | cubic-bezier(0.4, 0, 1, 1) | Elements leaving (accelerate) |

### 4.2 Breakpoints
Min widths, mobile-first, in `px`, ascending. Same names as the Tailwind screens the mock uses; the spec's layout rules (ux-spec.md) refer to these names.
| Token | Min width | Usage |
|---|---|---|
| sm | 640px | Large phones, landscape |
| md | 768px | Tablet — table becomes cards below this |
| lg | 1024px | Laptop — sidebar shown from here |
| xl | 1280px | Desktop — content max width |

### 4.3 Z-index (layers)
Integers, ascending from back to front. Use the token, never a raw number.
| Token | Value | Usage |
|---|---|---|
| base | 0 | Page content |
| sticky | 100 | Sticky headers, table headers |
| dropdown | 200 | Menus, selects, comboboxes |
| overlay | 300 | Scrim behind dialogs and drawers |
| modal | 400 | Dialogs, drawers |
| toast | 500 | Toasts, snackbars |
| tooltip | 600 | Tooltips |

## 5. Components
For each: anatomy, variants, sizes, states (default/hover/focus/disabled/loading/error), do / don't.
- Button (primary, secondary, ghost, danger)
- Input, Select/Combobox, Date picker, Checkbox/Radio, Toggle
- Table (density, sorting, selection, totals row)
- Badge / Status
- Card, Modal/Dialog, Toast, Banner
- Tabs, Breadcrumb, Sidebar/Top nav, Bottom tab bar (mobile)
- Empty state, Skeleton

### 5.1 Component mapping
How each design component maps to the code the developers use. Stack: [from the architecture doc — write `TBD` until it is chosen]. One row per component or variant used in the mock.
- **Design component**: a `mk-*` class (in backticks) or a hand-rolled component listed above.
- **Code component**: component + key prop · `TBD` · `custom <Name>` when it must be built.
- **Source**: library + path, or the project path to create for `custom`; `—` when Code is `TBD`.
- **Props / variants**: map variants and sizes **and the kit's state attributes** (`aria-busy`, `aria-invalid`, `aria-pressed`, `aria-current`) to the library's real prop — or write that the library sets it itself (e.g. shadcn `FormControl` sets `aria-invalid`). Never name a prop the library doesn't have.
- **Notes**: library defaults that bypass the tokens, e.g. a hard-coded `z-50` → use `z-modal` / `z-dropdown` from §4.3.

| Design component | Code component | Source | Props / variants | Notes |
|---|---|---|---|---|
| `mk-btn mk-btn-primary` | TBD | — | `mk-btn-sm` / default / `mk-btn-lg` → size · `aria-busy` → loading state | |

## 6. Iconography
Set: [Phosphor / Tabler / Fluent / Material Symbols] · Iconify prefix `[ph:]` · Style: [Regular] (active: [Fill]) · Sizes: 16 / 20 / 24 · Color: currentColor
Why this set: [one line — e.g. "Fluent reads instantly to users who live in Office/AX"]
Dev package: [e.g. @phosphor-icons/web (webfont, PHP/Yii) · @phosphor-icons/react]
Rules: no emoji in UI · icon + label for primary/destructive actions · icon-only buttons need aria-label + tooltip

| Purpose | Icon | Used in |
|---|---|---|
| add | | |
| edit | | |
| delete | | |
| search | | |

Imagery: [illustration style, or "none — text and icons only"]

## 7. Screen inventory
Every screen in the app. IDs match the wireframe and mockup.
Columns are read by name (`verify.py`). **Req ID**: the requirement IDs this screen serves, from the project's requirements doc (e.g. `R3`, `FR-01`, comma-separated), or `—` for system screens (404, error). **Priority**: `MVP` · `P2` · `P3` · `Later`. **Status**: `draft` · `review` · `approved` (developers may build it) · `changed` (was approved, then edited — see the changelog). Values are case-sensitive; no empty cells.
| ID | Screen | Module | Wireframe | Mockup | Req ID | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| login | Sign in | Auth | ✅ | ✅ | R1 | MVP | draft | |
