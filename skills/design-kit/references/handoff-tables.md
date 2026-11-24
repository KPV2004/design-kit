# Hand-off Tables

How to fill the tables a developer, QA or PM reads first: roles & permissions, acceptance criteria, inventory priority/status, component mapping and formats. Column names are exact — `verify.py` reads them by name.

## Contents
1. Screen inventory: Req ID, Priority, Status
2. Roles & permissions
3. Acceptance criteria
4. Component mapping
5. Formats & locale

## 1. Screen inventory: Req ID, Priority, Status (design.md §7)
- **Req ID** links each screen to the requirement it serves (`R3`, `FR-01`, comma-separated). Take the IDs from the project's requirements doc; never invent them — if there is none, ask the PM or record `R1…` IDs in design.md §0 as assumptions. `—` only for system screens (404, error, maintenance).
- **Priority** sets build order: `MVP` (first release), `P2`, `P3`, `Later`. A screen on the primary flow is `MVP` even if it is boring (sign-in, empty state, 403).
- **Status** tells developers what is stable: `draft` (being designed) → `review` (with the user/PM) → `approved` (build it). When an approved screen is edited, set `changed` and add a changelog row; it returns to `approved` after the next review.
- Values are case-sensitive and never empty — `verify.py` errors otherwise.

## 2. Roles & permissions (ux-spec.md)
- List roles from the requirements (job titles users recognise), as lowercase kebab-case keys with a one-line description. Include `guest` when screens exist before sign-in. No separate rights → one role `user`.
- Matrix columns are fixed: `Role | Screen | View | Create | Edit | Approve | Delete`. Other actions (export, print, post) go in the condition text or the screen's Behavior list.
- Cells: `✅`, `✅ (condition)` for row-level rules ("own only", "while Draft", "≤ 50,000 THB"), `—` for not allowed. Conditions are short; the full rule goes in Interactions & behavior.
- `*` in Role or Screen covers every role / every screen (e.g. `* | not-found`). One row per role/screen pair otherwise.
- Every `—` under View needs a matching Permission cell in the States table: 403 page, redirect, or read-only. Every condition needs a matching disabled-with-reason state in the mock.
- Keep it consistent with the API contract: an action a role cannot perform must also return 403 from the endpoint — tell the Tech Lead/Backend when the matrix changes.

## 3. Acceptance criteria (ux-spec.md)
- One table, `ID | Screen | Req ID | Given | When | Then`; IDs `AC-01`, `AC-02`… never renumbered or reused (QA's test cases point to them).
- At least one row per inventory screen; flows that span screens list them all in Screen.
- **Given** — the starting state and role ("an approver with a pending PO"). **When** — one user action, in the user's words, not the button's CSS. **Then** — observable: text on screen, saved value, screen reached. Quote error text exactly from Fields & validation.
- Cover per screen, in this order: the main success path, one validation error with recovery, one permission case if roles differ, and the empty state for lists.
- Each Req ID in the inventory should have at least one AC; if a requirement has none, it is untested.

## 4. Component mapping (design.md §5.1)
- Ask the Tech Lead / Frontend for the stack and component library before filling it; until then Code = `TBD`, Source = `—`.
- One row per `mk-*` component or variant used in the mock, plus every hand-rolled component listed in §5.
- New components: `custom <StatusBadge>` with the path to create in Source, so developers don't guess names.
- Props / variants must map the kit's state attributes as well as visual variants — `aria-busy`, `aria-invalid`, `aria-pressed`, `aria-current` — these are the states developers most often drop. Map each to the library's real prop, or write that the library sets it itself (shadcn `FormControl` sets `aria-invalid`; Radix `ToggleGroup type="single"` uses radio semantics). Sizes use the kit's names: `mk-btn-sm` / default / `mk-btn-lg` (the kit has no md).
- Map to the library's **real** API — these names are design-side states, not props every library has (shadcn/ui `Button` has no `loading`; `aria-invalid` comes from `FormControl`; Radix Select puts it on the trigger). Note where the library's accessibility differs from the mock (e.g. a single-select toggle group uses radio semantics instead of `aria-pressed`).
- In Notes, map library defaults that bypass the tokens: a hard-coded z-index (shadcn `z-50` in dialog / select / popover) → the §4.3 token (`z-modal`, `z-dropdown`); a breakpoint the exported config doesn't define (`2xl`) → add it to §4.2.
- Non-web stacks: use the platform widget names (Flutter `FilledButton`, React Native `Pressable`) and keep §2.8 colour mapping in step.

## 5. Formats & locale (ux-spec.md)
- Columns `Type | Locale | Pattern | Example | Notes`. Cover at least: date, time, datetime, timezone, number, currency, plural (add percent when used).
- Locale is BCP 47 (`th-TH`, `en-US`) or `all`. Patterns are CLDR/ICU (`dd/MM/yyyy`, `#,##0.00`) so developers can pass them to `Intl` / `intl` / ICU directly.
- Thai: state the era (พ.ศ. = Gregorian + 543), and whether month names are abbreviated (`พ.ย.`). Thai has no plural forms — one string; keep the `plural` row so English isn't forgotten.
- Currency: symbol or code, decimals, negative format, and the column alignment in tables (right, tabular-nums).
- APIs carry ISO 8601 dates in UTC and unformatted numbers; formatting is UI-only — say so in Notes.
- Sample data in wireframes and mock must follow these patterns.
