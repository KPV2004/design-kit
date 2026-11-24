# [App] — UX Spec
> Version 1.0 — matches design.md 1.0
> **This spec must stand alone.** A developer implements from it without reopening app code — anything they must know (behavior, exact error text, endpoints, dark theme, edge cases) lives in these tables, never only in a wireframe annotation. When designing for an existing codebase, extract the facts first (validators, error strings, API client, theme/l10n files) and paste them here verbatim.

## Summary

## Assumptions & open questions

## User flow
```mermaid
flowchart LR
  login[Sign in] -->|success| list[Document list]
  list -->|new| detail[Detail / form]
  detail -->|save| list
```

## Roles & permissions
Who may do what on each screen. `verify.py` checks every role and screen ID. Role keys are lowercase kebab-case; an app without separate rights uses one role `user` (plus `guest` if screens exist before sign-in).

### Roles
| Role | Description |
|---|---|
| guest | not signed in — auth and system screens only |
| user | signed-in user |

### Permission matrix
`Screen` takes one ID, several comma-separated, or `*` (every screen); `Role` takes a declared role or `*` (every role). Cells: `✅` · `✅ (condition)` · `—` (not allowed). View `—` means the screen shows its permission state from the States table (403 or redirect), not just a hidden menu item.
| Role | Screen | View | Create | Edit | Approve | Delete |
|---|---|---|---|---|---|---|
| guest | login | ✅ | — | — | — | — |
| user | list, detail | ✅ | — | — | — | — |
| user | form | ✅ | ✅ | ✅ (own only) | — | — |

## Screens
One `### [id]` heading per inventory screen (several IDs may share a heading). Every `.anno` marker in the wireframe/mockup must have a matching entry in a table below — annotations are pointers, these tables are the source of truth.

### [screen-id] Screen name
- **Purpose:**
- **Layout:** including every responsive rule a dev must implement, named by the design.md §4.2 breakpoints (e.g. "table becomes cards below `md`", "sidebar shown from `lg`") — never breakpoint details only in an annotation
- **Key components:**
- **Behavior:** the things code would otherwise have to answer
  - Focus & input: autofocus? keyboard type (decimal / email / phone), input formatters (currency grouping, dd/MM/yyyy)
  - Primary action: on success — pop back, navigate, or stay + toast? on failure — stay, and where the error shows
  - Optimistic updates: does the list change immediately or after the request returns?
  - Auto-save vs explicit save: is there a Save button at all? what triggers persistence?
- **Annotations:** (1) … (2) … — match the `.anno` markers in wireframe and mockup

## Acceptance criteria
One table for the whole app — QA writes tests from it. Every inventory screen appears in at least one row. **ID**: `AC-01`, `AC-02`… (unique, never reused). **Screen**: one ID or several comma-separated. **Req ID**: from the inventory, or `—`. **Then** must be observable (text on screen, saved value, screen reached); for errors, quote the exact error text from Fields & validation.

| ID | Screen | Req ID | Given | When | Then |
|---|---|---|---|---|---|
| AC-01 | login, list | R1 | a user with a valid account | they sign in | Documents opens |
| AC-02 | list, detail | R2 | a user with 3 documents | they open the first row | its detail opens |
| AC-03 | form | R3 | the amount is 0 | the user presses Save | "Enter an amount greater than 0." shows under the field and nothing is saved |

## States
State matrix — every screen that shows data gets a row. Write "n/a" where a state doesn't apply; don't leave states only in annotations.

| Screen | Empty | Loading | Error | Success | Permission |
|---|---|---|---|---|---|
| list | first use: "No documents yet" + CTA | skeleton rows | banner + Retry | — | viewer: read-only |

## Fields & validation
Exact error wording — developers paste it verbatim into the UI and register each string in the copy deck. If the app already has the strings in code, use those, not paraphrases.

| Screen | Field | Type | Required | Rule | Error message (exact wording) |
|---|---|---|---|---|---|
| form | amount | decimal | yes | > 0 | "Enter an amount greater than 0." |

## Interactions & behavior
Cross-screen behavior that a wireframe can't show. If a hidden quirk exists (auto-save, optimistic update, read-only mode), it gets a row here.

| Screen | Trigger | Behavior |
|---|---|---|
| form | Save success | pop back to the list, highlight the new row |
| form | Save fails (409) | stay on the form, inline error, values kept |

## Copy deck
Every UI string with exact wording per locale (use the app's real locales, e.g. EN + TH). Strings live here — not scattered across screens or code.

| Key | Screen | EN | TH | Notes |
|---|---|---|---|---|
| list.empty.title | list | No documents yet | ยังไม่มีรายการ | reused on the dashboard |

## Formats & locale
How every date, time, number and currency is shown, per locale. Patterns are CLDR/ICU. Thai UIs state the era (Buddhist พ.ศ. or Gregorian ค.ศ.). APIs exchange ISO 8601 and plain numbers; formatting happens only in the UI.

| Type | Locale | Pattern | Example | Notes |
|---|---|---|---|---|
| date | en-GB | dd/MM/yyyy | 24/11/2026 | |
| date | th-TH | d MMM yyyy (Buddhist era) | 24 พ.ย. 2569 | |
| time | all | HH:mm (24 h) | 14:05 | |
| datetime | all | date + " " + time | 24/11/2026 14:05 | |
| timezone | all | Asia/Bangkok, stored in UTC | — | show the zone only if users span zones |
| number | all | #,##0.## | 1,234.5 | tabular-nums in tables |
| currency | th-TH | #,##0.00 | 50,000.00 | THB; negative -1,200.00 |
| plural | en | one / other | 1 item · 3 items | Thai has no plural forms — one string |

## Dev diagrams
### Data model (ER)
```mermaid
erDiagram
  USER ||--o{ DOCUMENT : creates
```

### Document status (state)
```mermaid
stateDiagram-v2
  [*] --> draft
```

### Save document (sequence)
```mermaid
sequenceDiagram
  actor U as User
  participant API
  U->>API: POST /documents
```

## API contract
Method, path, request/response fields and errors — copied from the existing API client when there is one, never invented silently. Endpoint paths, status names and field names must match the ER diagram, state diagrams, and Fields table exactly.

| Method | Path | Used by (screen ID) | Request body | Response | Errors (status → message shown) |
|---|---|---|---|---|---|
| POST | /documents | form | `{ name, amount }` | 201 → document | 409 → "Already posted by another user" |

## Accessibility
One row per inventory screen (`verify.py` checks). No empty cells — write `n/a`. **Announce**: what a screen reader hears without moving focus, as `polite: …` or `assertive: …` (errors), several joined with ` · `. **Focus on open**: what gets focus when the screen or dialog opens. **Focus return**: where focus goes after a dialog/sheet closes or after Save. **Tab order**: elements joined with `→`.

| Screen | Announce (aria-live) | Focus on open | Focus return | Tab order |
|---|---|---|---|---|
| login | assertive: sign-in error | email field | n/a | email → password → Sign in → Forgot password |
| list | polite: result count after filtering | h1 "Documents" | back from detail: the row that was opened | search → filters → New → table rows → pagination |
| detail | polite: "Saved" toast | h1 document name | dialog closes → the button that opened it | back → actions → content |
| form | assertive: error summary on a failed save | first field | after a failed save: first invalid field | fields in order → Cancel → Save |

### Global
- Target size ≥ 24×24 CSS px (WCAG 2.2 SC 2.5.8); the kit uses 40px, 44px on touch
- Usable at 200% zoom; reflows at 320px width without horizontal scroll (data tables excepted)
- Mobile: layouts hold at the OS's largest text size (dynamic type); no fixed-height text containers
- Honour `prefers-reduced-motion` (motion tokens export as 0ms)
- Status never by color alone — badge text or icon too

## Risks for implementation
