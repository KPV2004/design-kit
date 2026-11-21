# [App name] — Design System

> Version: 1.0 · Updated: [dd/MM/yyyy] · Product type: [Enterprise / Web app / Native mobile / Mixed] · Device model: [Responsive web / Native mobile / Desktop-only]
> Source of truth for colors, typography, spacing, and components. The wireframes, mockup, and UX spec must use the names defined here.

## 0. Assumptions
List anything not confirmed by the user (brand, product name, login method...). Mark each as confirmed once the user agrees.

## Changelog
| Version | Date | Change |
|---|---|---|
| 1.0 | [date] | Initial design system |

## 1. Design principles
3–5 principles specific to this app (e.g. "ลดการพิมพ์ — ใช้ dropdown/scan ทุกครั้งที่ทำได้").

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
| Token | Value | Where |
|---|---|---|
| bg-page | neutral-50 | App background |
| bg-surface | white | Cards, tables, modals |
| text-body | neutral-800 | Main text |
| text-muted | neutral-500 | Helper text, captions |
| border-default | neutral-200 | Dividers, input borders |
| focus-ring | brand-500 | Keyboard focus |

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

## 3. Typography
| Token | Size / line-height | Weight | Usage |
|---|---|---|---|
| display | 30 / 1.4 | 700 | Page hero (web/mobile only) |
| h1 | 24 / 1.5 | 600 | Page title |
| h2 | 18 / 1.5 | 600 | Section title |
| body | 14–16 / 1.65 | 400 | Text (16 on mobile) |
| small | 12 / 1.6 | 400 | Captions, table meta |
| mono | 13 | 400 | Codes, amounts (tabular-nums) |

Font: IBM Plex Sans Thai, fallback Tahoma, system-ui. Thai needs line-height ≥ 1.6.

## 4. Spacing, radius, elevation
- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48
- Radius: sm 4 · md 6 · lg 8 · xl 12 · full
- Shadow: sm (cards), md (dropdowns), lg (modals)
- Layout: container width, sidebar width, grid columns, breakpoints

## 5. Components
For each: anatomy, variants, sizes, states (default/hover/focus/disabled/loading/error), do / don't.
- Button (primary, secondary, ghost, danger)
- Input, Select/Combobox, Date picker, Checkbox/Radio, Toggle
- Table (density, sorting, selection, totals row)
- Badge / Status
- Card, Modal/Dialog, Toast, Banner
- Tabs, Breadcrumb, Sidebar/Top nav, Bottom tab bar (mobile)
- Empty state, Skeleton

## 6. Iconography
Set: [Phosphor / Tabler / Fluent / Material Symbols] · Iconify prefix `[ph:]` · Style: [Regular] (active: [Fill]) · Sizes: 16 / 20 / 24 · Color: currentColor
Why this set: [one line — e.g. "Fluent ให้ผู้ใช้ที่คุ้นกับ Office/AX จำปุ่มได้ทันที"]
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
| ID | Screen | Module | Wireframe | Mockup | Notes |
|---|---|---|---|---|---|
| login | เข้าสู่ระบบ | Auth | ✅ | ✅ | |
