# Procura — Design QA
> Version 1.2 — matches design.md 1.2
> Pre-handoff checklist (designer) and build review against mock.html (designer + QA). See the design-kit reference `design-qa.md`.

## Pre-handoff checklist
| ID | Check | Heuristic | Result | Notes |
|---|---|---|---|---|
| HC-01 | Every screen shows where the user is (title, active nav item, breadcrumb) | Visibility of system status | pass | breadcrumb on po-detail |
| HC-02 | Every action shows progress and a result (busy button, toast, inline message) | Visibility of system status | pass | Sign in / Submit use aria-busy; toasts after approve, reject, submit |
| HC-03 | Labels and messages use the users' words, per Voice & tone (design.md §8) | Match with the real world | pass | "order", "approve / reject" |
| HC-04 | Every destructive action names the object and can be cancelled or undone | User control and freedom | pass | "Reject PO-…?"; discard confirm on the form |
| HC-05 | The same component, icon and word mean the same thing on every screen | Consistency and standards | pass | |
| HC-06 | Pickers, defaults and disabled-with-reason prevent errors before they happen | Error prevention | pass | supplier picker; approvers land on Pending |
| HC-07 | Options and current values are visible; nothing depends on remembering another screen | Recognition rather than recall | pass | amount, supplier, status together in the detail header |
| HC-08 | Frequent tasks have shortcuts (keyboard, bulk actions, remembered filters) | Flexibility and efficiency | n/a | bulk approve is out of scope for v1 (§0); filters persist in the URL |
| HC-09 | One primary action per view; color only for status and that action | Aesthetic and minimalist design | pass | |
| HC-10 | Every error says what happened and how to fix it, using the exact text in ux-spec Fields & validation | Help users recover from errors | pass | |
| HC-11 | Empty, loading, error and permission states exist for every data screen (ux-spec States) | Help and documentation | pass | |
| HC-12 | Accessibility table complete; contrast, focus and target sizes pass (`verify.py`) | Accessibility | pass | |
| HC-13 | Long names, many rows and Thai text tested in the mock at desktop and mobile | Robustness | pass | long supplier names wrap to 2 lines on cards |

## Tolerances
| Property | Tolerance | How to check |
|---|---|---|
| layout | same structure and order; table becomes cards below `md`, sidebar from `lg` | resize through each breakpoint |
| spacing | ±2px, and the value is on the spacing scale | DevTools box model vs the mock |
| color | exact token (no raw hex), in Default and Dark | DevTools computed style; theme switch |
| typography | exact type token; amounts in tabular figures | DevTools computed style |
| icon | same Phosphor icon name from design.md §6, same size | inspect element |
| copy | exact string from the ux-spec copy deck, every character | text compare |
| state | every state in the ux-spec States matrix reachable | throttle network; empty test account; approver vs requester |
| interaction | behavior matches ux-spec Interactions & behavior | walk through each row |
| a11y | ux-spec Accessibility table: announcements, focus on open / return, tab order | keyboard only + VoiceOver |
| motion | motion token ±20ms; nothing moves under reduced motion | DevTools animations panel; OS setting |

## Build review
**Scope:** every screen with Status `approved` × every state in the ux-spec States matrix × `mobile` 375px · `tablet` at `md` · `desktop` at `lg` × Default and Dark.
**Reference:** `mock.html?frame=1#<screen-id>:mock` beside the build.
**Pass:** no `blocker` or `major` row is `open` or `fixed`.

Round 1 — 2026-11-24 — build example (no real build; illustrative rows) — design 1.2 — reviewers: Designer, QA

| ID | Screen | Device | Theme | State | Property | Expected | Actual | Severity | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| DQ-01 | po-list | mobile | Default | default | layout | rows become cards below `md` | table scrolls sideways at 375px | major | verified | example row |
| DQ-02 | po-detail | desktop | Dark | default | color | Approve button `brand-600` (dark theme value) | raw `#2563eb` | major | verified | example row |
| DQ-03 | po-form | mobile | Default | error | copy | "Enter an amount above 0." | "Amount is required" | blocker | verified | example row |
| DQ-04 | login | tablet | all | default | spacing | card padding 24 (spacing token) | 22px | minor | wontfix | within ±2px — closed by Designer |
