# Procura — Design System

> Version: 1.1 · Updated: 2026-11-24 · Product type: Enterprise · Device model: Responsive web · Stack: Tailwind web · Dark mode: yes — light + dark
> Source of truth for colors, typography, spacing, and components. The wireframes, mockup, and UX spec must use the names defined here.

## 0. Assumptions
- Product name "Procura" is a placeholder (test project for the design-kit component kits).
- Internal tool for a mid-size Thai company; UI language English, amounts in THB, dates dd/MM/yyyy.
- Two roles: **Requester** (creates POs) and **Approver** (approves/rejects up to 500,000 THB). Sign-in with company username + password (no SSO in v1).
- Requesters mostly on desktop; approvers often approve from a phone between meetings.
- No requirements doc exists for this example, so requirement IDs are assumed: **R1** sign in · **R2** find and track POs · **R3** create and submit a PO · **R4** approve or reject a PO.
- Stack for the component mapping (§5.1) assumed: React + shadcn/ui.

## Changelog
| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-23 | Initial design system |
| 1.1 | 2026-11-24 | Hand-off tables added: §4.1–4.3 motion / breakpoint / z-index tokens, §5.1 component mapping, §7 Req ID / Priority / Status (all screens) |

## 1. Design principles
1. **Approve in one glance** — amount, supplier and status are always visible together; approvers never open a tab to decide.
2. **Prefer picking over typing** — supplier and cost center are pickers; PO number is generated.
3. **Status is never color alone** — every badge has a label and a dot; errors have text.
4. **Destructive steps name the object** — "Reject PO-2611-0042?", never "Are you sure?".

## 2. Colors

### 2.1 Brand scale
| Token | Hex | Usage |
|---|---|---|
| brand-50 | #eff6ff | Selected row, soft background |
| brand-100 | #dbeafe | Hover on soft background, avatar |
| brand-200 | #bfdbfe | |
| brand-300 | #93c5fd | |
| brand-400 | #60a5fa | Primary text/links in dark mode |
| brand-500 | #3b82f6 | |
| brand-600 | #2563eb | Links, focus ring |
| brand-700 | #1d4ed8 | Primary button (white text 6.70:1) |
| brand-800 | #1e40af | Primary hover/pressed |
| brand-900 | #1e3a8a | Text on brand-100 |

### 2.2 Neutral scale
| Token | Hex | Usage |
|---|---|---|
| neutral-50 | #f8fafc | Page background |
| neutral-100 | #f1f5f9 | Disabled field background |
| neutral-200 | #e2e8f0 | Dividers, skeleton |
| neutral-300 | #cbd5e1 | Input borders |
| neutral-400 | #94a3b8 | Empty-state icon, input hover |
| neutral-500 | #64748b | Muted text |
| neutral-600 | #475569 | |
| neutral-700 | #334155 | |
| neutral-800 | #1e293b | Body text |
| neutral-900 | #0f172a | Toast, tooltip background |

### 2.3 Semantic colors
| Token | 50 (bg) | 600 (main) | 700 (text) | Usage |
|---|---|---|---|---|
| danger | #fef2f2 | #dc2626 | #b91c1c | Rejected, errors, destructive actions |
| success | #f0fdf4 | #16a34a | #15803d | Approved |
| warning | #fffbeb | #d97706 | #b45309 | Pending approval |
| info | #f0f9ff | #0284c7 | #0369a1 | Submitted / informational |

### 2.4 Usage tokens
| Token | Light | Dark | Where |
|---|---|---|---|
| bg-page | neutral-50 | #020617 | App background |
| bg-surface | white | neutral-900 | Cards, tables, modals |
| text-body | neutral-800 | neutral-100 | Main text |
| text-muted | neutral-500 | neutral-400 | Helper text, captions |
| border-default | neutral-200 | neutral-700 | Dividers |
| border-input | neutral-300 | neutral-600 | Input borders |
| focus-ring | brand-600 | brand-400 | Keyboard focus |

### 2.5 Status mapping
| Status | Badge | Label |
|---|---|---|
| draft | mk-badge (neutral) | Draft |
| pending | mk-badge-warning | Pending approval |
| approved | mk-badge-success | Approved |
| rejected | mk-badge-danger | Rejected |

### 2.6 Chart palette
Not used in v1 (no dashboard).

### 2.7 Contrast checks
| Pair | Ratio | Pass |
|---|---|---|
| text-body on bg-page | 13.98 | AA |
| text-muted on bg-surface | 4.76 | AA |
| white on brand-700 (primary button) | 6.70 | AA |
| white on brand-600 | 5.17 | AA |
| warning-700 on warning-50 (Pending badge) | 4.84 | AA |
| success-700 on success-50 (Approved badge) | 4.79 | AA |
| danger-700 on danger-50 (Rejected badge, error alert) | 5.91 | AA |
| info-700 on info-50 | 5.57 | AA |
| danger-700 on white (field error text) | 6.47 | AA |
| text-body dark on bg-page dark | 18.41 | AA |
| text-muted dark on bg-surface dark | 6.96 | AA |
| white on brand-700 (dark-mode primary) | 6.70 | AA |
| brand-400 on bg-surface dark (dark links) | 7.02 | AA |
| focus ring brand-600 vs white (non-text, 3:1) | 5.17 | AA |

Dark-theme badges and alerts use text-body for text and keep the status hue in the dot/bar (engine `.theme-dark` rule) — 700-on-dark-tint pairs fall below 4.5.

### 2.9 Theme variants (mock theme picker)
| Theme | Token | Value |
|---|---|---|
| Dark | bg-page | #020617 |
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
| h1 | 24 / 1.5 | 600 | Page title |
| h2 | 18 / 1.5 | 600 | Section title |
| body | 14 / 1.65 (16 on mobile) | 400 | Text |
| small | 12 / 1.6 | 400 | Captions, table meta |
| mono | 14 | 400 | PO numbers, amounts (tabular-nums) |

Font: Inter; fallback system-ui. One typeface.

## 4. Spacing, radius, elevation, motion, layers
- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48
- Radius: md 6 (controls) · lg 8 (cards) · xl 12 (dialogs) · full (badges, chips)
- Shadow: sm (cards), md (menus), lg (dialogs)
- Layout: sidebar 240px (from `lg`), content max 1280px (breakpoints in §4.2)

### 4.1 Motion tokens
| Token | Value | Usage |
|---|---|---|
| duration-fast | 120ms | Hover, focus ring, chip toggle |
| duration-base | 200ms | Menus, tabs, toast in |
| duration-slow | 320ms | Reject dialog, mobile sheet |
| ease-standard | cubic-bezier(0.2, 0, 0, 1) | Moves and resizes |
| ease-enter | cubic-bezier(0, 0, 0.2, 1) | Dialog and toast entering |
| ease-exit | cubic-bezier(0.4, 0, 1, 1) | Dialog and toast leaving |

### 4.2 Breakpoints
| Token | Min width | Usage |
|---|---|---|
| sm | 640px | Large phones, landscape |
| md | 768px | Tablet — PO table becomes cards below this |
| lg | 1024px | Sidebar shown from here |
| xl | 1280px | Content max width |

### 4.3 Z-index (layers)
| Token | Value | Usage |
|---|---|---|
| base | 0 | Page content |
| sticky | 100 | Table header, mobile action bar, form footer |
| dropdown | 200 | Supplier picker, user menu |
| overlay | 300 | Scrim behind the reject dialog |
| modal | 400 | Reject dialog, discard confirm |
| toast | 500 | Approve / submit toasts |
| tooltip | 600 | Tooltips |

## 5. Components
Built from the design-kit component kits — wireframes `wf-*`, mock `mk-*` (states: default/hover/focus/disabled/loading/error are in the kit).
- Button — `mk-btn` primary / secondary / ghost / danger; sm / lg; `aria-busy` loading
- Field — `mk-field` + `mk-label` (`mk-req`) + `mk-input` / `mk-select` / `mk-textarea` + `mk-help` / `mk-error`
- Table — `mk-table` with `.num` amounts; becomes a card list below 768px
- Badge — `mk-badge-*` per §2.5
- Chips — `mk-chip` status filters (`aria-pressed`)
- Side nav — `mk-nav-item` (`aria-current="page"`); mobile uses a top app bar
- Tabs, breadcrumb, pagination, alert, dialog (`mk-scrim` + `mk-modal`), toast, skeleton, empty

### 5.1 Component mapping
Stack: React + shadcn/ui (assumed, §0).
| Design component | Code component | Source | Props / variants | Notes |
|---|---|---|---|---|
| `mk-btn mk-btn-primary` | `<Button variant="default">` | shadcn/ui `components/ui/button` | `mk-btn-sm` / `mk-btn-lg` → size sm / lg · `aria-busy` → loading (disabled + spinner) | one per view |
| `mk-btn mk-btn-secondary` | `<Button variant="outline">` | shadcn/ui `components/ui/button` | as primary | |
| `mk-btn mk-btn-ghost` | `<Button variant="ghost">` | shadcn/ui `components/ui/button` | as primary | |
| `mk-btn mk-btn-danger` | `<Button variant="destructive">` | shadcn/ui `components/ui/button` | as primary | "Reject order" only |
| `mk-btn mk-btn-icon` | `<Button size="icon">` | shadcn/ui `components/ui/button` | `aria-label` required | |
| `mk-field` + `mk-label` + `mk-input` + `mk-help` / `mk-error` | `<FormField>` + `<FormLabel>` + `<Input>` + `<FormDescription>` / `<FormMessage>` | shadcn/ui `components/ui/form` | `aria-invalid` → invalid · `mk-req` → required | error text from ux-spec Fields & validation |
| `mk-select` | `<Select>` | shadcn/ui `components/ui/select` | `aria-invalid` → invalid | cost center |
| `mk-textarea` | `<Textarea>` | shadcn/ui `components/ui/textarea` | `aria-invalid` → invalid | note, reject reason |
| `mk-check` | `<Checkbox>` | shadcn/ui `components/ui/checkbox` | | |
| `mk-table` | `<Table>` | shadcn/ui `components/ui/table` | `.num` → right-aligned, tabular-nums | becomes cards below `md` |
| `mk-badge-*` | custom `<StatusBadge>` | `src/components/status-badge.tsx` | PO status → variant per §2.5 | text + dot, never color alone |
| `mk-chip` | `<Toggle>` | shadcn/ui `components/ui/toggle` | `aria-pressed` → pressed | status filters, single-select |
| `mk-nav-item` | `<NavLink>` | react-router | `aria-current="page"` → active | |
| `mk-tabs` / `mk-tab` | `<Tabs>` / `<TabsTrigger>` | shadcn/ui `components/ui/tabs` | `aria-selected` → active value | |
| `mk-scrim` + `mk-modal` | `<Dialog>` | shadcn/ui `components/ui/dialog` | open via trigger; focus return built in | |
| `mk-alert-danger` | `<Alert variant="destructive">` | shadcn/ui `components/ui/alert` | | |
| `mk-breadcrumb` | `<Breadcrumb>` | shadcn/ui `components/ui/breadcrumb` | | |
| `mk-pagination` | `<Pagination>` | shadcn/ui `components/ui/pagination` | | server-side, 50 per page |
| `mk-skeleton` | `<Skeleton>` | shadcn/ui `components/ui/skeleton` | | |
| `mk-empty` | custom `<EmptyState>` | `src/components/empty-state.tsx` | title, body, action | |
| `mk-card` / `mk-stat` | `<Card>` | shadcn/ui `components/ui/card` | | |
| `mk-avatar` | `<Avatar>` | shadcn/ui `components/ui/avatar` | | |
| Toast | `<Toaster>` + `toast()` | sonner | announces politely | |

## 6. Iconography
Set: Phosphor · Iconify prefix `ph:` · Style: Regular · Sizes: 16 / 20 / 24 · Color: currentColor
Why this set: neutral, legible at 16px in dense tables; not the default of most AI builders.
Dev package: @phosphor-icons/react
Rules: no emoji in UI · icon + label for primary/destructive actions · icon-only buttons need aria-label + tooltip

| Purpose | Icon | Used in |
|---|---|---|
| add | ph:plus | po-list, design-system |
| edit | ph:pencil-simple | po-detail |
| delete | ph:trash | design-system |
| search | ph:magnifying-glass | po-list |
| retry | ph:arrow-clockwise | po-list error |
| empty | ph:tray | po-list empty |
| approve | ph:check-circle | po-detail |
| reject | ph:x-circle | po-detail |
| back | ph:arrow-left | po-detail, po-form |
| orders | ph:file-text | nav |
| suppliers | ph:buildings | nav |
| reports | ph:chart-bar | nav |
| notifications | ph:bell | top bar |

Imagery: none — text and icons only.

## 7. Screen inventory
Every screen in the app. IDs match the wireframe and mockup.
| ID | Screen | Module | Wireframe | Mockup | Req ID | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| login | Sign in | Auth | ✅ | ✅ | R1 | MVP | approved | |
| po-list | Purchase orders | Purchasing | ✅ | ✅ | R2, R4 | MVP | approved | table → cards on mobile |
| po-detail | Purchase order detail | Purchasing | ✅ | ✅ | R2, R4 | MVP | approved | approve / reject |
| po-form | New purchase order | Purchasing | ✅ | ✅ | R3 | MVP | approved | |
| not-found | Page not found | System | ✅ | — | — | MVP | approved | |
