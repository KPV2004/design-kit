# Iconography

Icons are one of the fastest giveaways of a generated UI. The goal: icons that look chosen by a designer for *this* product, used sparingly, and consistent enough that a developer can reproduce them exactly.

## Contents
1. What makes icons look "AI-generated"
2. Choosing a set
3. Rules of use
4. Icon map (in design.md)
5. Using icons in mockups
6. Developer handoff

## 1. What makes icons look "AI-generated"

Avoid all of these unless the user explicitly asks:

- **Emoji as UI icons** (✨ 🚀 📊 ✅ 💡 👁 🔒). Emoji render differently per OS, can't be colored or sized consistently, and scream "prompted". Never in screens — buttons, empty states, headings, toasts, password toggles.
- **Sparkles / magic wand / robot** anywhere the feature isn't actually AI.
- **An icon on every heading, card, and list item.** Decoration-icons dilute the ones that carry meaning.
- **The feature-card trope**: a grid of cards each with an icon in a pastel rounded square + title + one line. Use it only on a real marketing page, and even then vary it.
- **Gradient or multicolor icons**, glowing icons, icons in colored circles for no status reason.
- **Lucide by default.** It is a fine set, but it's the default of shadcn/ui and most AI app builders, so a Lucide-everywhere UI reads as generated. Pick it only when the user's stack already uses it.
- **Mixed sets** (Lucide arrows + Heroicons user + Material settings) — stroke widths and corner radii clash.
- **Wrong metaphors**: rocket for "start", lightbulb for "tips", target for "goals", shield-check for anything security-ish.

## 2. Choosing a set

Pick **one** set per product and record it in design.md §6. Recommendations by product type:

| Product | Recommended set | Iconify prefix | Why |
|---|---|---|---|
| ERP / back-office in a Microsoft environment (Dynamics AX/365, Office users) | **Fluent UI System Icons** (Regular 20, Filled for active) | `fluent:` (e.g. `fluent:add-20-regular`) | Same visual language as Office/Dynamics — users recognize Save, Filter, Print instantly |
| Other internal tools, dashboards, admin | **Tabler Icons** (stroke 1.5–2) | `tabler:` | 5,000+ icons covering niche business concepts (warehouse, barcode, invoice), neutral and crisp |
| Customer-facing web app / SaaS | **Phosphor** (Regular; Bold for emphasis) | `ph:` (`ph:plus`, `ph:plus-bold`, `ph:house-fill`) | Distinctive slightly-rounded character, 6 weights; doesn't look like default AI output |
| Consumer / friendly product (personal finance, lifestyle) | **Phosphor** Regular, or Duotone for illustrations only | `ph:` / `ph:*-duotone` | Warm without being childish |
| Native iOS | SF Symbols (design reference; mock with Phosphor Regular) | `ph:` | SF Symbols can't be embedded in web mockups; Phosphor is closest in feel |
| Native Android | **Material Symbols** (Outlined, weight 400) | `material-symbols:` | Platform convention |
| Existing product | Whatever it already uses | — | Consistency beats preference |

Other good, less-common sets: Remix Icon (`ri:`), Iconoir (`iconoir:`). Heroicons (`heroicons:`) is small and strongly associated with Tailwind UI templates.

## 3. Rules of use

1. **Icons support labels, they don't replace them.** Primary and destructive actions: icon + text. Icon-only buttons only for universally known actions (close, search, more, edit-in-row) and always with `aria-label` + tooltip.
2. **One style per state**: outline/regular everywhere; filled only for the *active* state (selected nav tab, toggled favorite).
3. **Sizes on a grid**: 16 (dense tables, inline with small text), 20 (buttons, inputs, nav), 24 (mobile tab bar, page header actions). Never arbitrary sizes. Keep stroke width fixed across sizes.
4. **Color = text color** (`text-neutral-600`/`currentColor`). Use brand color only inside primary buttons/links; semantic colors only for status (danger icon in an error banner).
5. **Align to text**: vertically centered with the label, 6–8px gap; in inputs, 12px from the edge.
6. **Familiar metaphors first**: trash = delete, pencil = edit, magnifier = search, funnel = filter, down-arrow-tray = download, printer = print, eye / eye-slash = show/hide password, ellipsis = more. For ERP, follow the metaphor users already know from their current system.
7. **Budget**: a typical screen needs 3–8 distinct icons. If you count more than ~12, remove decoration.
8. **Empty states**: one simple icon (48px, neutral-400) or none — not an emoji, not a cartoon.

## 4. Icon map (in design.md)

design.md §6 lists every icon the app uses, by purpose, so the same action always gets the same icon:

```markdown
## 6. Iconography
Set: Phosphor · Iconify prefix `ph:` · Style: Regular (active: Fill) · Sizes: 16 / 20 / 24
Dev package: @phosphor-icons/web (webfont) or @phosphor-icons/react

| Purpose | Icon | Used in |
|---|---|---|
| add | ph:plus | ปุ่มสร้างใหม่ |
| edit | ph:pencil-simple | แก้ไขในแถวตาราง |
| delete | ph:trash | ลบ (danger) |
| search | ph:magnifying-glass | ช่องค้นหา |
| show-password | ph:eye | ช่องรหัสผ่าน |
| hide-password | ph:eye-slash | ช่องรหัสผ่าน |
```

Purpose keys are kebab-case. Every icon in the mockup must come from this table.

## 5. Using icons in mockups

The mockup template loads the Iconify web component, which serves every set above from one script:

```html
<iconify-icon icon="ph:plus" width="20" aria-hidden="true"></iconify-icon>
```

- Copy the icon map into the mockup's `const icons = { add: 'ph:plus', ... }` — the Design system tab renders it so the user can review the set.
- Write icons as `<iconify-icon icon="...">` with the exact name from the map. Icon names are easy to misremember; `verify.py` loads every icon and reports names that don't exist, icons not in the map, and mixed prefixes.
- Decorative icons: `aria-hidden="true"`. Icon-only buttons: `aria-label` on the button.
- Wireframes: icons optional; if used, the same names in neutral gray so structure stays the focus.

## 6. Developer handoff

Name the package for the developer's stack in design.md:

| Set | Web font / plain HTML (PHP, Yii, server-rendered) | React |
|---|---|---|
| Phosphor | `@phosphor-icons/web` → `<i class="ph ph-plus"></i>` | `@phosphor-icons/react` |
| Tabler | `@tabler/icons-webfont` → `<i class="ti ti-plus"></i>` | `@tabler/icons-react` |
| Fluent | SVGs from `@fluentui/svg-icons` | `@fluentui/react-icons` |
| Material Symbols | Google Fonts `Material Symbols Outlined` | `@mui/icons-material` or font |
| Any | — | `@iconify/react` with the same names as the mockup |

Prefer pinned versions and self-hosting the font/SVGs in production rather than loading from a CDN at runtime.
