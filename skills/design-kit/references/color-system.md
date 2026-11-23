# Color System

Colors are defined once in `design.md`, then reused by the wireframes, the mockup (Tailwind config) and later by developers. Every color has a **role** — never pick a hex for a single element.

## Contents
1. Token structure
2. Building a palette
3. Contrast rules
4. Preset palettes
5. Status colors
6. Dark mode (optional)
7. Mapping to Tailwind

## 1. Token structure

Use three layers. Developers implement layer 2 and 3; layer 1 is the raw scale.

| Layer | Example | Purpose |
|---|---|---|
| Scale | `brand-50 … brand-900`, `neutral-50 … neutral-900` | Raw palette, 10 steps |
| Semantic | `primary`, `danger`, `success`, `warning`, `info` | Meaning |
| Usage | `bg-page`, `bg-surface`, `text-body`, `text-muted`, `border-default`, `focus-ring` | Where it's applied |

Scales required: **brand** (primary), **neutral** (gray, slightly tinted toward brand for harmony), and one scale each for **danger, success, warning, info**. Optionally an **accent** scale for highlights/charts.

## 2. Building a palette

1. Get the brand color from the user (logo, existing system, or a mood: "น่าเชื่อถือ", "สดใส", "พรีเมียม"). If none, pick a preset (section 4) suited to the product type and say so.
2. Place the brand color at step **600** (main buttons). Generate lighter steps 50–500 and darker 700–900 by keeping hue roughly constant, lowering saturation slightly at the extremes.
3. Neutral scale: hue of the brand at very low saturation (2–8%). Pure gray looks dead next to a colored brand.
4. Semantic colors: keep standard hues (red / green / amber / blue) so meaning stays obvious; adjust only lightness to match the brand's visual weight.
5. Chart palette: 6–8 colors that are distinguishable for color-blind users (vary lightness, not only hue). Put them in design.md as `chart-1 … chart-8`.

Limit: one brand hue + one optional accent. More hues make status colors harder to read.

## 3. Contrast rules (WCAG AA)

Check and record contrast ratios in design.md.

- Body text on background ≥ **4.5:1**
- Large text (≥ 18.66px bold or 24px) and UI components (borders of inputs, icons) ≥ **3:1**
- White text on `primary` button ≥ 4.5:1 — if the brand is light (yellow, light green), use dark text on it or use step 700 for buttons.
- Status badges: text step 700 on background step 50 usually passes; verify.

Compute contrast with relative luminance, or run this in the container:

```python
def lum(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def ratio(a,b):
    l1,l2=sorted([lum(a),lum(b)],reverse=True); return (l1+0.05)/(l2+0.05)
print(round(ratio('#ffffff','#2563eb'),2))
```

## 4. Preset palettes (step 600 shown; generate full scales)

`brand-600` is the link, selected-tab and focus color, so it must reach **4.5:1 on white**. Teal, green and orange are light at Tailwind's 600, so these presets use the next darker step as 600 — generate the rest of the scale around it.

| Preset | Brand 600 | On white | Neutral tint | Best for |
|---|---|---|---|---|
| **Corporate Blue** | `#2563eb` | 5.17 | slate | ERP, back-office, finance — calm, trusted |
| **Industrial Teal** | `#0f766e` | 5.47 | slate | Manufacturing, logistics, warehouse |
| **Deep Indigo** | `#4f46e5` | 6.29 | zinc | SaaS web apps, dashboards |
| **Fresh Green** | `#15803d` | 5.02 | stone | Finance/personal money apps, health |
| **Warm Orange** | `#c2410c` | 5.18 | stone | Consumer mobile, food, retail |
| **Neutral Mono** | `#18181b` | 17.72 | zinc | Minimal / premium; use accent for status |

For internal tools used all day, prefer lower saturation and lighter surfaces — strong colors fatigue the eye over hours.

## 5. Status colors

Keep consistent across every screen in the app and write them in design.md:

| Status | Badge bg / text | Example |
|---|---|---|
| Draft | neutral-100 / neutral-700 | ร่าง |
| Pending | warning-50 / warning-700 | รออนุมัติ |
| Approved / Success | success-50 / success-700 | อนุมัติแล้ว |
| Rejected / Error | danger-50 / danger-700 | ไม่อนุมัติ |
| Posted / Closed | info-50 / info-700 | ปิดแล้ว |

Never rely on color alone — badges always contain text; icons where space is tight.

## 6. Dark mode (only if requested or mobile consumer app)

Define usage tokens again for dark: `bg-page` neutral-950, `bg-surface` neutral-900, `text-body` neutral-100, `text-muted` neutral-400. Use brand step 400–500 for primary in dark mode (600 is too dim). Re-check contrast.

## 7. Mapping to Tailwind

In the mockup, put the full scales in the `const tokens` object (fed into `tailwind.config`) with the same names as design.md (`brand`, `neutral`, `danger`, ...). Then use classes like `bg-brand-600`, `text-neutral-500`. The names in design.md, the Tailwind config, and the spec must match exactly — this is what lets a developer move from mockup to real code without guessing.

For developers, run `scripts/export_tokens.py design.md tokens/` — it writes `tokens.css` (CSS variables, usage tokens referencing scale variables), `tailwind.config.js`, and `tokens.json` from the same tables, so the delivered code palette can never drift from design.md.
