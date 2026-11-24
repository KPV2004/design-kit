# [App] — Design QA
> Version 1.0 — matches design.md 1.0
> Two checks: the **pre-handoff checklist** before the design goes to developers, and the **build review** that compares the built app with mock.html. See `references/design-qa.md`.

## Pre-handoff checklist
The designer fills this before setting screens to `approved` in design.md §7. `Result`: `pass` · `fail` · `n/a` · `todo` — hand off only when nothing is `fail` or `todo`.

| ID | Check | Heuristic | Result | Notes |
|---|---|---|---|---|
| HC-01 | Every screen shows where the user is (title, active nav item, breadcrumb) | Visibility of system status | todo | |
| HC-02 | Every action shows progress and a result (busy button, toast, inline message) | Visibility of system status | todo | |
| HC-03 | Labels and messages use the users' words, per Voice & tone (design.md §8) | Match with the real world | todo | |
| HC-04 | Every destructive action names the object and can be cancelled or undone | User control and freedom | todo | |
| HC-05 | The same component, icon and word mean the same thing on every screen | Consistency and standards | todo | |
| HC-06 | Pickers, defaults and disabled-with-reason prevent errors before they happen | Error prevention | todo | |
| HC-07 | Options and current values are visible; nothing depends on remembering another screen | Recognition rather than recall | todo | |
| HC-08 | Frequent tasks have shortcuts (keyboard, bulk actions, remembered filters) | Flexibility and efficiency | todo | |
| HC-09 | One primary action per view; color only for status and that action | Aesthetic and minimalist design | todo | |
| HC-10 | Every error says what happened and how to fix it, using the exact text in ux-spec Fields & validation | Help users recover from errors | todo | |
| HC-11 | Empty, loading, error and permission states exist for every data screen (ux-spec States) | Help and documentation | todo | |
| HC-12 | Accessibility table complete; contrast, focus and target sizes pass (`verify.py`) | Accessibility | todo | |
| HC-13 | Long names, many rows and Thai text tested in the mock at desktop and mobile | Robustness | todo | |

## Tolerances
How close the build must be to mock.html. Anything outside these goes in the build review.

| Property | Tolerance | How to check |
|---|---|---|
| layout | same structure and order; responsive changes at the design.md §4.2 breakpoints | resize through each breakpoint |
| spacing | ±2px, and the value is on the spacing scale | DevTools box model vs the mock |
| color | exact token (no raw hex), in every theme | DevTools computed style; theme switch |
| typography | exact type token (size, weight, line-height) | DevTools computed style |
| icon | same icon name from design.md §6, same size | inspect element |
| copy | exact string from the ux-spec copy deck, every character | text compare |
| state | every state in the ux-spec States matrix reachable | force each state (network throttling, empty account) |
| interaction | behavior matches ux-spec Interactions & behavior | walk through each row |
| a11y | ux-spec Accessibility table: announcements, focus on open / return, tab order | keyboard only + screen reader |
| motion | motion token ±20ms; nothing moves under reduced motion | DevTools animations panel; OS reduced-motion setting |

## Build review
**Scope:** every screen with Status `approved` in design.md §7 × every state in the ux-spec States matrix × each device — `mobile` 375px · `tablet` at `md` · `desktop` at `lg` (§4.2) — × the Default theme plus Dark if shipped.
**Reference:** open `mock.html?frame=1#<screen-id>:mock` next to the build; set the theme with the toolbar (stored as `mk-theme` in localStorage) and the state with the state switcher (`data-state`). Pixel diffs only point at places to look — the Tolerances table decides.
**Pass:** no `blocker` or `major` row is `open` or `fixed` (`verify.py` warns while one is).

Round 1 — [yyyy-MM-dd] — build [commit or URL] — design [version] — reviewers: [names]

One row per difference. `Device`: `desktop` · `tablet` · `mobile`. `Theme`: `Default`, `all` or a §2.9 theme name. `State`: `default` · `empty` · `loading` · `error` · `success` · `permission`. `Property`: as in Tolerances. `Severity`: `blocker` (a state or flow is missing, or copy / error text is wrong) · `major` (wrong token, layout or accessibility) · `minor` (spacing, icon) · `cosmetic`. `Status`: `open` → `fixed` (developer) → `verified` (QA only) · `wontfix` (reason + who decided, in Evidence). `Evidence` (optional): screenshot path or note. Leave the table empty until the first round.

| ID | Screen | Device | Theme | State | Property | Expected | Actual | Severity | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
