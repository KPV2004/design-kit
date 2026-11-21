# Enterprise / ERP / Back-office Patterns

Users here are trained, repeat users who live in the tool for hours. Optimize for throughput, accuracy, and scanning dense data — not first-impression delight.

## Contents
1. List / search screens
2. Data entry forms
3. Header–lines documents (orders, journals)
4. Reports
5. Dashboards
6. Approval & status workflows
7. Common pitfalls

## 1. List / search screens
- Layout: page title + primary action (top right) → filter bar → result table → pagination/footer totals.
- Filters: most-used 3–5 filters visible inline; the rest in "ตัวกรองเพิ่มเติม". Show active filters as removable chips. Preserve filters when the user returns from a detail page.
- Table: sticky header, right-aligned numbers with thousand separators, fixed decimals per column, monospace or tabular-nums for codes and amounts (`tabular-nums` class).
- Row density: compact (py-1.5 to py-2). Offer column show/hide only if > 10 columns.
- Bulk actions appear only when rows are selected, in a bar showing "เลือก 12 รายการ".
- Large volume: always design server-side paging and say "แสดง 1–50 จาก 12,431" — never imply loading everything. Flag in Risks if a filter would be unindexed or unbounded.
- Empty result vs. no data at all are different states: "ไม่พบข้อมูลตามเงื่อนไข — ล้างตัวกรอง" vs. "ยังไม่มีรายการ — สร้างรายการแรก".

## 2. Data entry forms
- Group fields into labelled sections that mirror the paper form or the user's mental order.
- Labels above inputs (scan faster, handle long Thai labels). Mark required with * and explain once at top.
- Tab order follows visual order; Enter should not submit a multi-field form accidentally.
- Lookups (customer, item, warehouse): searchable combobox showing code + name; allow typing the code directly — power users know codes by heart.
- Show computed fields (totals, tax) as read-only with a subtle background, updated live.
- Unsaved-changes guard on navigation away.
- Save vs. Save & New vs. Post/Submit — make the irreversible one visually distinct.

## 3. Header–lines documents
- Header (customer, dates, references) collapsible after filled; lines grid takes most space.
- Editable grid: inline editing, add-row at bottom, keyboard navigation (arrows, Tab, Enter = next row), duplicate-line action.
- Line-level validation shown in the cell + summary count at top ("มี 2 รายการที่ต้องแก้ไข").
- Footer: totals right-aligned, sticky at the bottom.
- Status badge near the document number; lock fields once posted and explain why.

## 4. Reports
- Parameter panel first (date range presets: วันนี้, เดือนนี้, เดือนก่อน, กำหนดเอง), then Run.
- Show the parameters used above the result so a printed/exported report is self-describing.
- Group/subtotal rows visually distinct (bold, light background). Grand total at bottom.
- Export (Excel/CSV/PDF) as secondary actions. Note in Risks if export could exceed reasonable row limits.
- Long-running reports: show progress or queue ("ระบบจะแจ้งเมื่อรายงานพร้อม").

## 5. Dashboards
- Start from decisions: which question does each widget answer? Cut widgets that don't drive an action.
- Top row: 3–5 KPI cards (value, comparison vs. previous period, trend arrow colored by good/bad not up/down).
- Every KPI should drill down to the list behind it.
- Show "ข้อมูล ณ 20/11/2026 09:30" — stale data is a common source of wrong decisions.

## 6. Approval & status workflows
- Show a status timeline/stepper: who did what, when.
- Approver view: everything needed to decide on one screen; Approve / Reject (reason required) / Return.
- Status colors consistent system-wide: draft = gray, pending = amber, approved = green, rejected = red, posted/closed = blue/slate.

## 7. Common pitfalls
- Designing with 5 rows when production has 50,000.
- Dates without clear format (use dd/MM/yyyy; specify พ.ศ. vs ค.ศ. explicitly in the spec).
- Amounts without currency or decimal rules.
- No double-submit protection on Post/Save.
- Hiding the primary action below the fold on long forms — use a sticky action bar.
